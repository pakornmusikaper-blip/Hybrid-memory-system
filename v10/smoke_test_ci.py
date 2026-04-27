#!/usr/bin/env python3
"""
v10 smoke test — runs in CI without heavy dependencies.
"""

from __future__ import annotations

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


def run() -> int:
    errors: list[str] = []

    p = EventPrioritizer()
    result = p.decide({"id": "x", "content": "test", "type": "query"})
    if not result.priority:
        errors.append(f"bad priority: {result.priority}")

    mp = AdaptiveModePolicy()
    mode = mp.decide({"priority": "medium", "mode": "standard"}, {"cpu_percent": 50, "memory_percent": 50}, {"inbox": 0, "outbox": 0, "processed": 0, "poison": 0})
    if not mode.mode:
        errors.append("mode_policy returned empty")

    wp = ConsciousWakePolicy()
    wp.decide({"mode": "standard", "urgency": "normal"}, {"id": "x", "content": "test", "type": "query"}, 0.0)

    bp = CostBudgetPolicy()
    br = bp.decide({"action": "wake", "urgency": "normal"}, {"cpu_percent": 50, "memory_percent": 50}, 0.0)
    if not br.budget_band:
        errors.append("cost_budget_policy empty")

    routing = ModelRoutingPolicy()
    rd = routing.decide(privacy="normal", budget="normal", mode="standard", urgency="normal")
    if rd.backend not in {"local", "external", "heuristic"}:
        errors.append(f"bad routing: {rd.backend}")

    h = HeuristicAdapter()
    hr = h.generate("hello", "standard")
    if not hr.text:
        errors.append("heuristic empty")

    if errors:
        print("FAIL")
        for e in errors:
            print(f"  ERROR: {e}")
        return 1
    print("PASS")
    return 0


if __name__ == '__main__':
    sys.exit(run())
