"""
Substrate Agent CLI v2.3

Usage:
    python -m substrate run              # Start substrate in background
    python -m substrate serve <query>   # Serve a query to conscious layer
    python -m substrate status          # Show substrate status
    python -m substrate beliefs        # Show all beliefs
    python -m substrate stats          # Show statistics
    python -m substrate validate       # Run belief validation
    python -m substrate patterns       # Show recognized patterns
    python -m substrate growth         # Show growth summary
    python -m substrate contradictions # Show belief contradictions
    python -m substrate intuitions    # Show pending intuitions (v2.2)
    python -m substrate bridge         # Show bridge statistics (v2.2)
    python -m substrate gpu            # Show GPU info (v2.3)
"""

import sys
import argparse
from pathlib import Path

# Add v2 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from substrate.agent.core import SubstrateAgent


def main():
    parser = argparse.ArgumentParser(description="Substrate Agent CLI v2.3")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Start substrate agent")
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Serve a query")
    serve_parser.add_argument("query", help="Query to serve")
    
    # Status command
    subparsers.add_parser("status", help="Show substrate status")
    
    # Beliefs command
    beliefs_parser = subparsers.add_parser("beliefs", help="Show all beliefs")
    beliefs_parser.add_argument("--subject", help="Filter by subject")
    
    # Stats command
    subparsers.add_parser("stats", help="Show statistics")
    
    # Growth command (v2.1)
    subparsers.add_parser("growth", help="Show growth summary")
    
    # Validate command (v2.1)
    validate_parser = subparsers.add_parser("validate", help="Run belief validation")
    validate_parser.add_argument("--days", type=int, default=30, help="Validate beliefs older than N days")
    
    # Patterns command (v2.1)
    patterns_parser = subparsers.add_parser("patterns", help="Show recognized patterns")
    patterns_parser.add_argument("--min", type=int, default=3, help="Minimum occurrences")
    
    # Contradictions command (v2.1)
    subparsers.add_parser("contradictions", help="Show belief contradictions")

    # Intuitions command (v2.2)
    subparsers.add_parser("intuitions", help="Show pending intuitions")

    # Bridge command (v2.2)
    subparsers.add_parser("bridge", help="Show bridge statistics")

    # GPU command (v2.3)
    subparsers.add_parser("gpu", help="Show GPU info")
    
    args = parser.parse_args()
    
    # Find memory root
    memory_root = Path(__file__).parent.parent.parent / "knowledge-system"
    if not memory_root.exists():
        memory_root = Path.home() / ".openclaw" / "workspace" / "knowledge-system"
    
    print(f"[Substrate] Memory root: {memory_root}")
    
    # Initialize agent
    agent = SubstrateAgent(memory_root)
    
    if args.command == "run":
        print("[Substrate] Starting in background mode...")
        print("[Substrate] Press Ctrl+C to stop")
        try:
            agent.start()
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            agent.stop()
            
    elif args.command == "serve":
        if not args.query:
            print("Error: query required")
            sys.exit(1)
        result = agent.serve(args.query)
        print(f"\nSource: {result['source']}")
        print(f"Confidence: {result['confidence']}")
        print(f"\nData: {result['data']}")
        
    elif args.command == "status":
        stats = agent.get_stats()
        print("\n=== Substrate Agent Status ===")
        print(f"Running: {stats['running']}")
        print(f"Last cycle: {stats['last_cycle']}")
        print(f"Total cycles: {stats['cycles']}")
        print(f"Beliefs formed: {stats['beliefs_formed']}")
        print(f"Belief count: {stats['belief_count']}")
        print(f"Connections forged: {stats['connections_forged']}")
        print(f"Anticipations prepared: {stats['anticipations_prepared']}")
        print(f"Validations done: {stats.get('validations_done', 0)}")
        print(f"Patterns found: {stats.get('patterns_found', 0)}")
        
    elif args.command == "beliefs":
        beliefs = agent.get_beliefs(subject=args.subject)
        print(f"\n=== Beliefs ({len(beliefs)}) ===")
        for b in beliefs:
            print(f"\n[{b['id']}] {b.get('statement', '')[:100]}")
            print(f"   Confidence: {b.get('confidence', 0):.2f} | Status: {b.get('status', 'unknown')}")
            print(f"   Subject: {b.get('subject', 'unknown')}")
        
    elif args.command == "stats":
        stats = agent.get_stats()
        print("\n=== Statistics ===")
        for key, value in stats.items():
            print(f"{key}: {value}")
    
    # v2.1 commands
    elif args.command == "growth":
        summary = agent.growth.get_growth_summary()
        print("\n=== Growth Summary ===")
        print(f"Total beliefs: {summary['total_beliefs']}")
        print(f"Active beliefs: {summary['active_beliefs']}")
        print(f"Decaying beliefs: {summary['decaying_beliefs']}")
        print(f"Contradicted beliefs: {summary['contradicted_beliefs']}")
        print(f"Average confidence: {summary['avg_confidence']:.3f}")
        print(f"Total growth entries: {summary['total_growth_entries']}")
        print(f"Pattern files: {summary['patterns_identified']}")
        
    elif args.command == "validate":
        print(f"\n=== Validating beliefs older than {args.days} days ===")
        validated = agent.growth.validate_all_stale(days=args.days)
        print(f"Validated {len(validated)} beliefs")
        agent.stats["validations_done"] = agent.stats.get("validations_done", 0) + len(validated)
        
    elif args.command == "patterns":
        print(f"\n=== Recognizing patterns (min {args.min} occurrences) ===")
        patterns = agent.growth.recognize_patterns(min_occurrences=args.min)
        print(f"Found {len(patterns)} patterns:")
        for p in patterns:
            print(f"\n[{p['id']}] {p['type']}: {p['subject']}")
            print(f"   Beliefs: {p['belief_count']} | Avg confidence: {p['avg_confidence']:.2f}")
        agent.stats["patterns_found"] = agent.stats.get("patterns_found", 0) + len(patterns)
        
    elif args.command == "contradictions":
        print("\n=== Detecting belief contradictions ===")
        contradictions = agent.growth.detect_contradictions()
        if contradictions:
            print(f"Found {len(contradictions)} contradictions:")
            for c in contradictions:
                print(f"\n[{c['belief1']}] <> [{c['belief2']}]")
                print(f"   1: {c['statement1']}...")
                print(f"   2: {c['statement2']}...")
        else:
            print("No contradictions found!")
        
    elif args.command == "intuitions":
        print("\n=== Pending Intuitions ===")
        intuitions = agent.bridge.get_pending_intuitions()
        if intuitions:
            print(f"Found {len(intuitions)} pending intuitions:")
            for i in intuitions:
                print(f"\n[{i['id']}] [{i.get('priority', 'normal')}] {i.get('title', 'Untitled')}")
                print(f"   {i.get('description', '')}")
        else:
            print("No pending intuitions!")
        
    elif args.command == "bridge":
        print("\n=== Consciousness Bridge Statistics ===")
        stats = agent.bridge.get_bridge_stats()
        print(f"Inbox messages: {stats['inbox_count']}")
        print(f"Outbox messages: {stats['outbox_count']}")
        print(f"Total intuitions: {stats['total_intuitions']}")
        print(f"Pending intuitions: {stats['pending_intuitions']}")
        print(f"Pending queries: {stats['pending_queries']}")
        
    elif args.command == "gpu":
        print("\n=== GPU Information ===")
        from substrate.agent.gpu import GPUManager
        gpu_manager = GPUManager(agent.config)
        gpu_info = gpu_manager.get_gpu_info()
        print(f"CUDA Available: {gpu_info['cuda_available']}")
        print(f"Device Count: {gpu_info['device_count']}")
        if gpu_info['devices']:
            for device in gpu_info['devices']:
                print(f"\nDevice {device['id']}: {device['name']}")
                print(f"  Memory: {device['total_memory_gb']:.1f}GB")
                print(f"  Compute: {device['compute_capability']}")
        
        # Estimate model memory
        model_name = agent.config['model']['name']
        quant = agent.config['model'].get('quantization', 'none')
        est = gpu_manager.estimate_model_memory(model_name, quant)
        print(f"\nEstimated memory for {model_name} ({quant}): {est:.1f}GB")
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
