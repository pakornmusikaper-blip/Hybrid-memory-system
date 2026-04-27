#!/usr/bin/env python3
"""
v10.0 Decision dashboard builder.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))
sys.path.insert(0, str(repo / 'v5'))

from monitor import status_panel, beliefs_panel, concepts_panel, cognition_panel, reflections_panel
from v6.runtime_config import RuntimeConfig, ExternalBudget
from v6.usage_ledger import UsageLedger
from v6.usage_report import UsageReport
from v9.benchmark_report import load_report
from v9.trial_log import TrialLog
from v9.trial_history_report import TrialHistoryReport
from v9.quality_compare import QualityComparison


class DecisionDashboard:
    def __init__(self, *, root: Path, ledger_path: Path, benchmark_path: Path | None = None, trial_log_path: Path | None = None):
        self.root = Path(root)
        self.ledger_path = Path(ledger_path)
        self.benchmark_path = Path(benchmark_path) if benchmark_path else None
        self.trial_log_path = Path(trial_log_path) if trial_log_path else None

    def build(self) -> Dict:
        usage = UsageReport(
            UsageLedger(self.ledger_path),
            RuntimeConfig(external_enabled=True, budget=ExternalBudget()),
        ).build()

        latest_benchmark = None
        quality_summary = None
        if self.benchmark_path and self.benchmark_path.exists():
            report = load_report(self.benchmark_path)
            latest_benchmark = report.build()
            payload = json.loads(self.benchmark_path.read_text())
            quality_summary = QualityComparison().summary(QualityComparison().compare(payload))

        trial_history = None
        if self.trial_log_path and self.trial_log_path.exists():
            trial_history = TrialHistoryReport(TrialLog(self.trial_log_path)).build()

        return {
            "status": status_panel(self.root),
            "beliefs": beliefs_panel(self.root),
            "concepts": concepts_panel(self.root),
            "cognition": cognition_panel(self.root),
            "reflections": reflections_panel(self.root),
            "usage": usage,
            "latest_benchmark": latest_benchmark,
            "trial_history": trial_history,
            "quality_summary": quality_summary,
        }

    def render_text(self) -> str:
        data = self.build()
        lines = [
            data['status'],
            data['beliefs'],
            data['concepts'],
            data['cognition'],
            data['reflections'],
            '',
            '=' * 52,
            '  DECISION SUMMARY',
            '=' * 52,
            f"Usage requests/cost : {data['usage']['total_requests']} / ${data['usage']['total_cost_usd']:.6f}",
        ]
        if data['latest_benchmark']:
            lines.append(f"Latest benchmark     : {data['latest_benchmark']['assessment']}")
        if data['trial_history']:
            lines.append(f"Trial count          : {data['trial_history']['total_trials']}")
            lines.append(f"Trial ext successes  : {data['trial_history']['total_external_successes']}")
        if data['quality_summary']:
            lines.append(f"Avg richness         : {data['quality_summary']['avg_richness']}")
            lines.append(f"Avg appropriateness  : {data['quality_summary']['avg_appropriateness']}")
        lines.append('=' * 52)
        return '\n'.join(lines)
