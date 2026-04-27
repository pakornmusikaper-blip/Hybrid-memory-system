#!/usr/bin/env python3
"""
v10.x Operator notification hook — Telegram alerts for critical events.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict, List


TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_API = "https://api.telegram.org"


def send_telegram(text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        import urllib.request
        url = f"{TELEGRAM_API}/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception:
        return False


class OperatorNotifier:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled and bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

    def notify(self, level: str, title: str, body: str) -> bool:
        emoji = {"alert": "🚨", "warning": "⚠️", "info": "ℹ️", "success": "✅"}.get(level, "📌")
        text = f"{emoji} *{title}*\n{body}"
        if not self.enabled:
            print(f"[OperatorNotifier] (disabled) {text}")
            return False
        return send_telegram(text)

    def alert_circuit_open(self, provider: str, failures: int) -> bool:
        return self.notify(
            "alert",
            "Circuit Breaker OPEN",
            f"External provider `{provider}` has {failures} consecutive failures.\n"
            f"External path is now blocked. Check provider status.",
        )

    def alert_budget_exceeded(self, cost_usd: float, limit_usd: float) -> bool:
        return self.notify(
            "alert",
            "External Budget Exceeded",
            f"Usage ${cost_usd:.4f} exceeded limit ${limit_usd:.4f}.\n"
            f"External routing is now restricted.",
        )

    def alert_poison_queue(self, count: int) -> bool:
        return self.notify(
            "warning",
            "Poison Queue Pressure",
            f"{count} items in poison queue.\n"
            f"Review and clear failed tasks.",
        )

    def alert_reflection_needed(self, belief_count: int, coherence: float) -> bool:
        return self.notify(
            "info",
            "Reflection Recommended",
            f"{belief_count} beliefs, coherence {coherence:.2f}.\n"
            f"System may benefit from reflective analysis.",
        )

    def alert_trial_complete(self, trial_id: str, assessment: str) -> bool:
        return self.notify(
            "success",
            "Trial Complete",
            f"`{trial_id}` — {assessment}",
        )
