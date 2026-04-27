#!/usr/bin/env python3
"""
v4.0 Event Prioritization Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class PriorityDecision:
    priority: str
    mode: str
    wake_conscious: bool
    process_now: bool
    defer_seconds: int = 0
    reason: str = ""

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class EventPrioritizer:
    def decide(self, event: Dict) -> PriorityDecision:
        etype = event.get("type", "unknown")
        confidence = float(event.get("confidence", 0.0) or 0.0)
        urgent = bool(event.get("urgent", False))
        repeated_failures = int(event.get("repeated_failures", 0) or 0)

        if etype == "contradiction" and confidence >= 0.8:
            return PriorityDecision(
                priority="critical",
                mode="alert",
                wake_conscious=True,
                process_now=True,
                reason="high-confidence contradiction",
            )

        if etype == "correction" and urgent:
            return PriorityDecision(
                priority="critical",
                mode="alert",
                wake_conscious=True,
                process_now=True,
                reason="urgent correction from conscious layer",
            )

        if etype == "poison" and repeated_failures >= 3:
            return PriorityDecision(
                priority="high",
                mode="alert",
                wake_conscious=True,
                process_now=True,
                reason="repeated poison queue failure",
            )

        if etype == "query":
            return PriorityDecision(
                priority="high",
                mode="active-absorb",
                wake_conscious=False,
                process_now=True,
                reason="bridge query should be handled promptly",
            )

        if etype == "intuition" and confidence >= 0.7:
            return PriorityDecision(
                priority="high",
                mode="reflective",
                wake_conscious=True,
                process_now=True,
                reason="strong intuition candidate",
            )

        if etype in {"absorb", "review", "followup"}:
            return PriorityDecision(
                priority="normal",
                mode="active-absorb",
                wake_conscious=False,
                process_now=True,
                reason="routine cognition work",
            )

        if etype in {"cleanup", "refresh", "weak-belief"}:
            return PriorityDecision(
                priority="low",
                mode="light-prepare",
                wake_conscious=False,
                process_now=False,
                defer_seconds=300,
                reason="low-value maintenance can be deferred",
            )

        if etype == "duplicate":
            return PriorityDecision(
                priority="silent",
                mode="silent-drop",
                wake_conscious=False,
                process_now=False,
                defer_seconds=0,
                reason="duplicate event should be ignored quietly",
            )

        return PriorityDecision(
            priority="normal",
            mode="quiet-watch",
            wake_conscious=False,
            process_now=False,
            defer_seconds=60,
            reason="default cautious handling",
        )
