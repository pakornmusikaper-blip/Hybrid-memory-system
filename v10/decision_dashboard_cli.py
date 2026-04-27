#!/usr/bin/env python3
"""
CLI for v10.0 decision dashboard.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v10.decision_dashboard import DecisionDashboard


def main():
    parser = argparse.ArgumentParser(description='Substrate decision dashboard CLI')
    parser.add_argument('root')
    parser.add_argument('--ledger', required=True)
    parser.add_argument('--benchmark')
    parser.add_argument('--trial-log')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    dashboard = DecisionDashboard(
        root=Path(args.root),
        ledger_path=Path(args.ledger),
        benchmark_path=Path(args.benchmark) if args.benchmark else None,
        trial_log_path=Path(args.trial_log) if args.trial_log else None,
    )
    if args.json:
        print(json.dumps(dashboard.build(), indent=2))
    else:
        print(dashboard.render_text())


if __name__ == '__main__':
    main()
