#!/usr/bin/env python3
"""
Demo for v5.2 Belief Clustering & Concept Formation.
"""

from __future__ import annotations

import json

from belief_lifecycle import BeliefLifecycle, Belief
from clustering import BeliefClustering, cluster_beliefs


def main():
    lc = BeliefLifecycle()
    clustering = BeliefClustering()

    # create beliefs about same category
    b1_id = lc.add(Belief(id="b1", content="Hermes gateway handles multi-profile routing", category="systems", confidence=0.6))
    b2_id = lc.add(Belief(id="b2", content="Hermes profile switcher uses local state", category="systems", confidence=0.7))
    b3_id = lc.add(Belief(id="b3", content="Hermes status API exposes runtime metrics", category="systems", confidence=0.8))
    b4_id = lc.add(Belief(id="b4", content="Qwen model works well for local inference", category="models", confidence=0.6))

    beliefs = [lc.get(b1_id), lc.get(b2_id), lc.get(b3_id), lc.get(b4_id)]

    # cluster
    concepts = cluster_beliefs(beliefs, clustering)
    print(f"formed {len(concepts)} concepts")

    for c in concepts:
        print(f"  {c.id}: label={c.label}, beliefs={c.belief_ids}, stage={c.stage}, coherence={c.coherence}")

    # cite concept
    for c in concepts:
        for _ in range(5):
            clustering.cite(c.id)

    for c in concepts:
        print(f"after citations: {c.id} stage={c.stage} citations={c.citations}")

    print(json.dumps(clustering.stats(), indent=2))


if __name__ == "__main__":
    main()