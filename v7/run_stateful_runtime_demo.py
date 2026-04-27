#!/usr/bin/env python3
"""
Demo for v7.3 runtime state writer integration.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))
sys.path.insert(0, str(repo / 'v3'))

from daemon.runtime import SubstrateRuntime
from v7.stateful_hybrid_runtime import StatefulHybridRuntime


def main():
    root = Path('/tmp/v7_stateful_runtime_demo')
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    v3_runtime = SubstrateRuntime(root, repo / 'v3' / 'configs')
    for task in v3_runtime.scheduler.tasks:
        task.interval_seconds = 0

    srt = StatefulHybridRuntime(v3_runtime, root)
    events = [
        {"id": "evt1", "content": "Summarize memory pressure.", "operation": "summary", "privacy": "restricted", "type": "query", "confidence": 0.9, "category": "systems"},
        {"id": "evt2", "content": "Reflect on belief drift.", "operation": "reflect", "privacy": "normal", "type": "correction", "urgent": True, "category": "systems"},
        {"id": "evt3", "content": "Routine queue status note.", "operation": "generate", "privacy": "normal", "type": "query", "confidence": 0.7, "category": "operations"},
    ]

    results = []
    for event in events:
        v3_runtime.run_foreground(cycles=1, sleep_seconds=0)
        results.append(srt.process_event(event))

    print(json.dumps({
        'results': results,
        'beliefs_path': str(root / 'memory' / 'beliefs.json'),
        'concepts_path': str(root / 'memory' / 'concepts.json'),
        'cognition_path': str(root / 'runtime' / 'cognition.json'),
    }, indent=2))


if __name__ == '__main__':
    main()
