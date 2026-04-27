#!/usr/bin/env python3
"""
Demo for v4.1 adaptive cognition modes.
"""

from __future__ import annotations

import json

from mode_policy import AdaptiveModePolicy
from prioritizer import EventPrioritizer


def main():
    prioritizer = EventPrioritizer()
    policy = AdaptiveModePolicy()

    scenarios = [
        {
            "name": "critical contradiction healthy",
            "event": {"type": "contradiction", "confidence": 0.95},
            "health": {"status": "healthy"},
            "queue": {"inbox": 1},
        },
        {
            "name": "high query degraded",
            "event": {"type": "query"},
            "health": {"status": "degraded"},
            "queue": {"inbox": 8},
        },
        {
            "name": "low cleanup healthy",
            "event": {"type": "cleanup"},
            "health": {"status": "healthy"},
            "queue": {"inbox": 0},
        },
        {
            "name": "strong intuition healthy",
            "event": {"type": "intuition", "confidence": 0.82},
            "health": {"status": "healthy"},
            "queue": {"inbox": 2},
        },
        {
            "name": "normal followup degraded",
            "event": {"type": "followup"},
            "health": {"status": "degraded"},
            "queue": {"inbox": 2},
        },
    ]

    results = []
    for scenario in scenarios:
        p = prioritizer.decide(scenario["event"]).to_dict()
        m = policy.decide(p, scenario["health"], scenario["queue"]).to_dict()
        results.append({"scenario": scenario["name"], "priority": p, "mode": m})

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
