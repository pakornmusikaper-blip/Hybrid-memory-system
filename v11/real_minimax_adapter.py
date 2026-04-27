#!/usr/bin/env python3
"""
v11 Real MiniMax API transport adapter.
"""

from __future__ import annotations

import os
import urllib.request
import urllib.error
import json
import time
from dataclasses import dataclass, field
from typing import Dict

from v6.model_adapter import ModelResult, HeuristicAdapter


@dataclass
class MiniMaxConfig:
    model_name: str = "MiniMax-M2.7"
    api_base: str = "https://api.minimax.io"
    api_key_env: str = "MINIMAX_API_KEY"
    enabled: bool = False
    timeout_seconds: float = 30.0


class RealMiniMaxAdapter:
    def __init__(self, config: MiniMaxConfig | None = None):
        self.config = config or MiniMaxConfig()
        self.model_name = self.config.model_name
        self.provider = "minimax-api"
        self._fallback = HeuristicAdapter()

    def _available(self) -> tuple[bool, str]:
        if not self.config.enabled:
            return False, "minimax disabled by config"
        key = os.getenv(self.config.api_key_env)
        if not key:
            return False, f"missing env {self.config.api_key_env}"
        return True, "ok"

    def _build_request(self, prompt: str, mode: str) -> urllib.request.Request:
        url = f"{self.config.api_base}/api/v1/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {os.getenv(self.config.api_key_env)}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 256,
        }
        data = json.dumps(body).encode()
        return urllib.request.Request(url, data=data, headers=headers, method="POST")

    def generate(self, prompt: str, mode: str = "standard") -> ModelResult:
        ok, reason = self._available()
        if not ok:
            result = self._fallback.generate(prompt, mode)
            result.reason = f"minimax unavailable: {reason}"
            return result

        try:
            request = self._build_request(prompt, mode)
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                body = json.loads(response.read())
                choices = body.get("choices", [])
                if choices:
                    text = choices[0].get("message", {}).get("content", "")
                else:
                    text = body.get("choices", [{}])[0].get("message", {}).get("content", "")
                return ModelResult(True, text, self.model_name, self.provider, mode)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            result = self._fallback.generate(prompt, mode)
            result.reason = f"minimax http error {e.code}: {body[:200]}"
            return result
        except Exception as e:
            result = self._fallback.generate(prompt, mode)
            result.reason = f"minimax transport error: {e}"
            return result

    def summarize(self, text: str) -> ModelResult:
        return self.generate(f"Summarize compactly:\n\n{text}", "summary")

    def reflect(self, context: str) -> ModelResult:
        return self.generate(f"Reflect on this system state:\n\n{context}", "reflect")

    def health(self) -> Dict:
        ok, reason = self._available()
        if not ok:
            return {"ok": False, "provider": self.provider, "reason": reason}
        try:
            request = self._build_request("hello", "standard")
            with urllib.request.urlopen(request, timeout=5.0) as response:
                return {"ok": True, "provider": self.provider, "model": self.model_name}
        except Exception as e:
            return {"ok": False, "provider": self.provider, "reason": str(e)}
