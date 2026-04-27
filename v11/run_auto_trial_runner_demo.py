#!/usr/bin/env python3
"""
v11.x Auto trial runner demo — run lightweight scenarios and record to registry.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v11.auto_trial_runner import AutoTrialRunner


def main():
    root = Path('/tmp/v11_auto_trial_demo')
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    ledger = root / 'usage-ledger.json'
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(json.dumps({"date": "2026-04-27", "total_requests": 0, "total_cost_usd": 0.0, "providers": {}, "events": []}))

    scenarios = [
        {
            "name": "summary",
            "content": "Summarize recent memory pressure and queue state.",
            "operation": "summary",
            "privacy": "normal",
            "budget": "generous",
            "mode": "summary",
            "urgency": "high",
        },
        {
            "name": "reflection",
            "content": "Reflect on belief drift and concept coherence.",
            "operation": "reflect",
            "privacy": "normal",
            "budget": "generous",
            "mode": "reflect",
            "urgency": "high",
        },
        {
            "name": "low-value",
            "content": "Routine cleanup note.",
            "operation": "generate",
            "privacy": "normal",
            "budget": "tight",
            "mode": "light",
            "urgency": "low",
        },
    ]

    runner = AutoTrialRunner(
        root=root,
        ledger_path=ledger,
        benchmark_path=root / 'benchmark.json',
        trial_log_path=root / 'trial-log.json',
        trial_registry_path=root / 'trial-registry.json',
    )
    result = runner.run(scenarios)
    print(json.dumps(result, indent=2))

    # Show registry
    from v10.trial_registry import TrialRegistry
    registry = TrialRegistry(root / 'trial-registry.json')
    print("\n=== registry ===")
    print(json.dumps(registry.read_all(), indent=2))


if __name__ == '__main__':
    main()
