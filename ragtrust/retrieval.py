"""A deliberately simple keyword retriever."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Callable


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "how",
    "in",
    "is",
    "of",
    "on",
    "the",
    "to",
    "what",
    "when",
    "where",
    "which",
}


@dataclass(frozen=True)
class SearchResult:
    doc_id: str
    title: str
    source: str
    trust_score: float
    is_poisoned: bool
    relevance_score: float
    final_score: float


ScoreFunction = Callable[[dict, float], float]


def tokenize(text: str) -> list[str]:
    """Turn text into lowercase search terms and remove common filler words."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [word for word in words if word not in STOP_WORDS and len(word) > 1]


class KeywordRetriever:
    """Rank documents by capped query-term frequency."""

    def search(
        self,
        query: str,
        documents: list[dict],
        *,
        top_k: int = 3,
        score_function: ScoreFunction | None = None,
    ) -> list[SearchResult]:
        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        query_terms = set(tokenize(query))
        if not query_terms:
            return []

        ranked = []
        for document in documents:
            counts = Counter(tokenize(f"{document['title']} {document['content']}"))
            matched_terms = sum(min(counts[term], 3) for term in query_terms)
            relevance = matched_terms / len(query_terms)
            final_score = (
                score_function(document, relevance)
                if score_function is not None
                else relevance
            )
            ranked.append(
                SearchResult(
                    doc_id=document["doc_id"],
                    title=document["title"],
                    source=document["source"],
                    trust_score=float(document["trust_score"]),
                    is_poisoned=bool(document["is_poisoned"]),
                    relevance_score=round(relevance, 4),
                    final_score=round(final_score, 4),
                )
            )

        ranked.sort(key=lambda item: (-item.final_score, item.doc_id))
        return ranked[:top_k]

