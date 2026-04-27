#!/usr/bin/env python3
"""
Run v3.6 queue resilience demo.
"""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

from daemon.runtime import SubstrateRuntime


def main():
    root = Path("/tmp/substrate_v3_queue_resilience")
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    config_dir = Path(__file__).resolve().parent / "configs"
    runtime = SubstrateRuntime(root, config_dir)
    for task in runtime.scheduler.tasks:
        task.interval_seconds = 0

    # poison-test payload will fail intentionally and enter retry/backoff/poison path
    runtime.queues.enqueue_inbox({"id": "poison-001", "type": "poison-test"})

    result_steps = []
    for _ in range(4):
        runtime.run_foreground(cycles=1, sleep_seconds=1)
        result_steps.append(runtime.queues.stats())
        time.sleep(1)

    queue_root = root / "runtime" / "queues"
    poison_files = [p.name for p in (queue_root / "poison").glob("*.json")]
    inbox_files = [p.name for p in (queue_root / "inbox").glob("*.json")]

    print(
        json.dumps(
            {
                "steps": result_steps,
                "poison_files": poison_files,
                "inbox_files": inbox_files,
                "state": json.loads((root / "runtime" / "state.json").read_text()),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
