#!/usr/bin/env python3
"""
v9.3 Quality comparison heuristics.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class QualityRow:
    scenario: str
    variant: str
    provider: str
    fallback: bool
    route_backend: str
    output_chars: int
    richness_score: float
    appropriateness_score: float
    note: str

    def to_dict(self) -> Dict:
        return asdict(self)


class QualityComparison:
    def compare(self, payload: Dict) -> List[QualityRow]:
        rows: List[QualityRow] = []
        for result in payload.get("results", []):
            scenario = result.get("scenario", "unknown")
            route = result.get("route", {})
            res = result.get("result", {})
            if not res:
                rows.append(QualityRow(
                    scenario=scenario,
                    variant="skipped",
                    provider="none",
                    fallback=False,
                    route_backend=route.get("backend", "unknown"),
                    output_chars=0,
                    richness_score=0.0,
                    appropriateness_score=self._appropriateness_for_skip(route.get("backend", "unknown"), scenario),
                    note=result.get("reason", "skipped"),
                ))
                continue

            text = res.get("text", "")
            provider = res.get("provider", "unknown")
            fallback = bool(res.get("fallback", False))
            route_backend = route.get("backend", provider)
            rows.append(QualityRow(
                scenario=scenario,
                variant=route_backend,
                provider=provider,
                fallback=fallback,
                route_backend=route_backend,
                output_chars=len(text),
                richness_score=self._richness(text, fallback, provider),
                appropriateness_score=self._appropriateness(route_backend, scenario, fallback),
                note=self._note(provider, fallback, route_backend),
            ))
        return rows

    def summary(self, rows: List[QualityRow]) -> Dict:
        avg_richness = sum(r.richness_score for r in rows) / max(1, len(rows))
        avg_appropriateness = sum(r.appropriateness_score for r in rows) / max(1, len(rows))
        by_variant = {}
        for r in rows:
            by_variant[r.variant] = by_variant.get(r.variant, 0) + 1
        return {
            "rows": [r.to_dict() for r in rows],
            "avg_richness": round(avg_richness, 3),
            "avg_appropriateness": round(avg_appropriateness, 3),
            "by_variant": by_variant,
        }

    def _richness(self, text: str, fallback: bool, provider: str) -> float:
        base = min(1.0, len(text) / 180.0)
        if provider == "minimax-api":
            base += 0.15
        if fallback:
            base -= 0.2
        return round(max(0.0, min(1.0, base)), 3)

    def _appropriateness(self, route_backend: str, scenario: str, fallback: bool) -> float:
        if scenario in {"summary", "reflection"} and route_backend == "external":
            return 1.0 if not fallback else 0.7
        if scenario == "low-value" and route_backend in {"heuristic", "local"}:
            return 1.0
        return 0.6 if not fallback else 0.4

    def _appropriateness_for_skip(self, route_backend: str, scenario: str) -> float:
        if scenario == "low-value" and route_backend == "heuristic":
            return 1.0
        return 0.5

    def _note(self, provider: str, fallback: bool, route_backend: str) -> str:
        if fallback:
            return "fallback reduced confidence in comparative quality"
        if provider == "minimax-api":
            return "external path active"
        if route_backend == "heuristic":
            return "cheap path selected intentionally"
        return "local path active"
