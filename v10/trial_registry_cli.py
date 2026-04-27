#!/usr/bin/env python3
"""
CLI for trial registry.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v9.benchmark_report import load_report
from v10.trial_registry import TrialRegistry


def main():
    parser = argparse.ArgumentParser(description='Substrate trial registry CLI')
    parser.add_argument('registry_path')
    parser.add_argument('--add-report')
    parser.add_argument('--tag', action='append')
    parser.add_argument('--search-assessment')
    parser.add_argument('--search-tag')
    args = parser.parse_args()

    registry = TrialRegistry(Path(args.registry_path))
    if args.add_report:
        report = load_report(Path(args.add_report)).build()
        registry.add(source_path=args.add_report, summary=report, tags=args.tag or [])

    if args.search_assessment or args.search_tag:
        payload = registry.search(assessment=args.search_assessment, tag=args.search_tag)
    else:
        payload = registry.read_all()
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
