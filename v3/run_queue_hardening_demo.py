#!/usr/bin/env python3
"""
Run v3.5 queue hardening demo.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from daemon.runtime import SubstrateRuntime


def main():
    root = Path("/tmp/substrate_v3_queue_hardening")
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    config_dir = Path(__file__).resolve().parent / "configs"
    runtime = SubstrateRuntime(root, config_dir)
    for task in runtime.scheduler.tasks:
        task.interval_seconds = 0

    # original query
    runtime.queues.enqueue_inbox(
        {"id": "query-001", "type": "query", "query": "What is the system state?"}
    )
    runtime.run_foreground(cycles=1, sleep_seconds=1)

    # duplicate query
    runtime.queues.enqueue_inbox(
        {"id": "query-001", "type": "query", "query": "What is the system state?"}
    )
    runtime.run_foreground(cycles=1, sleep_seconds=1)

    # correction payload
    runtime.queues.enqueue_inbox(
        {
            "id": "corr-001",
            "type": "correction",
            "belief_id": "belief-123",
            "correction": "confidence should be lower",
        }
    )
    runtime.run_foreground(cycles=1, sleep_seconds=1)

    print(
        json.dumps(
            {
                "queue_stats": runtime.queues.stats(),
                "state": json.loads((root / "runtime" / "state.json").read_text()),
                "health": json.loads((root / "runtime" / "health.json").read_text()),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
