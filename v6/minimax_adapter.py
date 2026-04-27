#!/usr/bin/env python3
"""
v6.2 MiniMax adapter scaffold.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict

from v6.model_adapter import ModelResult, HeuristicAdapter


@dataclass
class MiniMaxConfig:
    model_name: str = "MiniMax-M2.7"
    api_base: str = "https://api.minimax.io"
    api_key_env: str = "MINIMAX_API_KEY"
    enabled: bool = False


class MiniMaxAdapter:
    def __init__(self, config: MiniMaxConfig | None = None):
        self.config = config or MiniMaxConfig()
        self.model_name = self.config.model_name
        self.provider = "minimax-api"
        self._fallback = HeuristicAdapter()

    def _available(self) -> tuple[bool, str]:
        if not self.config.enabled:
            return False, "minimax disabled by config"
        if not os.getenv(self.config.api_key_env):
            return False, f"missing env {self.config.api_key_env}"
        return True, "ok"

    def _mock_api(self, prompt: str, mode: str) -> str:
        return f"[minimax:{mode}] generated external response for: {prompt[:120]}"

    def generate(self, prompt: str, mode: str = "standard") -> ModelResult:
        ok, reason = self._available()
        if not ok:
            result = self._fallback.generate(prompt, mode)
            result.reason = f"minimax unavailable: {reason}"
            return result
        try:
            text = self._mock_api(prompt, mode)
            return ModelResult(True, text, self.model_name, self.provider, mode)
        except Exception as e:
            result = self._fallback.generate(prompt, mode)
            result.reason = f"minimax generation failed: {e}"
            return result

    def summarize(self, text: str) -> ModelResult:
        return self.generate(f"Summarize compactly:\n\n{text}", "summary")

    def reflect(self, context: str) -> ModelResult:
        return self.generate(f"Reflect on this system state:\n\n{context}", "reflect")

    def health(self) -> Dict:
        ok, reason = self._available()
        return {
            "ok": ok,
            "provider": self.provider,
            "model": self.model_name,
            "reason": reason,
        }
