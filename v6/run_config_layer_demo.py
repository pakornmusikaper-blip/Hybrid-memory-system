#!/usr/bin/env python3
"""
Demo for v6.5 config layer and budget controls.
"""

from __future__ import annotations

import json

from configured_router import ConfiguredRouter
from runtime_config import ExternalBudget, RuntimeConfig


def main():
    config = RuntimeConfig(
        local_enabled=True,
        external_enabled=True,
        budget=ExternalBudget(
            max_requests_per_day=2,
            max_cost_usd_per_day=0.0015,
            used_requests_today=0,
            used_cost_usd_today=0.0,
        ),
    )
    router = ConfiguredRouter(config)

    scenarios = [
        {"name": "restricted reflect", "privacy": "restricted", "budget": "generous", "mode": "reflect", "urgency": "high"},
        {"name": "first external", "privacy": "normal", "budget": "generous", "mode": "focused", "urgency": "high"},
        {"name": "second external", "privacy": "normal", "budget": "generous", "mode": "summary", "urgency": "high"},
        {"name": "third blocked by request limit", "privacy": "normal", "budget": "generous", "mode": "reflect", "urgency": "high"},
    ]

    results = []
    for s in scenarios:
        route = router.decide(
            privacy=s["privacy"],
            budget=s["budget"],
            mode=s["mode"],
            urgency=s["urgency"],
        )
        if route.backend == "external" and route.allowed:
            router.record_external_use(route.estimated_cost_usd)
        results.append({
            "scenario": s["name"],
            "route": route.to_dict(),
            "budget_state": config.budget.__dict__.copy(),
        })

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
