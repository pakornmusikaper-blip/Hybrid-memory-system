#!/usr/bin/env python3
"""
Run v3.2 supervisor demo.
"""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

from daemon.supervisor import Supervisor


def main():
    root = Path("/tmp/substrate_v3_supervisor")
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    config_dir = Path(__file__).resolve().parent / "configs"
    supervisor = Supervisor(root, config_dir)

    started = supervisor.start(cycles=5, sleep_seconds=1)
    time.sleep(2)
    status_running = supervisor.status()
    stopped = supervisor.stop()
    time.sleep(1)
    status_after = supervisor.status()

    print(
        json.dumps(
            {
                "started": started,
                "status_running": status_running,
                "stopped": stopped,
                "status_after": status_after,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
