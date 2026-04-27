#!/usr/bin/env python3
"""
v4.4 Intelligent Runtime — v4 policies integrated into v3 tick loop.
"""

from __future__ import annotations

import json
from pathlib import Path

from prioritizer import EventPrioritizer
from mode_policy import AdaptiveModePolicy
from wake_policy import ConsciousWakePolicy
from cost_budget_policy import CostBudgetPolicy


class IntelligentRuntime:
    def __init__(self, v3_runtime, v4_config: dict | None = None):
        self.runtime = v3_runtime
        v4_config = v4_config or {}
        self.prioritizer = EventPrioritizer()
        self.mode_policy = AdaptiveModePolicy()
        self.wake_policy = ConsciousWakePolicy()
        self.budget_policy = CostBudgetPolicy()
        self.spend_log: list[float] = []
        self.accumulated_insights: list[dict] = []

    def process_event(self, event: dict) -> dict:
        self.runtime.log(f"v4:processing event {event.get('id', 'unknown')}")

        priority = self.prioritizer.decide(event)
        self.runtime.log(f"v4:priority={priority.priority} mode={priority.mode}")

        health = self._get_health()
        mode_decision = self.mode_policy.decide(
            priority.to_dict(), health, self.runtime.queues.stats()
        )
        self.runtime.log(f"v4:mode={mode_decision.mode} depth={mode_decision.depth}")

        wake_decision = self.wake_policy.decide(
            mode_decision.to_dict(), event, self._recent_spend_trend()
        )
        self.runtime.log(f"v4:wake={wake_decision.action} urgency={wake_decision.urgency}")

        budget_decision = self.budget_policy.decide(
            wake_decision.to_dict(), health, self._recent_spend_trend()
        )
        self.runtime.log(
            f"v4:budget={budget_decision.budget_band} spend={budget_decision.spend_level}"
        )

        if wake_decision.action == "wake":
            self.runtime.log(f"v4:triggering conscious wake for event {event.get('id')}")
            result = self._execute_with_budget(event, mode_decision, budget_decision)
        elif wake_decision.action == "accumulate":
            self.runtime.log(f"v4:accumulating insight from event {event.get('id')}")
            self.accumulated_insights.append({"event": event, "wake": wake_decision.to_dict()})
            result = {"status": "accumulated", "event_id": event.get("id")}
        else:
            self.runtime.log(f"v4:silent drop for event {event.get('id')}")
            result = {"status": "silent", "event_id": event.get("id")}

        self._track_spend(budget_decision)
        return result

    def _execute_with_budget(self, event: dict, mode_decision, budget_decision):
        depth = budget_decision.max_depth
        prefer_heuristic = budget_decision.prefer_heuristic

        if depth == "deep":
            spend = 1.0
            output = {"depth": "deep", "heuristic": False}
        elif depth == "focused":
            spend = 0.7
            output = {"depth": "focused", "heuristic": prefer_heuristic}
        elif depth == "standard":
            spend = 0.5
            output = {"depth": "standard", "heuristic": prefer_heuristic}
        elif depth == "light":
            spend = 0.3
            output = {"depth": "light", "heuristic": True}
        else:
            spend = 0.1
            output = {"depth": "heuristic", "heuristic": True}

        self._track_spend_flat(spend)
        return {"status": "processed", **output}

    def _get_health(self) -> dict:
        health_path = self.runtime.runtime_dir / "health.json"
        if health_path.exists():
            with open(health_path) as f:
                return json.load(f)
        return {"status": "healthy"}

    def _recent_spend_trend(self) -> float:
        if not self.spend_log:
            return 0.5
        recent = self.spend_log[-5:]
        return sum(recent) / len(recent)

    def _track_spend(self, budget_decision):
        spend_map = {"minimum": 0.1, "moderate": 0.4, "maximum": 0.9}
        spend = spend_map.get(budget_decision.spend_level, 0.3)
        self.spend_log.append(spend)
        if len(self.spend_log) > 20:
            self.spend_log = self.spend_log[-20:]

    def _track_spend_flat(self, spend: float):
        self.spend_log.append(spend)
        if len(self.spend_log) > 20:
            self.spend_log = self.spend_log[-20:]

    def get_insights(self) -> list[dict]:
        return list(self.accumulated_insights)
