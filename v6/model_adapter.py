#!/usr/bin/env python3
"""
v6.0 Model Adapter Layer.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Protocol


@dataclass
class ModelResult:
    ok: bool
    text: str
    model: str
    provider: str
    mode: str
    fallback: bool = False
    reason: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


class ModelAdapter(Protocol):
    def generate(self, prompt: str, mode: str = "standard") -> ModelResult: ...
    def summarize(self, text: str) -> ModelResult: ...
    def reflect(self, context: str) -> ModelResult: ...
    def health(self) -> Dict: ...


class HeuristicAdapter:
    def __init__(self):
        self.model_name = "heuristic"
        self.provider = "local"

    def generate(self, prompt: str, mode: str = "standard") -> ModelResult:
        short = prompt[:160].strip().replace("\n", " ")
        return ModelResult(
            ok=True,
            text=f"[heuristic:{mode}] {short}",
            model=self.model_name,
            provider=self.provider,
            mode=mode,
            fallback=True,
            reason="heuristic fallback path",
        )

    def summarize(self, text: str) -> ModelResult:
        summary = text[:120].strip().replace("\n", " ")
        return ModelResult(
            ok=True,
            text=f"summary: {summary}",
            model=self.model_name,
            provider=self.provider,
            mode="summary",
            fallback=True,
            reason="heuristic summarization",
        )

    def reflect(self, context: str) -> ModelResult:
        snippet = context[:140].strip().replace("\n", " ")
        return ModelResult(
            ok=True,
            text=f"reflection: observed state -> {snippet}",
            model=self.model_name,
            provider=self.provider,
            mode="reflect",
            fallback=True,
            reason="heuristic reflection",
        )

    def health(self) -> Dict:
        return {"ok": True, "provider": self.provider, "model": self.model_name}


class MockQwenAdapter:
    def __init__(self, model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"):
        self.model_name = model_name
        self.provider = "local-transformers"

    def generate(self, prompt: str, mode: str = "standard") -> ModelResult:
        return ModelResult(
            ok=True,
            text=f"[qwen:{mode}] generated response for: {prompt[:100]}",
            model=self.model_name,
            provider=self.provider,
            mode=mode,
        )

    def summarize(self, text: str) -> ModelResult:
        return ModelResult(
            ok=True,
            text=f"[qwen:summary] {text[:80]}",
            model=self.model_name,
            provider=self.provider,
            mode="summary",
        )

    def reflect(self, context: str) -> ModelResult:
        return ModelResult(
            ok=True,
            text=f"[qwen:reflect] reflection on {context[:90]}",
            model=self.model_name,
            provider=self.provider,
            mode="reflect",
        )

    def health(self) -> Dict:
        return {"ok": True, "provider": self.provider, "model": self.model_name}


class AdapterRouter:
    def __init__(self, primary: ModelAdapter, fallback: ModelAdapter | None = None):
        self.primary = primary
        self.fallback = fallback or HeuristicAdapter()

    def generate(self, prompt: str, mode: str = "standard") -> ModelResult:
        try:
            result = self.primary.generate(prompt, mode)
            if result.ok:
                return result
        except Exception as e:
            return self.fallback.generate(f"primary failed: {e}; prompt={prompt}", mode)
        return self.fallback.generate(prompt, mode)

    def summarize(self, text: str) -> ModelResult:
        try:
            result = self.primary.summarize(text)
            if result.ok:
                return result
        except Exception as e:
            return self.fallback.summarize(f"primary failed: {e}; text={text}")
        return self.fallback.summarize(text)

    def reflect(self, context: str) -> ModelResult:
        try:
            result = self.primary.reflect(context)
            if result.ok:
                return result
        except Exception as e:
            return self.fallback.reflect(f"primary failed: {e}; context={context}")
        return self.fallback.reflect(context)

    def health(self) -> Dict:
        primary_health = self.primary.health()
        fallback_health = self.fallback.health()
        return {"primary": primary_health, "fallback": fallback_health}
