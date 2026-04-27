#!/usr/bin/env python3
"""
CLI for trial log append/report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v9.benchmark_report import load_report
from v9.trial_log import TrialLog
from v9.trial_history_report import TrialHistoryReport


def main():
    parser = argparse.ArgumentParser(description='Substrate trial log CLI')
    parser.add_argument('log_path', help='path to trial-log.json')
    parser.add_argument('--append-report', help='path to live benchmark json to summarize and append')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    log = TrialLog(Path(args.log_path))
    if args.append_report:
        report = load_report(Path(args.append_report))
        log.append(report.build(), args.append_report)

    history = TrialHistoryReport(log)
    if args.json:
        print(json.dumps(history.build(), indent=2))
    else:
        print(history.render_text())


if __name__ == '__main__':
    main()
