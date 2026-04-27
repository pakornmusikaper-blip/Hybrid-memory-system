#!/usr/bin/env python3
"""
v8.4 Validate production config bundle examples.
"""

from __future__ import annotations

import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    runtime_cfg = json.loads((root / 'runtime-config.example.json').read_text())
    budget_cfg = json.loads((root / 'budget-policy.example.json').read_text())
    env_example = (root / '.env.external.example').read_text()
    checklist = (root / 'ACTIVATION-CHECKLIST.md').read_text()

    result = {
        'runtime_config_has_external_toggle': 'external_enabled' in runtime_cfg,
        'runtime_config_has_budget': 'budget' in runtime_cfg,
        'budget_profiles': sorted(budget_cfg.keys()),
        'env_has_minimax_key': 'MINIMAX_API_KEY=' in env_example,
        'checklist_has_preflight': 'preflight passes' in checklist,
    }
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
