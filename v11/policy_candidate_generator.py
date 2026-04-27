#!/usr/bin/env python3
"""
v11.x Auto policy candidate generator.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class PolicyCandidate:
    area: str
    current_value: str
    proposed_value: str
    confidence: float
    reason: str

    def to_dict(self) -> Dict:
        return asdict(self)


class PolicyCandidateGenerator:
    def generate(self, dashboard: Dict) -> List[PolicyCandidate]:
        candidates: List[PolicyCandidate] = []

        usage = dashboard.get("usage", {})
        latest_benchmark = dashboard.get("latest_benchmark") or {}
        quality = dashboard.get("quality_summary") or {}
        trial_history = dashboard.get("trial_history") or {}

        cost_ratio = usage.get("cost_ratio", 0.0)
        request_ratio = usage.get("request_ratio", 0.0)
        ext_success = latest_benchmark.get("external_success_count", 0)
        avg_richness = quality.get("avg_richness", 0.0)
        avg_appropriateness = quality.get("avg_appropriateness", 0.0)
        total_trials = trial_history.get("total_trials", 0)

        # External budget candidate
        if cost_ratio < 0.35 and ext_success >= 2:
            candidates.append(PolicyCandidate(
                area="external_budget",
                current_value="normal",
                proposed_value="generous",
                confidence=0.72,
                reason="external path succeeds while budget headroom remains",
            ))
        if cost_ratio >= 0.8:
            candidates.append(PolicyCandidate(
                area="external_budget",
                current_value="generous",
                proposed_value="tight",
                confidence=0.88,
                reason="budget consumption high, risk of overspend",
            ))

        # Routing aggressiveness candidate
        if avg_appropriateness >= 0.9 and total_trials >= 3:
            candidates.append(PolicyCandidate(
                area="routing_aggressiveness",
                current_value="balanced",
                proposed_value="confident",
                confidence=0.80,
                reason="task-to-backend fit is strong across multiple trials",
            ))
        if avg_appropriateness < 0.7:
            candidates.append(PolicyCandidate(
                area="routing_aggressiveness",
                current_value="confident",
                proposed_value="balanced",
                confidence=0.85,
                reason="route appropriateness low, current thresholds may be too aggressive",
            ))

        # Output quality candidate
        if avg_richness < 0.4 and ext_success >= 1:
            candidates.append(PolicyCandidate(
                area="prompt_or_provider_formatting",
                current_value="basic",
                proposed_value="structured",
                confidence=0.84,
                reason="external output is stable but richness is low, improve prompts",
            ))

        # Evidence depth guard
        if total_trials < 3 and candidates:
            candidates = [
                c for c in candidates
                if c.confidence < 0.85
            ]
            candidates.append(PolicyCandidate(
                area="evidence_depth",
                current_value="insufficient",
                proposed_value="wait_for_more_trials",
                confidence=0.9,
                reason="few trials — validate changes before applying",
            ))

        return candidates
