#!/usr/bin/env python3
"""
Demo for v5.1 Belief Lifecycle.
"""

from __future__ import annotations

import json

from belief_lifecycle import BeliefLifecycle, Belief


def main():
    lc = BeliefLifecycle()

    # born
    b1_id = lc.add(Belief(
        id="b1",
        content="OpenClaw improves agent productivity",
        category="systems",
        stage="embryonic",
        confidence=0.3,
        sources=["user_feedback"],
    ))

    # two signals
    lc.add_signal(b1_id)
    lc.add_signal(b1_id)
    b1 = lc.get(b1_id)
    print(f"After 2 signals: stage={b1.stage}, conf={b1.confidence}")

    # more signals -> formative
    lc.add_signal(b1_id)
    lc.add_signal(b1_id)
    b1 = lc.get(b1_id)
    print(f"After 4 signals: stage={b1.stage}, conf={b1.confidence}")

    # stable
    b2_id = lc.add(Belief(
        id="b2",
        content="Hermes gateway status is authoritative",
        category="systems",
        stage="formative",
        confidence=0.6,
        sources=["design_doc"],
    ))
    for _ in range(4):
        lc.add_signal(b2_id)
    b2 = lc.get(b2_id)
    print(f"After 4 signals + no contradiction: stage={b2.stage}, conf={b2.confidence}")

    # contradictions -> weakening
    lc.add_contradiction(b2_id)
    lc.add_contradiction(b2_id)
    lc.add_contradiction(b2_id)
    b2 = lc.get(b2_id)
    print(f"After 3 contradictions: stage={b2.stage}, conf={b2.confidence}")

    # merge
    b3_id = lc.add(Belief(
        id="b3",
        content="Hermes status dashboard works",
        category="systems",
        stage="stable",
        confidence=0.7,
        sources=["testing"],
    ))
    survivor = lc.merge(b2_id, b3_id)
    print(f"Merged: survivor stage={survivor.stage}, sources={survivor.sources}")

    # retire
    lc.demote(b2_id)
    lc.demote(b2_id)
    b2 = lc.get(b2_id)
    print(f"After 2 demotions: stage={b2.stage}")

    print(json.dumps(lc.stats(), indent=2))


if __name__ == "__main__":
    main()