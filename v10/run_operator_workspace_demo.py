#!/usr/bin/env python3
"""
Demo for operator workspace — each command runs in isolation.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v9.benchmark_report import BenchmarkReport
from v10.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from v10.trial_registry import TrialRegistry


def setup():
    root = Path('/tmp/v10_workspace_demo')
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    (root / 'memory').mkdir(exist_ok=True)
    (root / 'runtime').mkdir(exist_ok=True)
    (root / 'beliefs.json').touch()
    (root / 'concepts.json').touch()
    (root / 'cognition.json').touch()
    (root / 'reflections.json').touch()
    (root / 'health.json').write_text('{}')

    ledger = root / 'usage-ledger.json'
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text('[]')

    registry = TrialRegistry(root / 'trial-registry.json')
    report1 = BenchmarkReport({
        'results': [
            {'route': {'backend': 'external'}, 'result': {'provider': 'minimax-api', 'fallback': False}},
            {'route': {'backend': 'heuristic'}, 'skipped_external': True},
        ],
        'after': {'total_requests': 1, 'total_cost_usd': 0.0008},
        'report': {'request_ratio': 0.2, 'cost_ratio': 0.16, 'warnings': []},
    }).build()
    registry.add(source_path='run1.json', summary=report1, tags=['starter', 'hybrid'])

    cb = CircuitBreaker(root / 'circuit-breaker.json', CircuitBreakerConfig(
        failures_to_open=3,
        cooldown_seconds=300.0,
        half_open_successes=2,
    ))

    return root


def run(args):
    script = repo / 'v10' / 'operator_workspace.py'
    result = subprocess.run(
        ['python3', str(script)] + args,
        capture_output=True, text=True,
    )
    print(result.stdout or result.stderr)
    return result.returncode


def main():
    root = setup()
    print("=== smoke ===")
    run([f'--root={root}', f'--ledger={root}/usage-ledger.json', 'smoke'])

    print("\n=== trials ===")
    run([f'--root={root}', f'--ledger={root}/usage-ledger.json', 'trials', '--path', f'{root}/trial-registry.json'])

    print("\n=== circuit ===")
    run([f'--circuit-path={root}/circuit-breaker.json', 'circuit', '--path', f'{root}/circuit-breaker.json'])


if __name__ == '__main__':
    main()
