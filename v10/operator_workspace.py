#!/usr/bin/env python3
"""
v10.x Unified operator workspace CLI.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v10.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from v10.decision_dashboard import DecisionDashboard
from v10.smoke_test import run_smoke_test
from v10.trial_registry import TrialRegistry
from v6.usage_ledger import UsageLedger
from v6.usage_report import UsageReport
from v6.runtime_config import RuntimeConfig, ExternalBudget


def cmd_status(args):
    from v5.monitor import status_panel
    root = Path(args.root)
    print(status_panel(root))


def cmd_dashboard(args):
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


def cmd_smoke(args):
    result = run_smoke_test()
    print(f"Smoke test: {result['status']}")
    for e in result["errors"]:
        print(f"  ERROR: {e}")
    for w in result["warnings"]:
        print(f"  WARNING: {w}")
    if result["status"] == "FAIL":
        sys.exit(1)


def cmd_usage(args):
    config = RuntimeConfig(external_enabled=True, budget=ExternalBudget())
    report = UsageReport(UsageLedger(Path(args.ledger)), config).build()
    print(json.dumps(report, indent=2))


def cmd_trials(args):
    registry = TrialRegistry(Path(args.path))
    print(json.dumps(registry.read_all(), indent=2))


def cmd_registry_search(args):
    registry = TrialRegistry(Path(args.path))
    results = registry.search(assessment=args.assessment, tag=args.tag)
    print(json.dumps(results, indent=2))


def cmd_circuit(args):
    cb = CircuitBreaker(Path(args.path))
    print(json.dumps(cb.snapshot().to_dict(), indent=2))


def main():
    parser = argparse.ArgumentParser(description='Substrate Operator Workspace')
    parser.add_argument('--root', default='/tmp/substrate_runtime_state', help='runtime root')
    parser.add_argument('--ledger', default='/tmp/substrate_runtime_state/usage-ledger.json', help='ledger path')
    parser.add_argument('--benchmark', help='benchmark report path')
    parser.add_argument('--trial-log', help='trial log path')
    parser.add_argument('--trial-registry', dest='trial_registry_path', help='trial registry path')
    parser.add_argument('--circuit-path', help='circuit breaker state path')

    sub = parser.add_subparsers(dest='cmd')

    sub.add_parser('status', help='runtime status snapshot')
    d = sub.add_parser('dashboard', help='full decision dashboard')
    d.add_argument('--json', action='store_true')
    sub.add_parser('smoke', help='smoke test')
    u = sub.add_parser('usage', help='usage report')
    t = sub.add_parser('trials', help='trial registry')
    t.add_argument('--path', required=True)
    s = sub.add_parser('registry-search', help='search trial registry')
    s.add_argument('--path', required=True)
    s.add_argument('--assessment')
    s.add_argument('--tag')
    c = sub.add_parser('circuit', help='circuit breaker status')
    c.add_argument('--path', required=True)

    args = parser.parse_args()

    if args.cmd == 'status':
        cmd_status(args)
    elif args.cmd == 'dashboard':
        cmd_dashboard(args)
    elif args.cmd == 'smoke':
        cmd_smoke(args)
    elif args.cmd == 'usage':
        cmd_usage(args)
    elif args.cmd == 'trials':
        cmd_trials(args)
    elif args.cmd == 'registry-search':
        cmd_registry_search(args)
    elif args.cmd == 'circuit':
        cmd_circuit(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
