#!/usr/bin/env python3
"""
Demo for v6.7 persisted usage ledger.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from runtime_config import ExternalBudget, RuntimeConfig
from configured_router import ConfiguredRouter
from usage_ledger import UsageLedger
from ledger_budget_bridge import sync_budget_from_ledger


def main():
    root = Path("/tmp/v6_usage_ledger_demo")
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    ledger = UsageLedger(root / "usage-ledger.json")
    config = RuntimeConfig(
        local_enabled=True,
        external_enabled=True,
        budget=ExternalBudget(max_requests_per_day=3, max_cost_usd_per_day=0.002),
    )
    sync_budget_from_ledger(config, ledger)
    router = ConfiguredRouter(config)

    scenarios = [
        {"privacy": "normal", "budget": "generous", "mode": "focused", "urgency": "high", "cost": 0.0008, "event_id": "e1"},
        {"privacy": "normal", "budget": "generous", "mode": "summary", "urgency": "high", "cost": 0.0004, "event_id": "e2"},
        {"privacy": "normal", "budget": "generous", "mode": "reflect", "urgency": "high", "cost": 0.0010, "event_id": "e3"},
    ]

    outputs = []
    for s in scenarios:
        route = router.decide(privacy=s["privacy"], budget=s["budget"], mode=s["mode"], urgency=s["urgency"])
        if route.backend == "external" and route.allowed:
            ledger.record("minimax-api", "MiniMax-M2.7", route.estimated_cost_usd, s["event_id"])
            sync_budget_from_ledger(config, ledger)
        outputs.append({
            "event_id": s["event_id"],
            "route": route.to_dict(),
            "budget": config.budget.__dict__.copy(),
            "ledger": ledger.snapshot(),
        })

    print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()
