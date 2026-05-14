#!/usr/bin/env python3
"""Demo for v12 Visual Workflow Agent."""

from __future__ import annotations

import base64
import tempfile
from pathlib import Path

from visual_workflow_agent import PromptWorkflowPlanner, build_anchor, dry_run_events


PNG_1X1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / "submit_button.png"
        target.write_bytes(base64.b64decode(PNG_1X1))
        anchor = build_anchor(f"submit={target}")
        spec = PromptWorkflowPlanner().plan(
            goal="Submit a form by finding the submit button image and clicking it safely.",
            anchors=[anchor],
            instruction="Click submit, wait 1 second, then report completion.",
        )
        for event in dry_run_events(spec):
            print(event)
        print("\nGenerated prompt:\n")
        print(spec.agent_prompt)


if __name__ == "__main__":
    main()
