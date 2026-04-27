#!/usr/bin/env python3
"""
Demo for v5.3 Self-Reflection Engine.
"""

from __future__ import annotations

import json

from belief_lifecycle import BeliefLifecycle, Belief
from clustering import BeliefClustering, cluster_beliefs
from self_reflection import SelfReflectionEngine


def main():
    lc = BeliefLifecycle()
    clustering = BeliefClustering()
    engine = SelfReflectionEngine()

    # create beliefs
    for b_id, content, cat in [
        ("b1", "Hermes gateway handles multi-profile routing", "systems"),
        ("b2", "Hermes profile switcher uses local state", "systems"),
        ("b3", "Hermes status API exposes runtime metrics", "systems"),
        ("b4", "Qwen model works well for local inference", "models"),
    ]:
        lc.add(Belief(id=b_id, content=content, category=cat, confidence=0.6))

    lc.add_signal("b1")
    lc.add_signal("b1")
    lc.add_signal("b1")
    lc.add_signal("b1")

    for _ in range(3):
        lc.add_contradiction("b2")

    beliefs = [lc.get(b_id) for b_id in ["b1", "b2", "b3", "b4"]]
    cluster_beliefs(beliefs, clustering)

    lc_state = lc.stats()
    clustering_state = clustering.stats()

    runtime_state = {"inbox": 3, "outbox": 1, "cycles": 120, "consecutive_errors": 0, "fallback_rate": 0.05}

    mode_usage = {"quiet-watch": 5, "active-absorb": 8, "reflective": 2}
    wake_history = ["silent", "accumulate", "wake", "silent", "accumulate", "accumulate"]

    r = engine.reflect("periodic", lc_state, clustering_state, runtime_state, mode_usage, wake_history)
    print(json.dumps(r.to_dict(), indent=2))


if __name__ == "__main__":
    main()