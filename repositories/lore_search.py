from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List



class LoreSearchRepository:

    @staticmethod
    def hybrid_search(
        db: Session,
        query_embedding: List[float],
        query: str,
        limit: int = 20
    ):
        sql = text("""
            SELECT
                *,
                (1 - (embedding <=> :embedding)) AS semantic_score,

                ts_rank(
                    to_tsvector('english',
                        coalesce(theme,'') || ' ' ||
                        coalesce(question,'') || ' ' ||
                        coalesce(lore,'')
                    ),
                    plainto_tsquery('english', :query)
                ) AS keyword_score

            FROM lore
            WHERE embedding IS NOT NULL
            ORDER BY semantic_score DESC
            LIMIT :limit
        """)

        result = db.execute(
            sql,
            {
                # IMPORTANT: pgvector expects list[float], NOT string
                "embedding": query_embedding,
                "query": query,
                "limit": limit
            }
        ).fetchall()

        return result