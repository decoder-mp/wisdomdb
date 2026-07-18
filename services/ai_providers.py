"""Local AI provider implementations for MVP text features."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Protocol

_STOPWORDS = {
    "a", "about", "after", "all", "am", "an", "and", "are", "as", "at", "be",
    "been", "before", "being", "between", "both", "but", "by", "can", "could",
    "did", "do", "does", "doing", "for", "from", "had", "has", "have", "help",
    "helping", "her", "here", "hers", "him", "his", "how", "i", "if", "in", "into",
    "is", "it", "its", "itself", "me", "more", "most", "my", "of", "on", "or",
    "our", "ours", "over", "she", "so", "some", "such", "than", "that", "the",
    "their", "theirs", "them", "then", "there", "these", "they", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "we", "were",
    "what", "when", "where", "which", "who", "why", "with", "would", "years", "you",
    "your",
}

_THEME_GROUPS = {
    "medicine": {"doctor", "physician", "medical", "medicine", "surgery", "surgeon", "clinic", "hospital", "hospitals"},
    "healthcare": {"health", "healthcare", "patient", "patients", "care", "nurse", "nursing", "wellness", "hospital", "clinic", "doctor"},
    "children": {"child", "children", "pediatric", "pediatrics", "youth", "family", "families"},
    "rural health": {"rural", "village", "community", "remote"},
    "education": {"education", "teaching", "teacher", "teachers", "school", "schools", "student", "students", "learning", "classroom"},
    "technology": {"technology", "software", "engineering", "engineer", "coding", "developer", "developers", "data", "systems", "computer"},
    "leadership": {"leadership", "manager", "management", "mentor", "mentoring", "team", "teams", "strategy"},
    "business": {"business", "operations", "sales", "customer", "customers", "market", "finance"},
    "public service": {"service", "public", "community", "civic", "nonprofit", "government"},
}

_PHRASE_PATTERNS = {
    "rural health": (("rural",), ("doctor", "medical", "medicine", "health", "healthcare", "hospital", "patient")),
    "patient care": (("patient", "patients"), ("care", "caregiving", "healthcare")),
    "community care": (("community",), ("care", "health", "healthcare", "support")),
}


class AIProvider(Protocol):
    name: str

    def extract_themes(self, text: str) -> list[str]:
        ...

    def summarize(self, text: str) -> str:
        ...

    def discover_wisdom(self, text: str) -> list[str]:
        ...


@dataclass
class LocalAIProvider:
    name: str = "local-nlp"

    def extract_themes(self, text: str) -> list[str]:
        tokens = self._content_tokens(text)
        if not tokens:
            return []

        token_counts = Counter(tokens)
        theme_scores: Counter[str] = Counter()

        for theme, vocabulary in _THEME_GROUPS.items():
            for token, count in token_counts.items():
                if token in vocabulary:
                    theme_scores[theme] += count

        token_set = set(tokens)
        for theme, pattern in _PHRASE_PATTERNS.items():
            left_terms, right_terms = pattern
            if token_set.intersection(left_terms) and token_set.intersection(right_terms):
                theme_scores[theme] += 3

        ranked = [theme for theme, _ in theme_scores.most_common(5)]

        if len(ranked) < 3:
            phrases = self._ranked_phrases(tokens)
            for phrase in phrases:
                if phrase not in ranked:
                    ranked.append(phrase)
                if len(ranked) >= 5:
                    break

        return ranked[:5]

    def summarize(self, text: str) -> str:
        sentences = self._sentences(text)
        if not sentences:
            return ""
        if len(sentences) == 1 and len(sentences[0].split()) <= 12:
            return sentences[0]

        keywords = Counter(self._content_tokens(text))
        scored_sentences: list[tuple[int, float, str]] = []
        for index, sentence in enumerate(sentences):
            sentence_tokens = self._content_tokens(sentence)
            if not sentence_tokens:
                continue
            score = sum(keywords[token] for token in sentence_tokens)
            score = score / max(len(sentence_tokens), 1)
            score += max(0.0, 0.6 - (index * 0.08))
            scored_sentences.append((index, score, sentence))

        if not scored_sentences:
            return sentences[0]

        sentence_count = 1 if len(sentences) <= 3 else 2 if len(sentences) <= 6 else 3
        selected = sorted(
            sorted(scored_sentences, key=lambda item: item[1], reverse=True)[:sentence_count],
            key=lambda item: item[0],
        )
        summary = " ".join(sentence for _, _, sentence in selected).strip()
        return summary[:450].strip()

    def discover_wisdom(self, text: str) -> list[str]:
        sentences = self._sentences(text)
        if not sentences:
            return []
        if len(sentences) <= 3:
            return sentences
        summary = self.summarize(text)
        return [segment.strip() for segment in self._sentences(summary) if segment.strip()][:3]

    def _ranked_phrases(self, tokens: list[str]) -> list[str]:
        bigrams = Counter(
            f"{tokens[index]} {tokens[index + 1]}"
            for index in range(len(tokens) - 1)
            if tokens[index] != tokens[index + 1]
        )
        ranked_phrases = [phrase for phrase, _ in bigrams.most_common(5)]
        ranked_keywords = [token for token, _ in Counter(tokens).most_common(5)]
        return ranked_phrases + ranked_keywords

    def _sentences(self, text: str) -> list[str]:
        parts = re.split(r"(?<=[.!?])\s+", text.strip())
        return [part.strip() for part in parts if part and part.strip()]

    def _content_tokens(self, text: str) -> list[str]:
        raw_tokens = re.findall(r"[A-Za-z][A-Za-z\-']+", text.lower())
        normalized = [self._normalize(token) for token in raw_tokens]
        return [token for token in normalized if token and token not in _STOPWORDS and len(token) > 2]

    def _normalize(self, token: str) -> str:
        cleaned = token.strip("-'")
        if cleaned.endswith("ies") and len(cleaned) > 4:
            cleaned = f"{cleaned[:-3]}y"
        elif cleaned.endswith("s") and len(cleaned) > 4 and not cleaned.endswith("ss"):
            cleaned = cleaned[:-1]
        aliases = {
            "physicians": "physician",
            "doctors": "doctor",
            "hospitals": "hospital",
            "kids": "children",
            "teaches": "teaching",
            "students": "student",
        }
        return aliases.get(cleaned, cleaned)


def build_ai_provider() -> AIProvider:
    return LocalAIProvider()
