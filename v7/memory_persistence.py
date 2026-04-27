#!/usr/bin/env python3
"""
v7.1 Persist belief/concept/cognition state to disk.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class MemoryPersistence:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.memory_dir = self.root / "memory"
        self.runtime_dir = self.root / "runtime"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.runtime_dir.mkdir(parents=True, exist_ok=True)

    def write_beliefs(self, beliefs) -> Path:
        path = self.memory_dir / "beliefs.json"
        payload = [b.to_dict() if hasattr(b, "to_dict") else b for b in beliefs]
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        return path

    def write_concepts(self, concepts) -> Path:
        path = self.memory_dir / "concepts.json"
        payload = [c.to_dict() if hasattr(c, "to_dict") else c for c in concepts]
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        return path

    def write_cognition(self, *, mode_distribution: Dict, wake_history: List[str]) -> Path:
        path = self.runtime_dir / "cognition.json"
        payload = {
            "mode_distribution": mode_distribution,
            "wake_history": wake_history,
        }
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        return path

    def snapshot(self) -> Dict:
        return {
            "beliefs": str(self.memory_dir / "beliefs.json"),
            "concepts": str(self.memory_dir / "concepts.json"),
            "cognition": str(self.runtime_dir / "cognition.json"),
        }
