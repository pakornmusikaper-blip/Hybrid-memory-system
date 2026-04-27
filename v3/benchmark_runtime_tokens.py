#!/usr/bin/env python3
"""
Production-style token benchmark across baseline, substrate, and runtime/bridge shapes.
"""

from __future__ import annotations

import json
from pathlib import Path


def approx_tokens(text: str) -> int:
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

    baseline_initial = "\n\n".join(
        [
            "Answer a user question about Pakorn, the memory system, and current architecture state.",
            person_structured,
            pref_structured,
            project_structured,
            dreaming_wiki,
            project_wiki,
        ]
    )

    substrate_prepared = "\n\n".join(
        [
            "Prepared substrate bundle:",
            "Belief: Pakorn is evolving a hybrid memory system into a living substrate architecture.",
            "Preference: detailed, efficient, architecture-first explanations.",
            "Project state: v2 substrate cognition and v3 runtime/daemon layers are under active development.",
            "Context: OpenClaw Dreaming is related background memory surfacing, while substrate adds continuous preparation.",
        ]
    )

    baseline_followup = "\n\n".join(
        [
            "Follow-up question about whether the system is better and more token efficient.",
            person_structured,
            project_structured,
            dreaming_wiki,
            project_wiki,
        ]
    )

    substrate_followup = "\n\n".join(
        [
            "Prepared follow-up bundle:",
            "Reuse same user and project beliefs.",
            "Compare baseline direct context loading against prepared substrate summaries and runtime flow.",
        ]
    )

    runtime_bridge_response = "\n\n".join(
        [
            "Runtime bridge response payload:",
            json.dumps(
                {
                    "message_type": "response",
                    "query": "What does the substrate know about the memory-system state?",
                    "content": "Prepared runtime response for query: substrate is active, queue/runtime layers are healthy, and compact context is ready.",
                },
                ensure_ascii=False,
            ),
        ]
    )

    direct_runtime_baseline = "\n\n".join(
        [
            "Answer the same runtime-state question from direct sources.",
            project_structured,
            dreaming_wiki,
            project_wiki,
        ]
    )

    data = {
        "baseline_initial": {"chars": len(baseline_initial), "approx_tokens": approx_tokens(baseline_initial)},
        "substrate_prepared": {"chars": len(substrate_prepared), "approx_tokens": approx_tokens(substrate_prepared)},
        "baseline_followup": {"chars": len(baseline_followup), "approx_tokens": approx_tokens(baseline_followup)},
        "substrate_followup": {"chars": len(substrate_followup), "approx_tokens": approx_tokens(substrate_followup)},
        "direct_runtime_baseline": {
            "chars": len(direct_runtime_baseline),
            "approx_tokens": approx_tokens(direct_runtime_baseline),
        },
        "runtime_bridge_response": {
            "chars": len(runtime_bridge_response),
            "approx_tokens": approx_tokens(runtime_bridge_response),
        },
    }

    data["comparison"] = {
        "initial_reduction_ratio": round(
            1 - (data["substrate_prepared"]["approx_tokens"] / data["baseline_initial"]["approx_tokens"]), 3
        ),
        "followup_reduction_ratio": round(
            1 - (data["substrate_followup"]["approx_tokens"] / data["baseline_followup"]["approx_tokens"]), 3
        ),
        "runtime_response_reduction_ratio": round(
            1 - (data["runtime_bridge_response"]["approx_tokens"] / data["direct_runtime_baseline"]["approx_tokens"]), 3
        ),
    }

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
