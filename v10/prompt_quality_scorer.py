#!/usr/bin/env python3
"""
v10.x Prompt quality scorer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict


@dataclass
class QualityScore:
    overall: float
    structure: float
    logic: float
    markers: float
    relevance: float
    length_score: float
    flags: list[str]

    def to_dict(self) -> Dict:
        return {
            "overall": round(self.overall, 3),
            "structure": round(self.structure, 3),
            "logic": round(self.logic, 3),
            "markers": round(self.markers, 3),
            "relevance": round(self.relevance, 3),
            "length_score": round(self.length_score, 3),
            "flags": self.flags,
        }


class PromptQualityScorer:
    # Signal patterns
    HEADER_RE = re.compile(r'^(#{1,3}|[A-Z][A-Z\s\-]+:|^\d+\.)', re.MULTILINE)
    LIST_RE = re.compile(r'^[\-\*•]|^(\d+\.)', re.MULTILINE)
    SECTION_RE = re.compile(r'\n{2,}', re.MULTILINE)
    BULLET_RE = re.compile(r'^[\-\*] ', re.MULTILINE)
    NUMBERED_RE = re.compile(r'^\d+\. ', re.MULTILINE)
    MARKER_RE = {
        'summary': re.compile(r'\b(summary|summarize|compact|key points?|tl;dr|to summarize)\b', re.IGNORECASE),
        'reflect': re.compile(r'\b(reflect|insight|pattern|drift|coherence|observe)\b', re.IGNORECASE),
        'generate': re.compile(r'\b(generate|create|produce|suggest|recommend)\b', re.IGNORECASE),
    }
    LOGIC_RE = re.compile(r'\b(because|therefore|since|result|conclusion|this means|however|but also)\b', re.IGNORECASE)
    REPETITION_RE = re.compile(r'(\b\w+\b).*\1.*\1')

    def score(self, text: str, operation: str = "generate") -> QualityScore:
        flags: list[str] = []

        length = len(text)
        length_score = self._length_score(length, operation)
        if length_score < 0.3:
            flags.append("output_too_short")
        elif length_score > 0.9:
            flags.append("output_excessively_verbose")

        structure = self._structure_score(text)
        if structure < 0.3:
            flags.append("missing_structure")

        logic = self._logic_score(text)
        if logic < 0.2:
            flags.append("low_reasoning")

        markers = self._marker_score(text, operation)
        if markers < 0.3 and operation in ("summary", "reflect"):
            flags.append("missing_operation_markers")

        relevance = self._relevance_score(text)
        if relevance < 0.5:
            flags.append("low_relevance")

        has_repetition = bool(self.REPETITION_RE.search(text))
        if has_repetition:
            flags.append("repetitive_output")

        overall = (
            structure * 0.2
            + logic * 0.2
            + markers * 0.15
            + relevance * 0.25
            + length_score * 0.2
        )
        if has_repetition:
            overall *= 0.7

        return QualityScore(
            overall=round(max(0.0, min(1.0, overall)), 3),
            structure=structure,
            logic=logic,
            markers=markers,
            relevance=relevance,
            length_score=length_score,
            flags=flags,
        )

    def _length_score(self, length: int, operation: str) -> float:
        targets = {"summary": 80, "reflect": 120, "generate": 60}
        target = targets.get(operation, 80)
        if length < 20:
            return 0.0
        ratio = length / target
        if ratio < 0.5:
            return ratio
        return min(1.0, ratio)

    def _structure_score(self, text: str) -> float:
        score = 0.0
        if self.HEADER_RE.search(text):
            score += 0.4
        if self.BULLET_RE.search(text):
            score += 0.3
        if self.NUMBERED_RE.search(text):
            score += 0.3
        sections = len(self.SECTION_RE.findall(text))
        score += min(0.3, sections * 0.15)
        return min(1.0, score)

    def _logic_score(self, text: str) -> float:
        matches = len(self.LOGIC_RE.findall(text))
        return min(1.0, matches / 3.0)

    def _marker_score(self, text: str, operation: str) -> float:
        pattern = self.MARKER_RE.get(operation, self.MARKER_RE["generate"])
        matches = len(pattern.findall(text))
        return min(1.0, matches / 2.0)

    def _relevance_score(self, text: str) -> float:
        # Penalize if output contains obvious off-topic content
        off_topic = ["unrelated", "i dont know", "no information", "cannot", "no context"]
        for phrase in off_topic:
            if phrase in text.lower():
                return 0.3
        return 0.8

    def compare(self, local_text: str, external_text: str, operation: str = "generate") -> Dict:
        local_score = self.score(local_text, operation)
        external_score = self.score(external_text, operation)
        winner = "external" if external_score.overall > local_score.overall else "local"
        return {
            "local": local_score.to_dict(),
            "external": external_score.to_dict(),
            "winner": winner,
        }
