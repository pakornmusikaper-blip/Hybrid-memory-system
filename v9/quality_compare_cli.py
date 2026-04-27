#!/usr/bin/env python3
"""
CLI for quality comparison.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v9.quality_compare import QualityComparison


def main():
    parser = argparse.ArgumentParser(description='Substrate quality comparison CLI')
    parser.add_argument('path', help='path to live_minimax_test output json')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    payload = json.loads(Path(args.path).read_text())
    qc = QualityComparison()
    summary = qc.summary(qc.compare(payload))
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
