#!/usr/bin/env python3
"""
Demo for v9.5 comparative pack runner.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v9.comparative_runner import ComparativeRunner


def main():
    scenarios = [
        {
            "name": "summary",
            "content": "Summarize recent memory pressure and queue state.",
            "operation": "summary",
            "privacy": "normal",
            "budget": "generous",
            "mode": "summary",
            "urgency": "high",
        },
        {
            "name": "reflection",
            "content": "Reflect on belief drift and concept coherence.",
            "operation": "reflect",
            "privacy": "normal",
            "budget": "generous",
            "mode": "reflect",
            "urgency": "high",
        },
        {
            "name": "low-value",
            "content": "Routine cleanup note.",
            "operation": "generate",
            "privacy": "normal",
            "budget": "tight",
            "mode": "light",
            "urgency": "low",
        },
    ]
    runner = ComparativeRunner()
    print(json.dumps(runner.run(scenarios), indent=2))


if __name__ == '__main__':
    main()
