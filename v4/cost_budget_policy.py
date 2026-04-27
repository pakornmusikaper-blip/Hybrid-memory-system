#!/usr/bin/env python3
"""
v4.3 Cost-Aware Cognition Budget.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class BudgetDecision:
    budget_band: str
    spend_level: str
    prefer_heuristic: bool
    max_depth: str
    reason: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class CostBudgetPolicy:
    def decide(self, wake_decision: Dict, runtime_health: Dict, recent_spend_trend: float = 0.5) -> BudgetDecision:
        action = wake_decision.get("action", "silent")
        urgency = wake_decision.get("urgency", "none")
        priority = str(wake_decision.get("priority", "normal"))
        health = runtime_health.get("status", "healthy")
        fallback_rate = float(runtime_health.get("fallback_rate") or 0.0)

        if health == "degraded" or fallback_rate >= 0.5:
            if urgency in {"immediate", "high"} and action == "wake":
                return BudgetDecision(
                    budget_band="tight",
                    spend_level="minimum",
                    prefer_heuristic=False,
                    max_depth="focused",
                    reason="degraded runtime conserves budget but urgent wake requires focused spend",
                )
            return BudgetDecision(
                budget_band="tight",
                spend_level="minimum",
                prefer_heuristic=True,
                max_depth="heuristic",
                reason="degraded runtime conserves resources",
            )

        if urgency == "immediate" or (priority == "critical" and action == "wake"):
            return BudgetDecision(
                budget_band="generous",
                spend_level="maximum",
                prefer_heuristic=False,
                max_depth="deep",
                reason="immediate critical event justifies full depth spend",
            )

        if urgency == "high" and action == "wake":
            return BudgetDecision(
                budget_band="normal",
                spend_level="moderate",
                prefer_heuristic=False,
                max_depth="focused",
                reason="high urgency deserves focused spend",
            )

        if recent_spend_trend > 0.8:
            return BudgetDecision(
                budget_band="tight",
                spend_level="minimum",
                prefer_heuristic=True,
                max_depth="light",
                reason="recent high spend triggers budget conservation",
            )

        if action == "accumulate" and priority in {"normal", "low"}:
            return BudgetDecision(
                budget_band="normal",
                spend_level="moderate",
                prefer_heuristic=True,
                max_depth="standard",
                reason="accumulated signals get moderate spend with heuristic preference",
            )

        if action == "silent" or priority in {"low", "silent"}:
            return BudgetDecision(
                budget_band="tight",
                spend_level="minimum",
                prefer_heuristic=True,
                max_depth="heuristic",
                reason="silent/low priority events spend minimally",
            )

        return BudgetDecision(
            budget_band="normal",
            spend_level="moderate",
            prefer_heuristic=False,
            max_depth="standard",
            reason="default balanced budget decision",
        )
