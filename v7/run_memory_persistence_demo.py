#!/usr/bin/env python3
"""
Demo for v7.1 persisted memory files.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import sys
repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo / "v5"))

from belief_lifecycle import BeliefLifecycle, Belief
from clustering import BeliefClustering, cluster_beliefs
from memory_persistence import MemoryPersistence


def main():
    root = Path('/tmp/v7_memory_persistence_demo')
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    lc = BeliefLifecycle()
    lc.add(Belief(id='b1', content='Hermes gateway routing is stable', category='systems', confidence=0.7))
    lc.add(Belief(id='b2', content='Hermes profile switching uses local state', category='systems', confidence=0.6))
    lc.add(Belief(id='b3', content='Qwen local inference is acceptable on CPU', category='models', confidence=0.55))
    lc.add_signal('b1'); lc.add_signal('b1'); lc.add_signal('b1'); lc.add_signal('b1')
    lc.add_signal('b2'); lc.add_signal('b2')

    clustering = BeliefClustering()
    beliefs = lc.all()
    concepts = cluster_beliefs(beliefs, clustering)
    for c in concepts:
        clustering.cite(c.id)
        clustering.cite(c.id)

    persistence = MemoryPersistence(root)
    paths = persistence.snapshot()
    persistence.write_beliefs(lc.all())
    persistence.write_concepts(clustering.all())
    persistence.write_cognition(
        mode_distribution={"quiet-watch": 2, "active-absorb": 7, "reflective": 1},
        wake_history=["silent", "accumulate", "wake", "accumulate"],
    )

    print(json.dumps(paths, indent=2))


if __name__ == '__main__':
    main()
