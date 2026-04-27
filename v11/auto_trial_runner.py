#!/usr/bin/env python3
"""
v11.x Auto trial runner — run benchmarks, score quality, record to registry.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from datetime import datetime

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v9.benchmark_report import BenchmarkReport
from v9.quality_compare import QualityComparison
from v9.trial_log import TrialLog
from v9.trial_history_report import TrialHistoryReport
from v10.trial_registry import TrialRegistry
from v6.usage_ledger import UsageLedger


class AutoTrialRunner:
    def __init__(
        self,
        root: Path,
        ledger_path: Path,
        benchmark_path: Path,
        trial_log_path: Path,
        trial_registry_path: Path,
    ):
        self.root = Path(root)
        self.ledger_path = Path(ledger_path)
        self.benchmark_path = Path(benchmark_path)
        self.trial_log_path = Path(trial_log_path)
        self.trial_registry_path = Path(trial_registry_path)
        self.benchmark_path.parent.mkdir(parents=True, exist_ok=True)
        self.trial_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.trial_registry_path.parent.mkdir(parents=True, exist_ok=True)

    def run(self, scenarios: list[dict]) -> dict:
        from v9.comparative_runner import ComparativeRunner
        runner = ComparativeRunner()
        results = runner.run(scenarios)

        # Write benchmark payload
        payload = {"results": []}
        for variant, data in results.items():
            for r in data.get("results", []):
                entry = {
                    "variant": variant,
                    **r,
                }
                payload["results"].append(entry)

        # Attach ledger snapshot
        ledger = UsageLedger(self.ledger_path)
        payload["after"] = {
            "total_requests": ledger.state.total_requests,
            "total_cost_usd": ledger.state.total_cost_usd,
        }

        # Write benchmark report
        benchmark_report = BenchmarkReport(payload).build()
        self.benchmark_path.write_text(json.dumps(payload, indent=2))

        # Record to trial log
        trial_log = TrialLog(self.trial_log_path)
        trial_log.append(benchmark_report, str(self.benchmark_path))

        # Record to registry
        registry = TrialRegistry(self.trial_registry_path)
        trial_id = registry.add(
            source_path=str(self.benchmark_path),
            summary=benchmark_report,
            tags=["auto-trial", datetime.now().strftime("%Y-%m-%d")],
        )

        return {
            "trial_id": trial_id,
            "benchmark": benchmark_report,
            "payload_path": str(self.benchmark_path),
        }


def main():
    parser = argparse.ArgumentParser(description='Auto trial runner')
    parser.add_argument('--root', required=True)
    parser.add_argument('--ledger', required=True)
    parser.add_argument('--benchmark', required=True)
    parser.add_argument('--trial-log', required=True)
    parser.add_argument('--registry', required=True)
    parser.add_argument('--json', default='scenarios.json', help='scenario JSON')
    args = parser.parse_args()

    scenarios = json.loads(Path(args.json).read_text())
    runner = AutoTrialRunner(
        root=Path(args.root),
        ledger_path=Path(args.ledger),
        benchmark_path=Path(args.benchmark),
        trial_log_path=Path(args.trial_log),
        trial_registry_path=Path(args.registry),
    )
    result = runner.run(scenarios)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
