from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from services.embedding_service import EmbeddingService


class SearchService:

    @staticmethod
    def get_embedding(query: str):
        return EmbeddingService.get_embedding(query)

    @staticmethod
    def _is_postgres(db: Session) -> bool:
        bind = db.bind
        if bind is None:
            return False
        dialect = bind.dialect.name
        return dialect == "postgresql"

    @staticmethod
    def hybrid_search(db: Session, query: str):
        if SearchService._is_postgres(db):
            return SearchService._postgres_search(db, query)
        return SearchService._sqlite_search(db, query)

    @staticmethod
    def _postgres_search(db: Session, query: str):
        try:
            result = db.execute(
                text("""
                    SELECT
                        id, theme, question, lore, user_id, created_at,
                        ts_rank(
                            to_tsvector('english',
                                coalesce(theme,'') || ' ' ||
                                coalesce(question,'') || ' ' ||
                                coalesce(lore,'')
                            ),
                            plainto_tsquery(:query)
                        ) AS keyword_rank,
                        0.5 AS semantic_rank
                    FROM lore
                    WHERE
                        to_tsvector('english',
                            coalesce(theme,'') || ' ' ||
                            coalesce(question,'') || ' ' ||
                            coalesce(lore,'')
                        ) @@ plainto_tsquery(:query)
                    ORDER BY keyword_rank DESC
                    LIMIT 50
                """),
                {"query": query},
            )
            return result.fetchall()
        except SQLAlchemyError:
            return SearchService._sqlite_search(db, query)

    @staticmethod
    def _sqlite_search(db: Session, query: str):
        """Plain substring search for SQLite / fallback environments."""
        terms = [t.strip() for t in query.lower().split() if t.strip()]
        if not terms:
            return []
        try:
            rows = db.execute(text("SELECT id, theme, question, lore, user_id, created_at FROM lore")).fetchall()
        except SQLAlchemyError:
            return []

        scored = []
        for row in rows:
            haystack = f"{row.theme} {row.question} {row.lore}".lower()
            hits = sum(1 for t in terms if t in haystack)
            if hits > 0:
                scored.append((hits, row))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:50]]