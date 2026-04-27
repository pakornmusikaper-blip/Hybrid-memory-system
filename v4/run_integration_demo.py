#!/usr/bin/env python3
"""
Demo for v4.4 — intelligent runtime integrated with v3 daemon.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "v3"))

from daemon.runtime import SubstrateRuntime
from intelligent_runtime import IntelligentRuntime


def main():
    root = Path("/tmp/v4_integration_demo")
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    config_dir = Path(__file__).resolve().parent.parent / "v3" / "configs"
    v3_runtime = SubstrateRuntime(root, config_dir)
    for task in v3_runtime.scheduler.tasks:
        task.interval_seconds = 0

    iruntime = IntelligentRuntime(v3_runtime)

    events = [
        {"id": "q1", "type": "query", "confidence": 0.9},
        {"id": "c1", "type": "correction", "urgent": True},
        {"id": "cl1", "type": "cleanup"},
        {"id": "f1", "type": "followup", "confidence": 0.35},
    ]

    results = []
    for event in events:
        v3_runtime.run_foreground(cycles=1, sleep_seconds=1)
        result = iruntime.process_event(event)
        results.append({"event": event, "result": result})

    insights = iruntime.get_insights()
    queue_stats = v3_runtime.queues.stats()

    print(json.dumps({
        "results": results,
        "insights": insights,
        "queue_stats": queue_stats,
        "recent_spend_trend": iruntime._recent_spend_trend(),
    }, indent=2))


if __name__ == "__main__":
    main()
