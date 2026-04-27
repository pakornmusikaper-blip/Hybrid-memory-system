#!/usr/bin/env python3
"""
Run v3.3 queue processing demo.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from daemon.runtime import SubstrateRuntime


def main():
    root = Path("/tmp/substrate_v3_queue")
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    config_dir = Path(__file__).resolve().parent / "configs"
    runtime = SubstrateRuntime(root, config_dir)

    runtime.queues.enqueue_inbox(
        {
            "id": "query-001",
            "type": "query",
            "query": "What is the current memory-system state?",
        }
    )

    runtime.run_foreground(cycles=2, sleep_seconds=1)

    result = {
        "queue_stats": runtime.queues.stats(),
        "state": json.loads((root / "runtime" / "state.json").read_text()),
        "health": json.loads((root / "runtime" / "health.json").read_text()),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
