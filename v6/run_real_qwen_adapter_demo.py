#!/usr/bin/env python3
"""
Demo for v6.1 Real Qwen Adapter.
"""

from __future__ import annotations

import json

from real_qwen_adapter import RealQwenAdapter, QwenConfig


def main():
    adapter = RealQwenAdapter(QwenConfig())
    prompt = "The substrate should assess runtime health, summarize queue pressure, and decide if reflection is needed."

    results = {
        "health": adapter.health(),
        "generate_light": adapter.generate(prompt, "light").to_dict(),
        "generate_focused": adapter.generate(prompt, "focused").to_dict(),
        "summarize": adapter.summarize(prompt).to_dict(),
        "reflect": adapter.reflect(prompt).to_dict(),
    }

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
