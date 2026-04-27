#!/usr/bin/env python3
"""
Demo for prompt quality scorer.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v10.prompt_quality_scorer import PromptQualityScorer


def main():
    scorer = PromptQualityScorer()

    print("=== summary quality ===")
    external_summary = """
## Summary

- System health is 🟢 ALIVE
- 2 active beliefs in embryonic stage
- Queue all clear

**Conclusion:** System is operating within normal parameters.
"""
    local_summary = "System OK. 2 beliefs. Queue clear."
    result = scorer.compare(local_summary, external_summary, "summary")
    print(json.dumps(result, indent=2))

    print("\n=== reflect quality ===")
    external_reflect = """
## Reflection

I observe the following patterns:

1. **Belief drift:** Embryonic beliefs remain unstable
2. **Queue pressure:** Low, all clear
3. **Cognitive load:** Moderate

**Insight:** The system is absorbing context steadily without saturation.
"""
    local_reflect = "Beliefs still forming. Queue is clear."
    result = scorer.compare(local_reflect, external_reflect, "reflect")
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
