#!/usr/bin/env python3
"""
v10.x Memory budget enforcement.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class MemoryBudgetConfig:
    max_beliefs_mb: float = 2.0
    max_concepts_mb: float = 1.0
    max_cognition_mb: float = 0.5
    max_reflections_mb: float = 1.0
    max_total_mb: float = 5.0
    archive_old_threshold_days: int = 7


@dataclass
class MemoryBudgetSnapshot:
    current_mb: float
    max_mb: float
    usage_ratio: float
    files: Dict[str, float]
    over_budget: List[str]

    def to_dict(self) -> Dict:
        return {
            "current_mb": round(self.current_mb, 4),
            "max_mb": round(self.max_mb, 4),
            "usage_ratio": round(self.usage_ratio, 4),
            "files": {k: round(v, 4) for k, v in self.files.items()},
            "over_budget": self.over_budget,
        }


class MemoryBudgetEnforcer:
    def __init__(self, root: Path, config: MemoryBudgetConfig | None = None):
        self.root = Path(root)
        self.config = config or MemoryBudgetConfig()

    def snapshot(self) -> MemoryBudgetSnapshot:
        files = {
            "beliefs": self._size_mb(self.root / "memory" / "beliefs.json"),
            "concepts": self._size_mb(self.root / "memory" / "concepts.json"),
            "cognition": self._size_mb(self.root / "runtime" / "cognition.json"),
            "reflections": self._size_mb(self.root / "memory" / "reflections.json"),
        }
        current = sum(files.values())
        max_total = self.config.max_total_mb
        usage_ratio = current / max_total if max_total > 0 else 1.0
        over_budget = [
            name for name, size in files.items()
            if size > getattr(self.config, f"max_{name}_mb", 999.0)
        ]
        return MemoryBudgetSnapshot(
            current_mb=current,
            max_mb=max_total,
            usage_ratio=usage_ratio,
            files=files,
            over_budget=over_budget,
        )

    def archive_beliefs(self, days_threshold: int | None = None) -> List[str]:
        threshold = days_threshold or self.config.archive_old_threshold_days
        beliefs_path = self.root / "memory" / "beliefs.json"
        if not beliefs_path.exists():
            return []
        data = json.loads(beliefs_path.read_text())
        cutoff = time.time() - threshold * 86400
        archived: List[str] = []
        remaining = []
        for entry in data:
            updated = entry.get("updated_at") or entry.get("created_at", 0)
            if isinstance(updated, str) and updated:
                import datetime
                updated = datetime.datetime.fromisoformat(updated.replace("Z", "+00:00")).timestamp()
            if float(updated) < cutoff:
                archived.append(entry.get("id", "unknown"))
            else:
                remaining.append(entry)
        if archived:
            archive_dir = self.root / "memory" / "archive"
            archive_dir.mkdir(parents=True, exist_ok=True)
            archive_path = archive_dir / f"beliefs_{int(time.time())}.json"
            archive_path.write_text(json.dumps(archived, indent=2))
            beliefs_path.write_text(json.dumps(remaining, indent=2))
        return archived

    def compact_concepts(self) -> int:
        concepts_path = self.root / "memory" / "concepts.json"
        if not concepts_path.exists():
            return 0
        data = json.loads(concepts_path.read_text())
        kept = [c for c in data if c.get("stage") != "dissolved"]
        removed = len(data) - len(kept)
        concepts_path.write_text(json.dumps(kept, indent=2))
        return removed

    def _size_mb(self, path: Path) -> float:
        if not path.exists():
            return 0.0
        return path.stat().st_size / (1024 * 1024)
