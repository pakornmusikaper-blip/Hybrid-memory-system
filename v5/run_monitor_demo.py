#!/usr/bin/env python3
"""
Demo for Consciousness Monitor — simulates vital signs from v5 components.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from belief_lifecycle import BeliefLifecycle, Belief
from clustering import BeliefClustering, cluster_beliefs
from self_reflection import SelfReflectionEngine
from consciousness_monitor import ConsciousnessMonitor


def main():
    # setup simulated runtime dir
    runtime_dir = Path("/tmp/consciousness_monitor_demo")
    if runtime_dir.exists():
        shutil.rmtree(runtime_dir)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    (runtime_dir / "queue").mkdir()

    # write simulated state
    state = {"mode": "active-absorb", "cycles": 847, "last_success": "2026-04-27T10:35:00"}
    health = {"consecutive_errors": 1}
    import json
    with open(runtime_dir / "state.json", "w") as f:
        json.dump(state, f)
    with open(runtime_dir / "health.json", "w") as f:
        json.dump(health, f)

    # build lifecycle with beliefs
    lc = BeliefLifecycle()
    for b_id, content, cat, conf, signals in [
        ("b1", "Hermes gateway handles routing", "systems", 0.7, 4),
        ("b2", "Hermes profile switcher", "systems", 0.6, 2),
        ("b3", "Qwen model works locally", "models", 0.5, 1),
        ("b4", "Apollo CM diagnostics work", "systems", 0.8, 5),
        ("b5", "old belief about system", "systems", 0.3, 0),
    ]:
        lc.add(Belief(id=b_id, content=content, category=cat, confidence=conf))
        for _ in range(signals):
            lc.add_signal(b_id)
    lc.add_contradiction("b5")
    lc.add_contradiction("b5")
    lc.add_contradiction("b5")

    # clustering
    clustering = BeliefClustering()
    beliefs = [lc.get(b_id) for b_id in ["b1", "b2", "b3", "b4", "b5"]]
    cluster_beliefs(beliefs, clustering)
    for c in clustering.all():
        for _ in range(5):
            clustering.cite(c.id)

    # simulate mode/wake history
    mode_usage = {"quiet-watch": 3, "active-absorb": 12, "reflective": 4, "alert": 1}
    wake_history = ["silent", "silent", "accumulate", "wake", "accumulate", "accumulate", "wake", "silent"]

    # run monitor
    monitor = ConsciousnessMonitor(runtime_dir)
    vitals = monitor.check(lc, clustering, mode_usage, wake_history)

    print(vitals.summary())
    print()
    print(json.dumps(vitals.to_dict(), indent=2))


if __name__ == "__main__":
    main()