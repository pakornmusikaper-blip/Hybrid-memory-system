#!/usr/bin/env python3
"""
Demo for real minimax adapter and policy candidate generator.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v11.real_minimax_adapter import RealMiniMaxAdapter, MiniMaxConfig
from v11.policy_candidate_generator import PolicyCandidateGenerator


def main():
    print("=== real minimax adapter (disabled — no env var) ===")
    adapter = RealMiniMaxAdapter(MiniMaxConfig(enabled=False))
    result = adapter.generate("hello world", "standard")
    print(f"  ok={result.ok}, provider={result.provider}, reason={result.reason}")

    print("\n=== policy candidate generator ===")
    dashboard = {
        "usage": {"cost_ratio": 0.3, "request_ratio": 0.4},
        "latest_benchmark": {"external_success_count": 3},
        "quality_summary": {"avg_richness": 0.35, "avg_appropriateness": 0.92},
        "trial_history": {"total_trials": 4},
    }
    generator = PolicyCandidateGenerator()
    candidates = generator.generate(dashboard)
    for c in candidates:
        print(f"  [{c.area}] {c.current_value} -> {c.proposed_value} (conf={c.confidence:.2f})")
        print(f"    reason: {c.reason}")


if __name__ == '__main__':
    main()
