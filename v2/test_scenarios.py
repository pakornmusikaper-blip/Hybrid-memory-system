#!/usr/bin/env python3
"""
Scenario tests for Substrate Agent v2.5 hardening.
"""

import json
import shutil
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))

from substrate.agent.core import SubstrateAgent


def make_test_root(name: str) -> Path:
    root = Path(f"/tmp/{name}")
    if root.exists():
        shutil.rmtree(root)
    (root / "structured" / "people").mkdir(parents=True, exist_ok=True)
    (root / "wiki" / "systems").mkdir(parents=True, exist_ok=True)
    (root / "sources").mkdir(parents=True, exist_ok=True)
    return root


def write_fixture(root: Path):
    with open(root / "structured" / "people" / "pakorn.yaml", "w") as f:
        yaml.safe_dump(
            {
                "title": "Pakorn Musikaper",
                "summary": "Pakorn is building an autonomous hybrid memory system.",
                "tags": ["pakorn", "memory", "substrate"],
                "category": "people",
            },
            f,
            sort_keys=False,
        )
    with open(root / "wiki" / "systems" / "substrate.md", "w") as f:
        f.write("# Substrate\n\nSubstrate is the subconscious layer of the memory system.\n")


def write_config(root: Path) -> Path:
    config_dir = root / "local_config"
    config_dir.mkdir(parents=True, exist_ok=True)
    cfg = {
        "model": {
            "name": "Qwen/Qwen2-0.5B",
            "trust_remote_code": True,
            "quantization": "none",
        },
        "runtime": {"device": "cpu", "max_memory_gb": 2, "threads": 2},
        "operation": {
            "cycle_seconds": 1,
            "max_beliefs": 100,
            "confidence_decay_days": 30,
            "fallback_mode": True,
        },
        "growth": {"max_beliefs_per_cycle": 3, "connection_batch_size": 10},
        "validation": {"strict_mode": False, "allow_corrections": True, "decay_factor": 0.9},
        "anticipation": {"max_cached": 10, "freshness_hours": 24, "prewarm_on_startup": False},
        "communication": {"response_timeout_seconds": 2, "max_context_tokens": 512},
        "prompts": {
            "absorb": "Analyze: {context}",
            "weave": "Weave: {sources}",
            "belief": "Belief from context: {context} | related: {related}",
            "validate": "Validate: {belief} vs {facts}",
        },
    }
    path = config_dir / "default.yaml"
    with open(path, "w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)
    return path


def scenario_absorb_and_belief():
    root = make_test_root("substrate_scenario_absorb")
    write_fixture(root)
    cfg = write_config(root)
    agent = SubstrateAgent(root, cfg)

    # monkeypatch generate to avoid heavy inference during scenario hardening
    agent.generate = lambda prompt, max_tokens=256: '{"statement": "Pakorn prefers a living memory system", "confidence": 0.82, "reasoning": "derived from context"}'

    agent.absorb(
        {
            "source": "scenario_absorb",
            "content": "Pakorn wants a living memory system with subconscious processing.",
            "scenario": "living_memory",
        }
    )

    beliefs = agent.get_beliefs()
    assert len(beliefs) >= 1, "No beliefs created after absorb"
    return {"belief_count": len(beliefs), "first_belief": beliefs[0].get("statement", "")}


def scenario_bridge_query_response():
    root = make_test_root("substrate_scenario_bridge")
    write_fixture(root)
    cfg = write_config(root)
    agent = SubstrateAgent(root, cfg)

    query_id = agent.bridge.send_query("What is substrate?", {"source": "scenario"})
    agent.bridge.send_response(query_id, {"content": "Substrate is the subconscious layer."}, 0.91)

    inbox = agent.bridge.get_inbox(limit=5)
    pending = agent.bridge.get_pending_queries()
    assert len(inbox) >= 1, "No inbox response created"
    assert any(q["id"] == query_id for q in pending), "Expected pending query not found"
    return {"inbox_count": len(inbox), "pending_queries": len(pending)}


def scenario_contradiction_detection():
    root = make_test_root("substrate_scenario_contradiction")
    write_fixture(root)
    cfg = write_config(root)
    agent = SubstrateAgent(root, cfg)

    belief_a = {
        "id": "belief-a",
        "statement": "Pakorn is not building a memory system",
        "confidence": 0.7,
        "subject": "pakorn",
        "evidence": [{"source": "test", "strength": 0.8}],
        "created": "2026-04-27T00:00:00",
        "status": "active",
    }
    belief_b = {
        "id": "belief-b",
        "statement": "Pakorn is building a memory system",
        "confidence": 0.8,
        "subject": "pakorn",
        "evidence": [{"source": "test", "strength": 0.8}],
        "created": "2026-04-27T00:00:00",
        "status": "active",
    }
    agent._save_belief(belief_a)
    agent._save_belief(belief_b)

    contradictions = agent.growth.detect_contradictions()
    assert len(contradictions) >= 1, "Contradiction not detected"
    return {"contradictions": len(contradictions)}


def scenario_short_background_loop():
    root = make_test_root("substrate_scenario_loop")
    write_fixture(root)
    cfg = write_config(root)
    agent = SubstrateAgent(root, cfg)
    agent.generate = lambda prompt, max_tokens=256: '{"statement": "Background loop observation", "confidence": 0.6}'

    agent.start()
    time.sleep(2.5)
    agent.stop()

    stats = agent.get_stats()
    growth_logs = list((root / "v2" / "substrate" / "own_memory" / "growth_log").glob("*.jsonl"))
    assert stats["cycles"] >= 1, "Background loop did not cycle"
    assert len(growth_logs) >= 1, "No growth logs written"
    return {"cycles": stats["cycles"], "growth_logs": len(growth_logs)}


def main():
    results = {
        "absorb": scenario_absorb_and_belief(),
        "bridge": scenario_bridge_query_response(),
        "contradiction": scenario_contradiction_detection(),
        "background_loop": scenario_short_background_loop(),
    }
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
