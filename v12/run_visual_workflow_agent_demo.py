#!/usr/bin/env python3
"""Demo for v12 Visual Workflow Agent."""

from __future__ import annotations

import struct
import tempfile
import zlib
from pathlib import Path

from visual_workflow_agent import PromptWorkflowPlanner, build_anchor, dry_run_events, image_to_ai_language, scan_workflow_targets


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


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / "submit_button.png"
        screen = root / "screen.png"
        black = (0, 0, 0, 255)
        green = (0, 200, 80, 255)
        white = (255, 255, 255, 255)
        target_pixels = [green, green, green, green, white, green, green, green, green]
        screen_pixels = [black] * 64
        for ty in range(3):
            for tx in range(3):
                screen_pixels[(4 + ty) * 8 + (2 + tx)] = target_pixels[ty * 3 + tx]
        write_rgba_png(target, 3, 3, target_pixels)
        write_rgba_png(screen, 8, 8, screen_pixels)

        anchor = build_anchor(f"submit={target}", description="green submit button crop")
        spec = PromptWorkflowPlanner().plan(
            goal="Submit a form by finding the submit button image and clicking it safely.",
            anchors=[anchor],
            instruction="Click submit, wait 1 second, then report completion.",
        )
        print("AI-readable image language:\n")
        print(image_to_ai_language(target, name="submit", description="green submit button crop"))
        print("\nDry-run events:\n")
        for event in dry_run_events(spec):
            print(event)
        print("\nScan matches:\n")
        for match in scan_workflow_targets(screen, spec):
            print(match.to_dict())
        print("\nGenerated prompt:\n")
        print(spec.agent_prompt)


if __name__ == "__main__":
    main()
