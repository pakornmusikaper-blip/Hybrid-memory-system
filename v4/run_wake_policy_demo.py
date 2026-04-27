#!/usr/bin/env python3
"""
Demo for v4.2 conscious wake policy chained with prioritizer and mode policy.
"""

from __future__ import annotations

import json

from wake_policy import ConsciousWakePolicy
from mode_policy import AdaptiveModePolicy
from prioritizer import EventPrioritizer


def main():
    prioritizer = EventPrioritizer()
    mode_policy = AdaptiveModePolicy()
    wake_policy = ConsciousWakePolicy()

    scenarios = [
        {
            "name": "critical high-stakes belief shift",
            "event": {"type": "belief_shift", "confidence": 0.91, "priority": "critical"},
            "health": {"status": "healthy"},
            "queue": {"inbox": 2},
        },
        {
            "name": "direct query",
            "event": {"type": "query"},
            "health": {"status": "healthy"},
            "queue": {"inbox": 1},
        },
        {
            "name": "urgent correction",
            "event": {"type": "correction", "urgent": True},
            "health": {"status": "healthy"},
            "queue": {"inbox": 0},
        },
        {
            "name": "strong intuition reflective",
            "event": {"type": "intuition", "confidence": 0.85, "mode": "reflective"},
            "health": {"status": "healthy"},
            "queue": {"inbox": 3},
        },
        {
            "name": "low cleanup silent",
            "event": {"type": "cleanup"},
            "health": {"status": "healthy"},
            "queue": {"inbox": 1},
        },
        {
            "name": "weak signal accumulation",
            "event": {"type": "followup", "confidence": 0.4, "priority": "normal"},
            "health": {"status": "healthy"},
            "queue": {"inbox": 5},
            "evidence_strength": 0.3,
        },
    ]

    results = []
    for scenario in scenarios:
        p = prioritizer.decide(scenario["event"]).to_dict()
        m = mode_policy.decide(p, scenario["health"], scenario["queue"]).to_dict()
        w = wake_policy.decide(m, scenario["event"], scenario.get("evidence_strength", 0.5)).to_dict()
        results.append({
            "scenario": scenario["name"],
            "priority": {"priority": p["priority"], "mode": p["mode"]},
            "mode": {"mode": m["mode"], "depth": m["depth"]},
            "wake": w,
        })

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
