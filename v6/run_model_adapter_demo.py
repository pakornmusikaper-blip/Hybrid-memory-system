#!/usr/bin/env python3
"""
Demo for v6.0 Model Adapter Layer.
"""

from __future__ import annotations

import json

from model_adapter import AdapterRouter, HeuristicAdapter, MockQwenAdapter


class BrokenAdapter:
    def generate(self, prompt: str, mode: str = "standard"):
        raise RuntimeError("model offline")

    def summarize(self, text: str):
        raise RuntimeError("summary unavailable")

    def reflect(self, context: str):
        raise RuntimeError("reflection unavailable")

    def health(self):
        return {"ok": False, "provider": "broken", "model": "none"}


def main():
    qwen_router = AdapterRouter(primary=MockQwenAdapter(), fallback=HeuristicAdapter())
    broken_router = AdapterRouter(primary=BrokenAdapter(), fallback=HeuristicAdapter())

    prompt = "User asked the substrate to reflect on system health and summarize memory pressure."

    results = {
        "qwen_generate": qwen_router.generate(prompt, "focused").to_dict(),
        "qwen_summarize": qwen_router.summarize(prompt).to_dict(),
        "qwen_reflect": qwen_router.reflect(prompt).to_dict(),
        "qwen_health": qwen_router.health(),
        "broken_generate": broken_router.generate(prompt, "focused").to_dict(),
        "broken_summarize": broken_router.summarize(prompt).to_dict(),
        "broken_reflect": broken_router.reflect(prompt).to_dict(),
        "broken_health": broken_router.health(),
    }

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
