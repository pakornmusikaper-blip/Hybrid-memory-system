"""
Substrate Agent CLI

Usage:
    python -m substrate run              # Start substrate in background
    python -m substrate serve <query>   # Serve a query to conscious layer
    python -m substrate status         # Show substrate status
    python -m substrate beliefs        # Show all beliefs
    python -m substrate stats          # Show statistics
"""

import sys
import argparse
from pathlib import Path

# Add v2 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from substrate.agent.core import SubstrateAgent


def main():
    parser = argparse.ArgumentParser(description="Substrate Agent CLI")
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
    
    args = parser.parse_args()
    
    # Find memory root
    memory_root = Path(__file__).parent.parent.parent.parent / "knowledge-system"
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
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
