#!/usr/bin/env python3
"""
v6.5 Configured hybrid router with budget gates.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict

from v6.model_routing_policy import ModelRoutingPolicy
from v6.runtime_config import RuntimeConfig


@dataclass
class ConfiguredRoute:
    backend: str
    allowed: bool
    reason: str
    estimated_cost_usd: float

    def to_dict(self) -> Dict:
        return asdict(self)


class ConfiguredRouter:
    def __init__(self, config: RuntimeConfig | None = None):
        self.config = config or RuntimeConfig()
        self.policy = ModelRoutingPolicy()

    def decide(self, *, privacy: str, budget: str, mode: str, urgency: str) -> ConfiguredRoute:
        decision = self.policy.decide(privacy=privacy, budget=budget, mode=mode, urgency=urgency)

        if decision.backend == "external":
            if not self.config.external_enabled:
                return ConfiguredRoute("local", False, "external disabled by config", 0.0)
            est_cost = self._estimate_external_cost(mode)
            allowed, reason = self.config.budget.allows(est_cost)
            if not allowed:
                return ConfiguredRoute("local", False, reason, est_cost)
            return ConfiguredRoute("external", True, decision.reason, est_cost)

        if decision.backend == "local" and not self.config.local_enabled:
            return ConfiguredRoute("heuristic", False, "local disabled by config", 0.0)

        return ConfiguredRoute(decision.backend, True, decision.reason, 0.0)

    def record_external_use(self, est_cost_usd: float):
        self.config.budget.record(est_cost_usd)

    def _estimate_external_cost(self, mode: str) -> float:
        table = {
            "light": 0.0002,
            "standard": 0.0005,
            "summary": 0.0004,
            "focused": 0.0008,
            "reflect": 0.0010,
        }
        return table.get(mode, 0.0005)
