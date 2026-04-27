#!/usr/bin/env python3
"""
v11.x Run all operator checks — smoke, circuit, usage, quality, budget, dashboard.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v10.smoke_test import run_smoke_test
from v10.circuit_breaker import CircuitBreaker
from v10.memory_budget import MemoryBudgetEnforcer, MemoryBudgetConfig
from v10.prompt_quality_scorer import PromptQualityScorer
from v6.usage_ledger import UsageLedger
from v6.usage_report import UsageReport
from v6.runtime_config import RuntimeConfig, ExternalBudget
from v9.benchmark_report import load_report
from v9.trial_log import TrialLog
from v9.trial_history_report import TrialHistoryReport


def run_all_checks(
    root: Path,
    ledger_path: Path,
    circuit_path: Path,
    trial_log_path: Path | None = None,
    benchmark_path: Path | None = None,
) -> dict:
    results = {}

    print("=== [1/6] Smoke test ===")
    smoke = run_smoke_test()
    print(f"  status: {smoke['status']}")
    if smoke['errors']:
        for e in smoke['errors']:
            print(f"  ERROR: {e}")
    results['smoke'] = smoke

    print("\n=== [2/6] Circuit breaker ===")
    cb = CircuitBreaker(circuit_path) if circuit_path.exists() else None
    if cb:
        snap = cb.snapshot()
        print(f"  state: {snap.state}, consecutive_failures: {snap.consecutive_failures}")
        results['circuit'] = snap.to_dict()
    else:
        print("  no circuit state file found")
        results['circuit'] = None

    print("\n=== [3/6] Usage report ===")
    config = RuntimeConfig(external_enabled=True, budget=ExternalBudget())
    ledger = UsageLedger(ledger_path) if ledger_path.exists() else None
    if ledger:
        usage = UsageReport(ledger, config).build()
        print(f"  requests: {usage['total_requests']}, cost: ${usage['total_cost_usd']:.6f}")
        results['usage'] = usage
    else:
        print("  no ledger found")
        results['usage'] = None

    print("\n=== [4/6] Memory budget ===")
    enforcer = MemoryBudgetEnforcer(root, MemoryBudgetConfig())
    snap = enforcer.snapshot()
    print(f"  current: {snap.current_mb:.4f}MB / {snap.max_mb:.4f}MB (ratio={snap.usage_ratio:.2f})")
    if snap.over_budget:
        print(f"  over_budget: {snap.over_budget}")
    results['memory_budget'] = snap.to_dict()

    print("\n=== [5/6] Quality scorer ===")
    scorer = PromptQualityScorer()
    samples = [
        ("summary", "System OK. 2 beliefs. Queue clear.", "## Summary\n- System health is 🟢 ALIVE\n- 2 active beliefs in embryonic stage\n- Queue all clear\n\n**Conclusion:** System operating within normal parameters."),
        ("reflect", "Beliefs forming. Queue clear.", "## Reflection\n\n1. **Belief drift:** Embryonic beliefs remain unstable\n2. **Queue pressure:** Low, all clear\n3. **Cognitive load:** Moderate\n\n**Insight:** System is absorbing context without saturation."),
    ]
    quality_samples = []
    for op, low, high in samples:
        result = scorer.compare(low, high, op)
        print(f"  [{op}] winner={result['winner']}, external={result['external']['overall']:.3f}, local={result['local']['overall']:.3f}")
        quality_samples.append(result)
    results['quality_samples'] = quality_samples

    print("\n=== [6/6] Trial history ===")
    if trial_log_path and trial_log_path.exists():
        history = TrialHistoryReport(TrialLog(trial_log_path)).build()
        print(f"  total_trials: {history['total_trials']}, external_successes: {history['total_external_successes']}")
        results['trial_history'] = history
    else:
        print("  no trial log found")
        results['trial_history'] = None

    return results


def main():
    root = Path('/tmp/substrate_runtime_state')
    if not root.exists():
        root.mkdir(parents=True, exist_ok=True)

    results = run_all_checks(
        root=root,
        ledger_path=root / 'usage-ledger.json',
        circuit_path=root / 'circuit-breaker.json',
        trial_log_path=root / 'trial-log.json',
        benchmark_path=root / 'benchmark.json',
    )
    print("\n=== ALL CHECKS COMPLETE ===")


if __name__ == '__main__':
    main()
