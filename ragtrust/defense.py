"""A lightweight provenance-aware retrieval defence."""

from __future__ import annotations

import re


class ProvenanceReranker:
    """Combine keyword relevance with source trust and an instruction penalty."""

    _instruction_pattern = re.compile(
        r"\b(?:assistant|system message|ignore|when answering|generated answer|"
        r"output|respond with|include the phrase)\b",
        re.IGNORECASE,
    )

    def score(self, document: dict, relevance_score: float) -> float:
        trust_score = float(document["trust_score"])
        instruction_penalty = (
            0.25 if self._instruction_pattern.search(document["content"]) else 1.0
        )
        return relevance_score * trust_score * instruction_penalty

