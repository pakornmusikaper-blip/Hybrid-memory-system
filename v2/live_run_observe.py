#!/usr/bin/env python3
"""
Short live-run observation harness for v2.8.
"""

import json
import shutil
import time
from pathlib import Path

import yaml

from substrate.agent.core import SubstrateAgent


def build_temp_env(root: Path):
    if root.exists():
        shutil.rmtree(root)
    (root / "structured" / "systems").mkdir(parents=True, exist_ok=True)
    (root / "wiki" / "systems").mkdir(parents=True, exist_ok=True)
    (root / "sources").mkdir(parents=True, exist_ok=True)

    with open(root / "structured" / "systems" / "memory.yaml", "w") as f:
        yaml.safe_dump(
            {
                "title": "Hybrid Memory System",
                "summary": "A layered memory architecture with substrate support.",
                "tags": ["memory", "substrate", "hybrid"],
                "category": "systems",
            },
            f,
            sort_keys=False,
        )

    with open(root / "wiki" / "systems" / "substrate.md", "w") as f:
        f.write("# Substrate\n\nSubstrate continuously prepares context in the background.\n")


def build_temp_config(path: Path):
    cfg = {
        "model": {
            "name": "Qwen/Qwen2-0.5B",
            "trust_remote_code": True,
            "quantization": "none",
        },
        "runtime": {
            "device": "cpu",
            "max_memory_gb": 2,
            "threads": 2,
            "generation_timeout_seconds": 5,
        },
        "operation": {
            "cycle_seconds": 1,
            "max_beliefs": 100,
            "confidence_decay_days": 30,
            "fallback_mode": True,
            "heuristic_fallback": True,
        },
        "growth": {"max_beliefs_per_cycle": 3, "connection_batch_size": 10, "validation_interval_hours": 6},
        "validation": {"strict_mode": False, "allow_corrections": True, "decay_factor": 0.9},
        "anticipation": {"max_cached": 10, "freshness_hours": 24, "prewarm_on_startup": False},
        "communication": {"response_timeout_seconds": 2, "max_context_tokens": 512, "max_generation_tokens": 128},
        "prompts": {
            "absorb": "Analyze: {context}",
            "weave": "Weave: {sources}",
            "belief": "Belief from context: {context} | related: {related} | example: {format_example}",
            "validate": "Validate: {belief} vs {facts}",
        },
    }
    with open(path, "w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)


def main():
    root = Path("/tmp/substrate_live_run")
    build_temp_env(root)
    config_path = root / "live_config.yaml"
    build_temp_config(config_path)

    agent = SubstrateAgent(root, config_path)
    agent.generate = lambda prompt, max_tokens=128: '{"statement": "Live observation created a belief", "confidence": 0.67, "subject": "live-run"}'

    agent.start()
    time.sleep(1.5)
    agent.absorb(
        {
            "source": "live_run_event",
            "content": "Observe how substrate behaves during a short live run.",
            "scenario": "live_run",
        }
    )
    time.sleep(1.5)
    agent.stop()

    beliefs = agent.get_beliefs()
    growth_logs = list((root / "v2" / "substrate" / "own_memory" / "growth_log").glob("*.jsonl"))
    bridge_stats = agent.bridge.get_bridge_stats()
    stats = agent.get_stats()

    result = {
        "belief_count": len(beliefs),
        "growth_logs": len(growth_logs),
        "cycles": stats.get("cycles", 0),
        "bridge_stats": bridge_stats,
        "last_belief": beliefs[-1]["statement"] if beliefs else None,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
