#!/usr/bin/env python3
"""
v5.1 Belief Lifecycle Maturity.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional


STAGES = {"embryonic", "formative", "stable", "weakening", "retired"}


@dataclass
class Belief:
    id: str
    content: str
    category: str
    stage: str = "embryonic"
    confidence: float = 0.3
    sources: List[str] = field(default_factory=list)
    signals: int = 0
    contradictions: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    promoted: int = 0
    demotions: int = 0

    def to_dict(self) -> Dict:
        return asdict(self)

    def touch(self):
        self.updated_at = datetime.now().isoformat()


class BeliefLifecycle:
    def __init__(self):
        self.beliefs: Dict[str, Belief] = {}

    def add(self, belief: Belief) -> str:
        if belief.id in self.beliefs:
            return self._update(belief.id, belief.to_dict())
        self.beliefs[belief.id] = belief
        return belief.id

    def get(self, belief_id: str) -> Optional[Belief]:
        return self.beliefs.get(belief_id)

    def all(self) -> List[Belief]:
        return list(self.beliefs.values())

    def active(self) -> List[Belief]:
        return [b for b in self.beliefs.values() if b.stage != "retired"]

    def _update(self, belief_id: str, updates: Dict) -> str:
        b = self.beliefs[belief_id]
        for k, v in updates.items():
            if hasattr(b, k):
                setattr(b, k, v)
        b.touch()
        return belief_id

    def add_signal(self, belief_id: str) -> Optional[Belief]:
        b = self.beliefs.get(belief_id)
        if not b:
            return None
        b.signals += 1
        b.touch()
        self._maybe_promote(b)
        return b

    def add_contradiction(self, belief_id: str) -> Optional[Belief]:
        b = self.beliefs.get(belief_id)
        if not b:
            return None
        b.contradictions += 1
        b.touch()
        self._maybe_demote(b)
        return b

    def _maybe_promote(self, b: Belief):
        if b.stage == "embryonic" and b.signals >= 2:
            b.stage = "formative"
            b.confidence = min(0.7, b.confidence + 0.1)
            b.promoted += 1
        elif b.stage == "formative" and b.signals >= 4 and b.contradictions == 0:
            b.stage = "stable"
            b.confidence = min(0.9, b.confidence + 0.15)
            b.promoted += 1

    def _maybe_demote(self, b: Belief):
        if b.stage == "stable" and b.contradictions >= 3:
            b.stage = "weakening"
            b.confidence = max(0.3, b.confidence - 0.2)
            b.demotions += 1
        elif b.stage == "weakening" and b.contradictions >= 5:
            b.stage = "retired"
            b.confidence = max(0.1, b.confidence - 0.3)

    def merge(self, survivor_id: str, absorbed_id: str) -> Optional[Belief]:
        survivor = self.beliefs.get(survivor_id)
        absorbed = self.beliefs.get(absorbed_id)
        if not survivor or not absorbed:
            return None
        survivor.sources = list(set(survivor.sources + absorbed.sources))
        survivor.signals += absorbed.signals
        survivor.confidence = (survivor.confidence + absorbed.confidence) / 2
        survivor.touch()
        absorbed.stage = "retired"
        absorbed.confidence = 0.1
        return survivor

    def promote(self, belief_id: str) -> Optional[Belief]:
        b = self.beliefs.get(belief_id)
        if not b or b.stage not in {"formative", "stable"}:
            return None
        if b.stage == "formative" and b.signals >= 4 and b.contradictions == 0:
            b.stage = "stable"
            b.confidence = min(0.9, b.confidence + 0.15)
            b.promoted += 1
        return b

    def demote(self, belief_id: str) -> Optional[Belief]:
        b = self.beliefs.get(belief_id)
        if not b or b.stage not in {"formative", "stable", "weakening"}:
            return None
        old = b.stage
        if b.stage == "weakening":
            b.stage = "embryonic"
        elif b.stage == "stable":
            b.stage = "weakening"
        elif b.stage == "formative":
            b.stage = "embryonic"
        b.confidence = max(0.2, b.confidence - 0.15)
        b.demotions += 1
        return b

    def retire(self, belief_id: str) -> Optional[Belief]:
        b = self.beliefs.get(belief_id)
        if not b:
            return None
        b.stage = "retired"
        b.confidence = max(0.1, b.confidence - 0.3)
        return b

    def stats(self) -> Dict:
        active = self.active()
        by_stage = {}
        for b in active:
            by_stage[b.stage] = by_stage.get(b.stage, 0) + 1
        return {
            "total": len(self.beliefs),
            "active": len(active),
            "retired": len([b for b in self.beliefs.values() if b.stage == "retired"]),
            "by_stage": by_stage,
            "avg_confidence": sum(b.confidence for b in active) / max(1, len(active)),
        }