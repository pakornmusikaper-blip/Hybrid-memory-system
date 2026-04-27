#!/usr/bin/env python3
"""
v8.2 External activation preflight.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v6.runtime_config import ExternalBudget, RuntimeConfig
from v6.usage_ledger import UsageLedger
from v6.configured_router import ConfiguredRouter


def check_activation(*, ledger_path: Path, api_env: str = "MINIMAX_API_KEY") -> dict:
    checks = []

    api_key_present = bool(os.getenv(api_env))
    checks.append({"name": "api_key_present", "ok": api_key_present, "detail": api_env})

    ledger_ok = True
    ledger_detail = str(ledger_path)
    try:
        ledger = UsageLedger(ledger_path)
        ledger.save()
    except Exception as e:
        ledger_ok = False
        ledger_detail = str(e)
    checks.append({"name": "ledger_writable", "ok": ledger_ok, "detail": ledger_detail})

    config = RuntimeConfig(
        local_enabled=True,
        external_enabled=True,
        external_api_key_env=api_env,
        budget=ExternalBudget(max_requests_per_day=10, max_cost_usd_per_day=1.0),
    )
    router = ConfiguredRouter(config)
    decision = router.decide(privacy="normal", budget="generous", mode="reflect", urgency="high")
    checks.append({"name": "router_allows_external", "ok": decision.backend == "external", "detail": decision.reason})

    budget_ok = config.budget.max_requests_per_day > 0 and config.budget.max_cost_usd_per_day > 0
    checks.append({"name": "budget_limits_present", "ok": budget_ok, "detail": config.budget.__dict__.copy()})

    ok = all(c["ok"] for c in checks)
    return {"ok": ok, "checks": checks}


if __name__ == "__main__":
    result = check_activation(ledger_path=Path("./usage-ledger.json"))
    print(json.dumps(result, indent=2))
