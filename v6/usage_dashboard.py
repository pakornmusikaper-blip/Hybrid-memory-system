#!/usr/bin/env python3
"""
CLI dashboard for external usage ledger.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_config import ExternalBudget, RuntimeConfig
from usage_ledger import UsageLedger
from usage_report import UsageReport


def main():
    parser = argparse.ArgumentParser(description="Substrate external usage dashboard")
    parser.add_argument("ledger_path", help="path to usage-ledger.json")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--request-limit", type=int, default=100)
    parser.add_argument("--cost-limit", type=float, default=2.0)
    args = parser.parse_args()

    ledger = UsageLedger(Path(args.ledger_path))
    config = RuntimeConfig(
        external_enabled=True,
        budget=ExternalBudget(
            max_requests_per_day=args.request_limit,
            max_cost_usd_per_day=args.cost_limit,
        ),
    )
    report = UsageReport(ledger, config)

    if args.json:
        print(json.dumps(report.build(), indent=2))
    else:
        print(report.render_text())


if __name__ == "__main__":
    main()
