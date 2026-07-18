import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi.testclient import TestClient

from core.database import get_db
from core.dependencies import get_current_user
from routers import auth as auth_router


def _load_main_module():
    project_root = Path(__file__).resolve().parents[1]
    main_path = project_root / "main.py"

    spec = importlib.util.spec_from_file_location("lore_prototype_main", main_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


main = _load_main_module()


def _override_get_db():
    yield object()


def test_register_accepts_json(monkeypatch):
    monkeypatch.setattr(
        auth_router,
        "get_user_by_email",
        lambda db, email: None,
    )
    monkeypatch.setattr(
        auth_router,
        "create_user",
        lambda db, username, email, hashed_password, is_admin=False: SimpleNamespace(
            id=1,
            username=username,
            email=email,
            is_admin=is_admin,
        ),
    )

    main.app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(main.app)

    response = client.post(
        "/auth/register",
        json={
            "username": "johndoe",
            "email": "johndoe@test.com",
            "password": "test1234",
        },
    )

    main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "username": "johndoe",
        "email": "johndoe@test.com",
        "is_admin": False,
    }


def test_register_accepts_form_data(monkeypatch):
    monkeypatch.setattr(
        auth_router,
        "get_user_by_email",
        lambda db, email: None,
    )
    monkeypatch.setattr(
        auth_router,
        "create_user",
        lambda db, username, email, hashed_password, is_admin=False: SimpleNamespace(
            id=2,
            username=username,
            email=email,
            is_admin=is_admin,
        ),
    )

    main.app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(main.app)

    response = client.post(
        "/auth/register",
        data={
            "username": "janedoe",
            "email": "janedoe@test.com",
            "password": "safe1234",
        },
    )

    main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "username": "janedoe",
        "email": "janedoe@test.com",
        "is_admin": False,
    }


def test_register_returns_custom_message_for_invalid_json(monkeypatch):
    monkeypatch.setattr(
        auth_router,
        "get_user_by_email",
        lambda db, email: None,
    )

    main.app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(main.app)

    response = client.post(
        "/auth/register",
        content='{"username": "johndoe",',
        headers={"Content-Type": "application/json"},
    )

    main.app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["detail"][0]["message"] == (
        "Invalid JSON body. Check for missing quotes or commas."
    )


def test_register_returns_custom_message_for_missing_password(monkeypatch):
    monkeypatch.setattr(
        auth_router,
        "get_user_by_email",
        lambda db, email: None,
    )

    main.app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(main.app)

    response = client.post(
        "/auth/register",
        json={
            "username": "johndoe",
            "email": "johndoe@test.com",
        },
    )

    main.app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["detail"][0] == {
        "field": "password",
        "message": "password is required.",
    }


def test_register_does_not_grant_admin_without_provision_header(monkeypatch):
    monkeypatch.setenv("ADMIN_PROVISION_SECRET", "top-secret")
    monkeypatch.setattr(
        auth_router,
        "get_user_by_email",
        lambda db, email: None,
    )
    monkeypatch.setattr(
        auth_router,
        "create_user",
        lambda db, username, email, hashed_password, is_admin=False: SimpleNamespace(
            id=3,
            username=username,
            email=email,
            is_admin=is_admin,
        ),
    )

    main.app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(main.app)

    response = client.post(
        "/auth/register",
        json={
            "username": "modcandidate",
            "email": "modcandidate@test.com",
            "password": "safe1234",
            "is_admin": True,
        },
    )

    main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["is_admin"] is False


def test_register_grants_admin_with_valid_provision_header(monkeypatch):
    monkeypatch.setenv("ADMIN_PROVISION_SECRET", "top-secret")
    monkeypatch.setattr(
        auth_router,
        "get_user_by_email",
        lambda db, email: None,
    )
    monkeypatch.setattr(
        auth_router,
        "create_user",
        lambda db, username, email, hashed_password, is_admin=False: SimpleNamespace(
            id=4,
            username=username,
            email=email,
            is_admin=is_admin,
        ),
    )

    main.app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(main.app)

    response = client.post(
        "/auth/register",
        json={
            "username": "trustedadmin",
            "email": "trustedadmin@test.com",
            "password": "safe1234",
            "is_admin": True,
        },
        headers={"x-admin-provision": "top-secret"},
    )

    main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["is_admin"] is True


def test_register_form_grants_admin_with_valid_provision_header(monkeypatch):
    monkeypatch.setenv("ADMIN_PROVISION_SECRET", "top-secret")
    monkeypatch.setattr(
        auth_router,
        "get_user_by_email",
        lambda db, email: None,
    )
    monkeypatch.setattr(
        auth_router,
        "create_user",
        lambda db, username, email, hashed_password, is_admin=False: SimpleNamespace(
            id=5,
            username=username,
            email=email,
            is_admin=is_admin,
        ),
    )

    main.app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(main.app)

    response = client.post(
        "/auth/register",
        data={
            "username": "formadmin",
            "email": "formadmin@test.com",
            "password": "safe1234",
            "is_admin": "true",
        },
        headers={"x-admin-provision": "top-secret"},
    )

    main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["is_admin"] is True


def test_login_promotes_bootstrap_admin_user(monkeypatch):
    class FakeDB:
        def __init__(self):
            self.committed = False
            self.refreshed = None

        def commit(self):
            self.committed = True

        def refresh(self, user):
            self.refreshed = user

    fake_db = FakeDB()
    user = SimpleNamespace(
        id=99,
        email="seed.curator@lore.app",
        hashed_password="hashed",
        is_admin=False,
    )

    monkeypatch.setenv("BOOTSTRAP_ADMIN_EMAIL", "seed.curator@lore.app")
    monkeypatch.setattr(
        auth_router,
        "get_user_by_email",
        lambda db, email: user,
    )
    monkeypatch.setattr(
        auth_router,
        "verify_password",
        lambda plain, hashed: True,
    )
    monkeypatch.setattr(
        auth_router,
        "create_access_token",
        lambda subject: "test-token",
    )

    def _override_login_db():
        yield fake_db

    main.app.dependency_overrides[get_db] = _override_login_db
    client = TestClient(main.app)

    response = client.post(
        "/auth/login",
        data={
            "username": "seed.curator@lore.app",
            "password": "safe1234",
        },
    )

    main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "test-token",
        "token_type": "bearer",
    }
    assert user.is_admin is True
    assert fake_db.committed is True
    assert fake_db.refreshed is user


def test_change_password_updates_password_for_current_user(monkeypatch):
    class FakeDB:
        def __init__(self):
            self.committed = False
            self.refreshed = None

        def commit(self):
            self.committed = True

        def refresh(self, user):
            self.refreshed = user

    fake_db = FakeDB()
    current_user = SimpleNamespace(
        id=7,
        email="member@test.com",
        hashed_password="hashed-old",
        is_admin=False,
    )

    def _verify_password(plain, hashed):
        return (plain, hashed) == ("Oldpass123", "hashed-old")

    monkeypatch.setattr(auth_router, "verify_password", _verify_password)
    monkeypatch.setattr(auth_router, "hash_password", lambda plain: f"hashed::{plain}")

    def _override_password_db():
        yield fake_db

    def _override_current_user():
        return current_user

    main.app.dependency_overrides[get_db] = _override_password_db
    main.app.dependency_overrides[get_current_user] = _override_current_user
    client = TestClient(main.app)

    response = client.post(
        "/auth/change-password",
        json={
            "current_password": "Oldpass123",
            "new_password": "Newpass456",
        },
    )

    main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"message": "Password updated"}
    assert current_user.hashed_password == "hashed::Newpass456"
    assert fake_db.committed is True
    assert fake_db.refreshed is current_user


def test_change_password_rejects_incorrect_current_password(monkeypatch):
    current_user = SimpleNamespace(
        id=8,
        email="member@test.com",
        hashed_password="hashed-old",
        is_admin=False,
    )

    monkeypatch.setattr(auth_router, "verify_password", lambda plain, hashed: False)

    def _override_current_user():
        return current_user

    main.app.dependency_overrides[get_db] = _override_get_db
    main.app.dependency_overrides[get_current_user] = _override_current_user
    client = TestClient(main.app)

    response = client.post(
        "/auth/change-password",
        json={
            "current_password": "Wrongpass123",
            "new_password": "Newpass456",
        },
    )

    main.app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json()["detail"] == "Current password is incorrect"


def test_reset_password_requires_admin():
    current_user = SimpleNamespace(
        id=9,
        email="member@test.com",
        hashed_password="hashed-old",
        is_admin=False,
    )

    def _override_current_user():
        return current_user

    main.app.dependency_overrides[get_db] = _override_get_db
    main.app.dependency_overrides[get_current_user] = _override_current_user
    client = TestClient(main.app)

    response = client.post(
        "/auth/reset-password",
        json={
            "email": "target@test.com",
            "new_password": "Resetpass456",
        },
    )

    main.app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_reset_password_updates_target_user(monkeypatch):
    class FakeDB:
        def __init__(self):
            self.committed = False
            self.refreshed = None

        def commit(self):
            self.committed = True

        def refresh(self, user):
            self.refreshed = user

    fake_db = FakeDB()
    current_user = SimpleNamespace(
        id=10,
        email="admin@test.com",
        hashed_password="hashed-admin",
        is_admin=True,
    )
    target_user = SimpleNamespace(
        id=11,
        email="target@test.com",
        hashed_password="hashed-old",
        is_admin=False,
    )

    monkeypatch.setattr(
        auth_router,
        "get_user_by_email",
        lambda db, email: target_user if email == "target@test.com" else None,
    )
    monkeypatch.setattr(
        auth_router,
        "verify_password",
        lambda plain, hashed: False,
    )
    monkeypatch.setattr(auth_router, "hash_password", lambda plain: f"hashed::{plain}")

    def _override_password_db():
        yield fake_db

    def _override_current_user():
        return current_user

    main.app.dependency_overrides[get_db] = _override_password_db
    main.app.dependency_overrides[get_current_user] = _override_current_user
    client = TestClient(main.app)

    response = client.post(
        "/auth/reset-password",
        json={
            "email": "target@test.com",
            "new_password": "Resetpass456",
        },
    )

    main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"message": "Password reset"}
    assert target_user.hashed_password == "hashed::Resetpass456"
    assert fake_db.committed is True
    assert fake_db.refreshed is target_user


def test_forgot_password_sends_reset_email_when_user_exists(monkeypatch):
    user = SimpleNamespace(id=21, email="member@test.com")
    send_email = Mock()

    monkeypatch.setattr(auth_router, "get_user_by_email", lambda db, email: user)
    monkeypatch.setattr(auth_router, "_issue_password_reset_token", lambda db, target: "reset-token")
    monkeypatch.setattr(auth_router, "send_password_reset_email", send_email)
    monkeypatch.setattr(auth_router, "FRONTEND_BASE_URL", "https://web.lore.app")

    main.app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(main.app)

    response = client.post(
        "/auth/forgot-password",
        json={"email": "member@test.com"},
    )

    main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "reset link has been sent" in response.json()["message"]
    send_email.assert_called_once_with(
        "member@test.com",
        "https://web.lore.app/reset-password?token=reset-token",
    )


def test_forgot_password_returns_service_unavailable_when_email_unconfigured(monkeypatch):
    user = SimpleNamespace(id=22, email="member@test.com")

    monkeypatch.setattr(auth_router, "get_user_by_email", lambda db, email: user)
    monkeypatch.setattr(auth_router, "_issue_password_reset_token", lambda db, target: "reset-token")

    def _raise_email_error(recipient, link):
        raise auth_router.EmailConfigurationError("SMTP_HOST and EMAIL_FROM_ADDRESS must be configured for password reset emails.")

    monkeypatch.setattr(auth_router, "send_password_reset_email", _raise_email_error)

    main.app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(main.app)

    response = client.post(
        "/auth/forgot-password",
        json={"email": "member@test.com"},
    )

    main.app.dependency_overrides.clear()

    assert response.status_code == 503
    assert "SMTP_HOST and EMAIL_FROM_ADDRESS" in response.json()["detail"]


def test_complete_password_reset_updates_password_from_token(monkeypatch):
    class FakeQuery:
        def filter(self, *_args, **_kwargs):
            return self

        def all(self):
            return []

    class FakeDB:
        def __init__(self):
            self.committed = False

        def commit(self):
            self.committed = True

        def query(self, _model):
            return FakeQuery()

    fake_db = FakeDB()
    user = SimpleNamespace(
        id=23,
        email="member@test.com",
        hashed_password="hashed-old",
    )
    token_record = SimpleNamespace(id=1, used_at=None)

    monkeypatch.setattr(auth_router, "_consume_password_reset_token", lambda db, token: (user, token_record))
    monkeypatch.setattr(auth_router, "verify_password", lambda plain, hashed: False)
    monkeypatch.setattr(auth_router, "hash_password", lambda plain: f"hashed::{plain}")

    def _override_password_db():
        yield fake_db

    main.app.dependency_overrides[get_db] = _override_password_db
    client = TestClient(main.app)

    response = client.post(
        "/auth/complete-password-reset",
        json={
            "token": "reset-token-value-1234567890",
            "new_password": "Newpass456",
        },
    )

    main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"message": "Password reset complete"}
    assert user.hashed_password == "hashed::Newpass456"
    assert token_record.used_at is not None
    assert fake_db.committed is True


def test_complete_password_reset_rejects_invalid_token(monkeypatch):
    monkeypatch.setattr(auth_router, "_consume_password_reset_token", lambda db, token: (None, None))

    main.app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(main.app)

    response = client.post(
        "/auth/complete-password-reset",
        json={
            "token": "reset-token-value-1234567890",
            "new_password": "Newpass456",
        },
    )

    main.app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "Reset link is invalid or expired"
