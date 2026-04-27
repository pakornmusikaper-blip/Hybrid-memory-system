#!/usr/bin/env python3
"""
Demo for v6.3 Hybrid Runtime.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))
sys.path.insert(0, str(repo / "v3"))

from daemon.runtime import SubstrateRuntime
from v6.hybrid_runtime import HybridRuntime


def main():
    root = Path("/tmp/v6_hybrid_runtime_demo")
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    config_dir = repo / "v3" / "configs"
    v3_runtime = SubstrateRuntime(root, config_dir)
    for task in v3_runtime.scheduler.tasks:
        task.interval_seconds = 0

    hruntime = HybridRuntime(v3_runtime)

    events = [
        {
            "id": "evt1",
            "content": "Summarize recent memory pressure and operator alerts.",
            "operation": "summary",
            "privacy": "restricted",
            "type": "query",
            "confidence": 0.9,
        },
        {
            "id": "evt2",
            "content": "Reflect deeply on whether current belief drift requires conscious wake.",
            "operation": "reflect",
            "privacy": "normal",
            "type": "correction",
            "urgent": True,
        },
        {
            "id": "evt3",
            "content": "Low-priority cleanup note.",
            "operation": "generate",
            "privacy": "normal",
            "type": "cleanup",
        },
    ]

    results = []
    for event in events:
        v3_runtime.run_foreground(cycles=1, sleep_seconds=0)
        results.append(hruntime.process_event(event))

    print(json.dumps({
        "results": results,
        "insights": hruntime.get_insights(),
    }, indent=2))


if __name__ == "__main__":
    main()
