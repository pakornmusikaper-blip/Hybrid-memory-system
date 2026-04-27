#!/usr/bin/env python3
"""
v9.1 Real benchmark report builder.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class BenchmarkReport:
    def __init__(self, payload: Dict):
        self.payload = payload

    def build(self) -> Dict:
        results = self.payload.get("results", [])
        external = [r for r in results if r.get("result", {}).get("provider") == "minimax-api"]
        fallback = [r for r in results if r.get("result", {}).get("fallback") is True]
        skipped = [r for r in results if r.get("skipped_external")]
        route_counts = {}
        for r in results:
            backend = r.get("route", {}).get("backend", "unknown")
            route_counts[backend] = route_counts.get(backend, 0) + 1

        after = self.payload.get("after", {})
        report = self.payload.get("report", {})

        return {
            "total_scenarios": len(results),
            "external_success_count": len(external),
            "fallback_count": len(fallback),
            "skipped_external_count": len(skipped),
            "route_counts": route_counts,
            "ledger_total_requests": after.get("total_requests", 0),
            "ledger_total_cost_usd": after.get("total_cost_usd", 0.0),
            "request_ratio": report.get("request_ratio", 0.0),
            "cost_ratio": report.get("cost_ratio", 0.0),
            "warnings": report.get("warnings", []),
            "assessment": self._assessment(len(external), len(fallback), len(skipped), report.get("warnings", [])),
        }

    def _assessment(self, external_success_count: int, fallback_count: int, skipped_external_count: int, warnings: List[str]) -> str:
        if external_success_count >= 2 and fallback_count == 0 and not warnings:
            return "healthy hybrid external trial"
        if fallback_count > 0:
            return "external path unstable or unavailable"
        if skipped_external_count > 0 and external_success_count > 0:
            return "routing policy is discriminating by task value"
        return "mixed benchmark state"

    def render_text(self) -> str:
        data = self.build()
        lines = [
            "=" * 52,
            "  SUBSTRATE REAL BENCHMARK REPORT",
            "=" * 52,
            f"Total scenarios        : {data['total_scenarios']}",
            f"External successes     : {data['external_success_count']}",
            f"Fallback count         : {data['fallback_count']}",
            f"Skipped external tasks : {data['skipped_external_count']}",
            f"Route counts           : {data['route_counts']}",
            f"Ledger requests        : {data['ledger_total_requests']}",
            f"Ledger est. cost       : ${data['ledger_total_cost_usd']:.6f}",
            f"Request ratio          : {data['request_ratio']:.0%}",
            f"Cost ratio             : {data['cost_ratio']:.0%}",
            f"Assessment             : {data['assessment']}",
        ]
        if data['warnings']:
            lines.append("Warnings:")
            for warning in data['warnings']:
                lines.append(f"  - {warning}")
        lines.append("=" * 52)
        return "\n".join(lines)


def load_report(path: Path) -> BenchmarkReport:
    with open(path) as f:
        payload = json.load(f)
    return BenchmarkReport(payload)
