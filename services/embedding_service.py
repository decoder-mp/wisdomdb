import os
from typing import List
import threading
from math import sqrt


def _load_sentence_transformer_class():
    """Lazy-import sentence-transformers to avoid expensive startup imports."""
    try:
        from sentence_transformers import SentenceTransformer as _SentenceTransformer
        return _SentenceTransformer
    except Exception:  # pragma: no cover - optional in lightweight deployments
        return None


class EmbeddingService:
    """
    Singleton embedding service (fast + safe)
    """

    _model = None
    _model_available = None
    _lock = threading.Lock()
    _fallback_size = 128

    @classmethod
    def _fallback_embedding(cls, text: str) -> List[float]:
        vec = [0.0] * cls._fallback_size
        if not text:
            return vec

        for token in text.lower().split():
            vec[hash(token) % cls._fallback_size] += 1.0

        norm = sqrt(sum(v * v for v in vec))
        if norm == 0:
            return vec

        return [v / norm for v in vec]

    @classmethod
    def model(cls):
        if os.getenv("ENABLE_EMBEDDINGS", "false").lower() not in {"1", "true", "yes", "on"}:
            return None

        if cls._model_available is False:
            return None

        if cls._model is None:
            with cls._lock:
                if cls._model is None:
                    sentence_transformer_class = _load_sentence_transformer_class()
                    if sentence_transformer_class is None:
                        cls._model_available = False
                        return None

                    cls._model = sentence_transformer_class(
                        "BAAI/bge-small-en-v1.5"
                    )
        return cls._model

    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        model = cls.model()
        if model is None:
            return cls._fallback_embedding(text)
        return model.encode(text).tolist()

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2:
            return 0.0
        if len(vec1) != len(vec2):
            # pad shorter vector with zeros
            n = max(len(vec1), len(vec2))
            vec1 = list(vec1) + [0.0] * (n - len(vec1))
            vec2 = list(vec2) + [0.0] * (n - len(vec2))

        dot = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a * a for a in vec1) ** 0.5
        mag2 = sum(b * b for b in vec2) ** 0.5

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot / (mag1 * mag2)