from __future__ import annotations

import importlib.util
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from services.ai_service import AIService
from services.ai_providers import LocalAIProvider


def _load_main_module():
    project_root = Path(__file__).resolve().parents[1]
    main_path = project_root / "main.py"

    spec = importlib.util.spec_from_file_location("lore_prototype_main", main_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


main = _load_main_module()


def _unique_user(prefix: str):
    suffix = uuid4().hex[:8]
    return {
        "username": f"{prefix}_{suffix}",
        "email": f"{prefix}_{suffix}@test.com",
        "password": "safe1234",
    }


def _register(client: TestClient, user: dict[str, str]):
    response = client.post("/auth/register", json=user)
    assert response.status_code == 200, response.text


def _login(client: TestClient, user: dict[str, str]) -> str:
    response = client.post(
        "/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_lore(client: TestClient, token: str, payload: dict[str, object]) -> dict:
    response = client.post("/lore/", headers=_headers(token), json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_ai_endpoints_and_discovery_mvp_behavior():
    client = TestClient(main.app)
    AIService.set_provider(LocalAIProvider())

    user = _unique_user("aiuser")
    other = _unique_user("doctor")
    _register(client, user)
    _register(client, other)

    user_token = _login(client, user)
    other_token = _login(client, other)

    user_lore = _create_lore(
        client,
        user_token,
        {
            "person": "Caro Test",
            "profession": "Doctor",
            "years_experience": 20,
            "theme": "medicine",
            "question": "What matters most in rural hospitals?",
            "lore": "I have worked as a doctor for twenty years helping children in rural hospitals. Compassion and consistent care matter every day.",
        },
    )
    other_lore = _create_lore(
        client,
        other_token,
        {
            "person": "Mira Care",
            "profession": "Nurse",
            "years_experience": 14,
            "theme": "healthcare",
            "question": "How do you support patients in community clinics?",
            "lore": "Community clinics need patient care, teamwork, and steady healthcare routines for families.",
        },
    )

    extract_response = client.post(
        "/ai/extract-themes",
        json={
            "text": "I have worked as a doctor for twenty years helping children in rural hospitals.",
        },
    )
    assert extract_response.status_code == 200, extract_response.text
    themes = extract_response.json()["themes"]
    assert "medicine" in themes
    assert "rural health" in themes
    assert "children" in themes

    summary_response = client.post(
        "/ai/summarize",
        json={
            "text": (
                "I have worked as a doctor for twenty years in rural hospitals. "
                "Most of my work focuses on children and families who need consistent care. "
                "The lesson is that compassionate healthcare starts with listening carefully."
            )
        },
    )
    assert summary_response.status_code == 200, summary_response.text
    summary = summary_response.json()["summary"]
    assert "doctor" in summary.lower() or "healthcare" in summary.lower()
    assert summary != "doctor"

    discover_response = client.get("/ai/discover", params={"query": "doctor"})
    assert discover_response.status_code == 200, discover_response.text
    assert discover_response.json()["count"] >= 1
    assert any(item["profession"] == "Doctor" for item in discover_response.json()["results"])

    empty_discover = client.get("/ai/discover", params={"query": "astronautical botany"})
    assert empty_discover.status_code == 200
    assert empty_discover.json()["results"] == []

    discover_me = client.get("/ai/discover/me", headers=_headers(user_token))
    assert discover_me.status_code == 200, discover_me.text
    assert all(item["user_id"] != user_lore["user_id"] for item in discover_me.json()["results"])
    assert any(item["id"] == other_lore["id"] for item in discover_me.json()["results"])


def test_notifications_and_recommendations_end_to_end():
    client = TestClient(main.app)
    AIService.set_provider(LocalAIProvider())

    author = _unique_user("author")
    actor = _unique_user("actor")
    _register(client, author)
    _register(client, actor)

    author_token = _login(client, author)
    actor_token = _login(client, actor)

    author_lore = _create_lore(
        client,
        author_token,
        {
            "person": "Ada Lovelace",
            "profession": "Doctor",
            "years_experience": 12,
            "theme": "medicine",
            "question": "How do you keep learning after setbacks?",
            "lore": "Keep studying small systems, serve patients carefully, and keep learning from every clinic day.",
        },
    )
    actor_lore = _create_lore(
        client,
        actor_token,
        {
            "person": "Grace Helper",
            "profession": "Nurse",
            "years_experience": 10,
            "theme": "healthcare",
            "question": "How do you support hospital teams?",
            "lore": "Patient care improves when nurses and doctors coordinate clearly.",
        },
    )

    comment_response = client.post(
        f"/comments/{author_lore['id']}",
        headers=_headers(actor_token),
        json={"content": "This is helpful and practical."},
    )
    assert comment_response.status_code == 200, comment_response.text
    comment = comment_response.json()

    like_response = client.post(
        f"/likes/{author_lore['id']}",
        headers=_headers(actor_token),
    )
    assert like_response.status_code == 200

    bookmark_response = client.post(
        f"/bookmarks/{author_lore['id']}",
        headers=_headers(actor_token),
    )
    assert bookmark_response.status_code == 200

    notifications_response = client.get(
        "/notifications",
        headers=_headers(author_token),
    )
    assert notifications_response.status_code == 200, notifications_response.text
    notifications_payload = notifications_response.json()
    assert notifications_payload["count"] >= 3
    notification_types = {item["type"] for item in notifications_payload["results"]}
    assert {"comment", "like", "bookmark"}.issubset(notification_types)

    unread_response = client.get(
        "/notifications/unread",
        headers=_headers(author_token),
    )
    assert unread_response.status_code == 200
    assert unread_response.json()["count"] >= 3

    first_notification_id = notifications_payload["results"][0]["id"]
    mark_read_response = client.patch(
        f"/notifications/{first_notification_id}/read",
        headers=_headers(author_token),
    )
    assert mark_read_response.status_code == 200
    assert mark_read_response.json()["is_read"] is True

    read_all_response = client.patch(
        "/notifications/read-all",
        headers=_headers(author_token),
    )
    assert read_all_response.status_code == 200
    assert read_all_response.json()["updated"] >= 0

    delete_notification_response = client.delete(
        f"/notifications/{first_notification_id}",
        headers=_headers(author_token),
    )
    assert delete_notification_response.status_code == 200

    refresh_recommendations = client.get(
        "/recommendations/refresh",
        headers=_headers(actor_token),
    )
    assert refresh_recommendations.status_code == 200, refresh_recommendations.text
    recommendations_payload = refresh_recommendations.json()
    assert recommendations_payload["count"] >= 1
    assert all(item["lore"]["user_id"] != actor_lore["user_id"] for item in recommendations_payload["results"])
    assert all(item["score"] > 0 for item in recommendations_payload["results"])
    assert all(item["reason"] for item in recommendations_payload["results"])

    actor_notifications = client.get(
        "/notifications",
        headers=_headers(actor_token),
    )
    assert actor_notifications.status_code == 200
    assert any(
        item["type"] == "recommendation_refresh"
        and item["message"] == "Your recommendations have been updated."
        for item in actor_notifications.json()["results"]
    )

    get_recommendations = client.get(
        "/recommendations",
        headers=_headers(actor_token),
    )
    assert get_recommendations.status_code == 200
    assert get_recommendations.json()["count"] >= 1

    clear_recommendations = client.delete(
        "/recommendations",
        headers=_headers(actor_token),
    )
    assert clear_recommendations.status_code == 200

    comments_response = client.get(f"/comments/{author_lore['id']}")
    assert comments_response.status_code == 200
    assert any(item["id"] == comment["id"] for item in comments_response.json())

    update_comment_response = client.patch(
        f"/comments/{comment['id']}",
        headers=_headers(actor_token),
        json={"content": "Updated practical advice."},
    )
    assert update_comment_response.status_code == 200, update_comment_response.text
    assert update_comment_response.json()["content"] == "Updated practical advice."

    liked_response = client.get(
        "/likes/me",
        headers=_headers(actor_token),
    )
    assert liked_response.status_code == 200, liked_response.text
    assert any(item["lore_id"] == author_lore["id"] for item in liked_response.json())

    dismiss_recommendation = client.delete(
        f"/recommendations/{recommendations_payload['results'][0]['id']}",
        headers=_headers(actor_token),
    )
    assert dismiss_recommendation.status_code == 200, dismiss_recommendation.text
