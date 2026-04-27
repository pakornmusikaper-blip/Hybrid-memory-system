#!/usr/bin/env python3
"""
v6.8 Human-readable usage dashboard/report.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from v6.runtime_config import RuntimeConfig
from v6.usage_ledger import UsageLedger
from v6.ledger_budget_bridge import sync_budget_from_ledger


class UsageReport:
    def __init__(self, ledger: UsageLedger, config: RuntimeConfig):
        self.ledger = ledger
        self.config = sync_budget_from_ledger(config, ledger)

    def build(self) -> Dict:
        snap = self.ledger.snapshot()
        budget = self.config.budget
        req_ratio = budget.used_requests_today / max(1, budget.max_requests_per_day)
        cost_ratio = budget.used_cost_usd_today / max(0.000001, budget.max_cost_usd_per_day)
        warnings = []
        if req_ratio >= 1.0:
            warnings.append("request limit reached")
        elif req_ratio >= 0.8:
            warnings.append("request usage above 80%")
        if cost_ratio >= 1.0:
            warnings.append("cost limit reached")
        elif cost_ratio >= 0.8:
            warnings.append("cost usage above 80%")
        return {
            "date": snap["date"],
            "total_requests": snap["total_requests"],
            "total_cost_usd": snap["total_cost_usd"],
            "providers": snap["providers"],
            "recent_events": snap["events"][-10:],
            "request_limit": budget.max_requests_per_day,
            "cost_limit_usd": budget.max_cost_usd_per_day,
            "request_ratio": round(req_ratio, 3),
            "cost_ratio": round(cost_ratio, 3),
            "warnings": warnings,
        }

    def render_text(self) -> str:
        data = self.build()
        lines = [
            "=" * 52,
            "  SUBSTRATE EXTERNAL USAGE DASHBOARD",
            "=" * 52,
            f"Date               : {data['date']}",
            f"Total requests     : {data['total_requests']} / {data['request_limit']}",
            f"Total est. cost    : ${data['total_cost_usd']:.6f} / ${data['cost_limit_usd']:.6f}",
            f"Request usage      : {data['request_ratio']:.0%}",
            f"Cost usage         : {data['cost_ratio']:.0%}",
            "",
            "Providers:",
        ]
        providers = data["providers"] or {}
        if not providers:
            lines.append("  (no provider usage yet)")
        else:
            for name, meta in providers.items():
                lines.append(f"  - {name}: {meta['requests']} req, ${meta['cost_usd']:.6f}")

        lines.append("")
        lines.append("Recent events:")
        events = data["recent_events"]
        if not events:
            lines.append("  (no events yet)")
        else:
            for event in events:
                lines.append(
                    f"  - {event.get('ts')} | {event.get('provider')} | {event.get('model')} | ${event.get('cost_usd', 0):.6f} | {event.get('event_id')}"
                )

        if data["warnings"]:
            lines.append("")
            lines.append("Warnings:")
            for warning in data["warnings"]:
                lines.append(f"  - {warning}")

        lines.append("=" * 52)
        return "\n".join(lines)


def build_default_report(ledger_path: Path) -> str:
    ledger = UsageLedger(ledger_path)
    config = RuntimeConfig(external_enabled=True)
    report = UsageReport(ledger, config)
    return report.render_text()
