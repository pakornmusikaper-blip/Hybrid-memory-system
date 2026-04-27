#!/usr/bin/env python3
"""
v4.2 Conscious Wake Policy.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class WakeDecision:
    action: str
    urgency: str
    deliver_now: bool
    accumulate: bool
    summary_batch: bool
    reason: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class ConsciousWakePolicy:
    def __init__(self):
        self.accumulated: List[Dict] = []

    def decide(self, mode_decision: Dict, event: Dict, evidence_strength: float = 0.5) -> WakeDecision:
        etype = str(event.get("type", "unknown"))
        confidence = float(event.get("confidence") or 0.0)
        priority = str(mode_decision.get("priority", "normal"))
        mode = str(mode_decision.get("mode", "quiet-watch"))

        # queries always wake
        if etype == "query":
            return WakeDecision(
                action="wake",
                urgency="normal",
                deliver_now=True,
                accumulate=False,
                summary_batch=False,
                reason="direct query requires conscious response",
            )

        # urgent corrections always wake
        if etype == "correction" and bool(event.get("urgent")):
            return WakeDecision(
                action="wake",
                urgency="high",
                deliver_now=True,
                accumulate=False,
                summary_batch=False,
                reason="urgent correction triggers immediate response",
            )

        # critical high-confidence always wakes
        if priority == "critical" and confidence >= 0.8:
            return WakeDecision(
                action="wake",
                urgency="immediate",
                deliver_now=True,
                accumulate=False,
                summary_batch=False,
                reason="critical high-confidence event demands immediate attention",
            )

        # critical events should wake
        if priority == "critical":
            return WakeDecision(
                action="wake",
                urgency="high",
                deliver_now=True,
                accumulate=False,
                summary_batch=False,
                reason="critical event should wake conscious layer",
            )

        # reflective strong signals accumulate
        if mode == "reflective" and confidence >= 0.7:
            return WakeDecision(
                action="accumulate",
                urgency="low",
                deliver_now=False,
                accumulate=True,
                summary_batch=False,
                reason="strong reflection worth surfacing but not interrupting",
            )

        # reflective moderate signals batch
        if mode == "reflective":
            return WakeDecision(
                action="accumulate",
                urgency="low",
                deliver_now=False,
                accumulate=True,
                summary_batch=True,
                reason="reflection can be batched with other insights",
            )

        # low/silent priority stays quiet
        if priority in {"low", "silent"}:
            return WakeDecision(
                action="silent",
                urgency="none",
                deliver_now=False,
                accumulate=False,
                summary_batch=False,
                reason="low/silent priority events should not interrupt",
            )

        # weak evidence accumulates in batch
        if evidence_strength < 0.4:
            return WakeDecision(
                action="accumulate",
                urgency="low",
                deliver_now=False,
                accumulate=True,
                summary_batch=True,
                reason="weak evidence should batch with other weak signals",
            )

        # moderate signals batch
        if confidence < 0.6 and evidence_strength < 0.7:
            return WakeDecision(
                action="accumulate",
                urgency="low",
                deliver_now=False,
                accumulate=True,
                summary_batch=True,
                reason="moderate signal can be batched for periodic review",
            )

        # fallback
        return WakeDecision(
            action="silent",
            urgency="none",
            deliver_now=False,
            accumulate=False,
            summary_batch=False,
            reason="default silent handling",
        )
