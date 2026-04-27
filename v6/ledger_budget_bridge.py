#!/usr/bin/env python3
"""
v6.7 Bridge persisted ledger into runtime budget counters.
"""

from __future__ import annotations

from v6.runtime_config import RuntimeConfig
from v6.usage_ledger import UsageLedger


def sync_budget_from_ledger(config: RuntimeConfig, ledger: UsageLedger) -> RuntimeConfig:
    snapshot = ledger.snapshot()
    config.budget.used_requests_today = snapshot.get("total_requests", 0)
    config.budget.used_cost_usd_today = snapshot.get("total_cost_usd", 0.0)
    return config
