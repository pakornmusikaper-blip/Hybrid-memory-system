#!/usr/bin/env python3
"""
v8.6 Config-driven hybrid runtime.
"""

from __future__ import annotations

import json
from pathlib import Path

from v4.prioritizer import EventPrioritizer
from v4.mode_policy import AdaptiveModePolicy
from v4.wake_policy import ConsciousWakePolicy
from v4.cost_budget_policy import CostBudgetPolicy
from v6.model_adapter import HeuristicAdapter
from v6.real_qwen_adapter import RealQwenAdapter, QwenConfig
from v6.minimax_adapter import MiniMaxAdapter, MiniMaxConfig
from v6.configured_router import ConfiguredRouter
from v8.config_loader import RuntimeConfigLoader


class ConfigDrivenHybridRuntime:
    def __init__(self, v3_runtime, config_path: Path):
        self.runtime = v3_runtime
        self.config_path = Path(config_path)
        self.config = RuntimeConfigLoader(self.config_path).load()
        self.prioritizer = EventPrioritizer()
        self.mode_policy = AdaptiveModePolicy()
        self.wake_policy = ConsciousWakePolicy()
        self.budget_policy = CostBudgetPolicy()
        self.router = ConfiguredRouter(self.config)
        self.local_adapter = RealQwenAdapter(QwenConfig(model_name=self.config.local_model_name))
        self.external_adapter = MiniMaxAdapter(MiniMaxConfig(model_name=self.config.external_model_name, api_key_env=self.config.external_api_key_env, enabled=self.config.external_enabled))
        self.heuristic_adapter = HeuristicAdapter()
        self.spend_log: list[float] = []

    def reload_config(self):
        self.config = RuntimeConfigLoader(self.config_path).load()
        self.router = ConfiguredRouter(self.config)

    def process_event(self, event: dict) -> dict:
        self.reload_config()
        priority = self.prioritizer.decide(event)
        health = self._get_health()
        mode_decision = self.mode_policy.decide(priority.to_dict(), health, self.runtime.queues.stats())
        wake_decision = self.wake_policy.decide(mode_decision.to_dict(), event, self._recent_spend_trend())
        budget_decision = self.budget_policy.decide(wake_decision.to_dict(), health, self._recent_spend_trend())
        if event.get("force_budget_band"):
            budget_decision.budget_band = event["force_budget_band"]

        if wake_decision.action != "wake":
            return {"status": wake_decision.action, "event_id": event.get("id")}

        route = self.router.decide(
            privacy=event.get("privacy", self.config.privacy_default),
            budget=budget_decision.budget_band,
            mode=self._route_mode_from_budget(budget_decision.max_depth),
            urgency=wake_decision.urgency,
        )
        adapter = self._select_adapter(route.backend)
        operation = event.get("operation", "generate")
        payload = event.get("content", "")
        result = self._run_adapter(adapter, operation, payload, self._route_mode_from_budget(budget_decision.max_depth))
        if route.backend == "external" and route.allowed:
            self.router.record_external_use(route.estimated_cost_usd)
        self._track_spend(budget_decision)
        return {
            "status": "processed",
            "event_id": event.get("id"),
            "config_path": str(self.config_path),
            "route": route.to_dict(),
            "result": result.to_dict(),
        }

    def _run_adapter(self, adapter, operation: str, payload: str, mode: str):
        if operation == "summary":
            return adapter.summarize(payload)
        if operation == "reflect":
            return adapter.reflect(payload)
        return adapter.generate(payload, mode)

    def _route_mode_from_budget(self, depth: str) -> str:
        return {
            "heuristic": "light",
            "light": "light",
            "standard": "standard",
            "focused": "focused",
            "deep": "reflect",
        }.get(depth, "standard")

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
        self.spend_log.append(spend_map.get(budget_decision.spend_level, 0.3))
        self.spend_log = self.spend_log[-20:]
