#!/usr/bin/env python3
"""
Demo for v8.5 config loader.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v8.config_loader import RuntimeConfigLoader
from v6.configured_router import ConfiguredRouter


def main():
    root = Path('/tmp/v8_config_loader_demo')
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    config_path = root / 'runtime-config.json'
    config_path.write_text(json.dumps({
        "local_enabled": True,
        "external_enabled": True,
        "local_model_name": "Qwen/Qwen2.5-0.5B-Instruct",
        "external_model_name": "MiniMax-M2.7",
        "external_api_key_env": "MINIMAX_API_KEY",
        "privacy_default": "normal",
        "budget": {
            "max_requests_per_day": 3,
            "max_cost_usd_per_day": 0.002,
            "used_requests_today": 1,
            "used_cost_usd_today": 0.0008
        }
    }, indent=2))

    loader = RuntimeConfigLoader(config_path)
    config = loader.load()
    router = ConfiguredRouter(config)
    route = router.decide(privacy='normal', budget='generous', mode='reflect', urgency='high')

    print(json.dumps({
        'config': config.to_dict(),
        'route': route.to_dict(),
        'config_path': str(config_path),
    }, indent=2))


if __name__ == '__main__':
    main()
