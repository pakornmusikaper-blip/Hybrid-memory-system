#!/usr/bin/env python3
"""
Demo for v9.1 benchmark report.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from benchmark_report import load_report


def main():
    root = Path('/tmp/v9_benchmark_report_demo')
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    payload = {
        "results": [
            {
                "scenario": "summary",
                "route": {"backend": "external"},
                "result": {"provider": "minimax-api", "fallback": False},
            },
            {
                "scenario": "reflection",
                "route": {"backend": "external"},
                "result": {"provider": "minimax-api", "fallback": False},
            },
            {
                "scenario": "low-value",
                "route": {"backend": "heuristic"},
                "skipped_external": True,
            },
        ],
        "after": {
            "total_requests": 2,
            "total_cost_usd": 0.0014,
        },
        "report": {
            "request_ratio": 0.4,
            "cost_ratio": 0.28,
            "warnings": [],
        },
    }
    path = root / 'live-run.json'
    path.write_text(json.dumps(payload, indent=2))
    report = load_report(path)
    print(report.render_text())


if __name__ == '__main__':
    main()
