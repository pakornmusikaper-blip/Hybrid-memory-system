#!/usr/bin/env python3
"""
Demo for v9.2 persistent trial logs.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v9.benchmark_report import load_report
from v9.trial_log import TrialLog
from v9.trial_history_report import TrialHistoryReport


def main():
    root = Path('/tmp/v9_trial_log_demo')
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    run1 = {
        "results": [
            {"route": {"backend": "external"}, "result": {"provider": "minimax-api", "fallback": False}},
            {"route": {"backend": "heuristic"}, "skipped_external": True},
        ],
        "after": {"total_requests": 1, "total_cost_usd": 0.0008},
        "report": {"request_ratio": 0.2, "cost_ratio": 0.16, "warnings": []},
    }
    run2 = {
        "results": [
            {"route": {"backend": "external"}, "result": {"provider": "minimax-api", "fallback": False}},
            {"route": {"backend": "external"}, "result": {"provider": "minimax-api", "fallback": False}},
            {"route": {"backend": "heuristic"}, "skipped_external": True},
        ],
        "after": {"total_requests": 2, "total_cost_usd": 0.0014},
        "report": {"request_ratio": 0.4, "cost_ratio": 0.28, "warnings": []},
    }

    p1 = root / 'run1.json'
    p2 = root / 'run2.json'
    p1.write_text(json.dumps(run1, indent=2))
    p2.write_text(json.dumps(run2, indent=2))

    log = TrialLog(root / 'trial-log.json')
    log.append(load_report(p1).build(), str(p1))
    log.append(load_report(p2).build(), str(p2))

    history = TrialHistoryReport(log)
    print(history.render_text())


if __name__ == '__main__':
    main()
