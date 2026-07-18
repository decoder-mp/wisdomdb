"""Application AI facade with caching and provider fallback."""

from __future__ import annotations

import threading
import re
from typing import Any

from services.ai_providers import AIProvider
from services.ai_providers import build_ai_provider


class AIService:
    """Cached facade for text intelligence features used across the app."""

    _provider: AIProvider = build_ai_provider()
    _cache: dict[tuple[str, str, str], Any] = {}
    _lock = threading.Lock()

    @classmethod
    def _cache_key(cls, method_name: str, text: str) -> tuple[str, str, str]:
        return (cls._provider.name, method_name, text)

    @classmethod
    def _get_cached(cls, method_name: str, text: str):
        with cls._lock:
            return cls._cache.get(cls._cache_key(method_name, text))

    @classmethod
    def _set_cached(cls, method_name: str, text: str, value: Any):
        with cls._lock:
            cls._cache[cls._cache_key(method_name, text)] = value

    @classmethod
    def set_provider(cls, provider: AIProvider):
        """Replace the active provider. Useful for tests or future integrations."""

        with cls._lock:
            cls._provider = provider
            cls._cache.clear()

    @classmethod
    def provider_name(cls) -> str:
        return cls._provider.name

    @classmethod
    def extract_themes(cls, text: str) -> list[str]:
        if not text:
            return []

        cached = cls._get_cached("extract_themes", text)
        if cached is not None:
            return list(cached)

        result = cls._provider.extract_themes(text)
        normalized = [item.strip() for item in result if item and item.strip()]
        cls._set_cached("extract_themes", text, tuple(normalized))
        return normalized

    @classmethod
    def summarize(cls, text: str) -> str:
        if not text:
            return ""

        cached = cls._get_cached("summarize", text)
        if cached is not None:
            return str(cached)

        result = cls._provider.summarize(text) or cls._simple_summary(text)
        cls._set_cached("summarize", text, result)
        return result

    @classmethod
    def discover_wisdom(cls, text: str) -> list[str]:
        if not text:
            return []

        cached = cls._get_cached("discover_wisdom", text)
        if cached is not None:
            return list(cached)

        result = cls._provider.discover_wisdom(text)
        normalized = [item.strip() for item in result if item and item.strip()]
        if not normalized:
            normalized = cls._fallback_insights(text)

        cls._set_cached("discover_wisdom", text, tuple(normalized))
        return normalized

    @staticmethod
    def normalize_terms(values: list[str]) -> set[str]:
        normalized: set[str] = set()

        for value in values:
            for token in re.findall(r"[A-Za-z][A-Za-z\-']+", value.lower()):
                cleaned = token.strip("-'")
                if cleaned.endswith("ies") and len(cleaned) > 4:
                    cleaned = f"{cleaned[:-3]}y"
                elif cleaned.endswith("s") and len(cleaned) > 4 and not cleaned.endswith("ss"):
                    cleaned = cleaned[:-1]
                normalized.add(cleaned)

        return normalized

    @staticmethod
    def _simple_summary(text: str) -> str:
        sentences = [sentence.strip() for sentence in text.split(".") if sentence.strip()]
        return ". ".join(sentences[:2]).strip() or text[:280].strip()

    @staticmethod
    def _fallback_insights(text: str) -> list[str]:
        sentences = [sentence.strip() for sentence in text.split(".") if sentence.strip()]
        return sentences[:3]
