#!/usr/bin/env python3
"""
Demo for v6.8 usage dashboard.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from usage_ledger import UsageLedger
from runtime_config import ExternalBudget, RuntimeConfig
from usage_report import UsageReport


def main():
    root = Path('/tmp/v6_usage_dashboard_demo')
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    ledger = UsageLedger(root / 'usage-ledger.json')
    ledger.record('minimax-api', 'MiniMax-M2.7', 0.0008, 'e1')
    ledger.record('minimax-api', 'MiniMax-M2.7', 0.0004, 'e2')
    ledger.record('openai-api', 'gpt-x', 0.0003, 'e3')

    config = RuntimeConfig(
        external_enabled=True,
        budget=ExternalBudget(max_requests_per_day=4, max_cost_usd_per_day=0.002),
    )
    report = UsageReport(ledger, config)
    print(report.render_text())


if __name__ == '__main__':
    main()
