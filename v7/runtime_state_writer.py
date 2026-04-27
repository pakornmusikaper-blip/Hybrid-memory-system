#!/usr/bin/env python3
"""
v7.3 Runtime-integrated state writer.
"""

from __future__ import annotations

from pathlib import Path

from v7.memory_persistence import MemoryPersistence


class RuntimeStateWriter:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.persistence = MemoryPersistence(self.root)
        self.mode_distribution: dict[str, int] = {}
        self.wake_history: list[str] = []

    def record_mode(self, mode: str):
        self.mode_distribution[mode] = self.mode_distribution.get(mode, 0) + 1

    def record_wake(self, action: str):
        self.wake_history.append(action)
        self.wake_history = self.wake_history[-200:]

    def flush(self, *, beliefs, concepts, reflections=None):
        self.persistence.write_beliefs(beliefs)
        self.persistence.write_concepts(concepts)
        self.persistence.write_cognition(
            mode_distribution=self.mode_distribution,
            wake_history=self.wake_history,
        )
        if reflections is not None:
            self.persistence.write_reflections(reflections)
        return self.persistence.snapshot()
