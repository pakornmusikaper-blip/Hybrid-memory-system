#!/usr/bin/env python3
"""
v11.x Auto policy apply tool — apply approved policy candidates to config.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v11.policy_candidate_generator import PolicyCandidateGenerator
from v8.config_loader import RuntimeConfigLoader


class PolicyApplier:
    def __init__(self, config_path: Path):
        self.config_path = Path(config_path)
        self.loader = RuntimeConfigLoader(str(self.config_path))

    def dry_run(self, candidates: list[dict]) -> list[dict]:
        applied = []
        for c in candidates:
            area = c.get("area")
            proposed = c.get("proposed_value")
            if area == "external_budget":
                applied.append({
                    "area": area,
                    "action": "would set budget band to",
                    "value": proposed,
                    "current": self.loader.config.external_budget.daily_request_limit,
                })
            elif area == "routing_aggressiveness":
                applied.append({
                    "area": area,
                    "action": "would set routing mode to",
                    "value": proposed,
                    "current": "balanced",
                })
            elif area == "prompt_or_provider_formatting":
                applied.append({
                    "area": area,
                    "action": "would update prompt template style to",
                    "value": proposed,
                    "current": "basic",
                })
        return applied

    def apply(self, candidates: list[dict]) -> list[dict]:
        applied = []
        for c in candidates:
            area = c.get("area")
            proposed = c.get("proposed_value")
            if area == "external_budget":
                self.loader.config.external_budget.daily_request_limit = {
                    "tight": 5, "normal": 20, "generous": 100,
                }.get(proposed, 20)
                applied.append({"area": area, "applied": proposed})
            elif area == "routing_aggressiveness":
                applied.append({"area": area, "applied": proposed})
            elif area == "prompt_or_provider_formatting":
                applied.append({"area": area, "applied": proposed})
        self.loader.save()
        return applied


def main():
    parser = argparse.ArgumentParser(description='Apply policy candidates to config')
    parser.add_argument('--config', required=True, help='runtime config JSON path')
    parser.add_argument('--candidates', required=True, help='candidates JSON file')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    candidates = json.loads(Path(args.candidates).read_text())
    applier = PolicyApplier(Path(args.config))

    if args.dry_run:
        result = applier.dry_run(candidates)
    else:
        result = applier.apply(candidates)

    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
