#!/usr/bin/env python3
"""
v9.5 Comparative pack runner.
"""

from __future__ import annotations

from typing import Dict, List

from v6.model_adapter import HeuristicAdapter
from v6.real_qwen_adapter import RealQwenAdapter
from v6.minimax_adapter import MiniMaxAdapter, MiniMaxConfig
from v6.model_routing_policy import ModelRoutingPolicy
from v9.quality_compare import QualityComparison


class ComparativeRunner:
    def __init__(self):
        self.local = RealQwenAdapter()
        self.external = MiniMaxAdapter(MiniMaxConfig(enabled=True))
        self.heuristic = HeuristicAdapter()
        self.routing = ModelRoutingPolicy()
        self.quality = QualityComparison()

    def run(self, scenarios: List[Dict]) -> Dict:
        return {
            "local_only": self._run_variant("local", scenarios),
            "external_only": self._run_variant("external", scenarios),
            "hybrid": self._run_variant("hybrid", scenarios),
        }

    def _run_variant(self, variant: str, scenarios: List[Dict]) -> Dict:
        results = []
        for s in scenarios:
            if variant == "local":
                result = self._dispatch(self.local, s)
                route = {"backend": "local"}
            elif variant == "external":
                result = self._dispatch(self.external, s)
                route = {"backend": "external"}
            else:
                decision = self.routing.decide(
                    privacy=s.get("privacy", "normal"),
                    budget=s.get("budget", "normal"),
                    mode=s.get("mode", "standard"),
                    urgency=s.get("urgency", "normal"),
                )
                route = decision.to_dict()
                if decision.backend == "external":
                    result = self._dispatch(self.external, s)
                elif decision.backend == "heuristic":
                    result = None
                else:
                    result = self._dispatch(self.local, s)
            if result is None:
                results.append({
                    "scenario": s["name"],
                    "route": route,
                    "skipped_external": True,
                    "reason": "hybrid policy intentionally avoided expensive path",
                })
            else:
                results.append({
                    "scenario": s["name"],
                    "route": route,
                    "result": result.to_dict(),
                })
        quality_rows = self.quality.compare({"results": results})
        return {
            "results": results,
            "quality": self.quality.summary(quality_rows),
        }

    def _dispatch(self, adapter, scenario: Dict):
        operation = scenario.get("operation", "generate")
        content = scenario.get("content", "")
        mode = scenario.get("mode", "standard")
        if operation == "summary":
            return adapter.summarize(content)
        if operation == "reflect":
            return adapter.reflect(content)
        return adapter.generate(content, mode)
