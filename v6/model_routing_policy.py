#!/usr/bin/env python3
"""
v6.2 Hybrid model routing policy.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class RouteDecision:
    backend: str
    reason: str
    allow_external: bool
    prefer_fallback: bool

    def to_dict(self) -> Dict:
        return asdict(self)


class ModelRoutingPolicy:
    def decide(
        self,
        *,
        privacy: str = "normal",
        budget: str = "normal",
        mode: str = "standard",
        urgency: str = "normal",
    ) -> RouteDecision:
        if privacy == "restricted":
            return RouteDecision("local", "restricted privacy keeps data local", False, False)

        if budget == "tight":
            if mode == "light":
                return RouteDecision("heuristic", "tight budget with light mode uses heuristic", False, True)
            return RouteDecision("local", "tight budget prefers local model", False, False)

        if mode in {"reflect", "focused"} and urgency in {"high", "immediate"} and budget == "generous":
            return RouteDecision("external", "high-value deep cognition justifies external model", True, False)

        if mode == "summary" and budget == "generous":
            return RouteDecision("external", "generous budget allows higher-quality summary", True, False)

        return RouteDecision("local", "default route prefers local model", False, False)
