#!/usr/bin/env python3
"""
v10.1 Recommendation layer for operator actions.
"""

from __future__ import annotations

from typing import Dict, List


class RecommendationLayer:
    def recommend(self, dashboard: Dict) -> List[str]:
        recs: List[str] = []

        usage = dashboard.get("usage", {})
        latest_benchmark = dashboard.get("latest_benchmark") or {}
        trial_history = dashboard.get("trial_history") or {}
        quality = dashboard.get("quality_summary") or {}

        cost_ratio = usage.get("cost_ratio", 0.0)
        request_ratio = usage.get("request_ratio", 0.0)
        warnings = usage.get("warnings", [])
        ext_success = latest_benchmark.get("external_success_count", 0)
        fallback_count = latest_benchmark.get("fallback_count", 0)
        avg_appropriateness = quality.get("avg_appropriateness", 0.0)
        avg_richness = quality.get("avg_richness", 0.0)
        total_trials = trial_history.get("total_trials", 0)

        if fallback_count > 0:
            recs.append("investigate adapter fallback causes before increasing external usage")
        if cost_ratio >= 0.8 or request_ratio >= 0.8 or warnings:
            recs.append("tighten external budget or reduce external routing frequency")
        if ext_success >= 2 and avg_appropriateness >= 0.9 and cost_ratio < 0.5:
            recs.append("current hybrid policy looks healthy, consider keeping it stable")
        if ext_success >= 2 and avg_richness < 0.4:
            recs.append("external path is stable but output richness is low, improve prompt or provider formatting")
        if total_trials < 3:
            recs.append("collect more trials before making permanent routing changes")
        if avg_appropriateness < 0.7:
            recs.append("review routing policy, task classes may be hitting the wrong backend")
        if not recs:
            recs.append("no urgent operator action suggested")
        return recs
