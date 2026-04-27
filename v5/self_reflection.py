#!/usr/bin/env python3
"""
v5.3 Self-Reflection Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Reflection:
    id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    trigger: str = "periodic"
    structural: Dict = field(default_factory=dict)
    behavioral: Dict = field(default_factory=dict)
    quality: Dict = field(default_factory=dict)
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


class SelfReflectionEngine:
    def __init__(self):
        self.reflections: List[Reflection] = []

    def reflect(self, trigger: str, lifecycle_state: Dict, clustering_state: Dict, runtime_state: Dict, mode_usage: Dict, wake_history: List[str]) -> Reflection:
        structural = self._structural_snapshot(lifecycle_state, clustering_state, runtime_state)
        behavioral = self._behavioral_snapshot(mode_usage, wake_history)
        quality = self._quality_snapshot(lifecycle_state, runtime_state)

        summary = self._summarize(structural, behavioral, quality)
        recommendations = self._recommend(structural, behavioral, quality)

        r = Reflection(
            id=f"refl_{len(self.reflections)}_{datetime.now().strftime('%H%M%S')}",
            trigger=trigger,
            structural=structural,
            behavioral=behavioral,
            quality=quality,
            summary=summary,
            recommendations=recommendations,
        )
        self.reflections.append(r)
        return r

    def _structural_snapshot(self, lc_state: Dict, clustering_state: Dict, runtime_state: Dict) -> Dict:
        return {
            "total_beliefs": lc_state.get("total", 0),
            "active_beliefs": lc_state.get("active", 0),
            "retired_beliefs": lc_state.get("retired", 0),
            "belief_stages": lc_state.get("by_stage", {}),
            "avg_confidence": round(lc_state.get("avg_confidence", 0), 3),
            "total_concepts": clustering_state.get("total", 0),
            "concept_stages": clustering_state.get("by_stage", {}),
            "avg_coherence": round(clustering_state.get("avg_coherence", 0), 3),
            "queue_inbox": runtime_state.get("inbox", 0),
            "queue_outbox": runtime_state.get("outbox", 0),
            "cycles": runtime_state.get("cycles", 0),
        }

    def _behavioral_snapshot(self, mode_usage: Dict, wake_history: List[str]) -> Dict:
        total = sum(mode_usage.values())
        dominant = max(mode_usage, key=mode_usage.get) if mode_usage else "unknown"
        return {
            "mode_distribution": dict(mode_usage),
            "dominant_mode": dominant,
            "total_modes_used": len(mode_usage),
            "wake_count_30": len(wake_history[-30:]),
            "wake_accumulated": sum(1 for w in wake_history[-30:] if w == "accumulate"),
            "wake_woken": sum(1 for w in wake_history[-30:] if w == "wake"),
            "wake_silent": sum(1 for w in wake_history[-30:] if w == "silent"),
        }

    def _quality_snapshot(self, lc_state: Dict, runtime_state: Dict) -> Dict:
        errors = runtime_state.get("consecutive_errors", 0)
        fallback_rate = runtime_state.get("fallback_rate", 0.0)
        degraded = errors >= 3 or fallback_rate >= 0.3
        by_stage = lc_state.get("by_stage", {})
        weakening = by_stage.get("weakening", 0)
        return {
            "is_healthy": not degraded,
            "consecutive_errors": errors,
            "fallback_rate": round(fallback_rate, 3),
            "weakening_beliefs": weakening,
            "retired_ratio": round(lc_state.get("retired", 0) / max(1, lc_state.get("total", 1)), 3),
        }

    def _summarize(self, structural: Dict, behavioral: Dict, quality: Dict) -> str:
        parts = []
        if quality["is_healthy"]:
            parts.append("System healthy")
        else:
            parts.append("System degraded")
        parts.append(f"{structural['active_beliefs']} active beliefs")
        parts.append(f"{structural['total_concepts']} concepts ({structural['avg_coherence']} coherence)")
        parts.append(f"dominant mode: {behavioral['dominant_mode']}")
        if behavioral["wake_accumulated"] > behavioral["wake_woken"]:
            parts.append("mostly accumulating (low urgency)")
        return ", ".join(parts)

    def _recommend(self, structural: Dict, behavioral: Dict, quality: Dict) -> List[str]:
        recs = []
        if not quality["is_healthy"]:
            recs.append("switch to tight budget to conserve resources")
        if structural["avg_confidence"] < 0.4:
            recs.append("encourage more evidence signals for beliefs")
        if quality.get("weakening_beliefs", 0) > 0:
            recs.append("review weakening beliefs for potential retirement")
        if quality["retired_ratio"] > 0.3:
            recs.append("memory pruning active, check if too aggressive")
        if behavioral["dominant_mode"] == "quiet-watch":
            recs.append("system in passive mode, consider triggering active-absorb")
        return recs

    def latest(self) -> Optional[Reflection]:
        return self.reflections[-1] if self.reflections else None

    def all(self) -> List[Reflection]:
        return list(self.reflections)

    def summary(self) -> Dict:
        return {
            "total_reflections": len(self.reflections),
            "latest": self.latest().to_dict() if self.latest() else None,
        }