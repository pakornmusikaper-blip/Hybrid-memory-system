from __future__ import annotations

import base64
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from visual_workflow_agent import PromptWorkflowPlanner, WorkflowSpec, build_anchor, dry_run_events


PNG_1X1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="


class VisualWorkflowAgentTest(unittest.TestCase):
    def test_planner_creates_image_anchored_click_and_wait(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "button.png"
            image.write_bytes(base64.b64decode(PNG_1X1))
            anchor = build_anchor(f"submit={image}")
            spec = PromptWorkflowPlanner().plan(
                "submit the form",
                [anchor],
                "Click submit and wait 2 seconds",
            )
            self.assertEqual([step.action for step in spec.steps], ["assert_visible", "click", "wait"])
            self.assertEqual(spec.anchors[0].metadata["format"], "png")
            self.assertEqual(spec.anchors[0].metadata["width"], 1)
            self.assertIn("Visual anchors:", spec.agent_prompt)

    def test_workflow_round_trip_and_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / "button.png"
            workflow = root / "workflow.json"
            image.write_bytes(base64.b64decode(PNG_1X1))
            anchor = build_anchor(f"button={image}")
            spec = PromptWorkflowPlanner().plan("click button", [anchor], "")
            spec.save(workflow)
            loaded = WorkflowSpec.load(workflow)
            events = dry_run_events(loaded)
            self.assertTrue(events[0]["anchor_found_in_spec"])
            self.assertEqual(events[1]["action"], "click")


if __name__ == "__main__":
    unittest.main()
