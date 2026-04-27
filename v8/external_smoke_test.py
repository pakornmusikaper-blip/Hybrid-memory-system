#!/usr/bin/env python3
"""
v8.2 External smoke test (safe scaffold).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v6.minimax_adapter import MiniMaxAdapter, MiniMaxConfig
from v8.external_activation_check import check_activation


def main():
    ledger_path = Path('/tmp/substrate_external_smoke/usage-ledger.json')
    ledger_path.parent.mkdir(parents=True, exist_ok=True)

    preflight = check_activation(ledger_path=ledger_path)
    adapter = MiniMaxAdapter(MiniMaxConfig(enabled=True))
    health = adapter.health()
    result = adapter.generate("Smoke test prompt for external model.", "focused").to_dict()

    print(json.dumps({
        "preflight": preflight,
        "adapter_health": health,
        "result": result,
        "api_key_present": bool(os.getenv('MINIMAX_API_KEY')),
    }, indent=2))


if __name__ == '__main__':
    main()
