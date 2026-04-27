#!/usr/bin/env python3
"""
v6.4 Benchmark Matrix for local/external/hybrid modes.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List

from model_adapter import HeuristicAdapter
from real_qwen_adapter import RealQwenAdapter
from minimax_adapter import MiniMaxAdapter, MiniMaxConfig
from model_routing_policy import ModelRoutingPolicy


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


@dataclass
class BenchmarkRow:
    scenario: str
    execution_mode: str
    route: str
    model: str
    provider: str
    fallback: bool
    est_input_tokens: int
    est_output_tokens: int
    est_total_tokens: int
    est_cost_usd: float
    latency_class: str
    notes: str

    def to_dict(self) -> Dict:
        return asdict(self)


class BenchmarkMatrix:
    def __init__(self):
        self.local = RealQwenAdapter()
        self.external = MiniMaxAdapter(MiniMaxConfig(enabled=False))
        self.heuristic = HeuristicAdapter()
        self.routing = ModelRoutingPolicy()

    def run(self, scenarios: List[Dict]) -> List[BenchmarkRow]:
        rows: List[BenchmarkRow] = []
        for scenario in scenarios:
            rows.extend([
                self._run_local_only(scenario),
                self._run_external_only(scenario),
                self._run_hybrid(scenario),
            ])
        return rows

    def _run_local_only(self, s: Dict) -> BenchmarkRow:
        result = self._dispatch(self.local, s)
        return self._row_from_result(s["name"], "local-only", "local", result)

    def _run_external_only(self, s: Dict) -> BenchmarkRow:
        result = self._dispatch(self.external, s)
        return self._row_from_result(s["name"], "external-only", "external", result)

    def _run_hybrid(self, s: Dict) -> BenchmarkRow:
        decision = self.routing.decide(
            privacy=s.get("privacy", "normal"),
            budget=s.get("budget", "normal"),
            mode=s.get("mode", "standard"),
            urgency=s.get("urgency", "normal"),
        )
        if decision.backend == "external":
            result = self._dispatch(self.external, s)
        elif decision.backend == "heuristic":
            result = self._dispatch(self.heuristic, s)
        else:
            result = self._dispatch(self.local, s)
        row = self._row_from_result(s["name"], "hybrid-routed", decision.backend, result)
        row.notes = f"{decision.reason}; {row.notes}".strip("; ")
        return row

    def _dispatch(self, adapter, s: Dict):
        operation = s.get("operation", "generate")
        payload = s.get("content", "")
        mode = s.get("mode", "standard")
        if operation == "summary":
            return adapter.summarize(payload)
        if operation == "reflect":
            return adapter.reflect(payload)
        return adapter.generate(payload, mode)

    def _row_from_result(self, scenario: str, execution_mode: str, route: str, result) -> BenchmarkRow:
        input_tokens = estimate_tokens(result.reason if result.fallback and result.reason else result.text)
        output_tokens = estimate_tokens(result.text)
        total = input_tokens + output_tokens
        cost = self._estimate_cost(result.provider, total)
        latency = self._latency_class(result.provider, result.fallback)
        notes = result.reason or "primary path"
        return BenchmarkRow(
            scenario=scenario,
            execution_mode=execution_mode,
            route=route,
            model=result.model,
            provider=result.provider,
            fallback=result.fallback,
            est_input_tokens=input_tokens,
            est_output_tokens=output_tokens,
            est_total_tokens=total,
            est_cost_usd=cost,
            latency_class=latency,
            notes=notes,
        )

    def _estimate_cost(self, provider: str, total_tokens: int) -> float:
        if provider == "minimax-api":
            return round(total_tokens * 0.000002, 6)
        if provider == "local-transformers":
            return 0.0
        return 0.0

    def _latency_class(self, provider: str, fallback: bool) -> str:
        if fallback:
            return "very-low"
        if provider == "minimax-api":
            return "network-medium"
        if provider == "local-transformers":
            return "local-medium"
        return "very-low"
