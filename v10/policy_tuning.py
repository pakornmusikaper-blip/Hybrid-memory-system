#!/usr/bin/env python3
"""
v10.2 Policy tuning assistant.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class PolicySuggestion:
    area: str
    recommendation: str
    confidence: float
    reason: str

    def to_dict(self) -> Dict:
        return asdict(self)


class PolicyTuningAssistant:
    def suggest(self, dashboard: Dict) -> List[PolicySuggestion]:
        suggestions: List[PolicySuggestion] = []
        usage = dashboard.get("usage", {})
        latest_benchmark = dashboard.get("latest_benchmark") or {}
        quality = dashboard.get("quality_summary") or {}
        trial_history = dashboard.get("trial_history") or {}

        cost_ratio = usage.get("cost_ratio", 0.0)
        request_ratio = usage.get("request_ratio", 0.0)
        ext_success = latest_benchmark.get("external_success_count", 0)
        fallback_count = latest_benchmark.get("fallback_count", 0)
        avg_richness = quality.get("avg_richness", 0.0)
        avg_appropriateness = quality.get("avg_appropriateness", 0.0)
        total_trials = trial_history.get("total_trials", 0)

        if cost_ratio < 0.35 and ext_success >= 2:
            suggestions.append(PolicySuggestion(
                area="external_budget",
                recommendation="consider slightly increasing external request allowance",
                confidence=0.72,
                reason="external path is succeeding while budget usage remains low",
            ))

        if avg_richness < 0.4 and ext_success >= 2:
            suggestions.append(PolicySuggestion(
                area="prompt_or_provider_formatting",
                recommendation="improve external prompt templates before expanding usage",
                confidence=0.84,
                reason="external path is stable but output richness remains modest",
            ))

        if avg_appropriateness >= 0.9 and total_trials >= 2:
            suggestions.append(PolicySuggestion(
                area="routing_aggressiveness",
                recommendation="keep current hybrid routing thresholds stable",
                confidence=0.78,
                reason="task-to-backend fit looks strong across trials",
            ))

        if request_ratio > 0.8 or cost_ratio > 0.8:
            suggestions.append(PolicySuggestion(
                area="external_budget",
                recommendation="tighten daily budget or reduce external routing frequency",
                confidence=0.9,
                reason="usage is close to configured limits",
            ))

        if fallback_count > 0:
            suggestions.append(PolicySuggestion(
                area="reliability",
                recommendation="investigate fallback causes before raising external share",
                confidence=0.92,
                reason="fallbacks indicate external or local execution instability",
            ))

        if total_trials < 3:
            suggestions.append(PolicySuggestion(
                area="evidence_depth",
                recommendation="collect more trials before making permanent policy changes",
                confidence=0.88,
                reason="sample size is still small",
            ))

        if not suggestions:
            suggestions.append(PolicySuggestion(
                area="policy",
                recommendation="no tuning change suggested",
                confidence=0.6,
                reason="current evidence does not indicate a strong adjustment need",
            ))

        return suggestions
