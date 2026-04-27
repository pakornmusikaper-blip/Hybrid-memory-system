#!/usr/bin/env python3
"""
Demo for v6.9 unified operator CLI.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from usage_ledger import UsageLedger


def main():
    root = Path('/tmp/v6_operator_cli_demo')
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    (root / 'queue').mkdir(parents=True, exist_ok=True)

    with open(root / 'state.json', 'w') as f:
        json.dump({"mode": "active-absorb", "cycles": 222, "last_success": "2026-04-27T14:40:00"}, f)
    with open(root / 'health.json', 'w') as f:
        json.dump({"consecutive_errors": 0, "status": "healthy"}, f)

    ledger = UsageLedger(root / 'usage-ledger.json')
    ledger.record('minimax-api', 'MiniMax-M2.7', 0.0008, 'evt-1')
    ledger.record('minimax-api', 'MiniMax-M2.7', 0.0004, 'evt-2')

    print('Run this:')
    print(f"python3 {Path(__file__).resolve().parent / 'operator_cli.py'} {root} full --ledger {root / 'usage-ledger.json'} --request-limit 4 --cost-limit 0.002")


if __name__ == '__main__':
    main()
