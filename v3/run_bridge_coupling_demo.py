#!/usr/bin/env python3
"""
Run v3.7 bridge/runtime coupling demo.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from daemon.runtime import SubstrateRuntime


def main():
    root = Path("/tmp/substrate_v3_bridge_coupling")
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    config_dir = Path(__file__).resolve().parent / "configs"
    runtime = SubstrateRuntime(root, config_dir)
    for task in runtime.scheduler.tasks:
        task.interval_seconds = 0

    runtime.queues.enqueue_inbox(
        {
            "id": "bridge-query-001",
            "type": "query",
            "query": "What does the substrate know about the memory-system state?",
            "origin": "bridge",
        }
    )
    runtime.queues.enqueue_inbox(
        {
            "id": "bridge-correction-001",
            "type": "correction",
            "belief_id": "belief-xyz",
            "correction": "Lower the confidence because evidence is incomplete.",
            "origin": "bridge",
        }
    )

    runtime.run_foreground(cycles=2, sleep_seconds=1)

    outbox_dir = root / "runtime" / "queues" / "outbox"
    outbox_payloads = []
    for path in sorted(outbox_dir.glob("*.json")):
        outbox_payloads.append(json.loads(path.read_text()))

    print(
        json.dumps(
            {
                "queue_stats": runtime.queues.stats(),
                "outbox_payloads": outbox_payloads,
                "state": json.loads((root / "runtime" / "state.json").read_text()),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
