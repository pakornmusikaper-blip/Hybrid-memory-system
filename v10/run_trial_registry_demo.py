#!/usr/bin/env python3
"""
Demo for v10.3 trial registry.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v9.benchmark_report import BenchmarkReport
from v10.trial_registry import TrialRegistry


def main():
    root = Path('/tmp/v10_trial_registry_demo')
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    registry = TrialRegistry(root / 'trial-registry.json')

    report1 = BenchmarkReport({
        'results': [
            {'route': {'backend': 'external'}, 'result': {'provider': 'minimax-api', 'fallback': False}},
            {'route': {'backend': 'heuristic'}, 'skipped_external': True},
        ],
        'after': {'total_requests': 1, 'total_cost_usd': 0.0008},
        'report': {'request_ratio': 0.2, 'cost_ratio': 0.16, 'warnings': []},
    }).build()
    report2 = BenchmarkReport({
        'results': [
            {'route': {'backend': 'external'}, 'result': {'provider': 'minimax-api', 'fallback': False}},
            {'route': {'backend': 'external'}, 'result': {'provider': 'minimax-api', 'fallback': False}},
            {'route': {'backend': 'heuristic'}, 'skipped_external': True},
        ],
        'after': {'total_requests': 2, 'total_cost_usd': 0.0014},
        'report': {'request_ratio': 0.4, 'cost_ratio': 0.28, 'warnings': []},
    }).build()

    registry.add(source_path='run1.json', summary=report1, tags=['starter', 'hybrid'])
    registry.add(source_path='run2.json', summary=report2, tags=['healthy', 'hybrid'])

    print(json.dumps({
        'all': registry.read_all(),
        'search_assessment': registry.search(assessment='healthy hybrid external trial'),
        'search_tag': registry.search(tag='hybrid'),
    }, indent=2))


if __name__ == '__main__':
    main()
