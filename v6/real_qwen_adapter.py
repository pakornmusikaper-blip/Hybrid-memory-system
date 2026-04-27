#!/usr/bin/env python3
"""
v6.1 Real Qwen Adapter with lazy transformers import and safe fallback.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from v6.model_adapter import ModelResult, HeuristicAdapter


@dataclass
class QwenConfig:
    model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"
    device: str = "cpu"
    load_in_4bit: bool = True
    trust_remote_code: bool = True
    enable_model_load: bool = False


class RealQwenAdapter:
    def __init__(self, config: QwenConfig | None = None):
        self.config = config or QwenConfig()
        self.model_name = self.config.model_name
        self.provider = "local-transformers"
        self._pipeline = None
        self._load_error = None
        self._fallback = HeuristicAdapter()

    def _mode_params(self, mode: str) -> Dict:
        table = {
            "light": {"max_new_tokens": 48, "temperature": 0.7},
            "standard": {"max_new_tokens": 96, "temperature": 0.6},
            "focused": {"max_new_tokens": 160, "temperature": 0.4},
            "reflect": {"max_new_tokens": 120, "temperature": 0.3},
            "summary": {"max_new_tokens": 80, "temperature": 0.4},
        }
        return table.get(mode, table["standard"])

    def _ensure_pipeline(self):
        if self._pipeline is not None or self._load_error is not None:
            return
        if not self.config.enable_model_load:
            self._load_error = "model loading disabled by config"
            return
        try:
            from transformers import pipeline

            self._pipeline = pipeline(
                "text-generation",
                model=self.config.model_name,
                device_map="auto" if self.config.device != "cpu" else None,
            )
        except Exception as e:
            self._load_error = str(e)

    def _run(self, prompt: str, mode: str) -> ModelResult:
        self._ensure_pipeline()
        if self._pipeline is None:
            result = self._fallback.generate(prompt, mode)
            result.reason = f"qwen unavailable: {self._load_error}"
            return result
        try:
            params = self._mode_params(mode)
            output = self._pipeline(prompt, **params)
            if isinstance(output, list) and output:
                text = output[0].get("generated_text", "")
            else:
                text = str(output)
            return ModelResult(
                ok=True,
                text=text,
                model=self.model_name,
                provider=self.provider,
                mode=mode,
                fallback=False,
            )
        except Exception as e:
            result = self._fallback.generate(prompt, mode)
            result.reason = f"qwen generation failed: {e}"
            return result

    def generate(self, prompt: str, mode: str = "standard") -> ModelResult:
        return self._run(prompt, mode)

    def summarize(self, text: str) -> ModelResult:
        prompt = f"Summarize this compactly:\n\n{text}"
        return self._run(prompt, "summary")

    def reflect(self, context: str) -> ModelResult:
        prompt = f"Reflect on this system state compactly:\n\n{context}"
        return self._run(prompt, "reflect")

    def health(self) -> Dict:
        self._ensure_pipeline()
        return {
            "ok": self._pipeline is not None,
            "provider": self.provider,
            "model": self.model_name,
            "load_error": self._load_error,
        }
