#!/usr/bin/env python3
"""
v7.3 Stateful Hybrid Runtime with automatic persisted state writes.
"""

from __future__ import annotations

from pathlib import Path

from v5.belief_lifecycle import BeliefLifecycle, Belief
from v5.clustering import BeliefClustering, cluster_beliefs
from v6.hybrid_runtime import HybridRuntime
from v7.runtime_state_writer import RuntimeStateWriter


class StatefulHybridRuntime:
    def __init__(self, v3_runtime, root: Path):
        self.runtime = HybridRuntime(v3_runtime)
        self.lifecycle = BeliefLifecycle()
        self.clustering = BeliefClustering()
        self.state_writer = RuntimeStateWriter(root)

    def process_event(self, event: dict) -> dict:
        result = self.runtime.process_event(event)

        # reflect runtime decisions into simple persistent memory state
        if result.get("status") == "processed":
            content = event.get("content", "")
            category = event.get("category", "events")
            belief_id = event.get("id", "unknown")
            if self.lifecycle.get(belief_id) is None:
                self.lifecycle.add(Belief(id=belief_id, content=content, category=category, confidence=0.5))
            self.lifecycle.add_signal(belief_id)

        mode = result.get("mode", {}).get("mode")
        if mode:
            self.state_writer.record_mode(mode)
        wake = result.get("wake", {}).get("action")
        if wake:
            self.state_writer.record_wake(wake)

        concepts = cluster_beliefs(self.lifecycle.all(), self.clustering)
        for concept in concepts:
            self.clustering.cite(concept.id)

        snapshot = self.state_writer.flush(
            beliefs=self.lifecycle.all(),
            concepts=self.clustering.all(),
        )
        result["persisted"] = snapshot
        return result
