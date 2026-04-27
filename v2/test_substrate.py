#!/usr/bin/env python3
"""
Substrate Agent Test Script

Tests the substrate agent without downloading the full model.
Uses a simple mock to verify the architecture works.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add v2 to path
sys.path.insert(0, str(Path(__file__).parent / "v2"))

from substrate.agent.core import SubstrateAgent


def test_memory_operations():
    """Test basic memory operations."""
    print("\n=== Testing Memory Operations ===")

    # Create a test memory root
    test_root = Path("/tmp/substrate_test")
    test_root.mkdir(exist_ok=True)

    # Create minimal config
    config_dir = test_root / "config"
    config_dir.mkdir(exist_ok=True)

    config = {
        "model": {"name": "Qwen/Qwen2-1.5B", "trust_remote_code": True, "quantization": "none"},
        "runtime": {"device": "cpu", "max_memory_gb": 4, "threads": 2},
        "operation": {"cycle_seconds": 60, "max_beliefs": 100, "confidence_decay_days": 30},
        "growth": {"max_beliefs_per_cycle": 3, "connection_batch_size": 10},
        "validation": {"strict_mode": False, "allow_corrections": True, "decay_factor": 0.9},
        "anticipation": {"max_cached": 10, "freshness_hours": 1, "prewarm_on_startup": False},
        "prompts": {
            "absorb": "Analyze: {context}",
            "weave": "Weave: {sources}",
            "belief": "Form belief from: {context}",
            "validate": "Validate: {belief} vs {facts}",
        },
    }

    import yaml

    with open(config_dir / "default.yaml", "w") as f:
        yaml.dump(config, f)

    # Create substrate directories
    substrate_dir = test_root / "substrate" / "own_memory"
    for d in ["beliefs", "patterns", "anticipation_cache", "growth_log"]:
        (substrate_dir / d).mkdir(parents=True, exist_ok=True)

    # Initialize agent with test config
    agent = SubstrateAgent(test_root, config_dir / "default.yaml")

    # Test 1: Form a belief manually
    print("\n1. Testing belief formation...")
    belief = {
        "id": "test001",
        "statement": "Test belief about user preferences",
        "confidence": 0.7,
        "subject": "preferences",
        "evidence": [{"source": "test", "strength": 0.8}],
        "status": "active",
    }
    agent._save_belief(belief)
    print(f"   Saved belief: {belief['id']}")

    # Test 2: Retrieve beliefs
    print("\n2. Testing belief retrieval...")
    beliefs = agent._get_all_beliefs()
    print(f"   Found {len(beliefs)} beliefs")

    # Test 3: Link beliefs
    print("\n3. Testing belief linking...")
    belief2 = {
        "id": "test002",
        "statement": "Another test belief",
        "confidence": 0.6,
        "subject": "preferences",
        "evidence": [{"source": "test", "strength": 0.7}],
        "status": "active",
    }
    agent._save_belief(belief2)
    agent._link_beliefs("test001", "test002")
    print("   Linked test001 and test002")

    # Test 4: Anticipation cache
    print("\n4. Testing anticipation cache...")
    anticipation = {
        "id": "ant001",
        "scenario": "test_scenario",
        "context_bundle": {"summary": "Test anticipation"},
        "created": datetime.now().isoformat(),
        "freshness_hours": 1,
    }
    agent._save_anticipation(anticipation)
    cached = agent._get_cached_anticipation("test_scenario")
    print(f"   Cached and retrieved: {cached is not None}")

    # Test 5: Stats
    print("\n5. Testing statistics...")
    stats = agent.get_stats()
    print(f"   Stats: {stats}")

    # Cleanup
    import shutil

    shutil.rmtree(test_root)
    print("\n✓ All memory operations passed!")


def test_agent_initialization():
    """Test agent initialization without loading model."""
    print("\n=== Testing Agent Initialization ===")

    test_root = Path("/tmp/substrate_init_test")
    test_root.mkdir(exist_ok=True)

    # Create config
    config_dir = test_root / "config"
    config_dir.mkdir(exist_ok=True)

    config = {
        "model": {"name": "Qwen/Qwen2-1.5B"},
        "runtime": {"device": "cpu"},
        "operation": {"cycle_seconds": 60},
        "anticipation": {"freshness_hours": 24},
        "prompts": {
            "absorb": "Analyze: {context}",
            "weave": "Weave: {sources}",
            "belief": "Believe: {context}",
            "validate": "Validate: {belief}",
        },
    }

    import yaml

    with open(config_dir / "default.yaml", "w") as f:
        yaml.dump(config, f)

    # Create own_memory dirs
    (test_root / "substrate" / "own_memory" / "beliefs").mkdir(parents=True, exist_ok=True)

    agent = SubstrateAgent(test_root, config_dir / "default.yaml")

    print(f"   Agent initialized")
    print(f"   Config loaded: {agent.config['model']['name']}")
    print(f"   Beliefs dir: {agent.beliefs_dir}")
    print(f"   Model not loaded yet (lazy)")

    import shutil

    shutil.rmtree(test_root)

    print("\n✓ Agent initialization passed!")


def main():
    print("=" * 50)
    print("Substrate Agent Test Suite")
    print("=" * 50)

    # Run tests
    try:
        test_agent_initialization()
        test_memory_operations()

        print("\n" + "=" * 50)
        print("✓ All tests passed!")
        print("=" * 50)

        print("\nNext steps:")
        print("1. Download Qwen model:")
        print("   huggingface-cli download Qwen/Qwen2-1.5B")
        print("2. Start substrate agent:")
        print("   python -m substrate run")
        print("3. Query substrate:")
        print("   python -m substrate serve 'context about Project X'")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
