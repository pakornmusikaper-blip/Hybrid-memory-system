#!/usr/bin/env python3
"""
Deeper integration test against the real knowledge-system tree.
Uses heuristic / monkeypatched generation to avoid long CPU inference.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from substrate.agent.core import SubstrateAgent


def main():
    workspace = Path.home() / ".openclaw" / "workspace"
    memory_root = workspace / "knowledge-system"
    config_path = (
        workspace / "hybrid-memory-system" / "v2" / "substrate" / "config" / "default.yaml"
    )

    agent = SubstrateAgent(memory_root, config_path)
    agent.generate = (
        lambda prompt, max_tokens=256: '{"statement": "Knowledge system contains structured and wiki memory layers", "confidence": 0.74, "subject": "knowledge-system"}'
    )

    woven = agent.weave({"query": "memory system", "content": "memory system"})
    agent.absorb(
        {
            "source": "real_integration_test",
            "content": "The real knowledge-system contains structured and wiki directories used by substrate.",
            "scenario": "real_knowledge_system",
        }
    )

    beliefs = agent.get_beliefs(subject="knowledge-system")
    stats = agent.get_stats()

    result = {
        "structured_matches": len(woven.get("structured", [])),
        "wiki_matches": len(woven.get("wiki", [])),
        "beliefs_for_subject": len(beliefs),
        "beliefs_total": stats.get("belief_count", 0),
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
