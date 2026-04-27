#!/usr/bin/env python3
"""
Demo for v10.0 decision dashboard.
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
from v7.stateful_hybrid_runtime import StatefulHybridRuntime
from v6.usage_ledger import UsageLedger
from v9.trial_log import TrialLog
from v9.benchmark_report import BenchmarkReport
from v10.decision_dashboard import DecisionDashboard


def main():
    root = Path('/tmp/v10_decision_dashboard_demo')
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    v3_runtime = SubstrateRuntime(root, repo / 'v3' / 'configs')
    for task in v3_runtime.scheduler.tasks:
        task.interval_seconds = 0
    srt = StatefulHybridRuntime(v3_runtime, root)
    for event in [
        {"id": "evt1", "content": "Summarize memory pressure.", "operation": "summary", "privacy": "restricted", "type": "query", "confidence": 0.9, "category": "systems"},
        {"id": "evt2", "content": "Reflect on belief drift.", "operation": "reflect", "privacy": "normal", "type": "correction", "urgent": True, "category": "systems"},
    ]:
        srt.process_event(event)

    ledger = UsageLedger(root / 'usage-ledger.json')
    ledger.record('minimax-api', 'MiniMax-M2.7', 0.0008, 'evt-live-1')
    ledger.record('minimax-api', 'MiniMax-M2.7', 0.0004, 'evt-live-2')

    benchmark_payload = {
        "results": [
            {"scenario": "summary", "route": {"backend": "external"}, "result": {"provider": "minimax-api", "fallback": False, "text": "ok"}},
            {"scenario": "reflection", "route": {"backend": "external"}, "result": {"provider": "minimax-api", "fallback": False, "text": "ok"}},
            {"scenario": "low-value", "route": {"backend": "heuristic"}, "skipped_external": True, "reason": "cheap path"},
        ],
        "after": {"total_requests": 2, "total_cost_usd": 0.0012},
        "report": {"request_ratio": 0.4, "cost_ratio": 0.24, "warnings": []},
    }
    benchmark_path = root / 'benchmark.json'
    benchmark_path.write_text(json.dumps(benchmark_payload, indent=2))

    trial_log = TrialLog(root / 'trial-log.json')
    trial_log.append(BenchmarkReport(benchmark_payload).build(), str(benchmark_path))

    dashboard = DecisionDashboard(
        root=root,
        ledger_path=root / 'usage-ledger.json',
        benchmark_path=benchmark_path,
        trial_log_path=root / 'trial-log.json',
    )
    print(dashboard.render_text())


if __name__ == '__main__':
    main()
