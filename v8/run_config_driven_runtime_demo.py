#!/usr/bin/env python3
"""
Demo for v8.6 config-driven runtime hook-up.
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
from v8.config_driven_runtime import ConfigDrivenHybridRuntime


def main():
    root = Path('/tmp/v8_config_driven_runtime_demo')
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    config_path = root / 'runtime-config.json'

    config_path.write_text(json.dumps({
        "local_enabled": True,
        "external_enabled": False,
        "external_model_name": "MiniMax-M2.7",
        "budget": {"max_requests_per_day": 3, "max_cost_usd_per_day": 0.002}
    }, indent=2))

    v3_runtime = SubstrateRuntime(root, repo / 'v3' / 'configs')
    for task in v3_runtime.scheduler.tasks:
        task.interval_seconds = 0

    runtime = ConfigDrivenHybridRuntime(v3_runtime, config_path)

    event1 = {"id": "evt1", "content": "Reflect on system health.", "operation": "reflect", "privacy": "normal", "type": "correction", "urgent": True}
    result1 = runtime.process_event(event1)

    config_path.write_text(json.dumps({
        "local_enabled": True,
        "external_enabled": True,
        "external_model_name": "MiniMax-M2.7",
        "budget": {"max_requests_per_day": 3, "max_cost_usd_per_day": 0.002}
    }, indent=2))

    event2 = {"id": "evt2", "content": "Reflect on memory drift with generous budget.", "operation": "reflect", "privacy": "normal", "type": "correction", "urgent": True, "force_budget_band": "generous"}
    result2 = runtime.process_event(event2)

    print(json.dumps({
        'config_path': str(config_path),
        'result1': result1,
        'result2': result2,
    }, indent=2))


if __name__ == '__main__':
    main()
