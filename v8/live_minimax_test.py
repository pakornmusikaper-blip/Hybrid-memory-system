#!/usr/bin/env python3
"""
v8.3 Controlled live test pack for MiniMax path.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v6.minimax_adapter import MiniMaxAdapter, MiniMaxConfig
from v6.configured_router import ConfiguredRouter
from v6.runtime_config import RuntimeConfig, ExternalBudget
from v6.usage_ledger import UsageLedger
from v6.usage_report import UsageReport


def estimate_cost(mode: str) -> float:
    return {
        "summary": 0.0004,
        "reflect": 0.0010,
        "light": 0.0002,
        "focused": 0.0008,
        "standard": 0.0005,
    }.get(mode, 0.0005)


def main():
    root = Path('/tmp/v8_live_minimax_test')
    root.mkdir(parents=True, exist_ok=True)
    ledger = UsageLedger(root / 'usage-ledger.json')

    config = RuntimeConfig(
        local_enabled=True,
        external_enabled=True,
        budget=ExternalBudget(max_requests_per_day=5, max_cost_usd_per_day=0.005),
    )
    router = ConfiguredRouter(config)
    adapter = MiniMaxAdapter(MiniMaxConfig(enabled=True))

    scenarios = [
        {
            "name": "summary",
            "privacy": "normal",
            "budget": "generous",
            "mode": "summary",
            "urgency": "high",
            "content": "Summarize recent memory pressure, queue state, and operator alerts.",
            "operation": "summary",
            "event_id": "live-summary-1",
        },
        {
            "name": "reflection",
            "privacy": "normal",
            "budget": "generous",
            "mode": "reflect",
            "urgency": "high",
            "content": "Reflect on belief drift, concept coherence, and whether conscious wake should trigger.",
            "operation": "reflect",
            "event_id": "live-reflect-1",
        },
        {
            "name": "low-value",
            "privacy": "normal",
            "budget": "tight",
            "mode": "light",
            "urgency": "low",
            "content": "Routine cleanup note.",
            "operation": "generate",
            "event_id": "live-low-1",
        },
    ]

    before = ledger.snapshot()
    results = []
    for s in scenarios:
        route = router.decide(privacy=s['privacy'], budget=s['budget'], mode=s['mode'], urgency=s['urgency'])
        if s['name'] == 'low-value':
            results.append({
                'scenario': s['name'],
                'route': route.to_dict(),
                'skipped_external': True,
                'reason': 'low-value comparison should avoid expensive external usage',
            })
            continue

        if route.backend == 'external' and route.allowed:
            if s['operation'] == 'summary':
                result = adapter.summarize(s['content'])
            elif s['operation'] == 'reflect':
                result = adapter.reflect(s['content'])
            else:
                result = adapter.generate(s['content'], s['mode'])
            if result.provider == 'minimax-api' and not result.fallback:
                router.record_external_use(route.estimated_cost_usd)
                ledger.record(result.provider, result.model, route.estimated_cost_usd, s['event_id'])
            results.append({
                'scenario': s['name'],
                'route': route.to_dict(),
                'result': result.to_dict(),
            })
        else:
            results.append({
                'scenario': s['name'],
                'route': route.to_dict(),
                'skipped_external': True,
                'reason': 'route not external or budget blocked',
            })

    after = ledger.snapshot()
    report = UsageReport(ledger, config)

    print(json.dumps({
        'before': before,
        'results': results,
        'after': after,
        'report': report.build(),
        'report_text': report.render_text(),
    }, indent=2))


if __name__ == '__main__':
    main()
