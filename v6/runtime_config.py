#!/usr/bin/env python3
"""
v6.5 Config layer for hybrid model runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class ExternalBudget:
    max_requests_per_day: int = 100
    max_cost_usd_per_day: float = 2.0
    used_requests_today: int = 0
    used_cost_usd_today: float = 0.0

    def allows(self, est_cost_usd: float = 0.0) -> tuple[bool, str]:
        if self.used_requests_today >= self.max_requests_per_day:
            return False, "daily external request limit reached"
        if self.used_cost_usd_today + est_cost_usd > self.max_cost_usd_per_day:
            return False, "daily external cost limit reached"
        return True, "ok"

    def record(self, est_cost_usd: float = 0.0):
        self.used_requests_today += 1
        self.used_cost_usd_today += est_cost_usd


@dataclass
class RuntimeConfig:
    local_enabled: bool = True
    external_enabled: bool = False
    local_model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"
    external_model_name: str = "MiniMax-M2.7"
    external_api_key_env: str = "MINIMAX_API_KEY"
    privacy_default: str = "normal"
    budget: ExternalBudget = None

    def __post_init__(self):
        if self.budget is None:
            self.budget = ExternalBudget()

    def to_dict(self) -> Dict:
        payload = asdict(self)
        return payload
