#!/usr/bin/env python3
"""
v5.x Consciousness Monitor — real-time vital signs for the Substrate.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class VitalSigns:
    status: str  # alive / degraded / critical
    overall_score: float  # 0.0 - 1.0
    runtime: Dict
    queue: Dict
    beliefs: Dict
    concepts: Dict
    cognition: Dict
    reflections: Dict
    alerts: List[str]
    timestamp: str

    def to_dict(self) -> Dict:
        return asdict(self)

    def summary(self) -> str:
        lines = [
            f"[{self.status.upper()}] score={self.overall_score:.2f}",
            f"  Runtime: {self.runtime.get('mode', 'unknown')} | cycles={self.runtime.get('cycles', 0)}",
            f"  Queue: inbox={self.queue.get('inbox', 0)} outbox={self.queue.get('outbox', 0)} poison={self.queue.get('poison', 0)}",
            f"  Beliefs: {self.beliefs.get('active', 0)} active | {self.beliefs.get('avg_confidence', 0):.2f} avg conf",
            f"  Concepts: {self.concepts.get('total', 0)} total | {self.concepts.get('avg_coherence', 0):.2f} avg coherence",
            f"  Cognition: dominant={self.cognition.get('dominant_mode', 'unknown')} | wake ratio={self.cognition.get('wake_ratio', 0):.2f}",
            f"  Reflections: {self.reflections.get('count', 0)} total",
        ]
        if self.alerts:
            lines.append("  ALERTS:")
            for a in self.alerts:
                lines.append(f"    - {a}")
        return "\n".join(lines)


class ConsciousnessMonitor:
    def __init__(self, runtime_dir: Path | None = None):
        self.runtime_dir = runtime_dir or Path.cwd() / "runtime"

    def check(self, lifecycle=None, clustering=None, mode_usage: Dict | None = None, wake_history: List[str] | None = None, reflection_engine=None) -> VitalSigns:
        runtime = self._check_runtime()
        queue = self._check_queue()
        beliefs = self._check_beliefs(lifecycle)
        concepts = self._check_concepts(clustering)
        cognition = self._check_cognition(mode_usage or {}, wake_history or [])
        reflections = self._check_reflections(reflection_engine)
        alerts = self._check_alerts(runtime, queue, beliefs)
        status = self._compute_status(alerts, runtime)
        score = self._compute_score(runtime, beliefs, cognition, alerts)

        return VitalSigns(
            status=status,
            overall_score=score,
            runtime=runtime,
            queue=queue,
            beliefs=beliefs,
            concepts=concepts,
            cognition=cognition,
            reflections=reflections,
            alerts=alerts,
            timestamp=datetime.now().isoformat(),
        )

    def _check_runtime(self) -> Dict:
        state_path = self.runtime_dir / "state.json"
        health_path = self.runtime_dir / "health.json"
        result = {"mode": "unknown", "cycles": 0, "last_success": None, "consecutive_errors": 0}

        if state_path.exists():
            with open(state_path) as f:
                state = json.load(f)
            result["mode"] = state.get("mode", "unknown")
            result["cycles"] = state.get("cycles", 0)
            result["last_success"] = state.get("last_success")

        if health_path.exists():
            with open(health_path) as f:
                health = json.load(f)
            result["consecutive_errors"] = health.get("consecutive_errors", 0)

        return result

    def _check_queue(self) -> Dict:
        queue_dir = self.runtime_dir / "queue"
        inbox_path = queue_dir / "inbox.json"
        outbox_path = queue_dir / "outbox.json"
        processed_path = queue_dir / "processed.json"

        inbox_count = 0
        outbox_count = 0
        processed_count = 0
        poison_count = 0

        if inbox_path.exists():
            with open(inbox_path) as f:
                inbox_count = len(json.load(f))
        if outbox_path.exists():
            with open(outbox_path) as f:
                outbox_count = len(json.load(f))
        if processed_path.exists():
            with open(processed_path) as f:
                processed_count = len(json.load(f))

        # count poison items (items with fail_count >= 3)
        poison_path = queue_dir / "poison.json"
        if poison_path.exists():
            with open(poison_path) as f:
                poison_count = len(json.load(f))

        return {
            "inbox": inbox_count,
            "outbox": outbox_count,
            "processed": processed_count,
            "poison": poison_count,
        }

    def _check_beliefs(self, lifecycle) -> Dict:
        if lifecycle is None:
            return {"total": 0, "active": 0, "by_stage": {}, "avg_confidence": 0.0}
        stats = lifecycle.stats()
        return {
            "total": stats.get("total", 0),
            "active": stats.get("active", 0),
            "retired": stats.get("retired", 0),
            "by_stage": stats.get("by_stage", {}),
            "avg_confidence": round(stats.get("avg_confidence", 0.0), 3),
        }

    def _check_concepts(self, clustering) -> Dict:
        if clustering is None:
            return {"total": 0, "active": 0, "by_stage": {}, "avg_coherence": 0.0}
        stats = clustering.stats()
        return {
            "total": stats.get("total", 0),
            "active": stats.get("active", 0),
            "by_stage": stats.get("by_stage", {}),
            "avg_coherence": round(stats.get("avg_coherence", 0.0), 3),
        }

    def _check_cognition(self, mode_usage: Dict, wake_history: List[str]) -> Dict:
        total_modes = sum(mode_usage.values())
        dominant = max(mode_usage, key=mode_usage.get) if mode_usage else "unknown"

        recent_wakes = wake_history[-30:] if len(wake_history) > 30 else wake_history
        wake_count = len(recent_wakes)
        wake_woken = sum(1 for w in recent_wakes if w == "wake")
        wake_ratio = wake_woken / max(1, wake_count)

        return {
            "mode_distribution": dict(mode_usage),
            "dominant_mode": dominant,
            "total_mode_ticks": total_modes,
            "wake_history_depth": len(wake_history),
            "wake_woken_30": wake_woken,
            "wake_ratio": round(wake_ratio, 3),
        }

    def _check_reflections(self, engine=None) -> Dict:
        if engine is not None:
            latest = engine.latest()
            return {
                "count": len(engine.reflections),
                "latest": latest.to_dict() if latest else None,
                "recommendations": latest.recommendations if latest else [],
            }
        return {"count": 0, "latest": None, "recommendations": []}

    def _compute_status(self, alerts: List[str], runtime: Dict) -> str:
        if any("CRITICAL" in a for a in alerts):
            return "critical"
        if runtime.get("consecutive_errors", 0) >= 3:
            return "degraded"
        if alerts:
            return "degraded"
        return "alive"

    def _compute_score(self, runtime: Dict, beliefs: Dict, cognition: Dict, alerts: List[str]) -> float:
        score = 1.0
        score -= min(0.3, runtime.get("consecutive_errors", 0) * 0.1)
        score -= min(0.2, len(alerts) * 0.1)
        avg_conf = beliefs.get("avg_confidence", 0.5)
        score -= (1.0 - avg_conf) * 0.2
        score -= (1.0 - cognition.get("wake_ratio", 1.0)) * 0.1
        return max(0.0, min(1.0, score))

    def _check_alerts(self, runtime: Dict, queue: Dict, beliefs: Dict) -> List[str]:
        alerts = []
        errors = runtime.get("consecutive_errors", 0)
        if errors >= 3:
            alerts.append(f"CRITICAL: {errors} consecutive errors")
        if errors >= 1:
            alerts.append(f"WARNING: {errors} consecutive errors")
        inbox = queue.get("inbox", 0)
        if inbox >= 10:
            alerts.append(f"WARNING: inbox pressure high ({inbox} items)")
        poison = queue.get("poison", 0)
        if poison >= 1:
            alerts.append(f"WARNING: {poison} poison items in queue")
        by_stage = beliefs.get("by_stage", {})
        embryonic = by_stage.get("embryonic", 0)
        if embryonic >= 5:
            alerts.append(f"INFO: {embryonic} embryonic beliefs need signals")
        return alerts