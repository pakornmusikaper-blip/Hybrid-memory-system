#!/usr/bin/env python3
"""
v5.2 Belief Clustering & Concept Formation.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Concept:
    id: str
    label: str
    belief_ids: List[str] = field(default_factory=list)
    stage: str = "forming"
    coherence: float = 0.3
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    citations: int = 0

    def to_dict(self) -> Dict:
        return asdict(self)

    def touch(self):
        self.updated_at = datetime.now().isoformat()


class BeliefClustering:
    def __init__(self):
        self.concepts: Dict[str, Concept] = {}

    def form(self, concept_id: str, label: str, belief_ids: List[str]) -> Concept:
        concept = Concept(id=concept_id, label=label, belief_ids=list(belief_ids), stage="forming")
        self.concepts[concept_id] = concept
        return concept

    def absorb(self, concept_id: str, belief_id: str) -> Optional[Concept]:
        c = self.concepts.get(concept_id)
        if not c:
            return None
        if belief_id not in c.belief_ids:
            c.belief_ids.append(belief_id)
            c.touch()
        return c

    def split(self, concept_id: str, keep_ids: List[str], new_label: str, new_id: str) -> tuple[Optional[Concept], Optional[Concept]]:
        c = self.concepts.get(concept_id)
        if not c:
            return None, None
        remove_ids = [b for b in c.belief_ids if b not in keep_ids]
        c.belief_ids = list(keep_ids)
        c.touch()
        c.stage = "coherent"
        c.coherence = min(0.9, c.coherence + 0.1)
        if remove_ids:
            new_c = Concept(id=new_id, label=new_label, belief_ids=remove_ids, stage="forming")
            self.concepts[new_id] = new_c
            return c, new_c
        return c, None

    def dissolve(self, concept_id: str) -> Optional[Concept]:
        c = self.concepts.get(concept_id)
        if not c:
            return None
        c.stage = "dissolved"
        c.coherence = 0.1
        c.touch()
        return c

    def cite(self, concept_id: str) -> Optional[Concept]:
        c = self.concepts.get(concept_id)
        if not c:
            return None
        c.citations += 1
        c.touch()
        if c.stage == "forming" and c.citations >= 2:
            c.stage = "coherent"
            c.coherence = min(0.8, c.coherence + 0.2)
        elif c.stage == "coherent" and c.citations >= 5:
            c.stage = "mature"
            c.coherence = min(0.95, c.coherence + 0.1)
        return c

    def get(self, concept_id: str) -> Optional[Concept]:
        return self.concepts.get(concept_id)

    def all(self) -> List[Concept]:
        return [c for c in self.concepts.values() if c.stage != "dissolved"]

    def stats(self) -> Dict:
        active = [c for c in self.concepts.values() if c.stage != "dissolved"]
        by_stage = {}
        for c in active:
            by_stage[c.stage] = by_stage.get(c.stage, 0) + 1
        return {
            "total": len(self.concepts),
            "active": len(active),
            "by_stage": by_stage,
            "avg_coherence": sum(c.coherence for c in active) / max(1, len(active)),
        }


def cluster_beliefs(beliefs: List, clustering: BeliefClustering, config: Dict | None = None) -> List[Concept]:
    config = config or {}
    concepts = []

    # group by category first
    by_category: Dict[str, List] = {}
    for b in beliefs:
        cat = getattr(b, "category", "unknown")
        by_category.setdefault(cat, []).append(b)

    for cat, cat_beliefs in by_category.items():
        if len(cat_beliefs) < 2:
            continue

        # form a concept for each category cluster
        belief_ids = [b.id for b in cat_beliefs]
        concept_id = f"concept_{cat}"
        label = cat
        c = clustering.form(concept_id, label, belief_ids)
        c.stage = "coherent"
        # coherence based on number of beliefs in cluster
        c.coherence = min(0.7, len(cat_beliefs) * 0.2)
        concepts.append(c)

    return concepts