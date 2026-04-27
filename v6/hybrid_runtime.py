#!/usr/bin/env python3
"""
v6.3 Hybrid Runtime integrates v4 cognition with v6 model routing/adapters.
"""

from __future__ import annotations

import json
from pathlib import Path

from v4.prioritizer import EventPrioritizer
from v4.mode_policy import AdaptiveModePolicy
from v4.wake_policy import ConsciousWakePolicy
from v4.cost_budget_policy import CostBudgetPolicy
from v6.model_adapter import HeuristicAdapter
from v6.model_routing_policy import ModelRoutingPolicy
from v6.real_qwen_adapter import RealQwenAdapter
from v6.minimax_adapter import MiniMaxAdapter


class HybridRuntime:
    def __init__(self, v3_runtime):
        self.runtime = v3_runtime
        self.prioritizer = EventPrioritizer()
        self.mode_policy = AdaptiveModePolicy()
        self.wake_policy = ConsciousWakePolicy()
        self.budget_policy = CostBudgetPolicy()
        self.routing_policy = ModelRoutingPolicy()
        self.local_adapter = RealQwenAdapter()
        self.external_adapter = MiniMaxAdapter()
        self.heuristic_adapter = HeuristicAdapter()
        self.spend_log: list[float] = []
        self.accumulated_insights: list[dict] = []

    def process_event(self, event: dict) -> dict:
        self.runtime.log(f"v6:processing:{event.get('id', 'unknown')}")

        priority = self.prioritizer.decide(event)
        health = self._get_health()
        mode_decision = self.mode_policy.decide(priority.to_dict(), health, self.runtime.queues.stats())
        wake_decision = self.wake_policy.decide(mode_decision.to_dict(), event, self._recent_spend_trend())
        budget_decision = self.budget_policy.decide(wake_decision.to_dict(), health, self._recent_spend_trend())

        self.runtime.log(f"v6:priority={priority.priority} mode={mode_decision.mode} wake={wake_decision.action} budget={budget_decision.budget_band}")

        if wake_decision.action == "silent":
            return {"status": "silent", "event_id": event.get("id")}

        if wake_decision.action == "accumulate":
            self.accumulated_insights.append({
                "event": event,
                "priority": priority.to_dict(),
                "mode": mode_decision.to_dict(),
                "wake": wake_decision.to_dict(),
                "budget": budget_decision.to_dict(),
            })
            return {"status": "accumulated", "event_id": event.get("id")}

        route = self.routing_policy.decide(
            privacy=event.get("privacy", "normal"),
            budget=budget_decision.budget_band,
            mode=self._route_mode_from_budget(budget_decision.max_depth),
            urgency=wake_decision.urgency,
        )
        self.runtime.log(f"v6:route={route.backend} reason={route.reason}")

        adapter = self._select_adapter(route.backend)
        operation = event.get("operation", "generate")
        payload = event.get("content", event.get("prompt", ""))
        result = self._run_adapter(adapter, operation, payload, self._route_mode_from_budget(budget_decision.max_depth))
        self._track_spend(budget_decision)

        return {
            "status": "processed",
            "event_id": event.get("id"),
            "route": route.to_dict(),
            "result": result.to_dict(),
            "priority": priority.to_dict(),
            "mode": mode_decision.to_dict(),
            "wake": wake_decision.to_dict(),
            "budget": budget_decision.to_dict(),
        }

    def _run_adapter(self, adapter, operation: str, payload: str, mode: str):
        if operation == "summary":
            return adapter.summarize(payload)
        if operation == "reflect":
            return adapter.reflect(payload)
        return adapter.generate(payload, mode)

    def _route_mode_from_budget(self, depth: str) -> str:
        table = {
            "heuristic": "light",
            "light": "light",
            "standard": "standard",
            "focused": "focused",
            "deep": "reflect",
        }
        return table.get(depth, "standard")

    def _select_adapter(self, backend: str):
        if backend == "external":
            return self.external_adapter
        if backend == "heuristic":
            return self.heuristic_adapter
        return self.local_adapter

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

    def get_insights(self):
        return list(self.accumulated_insights)
