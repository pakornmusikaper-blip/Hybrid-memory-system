#!/usr/bin/env python3
"""
Demo for v9.3 quality comparison.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v9.quality_compare import QualityComparison


def main():
    payload = {
        "results": [
            {
                "scenario": "summary",
                "route": {"backend": "external"},
                "result": {
                    "provider": "minimax-api",
                    "fallback": False,
                    "text": "[minimax:summary] generated external response for: Summarize compactly: recent memory pressure and queue state.",
                },
            },
            {
                "scenario": "reflection",
                "route": {"backend": "external"},
                "result": {
                    "provider": "minimax-api",
                    "fallback": False,
                    "text": "[minimax:reflect] generated external response for: Reflect on belief drift, concept coherence, and wake behavior.",
                },
            },
            {
                "scenario": "low-value",
                "route": {"backend": "heuristic"},
                "skipped_external": True,
                "reason": "low-value comparison should avoid expensive external usage",
            },
        ]
    }
    qc = QualityComparison()
    print(json.dumps(qc.summary(qc.compare(payload)), indent=2))


if __name__ == '__main__':
    main()
