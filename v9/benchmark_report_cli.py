#!/usr/bin/env python3
"""
CLI for v9.1 benchmark report.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmark_report import load_report


def main():
    parser = argparse.ArgumentParser(description='Substrate real benchmark report CLI')
    parser.add_argument('path', help='path to live_minimax_test output json')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    report = load_report(Path(args.path))
    if args.json:
        print(json.dumps(report.build(), indent=2))
    else:
        print(report.render_text())


if __name__ == '__main__':
    main()
