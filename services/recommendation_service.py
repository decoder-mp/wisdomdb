from __future__ import annotations

from sqlalchemy.orm import Session

from repositories.likes import count_likes
from repositories.lore import LoreRepository
from repositories.recommendation_repository import clear_for_user
from repositories.recommendation_repository import create
from repositories.recommendation_repository import delete_recommendation
from repositories.recommendation_repository import get_for_user
from repositories.recommendation_repository import get_by_id
from repositories.users import list_users
from services.ai_service import AIService
from services.notification_service import NotificationService


class RecommendationService:
    @staticmethod
    def get_recommendations(
        db: Session,
        current_user,
        limit: int = 10,
    ):
        existing = get_for_user(db, current_user.id)
        if existing:
            return existing[:limit]
        return RecommendationService.refresh_recommendations(db, current_user, limit=limit)

    @staticmethod
    def refresh_recommendations(
        db: Session,
        current_user,
        limit: int = 10,
    ):
        clear_for_user(db, current_user.id)
        candidates = RecommendationService._build_ranked_candidates(db, current_user, limit=limit)
        saved = []
        for item in candidates[:limit]:
            saved.append(
                create(
                    db,
                    user_id=current_user.id,
                    lore_id=item["lore"].id,
                    score=item["score"],
                    reason=item["reason"],
                )
            )
        NotificationService.create_recommendation_refresh_notification(db, current_user.id)
        return saved

    @staticmethod
    def notify_interested_users_for_new_lore(
        db: Session,
        new_lore,
        strong_match_threshold: float = 4.0,
    ):
        users = list_users(db)
        notified = 0

        for user in users:
            if user.id == new_lore.user_id:
                continue

            ranked = RecommendationService._build_ranked_candidates(db, user, limit=25)
            match = next((item for item in ranked if item["lore"].id == new_lore.id), None)
            if not match:
                continue
            if match["score"] < strong_match_threshold:
                continue

            created = NotificationService.create_new_lore_interest_notification(
                db,
                recipient_id=user.id,
                lore_id=new_lore.id,
                theme=new_lore.theme,
            )
            if created:
                notified += 1

        return notified

    @staticmethod
    def clear_recommendations(
        db: Session,
        current_user,
    ):
        return clear_for_user(db, current_user.id)

    @staticmethod
    def delete_recommendation(
        db: Session,
        current_user,
        recommendation_id: int,
    ):
        recommendation = get_by_id(db, recommendation_id)
        if not recommendation or recommendation.user_id != current_user.id:
            return None
        delete_recommendation(db, recommendation)
        return recommendation_id

    @staticmethod
    def recommend_for_new_user(
        db: Session,
        current_user=None,
        limit: int = 10,
    ):
        lore_repo = LoreRepository()
        entries = lore_repo.get_all(db)
        if current_user is not None:
            entries = [entry for entry in entries if entry.user_id != current_user.id]

        scored = []
        for entry in entries:
            popularity = count_likes(db, entry.id)
            score = round((popularity * 0.4) + min(entry.years_experience / 10.0, 3.0), 2)
            scored.append(
                {
                    "lore": entry,
                    "score": score,
                    "reason": "Popular lore with relevant experience behind it.",
                }
            )

        scored.sort(key=lambda item: (item["score"], item["lore"].created_at), reverse=True)
        return scored[:limit]

    @staticmethod
    def recommend_for_user(
        db: Session,
        current_user,
        limit: int = 10,
    ):
        return RecommendationService._build_ranked_candidates(db, current_user, limit=limit)

    @staticmethod
    def _build_ranked_candidates(
        db: Session,
        current_user,
        limit: int = 10,
    ):
        lore_repo = LoreRepository()
        own_lore = lore_repo.get_for_user(db, current_user.id)
        other_lore = lore_repo.get_excluding_user(db, current_user.id)

        if not other_lore:
            return []

        if not own_lore:
            return RecommendationService.recommend_for_new_user(db, current_user=current_user, limit=limit)

        own_theme_terms = AIService.normalize_terms(
            [item.theme for item in own_lore] + AIService.extract_themes(" ".join(item.lore for item in own_lore))
        )
        own_profession_terms = AIService.normalize_terms([item.profession for item in own_lore])
        own_question_terms = AIService.normalize_terms(
            AIService.extract_themes(" ".join(item.question for item in own_lore))
        )

        ranked_items = []
        for lore in other_lore:
            candidate_theme_terms = AIService.normalize_terms(
                [lore.theme] + AIService.extract_themes(f"{lore.theme} {lore.lore}")
            )
            candidate_profession_terms = AIService.normalize_terms([lore.profession])
            candidate_question_terms = AIService.normalize_terms(
                AIService.extract_themes(lore.question)
            )

            theme_overlap = own_theme_terms.intersection(candidate_theme_terms)
            profession_overlap = own_profession_terms.intersection(candidate_profession_terms)
            question_overlap = own_question_terms.intersection(candidate_question_terms)
            popularity = count_likes(db, lore.id)

            score = 0.0
            reasons: list[str] = []

            if theme_overlap:
                score += len(theme_overlap) * 3.0
                reasons.append(f"shared themes: {', '.join(sorted(theme_overlap)[:2])}")
            if profession_overlap:
                score += len(profession_overlap) * 2.5
                reasons.append(f"related profession: {', '.join(sorted(profession_overlap)[:2])}")
            if question_overlap:
                score += len(question_overlap) * 1.5
                reasons.append(f"similar question keywords: {', '.join(sorted(question_overlap)[:2])}")
            if popularity:
                score += min(popularity, 10) * 0.25
                reasons.append("popular with readers")

            if score <= 0:
                continue

            ranked_items.append(
                {
                    "lore": lore,
                    "score": round(score, 2),
                    "reason": "; ".join(reasons[:3]) or "Relevant to your interests.",
                }
            )

        if not ranked_items:
            return RecommendationService.recommend_for_new_user(db, current_user=current_user, limit=limit)

        ranked_items.sort(key=lambda item: (item["score"], item["lore"].created_at), reverse=True)
        return ranked_items[:limit]
