#!/usr/bin/env python3
"""
v8.5 Runtime config loader.
"""

from __future__ import annotations

import json
from pathlib import Path

from v6.runtime_config import ExternalBudget, RuntimeConfig


class RuntimeConfigLoader:
    def __init__(self, path: Path):
        self.path = Path(path)

    def load(self) -> RuntimeConfig:
        raw = {}
        if self.path.exists():
            with open(self.path) as f:
                raw = json.load(f)

        budget_raw = raw.get("budget", {})
        budget = ExternalBudget(
            max_requests_per_day=budget_raw.get("max_requests_per_day", 100),
            max_cost_usd_per_day=budget_raw.get("max_cost_usd_per_day", 2.0),
            used_requests_today=budget_raw.get("used_requests_today", 0),
            used_cost_usd_today=budget_raw.get("used_cost_usd_today", 0.0),
        )

        return RuntimeConfig(
            local_enabled=raw.get("local_enabled", True),
            external_enabled=raw.get("external_enabled", False),
            local_model_name=raw.get("local_model_name", "Qwen/Qwen2.5-0.5B-Instruct"),
            external_model_name=raw.get("external_model_name", "MiniMax-M2.7"),
            external_api_key_env=raw.get("external_api_key_env", "MINIMAX_API_KEY"),
            privacy_default=raw.get("privacy_default", "normal"),
            budget=budget,
        )
