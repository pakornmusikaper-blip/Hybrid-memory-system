#!/usr/bin/env python3
"""
Demo for operator notifier.
"""

from __future__ import annotations

import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v10.operator_notifier import OperatorNotifier


def main():
    notifier = OperatorNotifier()

    print("=== notifier demo (disabled without env vars) ===")
    results = [
        notifier.alert_circuit_open("minimax-api", 3),
        notifier.alert_budget_exceeded(0.012, 0.01),
        notifier.alert_poison_queue(3),
        notifier.alert_reflection_needed(5, 0.4),
        notifier.alert_trial_complete("trial-0001", "healthy hybrid external trial"),
    ]
    for r in results:
        print(f"  sent={r}")


if __name__ == '__main__':
    main()
