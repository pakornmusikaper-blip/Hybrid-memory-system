#!/usr/bin/env python3
"""
v6.7 Persisted external usage ledger.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class ProviderUsage:
    requests: int = 0
    cost_usd: float = 0.0


@dataclass
class UsageLedgerState:
    date: str
    total_requests: int = 0
    total_cost_usd: float = 0.0
    providers: Dict[str, ProviderUsage] = field(default_factory=dict)
    events: List[Dict] = field(default_factory=list)


class UsageLedger:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load_or_init()

    def _today(self) -> str:
        return datetime.now().date().isoformat()

    def _load_or_init(self) -> UsageLedgerState:
        if self.path.exists():
            with open(self.path) as f:
                raw = json.load(f)
            if raw.get("date") == self._today():
                providers = {
                    k: ProviderUsage(**v) for k, v in raw.get("providers", {}).items()
                }
                return UsageLedgerState(
                    date=raw.get("date", self._today()),
                    total_requests=raw.get("total_requests", 0),
                    total_cost_usd=raw.get("total_cost_usd", 0.0),
                    providers=providers,
                    events=raw.get("events", []),
                )
        return UsageLedgerState(date=self._today())

    def record(self, provider: str, model: str, est_cost_usd: float, event_id: str | None = None):
        if self.state.date != self._today():
            self.state = UsageLedgerState(date=self._today())
        if provider not in self.state.providers:
            self.state.providers[provider] = ProviderUsage()
        usage = self.state.providers[provider]
        usage.requests += 1
        usage.cost_usd += est_cost_usd
        self.state.total_requests += 1
        self.state.total_cost_usd += est_cost_usd
        self.state.events.append({
            "ts": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "cost_usd": est_cost_usd,
            "event_id": event_id,
        })
        self.state.events = self.state.events[-200:]
        self.save()

    def snapshot(self) -> Dict:
        return {
            "date": self.state.date,
            "total_requests": self.state.total_requests,
            "total_cost_usd": round(self.state.total_cost_usd, 6),
            "providers": {
                k: {"requests": v.requests, "cost_usd": round(v.cost_usd, 6)}
                for k, v in self.state.providers.items()
            },
            "events": list(self.state.events),
        }

    def save(self):
        payload = self.snapshot()
        with open(self.path, "w") as f:
            json.dump(payload, f, indent=2)
