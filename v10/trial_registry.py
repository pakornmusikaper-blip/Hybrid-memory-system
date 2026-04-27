#!/usr/bin/env python3
"""
v10.3 Trial registry / experiment index.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class TrialRegistry:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, *, source_path: str | None, summary: Dict, tags: List[str] | None = None):
        entries = self.read_all()
        trial_id = f"trial-{len(entries)+1:04d}"
        entries.append({
            "trial_id": trial_id,
            "ts": datetime.now().isoformat(),
            "source_path": source_path,
            "assessment": summary.get("assessment"),
            "external_success_count": summary.get("external_success_count"),
            "ledger_total_cost_usd": summary.get("ledger_total_cost_usd"),
            "route_counts": summary.get("route_counts"),
            "tags": tags or [],
        })
        self._write(entries)
        return trial_id

    def read_all(self) -> List[Dict]:
        if not self.path.exists():
            return []
        with open(self.path) as f:
            return json.load(f)

    def search(self, *, assessment: str | None = None, tag: str | None = None) -> List[Dict]:
        entries = self.read_all()
        if assessment:
            entries = [e for e in entries if e.get("assessment") == assessment]
        if tag:
            entries = [e for e in entries if tag in e.get("tags", [])]
        return entries

    def _write(self, entries: List[Dict]):
        with open(self.path, "w") as f:
            json.dump(entries[-500:], f, indent=2)
