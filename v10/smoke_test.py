#!/usr/bin/env python3
"""
v10.x Smoke test runner for regression safety.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v4.prioritizer import EventPrioritizer
from v4.mode_policy import AdaptiveModePolicy
from v4.wake_policy import ConsciousWakePolicy
from v4.cost_budget_policy import CostBudgetPolicy
from v6.model_adapter import HeuristicAdapter
from v6.model_routing_policy import ModelRoutingPolicy
from v6.minimax_adapter import MiniMaxAdapter


def run_smoke_test() -> dict:
    errors = []
    warnings = []

    try:
        p = EventPrioritizer()
        event = {"id": "smoke1", "content": "test", "type": "query"}
        result = p.decide(event)
        if result.priority not in {"critical", "high", "medium", "low", "minimal"}:
            errors.append(f"bad priority: {result.priority}")
    except Exception as e:
        errors.append(f"prioritizer error: {e}")

    try:
        mp = AdaptiveModePolicy()
        health = {"cpu_percent": 50, "memory_percent": 50}
        queues = {"inbox": 0, "outbox": 0, "processed": 0, "poison": 0}
        mode_result = mp.decide({"priority": "medium", "mode": "standard"}, health, queues)
        if not mode_result.mode:
            errors.append("mode_policy returned empty mode")
    except Exception as e:
        errors.append(f"mode_policy error: {e}")

    try:
        wp = ConsciousWakePolicy()
        wake_result = wp.decide(
            {"mode": "standard", "urgency": "normal"},
            {"id": "smoke2", "content": "test event", "type": "query"},
            0.0,
        )
    except Exception as e:
        errors.append(f"wake_policy error: {e}")

    try:
        bp = CostBudgetPolicy()
        budget_result = bp.decide(
            {"action": "wake", "urgency": "normal"},
            {"cpu_percent": 50, "memory_percent": 50},
            0.0,
        )
        if not budget_result.budget_band:
            errors.append("cost_budget_policy returned empty budget_band")
    except Exception as e:
        errors.append(f"cost_budget_policy error: {e}")

    try:
        routing = ModelRoutingPolicy()
        decision = routing.decide(privacy="normal", budget="normal", mode="standard", urgency="normal")
        if decision.backend not in {"local", "external", "heuristic"}:
            errors.append(f"bad routing backend: {decision.backend}")
    except Exception as e:
        errors.append(f"routing_policy error: {e}")

    try:
        heuristic = HeuristicAdapter()
        result = heuristic.generate("hello", "standard")
        if not result.text:
            errors.append("heuristic generate returned empty text")
        if result.provider != "heuristic" and result.provider != "local":
            errors.append(f"bad heuristic provider: {result.provider}")
    except Exception as e:
        errors.append(f"heuristic adapter error: {e}")

    try:
        external = MiniMaxAdapter()
        result = external.generate("hello", "standard")
        # external may fail but should not raise
    except Exception as e:
        warnings.append(f"external adapter raised (expected in test env): {e}")

    status = "PASS" if not errors else "FAIL"
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
    }


def main():
    result = run_smoke_test()
    print(f"Smoke test: {result['status']}")
    for e in result["errors"]:
        print(f"  ERROR: {e}")
    for w in result["warnings"]:
        print(f"  WARNING: {w}")
    if result["status"] == "FAIL":
        sys.exit(1)


if __name__ == '__main__':
    main()
