#!/usr/bin/env python3
"""
v4.1 Adaptive cognition mode policy.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class ModeDecision:
    mode: str
    depth: str
    wake_conscious: bool
    compact: bool
    reason: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class AdaptiveModePolicy:
    def decide(self, priority_decision: Dict, runtime_health: Dict, queue_stats: Dict | None = None) -> ModeDecision:
        queue_stats = queue_stats or {}
        priority = priority_decision.get("priority", "normal")
        suggested_mode = priority_decision.get("mode", "quiet-watch")
        wake = bool(priority_decision.get("wake_conscious", False))
        health = runtime_health.get("status", "healthy")
        backlog = int(queue_stats.get("inbox", 0) or 0)

        if health in {"failed", "degraded"}:
            if priority in {"critical", "high"}:
                return ModeDecision(
                    mode="alert",
                    depth="compact",
                    wake_conscious=True,
                    compact=True,
                    reason="degraded runtime handling urgent event conservatively",
                )
            return ModeDecision(
                mode="quiet-watch",
                depth="minimal",
                wake_conscious=False,
                compact=True,
                reason="degraded runtime defers non-urgent cognition",
            )

        if priority == "critical":
            return ModeDecision(
                mode="alert",
                depth="focused",
                wake_conscious=True,
                compact=False,
                reason="critical event requires immediate escalation",
            )

        if priority == "high":
            return ModeDecision(
                mode="active-absorb",
                depth="focused" if backlog < 5 else "compact",
                wake_conscious=wake,
                compact=backlog >= 5,
                reason="high-priority event should be processed promptly",
            )

        if priority == "normal":
            if suggested_mode == "reflective":
                return ModeDecision(
                    mode="reflective",
                    depth="deep",
                    wake_conscious=False,
                    compact=False,
                    reason="normal event with reflective value",
                )
            return ModeDecision(
                mode="active-absorb",
                depth="standard",
                wake_conscious=False,
                compact=False,
                reason="routine normal cognition",
            )

        if priority == "low":
            return ModeDecision(
                mode="light-prepare",
                depth="light",
                wake_conscious=False,
                compact=True,
                reason="low-value work should be prepared lightly",
            )

        return ModeDecision(
            mode="quiet-watch",
            depth="minimal",
            wake_conscious=False,
            compact=True,
            reason="silent or unknown event should remain quiet",
        )
