#!/usr/bin/env python3
"""
Demo for v4.0 prioritization engine.
"""

from __future__ import annotations

import json

from prioritizer import EventPrioritizer


def main():
    prioritizer = EventPrioritizer()
    events = [
        {"id": "e1", "type": "contradiction", "confidence": 0.92},
        {"id": "e2", "type": "query"},
        {"id": "e3", "type": "cleanup"},
        {"id": "e4", "type": "duplicate"},
        {"id": "e5", "type": "correction", "urgent": True},
        {"id": "e6", "type": "intuition", "confidence": 0.75},
        {"id": "e7", "type": "poison", "repeated_failures": 4},
    ]

    results = []
    for event in events:
        decision = prioritizer.decide(event)
        results.append({"event": event, "decision": decision.to_dict()})

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
