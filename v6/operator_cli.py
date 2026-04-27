#!/usr/bin/env python3
"""
v6.9 Unified Operator CLI.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo / "v5"))

from monitor import status_panel, beliefs_panel, concepts_panel, cognition_panel
from runtime_config import ExternalBudget, RuntimeConfig
from usage_ledger import UsageLedger
from usage_report import UsageReport


def build_usage(ledger_path: Path, request_limit: int, cost_limit: float):
    ledger = UsageLedger(ledger_path)
    config = RuntimeConfig(
        external_enabled=True,
        budget=ExternalBudget(
            max_requests_per_day=request_limit,
            max_cost_usd_per_day=cost_limit,
        ),
    )
    return UsageReport(ledger, config)


def command_status(root: Path) -> str:
    return "\n".join([
        status_panel(root),
        beliefs_panel(root),
        concepts_panel(root),
        cognition_panel(root),
    ])


def command_full(root: Path, ledger_path: Path, request_limit: int, cost_limit: float) -> str:
    usage = build_usage(ledger_path, request_limit, cost_limit)
    return "\n\n".join([
        command_status(root),
        usage.render_text(),
    ])


def main():
    parser = argparse.ArgumentParser(description="Substrate unified operator CLI")
    parser.add_argument("root", help="runtime root path")
    parser.add_argument("command", choices=["status", "usage", "full"])
    parser.add_argument("--ledger", default="usage-ledger.json", help="usage ledger path")
    parser.add_argument("--request-limit", type=int, default=100)
    parser.add_argument("--cost-limit", type=float, default=2.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    ledger_path = Path(args.ledger)

    if args.command == "status":
        if args.json:
            payload = {
                "status": status_panel(root),
                "beliefs": beliefs_panel(root),
                "concepts": concepts_panel(root),
                "cognition": cognition_panel(root),
            }
            print(json.dumps(payload, indent=2))
        else:
            print(command_status(root))
        return

    if args.command == "usage":
        usage = build_usage(ledger_path, args.request_limit, args.cost_limit)
        if args.json:
            print(json.dumps(usage.build(), indent=2))
        else:
            print(usage.render_text())
        return

    if args.command == "full":
        usage = build_usage(ledger_path, args.request_limit, args.cost_limit)
        if args.json:
            payload = {
                "status": status_panel(root),
                "beliefs": beliefs_panel(root),
                "concepts": concepts_panel(root),
                "cognition": cognition_panel(root),
                "usage": usage.build(),
            }
            print(json.dumps(payload, indent=2))
        else:
            print(command_full(root, ledger_path, args.request_limit, args.cost_limit))


if __name__ == "__main__":
    main()
