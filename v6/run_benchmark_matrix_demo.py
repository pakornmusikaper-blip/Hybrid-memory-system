#!/usr/bin/env python3
"""
Demo for v6.4 Benchmark Matrix.
"""

from __future__ import annotations

import json

from benchmark_matrix import BenchmarkMatrix


def main():
    matrix = BenchmarkMatrix()
    scenarios = [
        {
            "name": "restricted summary",
            "content": "Summarize recent memory pressure and queue state for operator review.",
            "operation": "summary",
            "privacy": "restricted",
            "budget": "generous",
            "mode": "summary",
            "urgency": "high",
        },
        {
            "name": "urgent reflection",
            "content": "Reflect on belief drift and determine whether conscious wake is required immediately.",
            "operation": "reflect",
            "privacy": "normal",
            "budget": "generous",
            "mode": "reflect",
            "urgency": "high",
        },
        {
            "name": "routine status",
            "content": "Generate a routine system status update for the operator.",
            "operation": "generate",
            "privacy": "normal",
            "budget": "normal",
            "mode": "standard",
            "urgency": "normal",
        },
        {
            "name": "low cleanup",
            "content": "Low-value cleanup notice.",
            "operation": "generate",
            "privacy": "normal",
            "budget": "tight",
            "mode": "light",
            "urgency": "low",
        },
    ]
    rows = [row.to_dict() for row in matrix.run(scenarios)]
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
