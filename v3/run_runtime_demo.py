#!/usr/bin/env python3
"""
Run the v3.1 runtime for a short foreground demo.
"""

import json
import shutil
from pathlib import Path

from daemon.runtime import SubstrateRuntime


def main():
    root = Path("/tmp/substrate_v3_runtime")
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    config_dir = Path(__file__).resolve().parent / "configs"
    runtime = SubstrateRuntime(root, config_dir)
    runtime.run_foreground(cycles=4, sleep_seconds=1)

    with open(root / "runtime" / "state.json") as f:
        state = json.load(f)
    with open(root / "runtime" / "health.json") as f:
        health = json.load(f)

    print(json.dumps({"state": state, "health": health}, indent=2))


if __name__ == "__main__":
    main()
