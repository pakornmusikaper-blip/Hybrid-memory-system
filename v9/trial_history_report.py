#!/usr/bin/env python3
"""
v9.2 Historical report over trial logs.
"""

from __future__ import annotations

from typing import Dict

from v9.trial_log import TrialLog


class TrialHistoryReport:
    def __init__(self, trial_log: TrialLog):
        self.trial_log = trial_log

    def build(self) -> Dict:
        entries = self.trial_log.read_all()
        total = len(entries)
        external_successes = sum(e.get("summary", {}).get("external_success_count", 0) for e in entries)
        total_cost = sum(e.get("summary", {}).get("ledger_total_cost_usd", 0.0) for e in entries)
        assessments = {}
        for e in entries:
            a = e.get("summary", {}).get("assessment", "unknown")
            assessments[a] = assessments.get(a, 0) + 1
        latest = entries[-1] if entries else None
        return {
            "total_trials": total,
            "total_external_successes": external_successes,
            "total_estimated_cost_usd": round(total_cost, 6),
            "assessments": assessments,
            "latest": latest,
        }

    def render_text(self) -> str:
        data = self.build()
        lines = [
            "=" * 52,
            "  SUBSTRATE TRIAL HISTORY REPORT",
            "=" * 52,
            f"Total trials             : {data['total_trials']}",
            f"Total external successes : {data['total_external_successes']}",
            f"Total est. cost          : ${data['total_estimated_cost_usd']:.6f}",
            f"Assessments              : {data['assessments']}",
        ]
        latest = data.get("latest")
        if latest:
            lines.append(f"Latest trial ts          : {latest.get('ts')}")
            lines.append(f"Latest assessment        : {latest.get('summary', {}).get('assessment')}")
        lines.append("=" * 52)
        return "\n".join(lines)
