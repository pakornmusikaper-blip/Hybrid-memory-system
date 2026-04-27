#!/usr/bin/env python3
"""
Approximate token-efficiency benchmark for baseline vs substrate-style prompts.
"""

from __future__ import annotations

import json
from pathlib import Path


def approx_tokens(text: str) -> int:
    # rough approximation for mixed English/markdown text
    return max(1, len(text) // 4)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main():
    workspace = Path.home() / ".openclaw" / "workspace"
    ks = workspace / "knowledge-system"

    person_structured = read(ks / "structured" / "people" / "pakorn-musikaper.yaml")
    pref_structured = read(ks / "structured" / "preferences" / "pakorn-agent-preferences.yaml")
    project_structured = read(ks / "structured" / "projects" / "openclaw-hermes-memory-upgrade.yaml")
    dreaming_wiki = read(ks / "wiki" / "systems" / "OpenClaw Dreaming System.md")
    project_wiki = read(ks / "wiki" / "projects" / "OpenClaw Hermes Memory Architecture Upgrade.md")

    baseline_prompt = "\n\n".join(
        [
            "Answer the user's question about Pakorn and the memory architecture.",
            person_structured,
            pref_structured,
            project_structured,
            dreaming_wiki,
            project_wiki,
        ]
    )

    substrate_bundle = "\n\n".join(
        [
            "Prepared substrate bundle:",
            "Belief: Pakorn is building a layered memory system with a subconscious substrate.",
            "Preference: likes detailed, efficient technical development.",
            "Project state: hybrid-memory-system evolved into v2 substrate and v3 daemon work.",
            "Relevant system: OpenClaw Dreaming provides background memory surfacing; substrate extends this into continuous preparation.",
        ]
    )

    followup_baseline = "\n\n".join(
        [
            "Follow-up question about how the system compares to prior memory behavior.",
            person_structured,
            project_structured,
            dreaming_wiki,
        ]
    )

    followup_substrate = "\n\n".join(
        [
            "Prepared follow-up bundle:",
            "Belief reuse: same project and same user preferences as prior turn.",
            "Delta: compare baseline memory loading with substrate prepared context.",
        ]
    )

    data = {
        "baseline": {
            "chars": len(baseline_prompt),
            "approx_tokens": approx_tokens(baseline_prompt),
        },
        "substrate": {
            "chars": len(substrate_bundle),
            "approx_tokens": approx_tokens(substrate_bundle),
        },
        "followup_baseline": {
            "chars": len(followup_baseline),
            "approx_tokens": approx_tokens(followup_baseline),
        },
        "followup_substrate": {
            "chars": len(followup_substrate),
            "approx_tokens": approx_tokens(followup_substrate),
        },
    }

    data["comparison"] = {
        "initial_reduction_ratio": round(1 - (data["substrate"]["approx_tokens"] / data["baseline"]["approx_tokens"]), 3),
        "followup_reduction_ratio": round(1 - (data["followup_substrate"]["approx_tokens"] / data["followup_baseline"]["approx_tokens"]), 3),
    }

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
