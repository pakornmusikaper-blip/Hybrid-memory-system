from __future__ import annotations

import base64
import struct
import sys
import tempfile
import zlib
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from visual_workflow_agent import (
    PromptWorkflowPlanner,
    WorkflowSpec,
    build_anchor,
    dry_run_events,
    find_template_in_image,
    image_to_ai_language,
)


PNG_1X1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="


def write_rgba_png(path: Path, width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> None:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend(pixels[y * width + x])
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(raw)))
        + chunk(b"IEND", b"")
    )


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

    def test_image_to_ai_language_embeds_preview_and_data_uri(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "button.png"
            write_rgba_png(image, 2, 1, [(255, 0, 0, 255), (0, 0, 255, 255)])
            payload = image_to_ai_language(image, name="button", include_data_uri=True)
            self.assertEqual(payload["dimensions"], {"width": 2, "height": 1})
            self.assertTrue(payload["data_uri"].startswith("data:image/png;base64,"))
            self.assertIn("ascii_preview", payload)

    def test_template_scanner_finds_button_and_click_center(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            screen = root / "screen.png"
            button = root / "button.png"
            black = (0, 0, 0, 255)
            red = (255, 0, 0, 255)
            blue = (0, 0, 255, 255)
            screen_pixels = [black] * 25
            screen_pixels[2 * 5 + 3] = red
            screen_pixels[2 * 5 + 4] = blue
            screen_pixels[3 * 5 + 3] = blue
            screen_pixels[3 * 5 + 4] = red
            write_rgba_png(screen, 5, 5, screen_pixels)
            write_rgba_png(button, 2, 2, [red, blue, blue, red])
            match = find_template_in_image(screen, button, target="button", threshold=1.0)
            self.assertIsNotNone(match)
            self.assertEqual(match.to_dict()["box"], {"x": 3, "y": 2, "width": 2, "height": 2})
            self.assertEqual(match.to_dict()["click"], {"x": 4, "y": 3})


if __name__ == "__main__":
    unittest.main()
