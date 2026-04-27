#!/usr/bin/env python3
"""
Demo for memory budget enforcement.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v10.memory_budget import MemoryBudgetEnforcer, MemoryBudgetConfig


def main():
    root = Path('/tmp/v10_memory_budget_demo')
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    (root / 'memory').mkdir(exist_ok=True)
    (root / 'runtime').mkdir(exist_ok=True)

    (root / 'memory' / 'beliefs.json').write_text(json.dumps([
        {"id": "b1", "content": "test", "stage": "stable", "created_at": "2026-04-01T00:00:00"},
        {"id": "b2", "content": "test2", "stage": "stable", "created_at": "2026-04-20T00:00:00"},
    ], indent=2))
    (root / 'memory' / 'concepts.json').write_text(json.dumps([
        {"id": "c1", "name": "test", "stage": "dissolved"},
        {"id": "c2", "name": "test2", "stage": "coherent"},
    ], indent=2))
    (root / 'runtime' / 'cognition.json').write_text('{"cycles": 10}')
    (root / 'memory' / 'reflections.json').write_text('[{"id": "r1"}]')

    enforcer = MemoryBudgetEnforcer(root, MemoryBudgetConfig(max_total_mb=0.001))
    snap = enforcer.snapshot()
    print(f"snapshot: {json.dumps(snap.to_dict(), indent=2)}")

    removed = enforcer.compact_concepts()
    print(f"\ncompact_concepts: removed {removed} dissolved entries")

    archived = enforcer.archive_beliefs(days_threshold=7)
    print(f"archive_beliefs: archived {len(archived)} old entries")


if __name__ == '__main__':
    main()
