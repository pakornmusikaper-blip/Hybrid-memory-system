#!/usr/bin/env python3
"""
Demo for v4.3 cost-aware budget chained with v4.0-v4.2.
"""

from __future__ import annotations

import json

from cost_budget_policy import CostBudgetPolicy
from wake_policy import ConsciousWakePolicy
from mode_policy import AdaptiveModePolicy
from prioritizer import EventPrioritizer


def main():
    prioritizer = EventPrioritizer()
    mode_policy = AdaptiveModePolicy()
    wake_policy = ConsciousWakePolicy()
    budget_policy = CostBudgetPolicy()

    scenarios = [
        {
            "name": "critical query healthy runtime",
            "event": {"type": "query", "confidence": 0.9},
            "health": {"status": "healthy"},
            "queue": {"inbox": 2},
            "recent_spend_trend": 0.3,
        },
        {
            "name": "urgent correction degraded runtime",
            "event": {"type": "correction", "urgent": True},
            "health": {"status": "degraded"},
            "queue": {"inbox": 5},
            "recent_spend_trend": 0.2,
        },
        {
            "name": "moderate reflection healthy tight budget",
            "event": {"type": "intuition", "confidence": 0.75},
            "health": {"status": "healthy"},
            "queue": {"inbox": 3},
            "recent_spend_trend": 0.9,
        },
        {
            "name": "low cleanup silent",
            "event": {"type": "cleanup"},
            "health": {"status": "healthy"},
            "queue": {"inbox": 1},
            "recent_spend_trend": 0.4,
        },
    ]

    results = []
    for s in scenarios:
        p = prioritizer.decide(s["event"]).to_dict()
        m = mode_policy.decide(p, s["health"], s["queue"]).to_dict()
        w = wake_policy.decide(m, s["event"], s.get("evidence_strength", 0.5)).to_dict()
        b = budget_policy.decide(w, s["health"], s.get("recent_spend_trend", 0.5)).to_dict()
        results.append({
            "scenario": s["name"],
            "priority": p["priority"],
            "mode": m["mode"],
            "wake": w["action"],
            "budget": b["budget_band"],
            "spend": b["spend_level"],
            "heuristic": b["prefer_heuristic"],
            "max_depth": b["max_depth"],
        })

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
