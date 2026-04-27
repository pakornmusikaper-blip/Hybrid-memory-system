#!/usr/bin/env python3
"""
Run v3.8 operator demo.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from daemon.runtime import SubstrateRuntime
from operator_surface import OperatorSurface


def main():
    root = Path("/tmp/substrate_v3_operator")
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    config_dir = Path(__file__).resolve().parent / "configs"
    runtime = SubstrateRuntime(root, config_dir)
    for task in runtime.scheduler.tasks:
        task.interval_seconds = 0

    runtime.queues.enqueue_inbox({"id": "poison-operator-001", "type": "poison-test", "attempts": 2})
    runtime.run_foreground(cycles=1, sleep_seconds=1)

    ops = OperatorSurface(root)
    poison_items = ops.list_poison()
    retry_result = {}
    if poison_items:
        retry_result = ops.retry_poison(poison_items[0]["file"])

    result = {
        "status": ops.status(),
        "queue_stats": ops.queue_stats(),
        "poison_items_before_retry": poison_items,
        "retry_result": retry_result,
        "queue_stats_after_retry": ops.queue_stats(),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
