#!/usr/bin/env python3
"""
Demo for v6.2 hybrid routing.
"""

from __future__ import annotations

import json

from minimax_adapter import MiniMaxAdapter
from model_adapter import HeuristicAdapter
from model_routing_policy import ModelRoutingPolicy
from real_qwen_adapter import RealQwenAdapter


def main():
    routing = ModelRoutingPolicy()
    local = RealQwenAdapter()
    external = MiniMaxAdapter()
    heuristic = HeuristicAdapter()

    scenarios = [
        {"name": "restricted privacy", "privacy": "restricted", "budget": "generous", "mode": "reflect", "urgency": "high"},
        {"name": "tight light", "privacy": "normal", "budget": "tight", "mode": "light", "urgency": "low"},
        {"name": "high value external", "privacy": "normal", "budget": "generous", "mode": "focused", "urgency": "high"},
        {"name": "default local", "privacy": "normal", "budget": "normal", "mode": "standard", "urgency": "normal"},
    ]

    results = []
    prompt = "Assess memory pressure, summarize recent beliefs, and decide if conscious wake is required."

    for s in scenarios:
        decision = routing.decide(
            privacy=s["privacy"],
            budget=s["budget"],
            mode=s["mode"],
            urgency=s["urgency"],
        )
        if decision.backend == "external":
            result = external.generate(prompt, s["mode"]).to_dict()
        elif decision.backend == "heuristic":
            result = heuristic.generate(prompt, s["mode"]).to_dict()
        else:
            result = local.generate(prompt, s["mode"]).to_dict()
        results.append({"scenario": s["name"], "route": decision.to_dict(), "result": result})

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
