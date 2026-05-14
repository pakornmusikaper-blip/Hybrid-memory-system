#!/usr/bin/env python3
"""
v12 Visual Workflow Agent core.

This module builds safe, portable workflow specifications from an operator goal,
attached visual anchors, and optional natural-language instructions.  It is
intentionally dependency-light: image files are fingerprinted and described, and
execution is emitted as a dry-run event stream unless a future screen executor is
plugged in.
"""

from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
import re
import struct
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SUPPORTED_ACTIONS = {"click", "type", "wait", "hotkey", "assert_visible", "prompt"}


@dataclass
class VisualAnchor:
    """A reusable image target that the agent can look for on screen."""

    name: str
    image_path: str
    description: str = ""
    click_policy: str = "center"
    confidence_threshold: float = 0.86
    offset_x: int = 0
    offset_y: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "image_path": self.image_path,
            "description": self.description,
            "click_policy": self.click_policy,
            "confidence_threshold": self.confidence_threshold,
            "offset": {"x": self.offset_x, "y": self.offset_y},
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "VisualAnchor":
        offset = payload.get("offset", {})
        return cls(
            name=payload["name"],
            image_path=payload["image_path"],
            description=payload.get("description", ""),
            click_policy=payload.get("click_policy", "center"),
            confidence_threshold=float(payload.get("confidence_threshold", 0.86)),
            offset_x=int(offset.get("x", 0)),
            offset_y=int(offset.get("y", 0)),
            metadata=payload.get("metadata", {}),
        )


@dataclass
class WorkflowStep:
    """One workflow action produced by the planner."""

    action: str
    target: str | None = None
    text: str | None = None
    seconds: float | None = None
    keys: list[str] = field(default_factory=list)
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"action": self.action}
        if self.target:
            payload["target"] = self.target
        if self.text is not None:
            payload["text"] = self.text
        if self.seconds is not None:
            payload["seconds"] = self.seconds
        if self.keys:
            payload["keys"] = self.keys
        if self.reason:
            payload["reason"] = self.reason
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WorkflowStep":
        action = payload["action"]
        if action not in SUPPORTED_ACTIONS:
            raise ValueError(f"unsupported workflow action: {action}")
        return cls(
            action=action,
            target=payload.get("target"),
            text=payload.get("text"),
            seconds=payload.get("seconds"),
            keys=list(payload.get("keys", [])),
            reason=payload.get("reason", ""),
        )


@dataclass
class WorkflowSpec:
    """Serializable visual workflow plan."""

    goal: str
    anchors: list[VisualAnchor]
    steps: list[WorkflowStep]
    version: str = "v12.visual-workflow-agent/1"
    safety: dict[str, Any] = field(default_factory=lambda: {
        "mode": "dry_run_first",
        "require_operator_review": True,
        "max_steps": 40,
        "stop_on_missing_anchor": True,
    })
    agent_prompt: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "goal": self.goal,
            "safety": self.safety,
            "anchors": [anchor.to_dict() for anchor in self.anchors],
            "steps": [step.to_dict() for step in self.steps],
            "agent_prompt": self.agent_prompt,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WorkflowSpec":
        return cls(
            version=payload.get("version", "v12.visual-workflow-agent/1"),
            goal=payload["goal"],
            safety=payload.get("safety", {}),
            anchors=[VisualAnchor.from_dict(item) for item in payload.get("anchors", [])],
            steps=[WorkflowStep.from_dict(item) for item in payload.get("steps", [])],
            agent_prompt=payload.get("agent_prompt", ""),
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "WorkflowSpec":
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))


@dataclass(frozen=True)
class PixelImage:
    """Decoded image pixels used by the scanner."""

    width: int
    height: int
    pixels: list[tuple[int, int, int, int]]

    def at(self, x: int, y: int) -> tuple[int, int, int, int]:
        return self.pixels[y * self.width + x]


@dataclass(frozen=True)
class VisualMatch:
    """A template match found on a screenshot or screen image."""

    target: str
    score: float
    x: int
    y: int
    width: int
    height: int
    click_x: int
    click_y: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "score": round(self.score, 6),
            "box": {"x": self.x, "y": self.y, "width": self.width, "height": self.height},
            "click": {"x": self.click_x, "y": self.click_y},
        }


def read_image_metadata(path: Path) -> dict[str, Any]:
    """Return stable metadata for a visual anchor without third-party libraries."""

    data = path.read_bytes()
    meta: dict[str, Any] = {
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "format": "unknown",
    }
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        meta.update({
            "format": "png",
            "width": int.from_bytes(data[16:20], "big"),
            "height": int.from_bytes(data[20:24], "big"),
        })
    elif data.startswith((b"GIF87a", b"GIF89a")) and len(data) >= 10:
        meta.update({
            "format": "gif",
            "width": int.from_bytes(data[6:8], "little"),
            "height": int.from_bytes(data[8:10], "little"),
        })
    elif data.startswith(b"\xff\xd8"):
        size = _read_jpeg_size(data)
        meta.update({"format": "jpeg"})
        if size:
            meta.update({"width": size[0], "height": size[1]})
    return meta


def _read_jpeg_size(data: bytes) -> tuple[int, int] | None:
    index = 2
    while index + 9 < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            height = int.from_bytes(data[index + 5:index + 7], "big")
            width = int.from_bytes(data[index + 7:index + 9], "big")
            return width, height
        segment_length = int.from_bytes(data[index + 2:index + 4], "big")
        index += 2 + segment_length
    return None


def image_to_ai_language(
    path: Path,
    name: str = "image",
    description: str = "",
    include_data_uri: bool = False,
    max_data_uri_bytes: int = 262_144,
) -> dict[str, Any]:
    """Convert an image into an AI-readable JSON description.

    The payload contains stable facts, a compact visual summary, and optionally a
    data URI that a multimodal model can ingest as an attachment.  The summary is
    deliberately factual; semantic interpretation still belongs to the vision
    model or operator-provided description.
    """

    data = path.read_bytes()
    metadata = read_image_metadata(path)
    language: dict[str, Any] = {
        "kind": "visual_anchor_image",
        "name": name,
        "description": description,
        "file_name": path.name,
        "mime_type": mimetypes.guess_type(str(path))[0] or f"image/{metadata.get('format', 'unknown')}",
        "sha256": metadata["sha256"],
        "bytes": metadata["bytes"],
        "format": metadata.get("format", "unknown"),
        "dimensions": {
            "width": metadata.get("width"),
            "height": metadata.get("height"),
        },
    }
    if metadata.get("format") == "png":
        pixels = decode_png_pixels(path)
        language["dominant_colors"] = dominant_colors(pixels, limit=5)
        language["ascii_preview"] = ascii_preview(pixels)
    else:
        language["note"] = "pixel preview currently supports PNG; attach this file as image input for full vision understanding"
    if include_data_uri and len(data) <= max_data_uri_bytes:
        language["data_uri"] = f"data:{language['mime_type']};base64,{base64.b64encode(data).decode('ascii')}"
    elif include_data_uri:
        language["data_uri_omitted"] = f"image has {len(data)} bytes, above max_data_uri_bytes={max_data_uri_bytes}"
    return language


def decode_png_pixels(path: Path) -> PixelImage:
    """Decode common non-interlaced 8-bit PNGs into RGBA pixels."""

    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"not a PNG image: {path}")
    index = 8
    width = height = bit_depth = color_type = interlace = None
    compressed = bytearray()
    while index + 8 <= len(data):
        length = struct.unpack(">I", data[index:index + 4])[0]
        chunk_type = data[index + 4:index + 8]
        chunk = data[index + 8:index + 8 + length]
        index += 12 + length
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack(">IIBBBBB", chunk)
        elif chunk_type == b"IDAT":
            compressed.extend(chunk)
        elif chunk_type == b"IEND":
            break
    if None in {width, height, bit_depth, color_type, interlace}:
        raise ValueError(f"invalid PNG header: {path}")
    if bit_depth != 8 or interlace != 0 or color_type not in {0, 2, 4, 6}:
        raise ValueError("scanner supports non-interlaced 8-bit PNG color types 0, 2, 4, and 6")
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[color_type]
    stride = width * channels
    raw = zlib.decompress(bytes(compressed))
    rows: list[bytes] = []
    cursor = 0
    previous = bytes(stride)
    for _ in range(height):
        filter_type = raw[cursor]
        cursor += 1
        scanline = bytearray(raw[cursor:cursor + stride])
        cursor += stride
        recon = _unfilter_png_scanline(filter_type, scanline, previous, channels)
        rows.append(bytes(recon))
        previous = bytes(recon)
    pixels: list[tuple[int, int, int, int]] = []
    for row in rows:
        for x in range(0, len(row), channels):
            if color_type == 0:
                gray = row[x]
                pixels.append((gray, gray, gray, 255))
            elif color_type == 2:
                pixels.append((row[x], row[x + 1], row[x + 2], 255))
            elif color_type == 4:
                gray = row[x]
                pixels.append((gray, gray, gray, row[x + 1]))
            else:
                pixels.append((row[x], row[x + 1], row[x + 2], row[x + 3]))
    return PixelImage(width=width, height=height, pixels=pixels)


def _unfilter_png_scanline(filter_type: int, scanline: bytearray, previous: bytes, bpp: int) -> bytearray:
    out = bytearray(len(scanline))
    for i, value in enumerate(scanline):
        left = out[i - bpp] if i >= bpp else 0
        up = previous[i] if previous else 0
        upper_left = previous[i - bpp] if previous and i >= bpp else 0
        if filter_type == 0:
            predictor = 0
        elif filter_type == 1:
            predictor = left
        elif filter_type == 2:
            predictor = up
        elif filter_type == 3:
            predictor = (left + up) // 2
        elif filter_type == 4:
            predictor = _paeth(left, up, upper_left)
        else:
            raise ValueError(f"unsupported PNG filter type: {filter_type}")
        out[i] = (value + predictor) & 0xFF
    return out


def _paeth(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    distances = (abs(estimate - left), abs(estimate - up), abs(estimate - upper_left))
    if distances[0] <= distances[1] and distances[0] <= distances[2]:
        return left
    if distances[1] <= distances[2]:
        return up
    return upper_left


def dominant_colors(image: PixelImage, limit: int = 5) -> list[dict[str, Any]]:
    buckets: dict[tuple[int, int, int], int] = {}
    for red, green, blue, alpha in image.pixels:
        if alpha == 0:
            continue
        key = (red // 32 * 32, green // 32 * 32, blue // 32 * 32)
        buckets[key] = buckets.get(key, 0) + 1
    total = sum(buckets.values()) or 1
    ranked = sorted(buckets.items(), key=lambda item: item[1], reverse=True)[:limit]
    return [
        {"rgb_bucket": list(color), "coverage": round(count / total, 4)}
        for color, count in ranked
    ]


def ascii_preview(image: PixelImage, max_width: int = 24, max_height: int = 12) -> list[str]:
    if image.width == 0 or image.height == 0:
        return []
    shades = " .:-=+*#%@"
    x_step = max(1, image.width // max_width)
    y_step = max(1, image.height // max_height)
    lines: list[str] = []
    for y in range(0, image.height, y_step):
        chars: list[str] = []
        for x in range(0, image.width, x_step):
            red, green, blue, alpha = image.at(x, y)
            if alpha == 0:
                chars.append(" ")
                continue
            luminance = int(0.2126 * red + 0.7152 * green + 0.0722 * blue)
            chars.append(shades[min(len(shades) - 1, luminance * len(shades) // 256)])
        lines.append("".join(chars[:max_width]))
        if len(lines) >= max_height:
            break
    return lines


def find_template_in_image(
    screen_path: Path,
    template_path: Path,
    target: str = "target",
    threshold: float = 0.96,
    click_policy: str = "center",
    offset_x: int = 0,
    offset_y: int = 0,
) -> VisualMatch | None:
    """Scan a screenshot/image for a PNG template and return a click point."""

    screen = decode_png_pixels(screen_path)
    template = decode_png_pixels(template_path)
    if template.width > screen.width or template.height > screen.height:
        return None
    best_score = -1.0
    best_xy = (0, 0)
    for y in range(screen.height - template.height + 1):
        for x in range(screen.width - template.width + 1):
            score = _template_score(screen, template, x, y)
            if score > best_score:
                best_score = score
                best_xy = (x, y)
            if score >= 1.0:
                return _build_visual_match(target, template, best_xy[0], best_xy[1], score, click_policy, offset_x, offset_y)
    if best_score < threshold:
        return None
    return _build_visual_match(target, template, best_xy[0], best_xy[1], best_score, click_policy, offset_x, offset_y)


def scan_workflow_targets(screen_path: Path, spec: WorkflowSpec) -> list[VisualMatch]:
    """Find all workflow anchors on a screenshot."""

    matches: list[VisualMatch] = []
    for anchor in spec.anchors:
        match = find_template_in_image(
            screen_path=screen_path,
            template_path=Path(anchor.image_path),
            target=anchor.name,
            threshold=anchor.confidence_threshold,
            click_policy=anchor.click_policy,
            offset_x=anchor.offset_x,
            offset_y=anchor.offset_y,
        )
        if match:
            matches.append(match)
    return matches


def _template_score(screen: PixelImage, template: PixelImage, origin_x: int, origin_y: int) -> float:
    diff = 0
    compared = 0
    for ty in range(template.height):
        for tx in range(template.width):
            tr, tg, tb, ta = template.at(tx, ty)
            if ta == 0:
                continue
            sr, sg, sb, _ = screen.at(origin_x + tx, origin_y + ty)
            diff += abs(sr - tr) + abs(sg - tg) + abs(sb - tb)
            compared += 3
    if compared == 0:
        return 0.0
    return max(0.0, 1.0 - (diff / (compared * 255)))


def _build_visual_match(
    target: str,
    template: PixelImage,
    x: int,
    y: int,
    score: float,
    click_policy: str,
    offset_x: int,
    offset_y: int,
) -> VisualMatch:
    if click_policy == "top_left":
        click_x, click_y = x, y
    else:
        click_x, click_y = x + template.width // 2, y + template.height // 2
    return VisualMatch(
        target=target,
        score=score,
        x=x,
        y=y,
        width=template.width,
        height=template.height,
        click_x=click_x + offset_x,
        click_y=click_y + offset_y,
    )


def build_anchor(
    spec: str,
    base_dir: Path | None = None,
    description: str = "",
    include_image_language: bool = True,
    include_data_uri: bool = False,
) -> VisualAnchor:
    """Build an anchor from NAME=PATH or PATH syntax."""

    if "=" in spec:
        name, raw_path = spec.split("=", 1)
    else:
        raw_path = spec
        name = Path(raw_path).stem
    image_path = Path(raw_path).expanduser()
    if base_dir and not image_path.is_absolute():
        image_path = (base_dir / image_path).resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"visual anchor image not found: {image_path}")
    if not name.strip():
        raise ValueError("visual anchor name cannot be empty")
    safe_name = _safe_name(name)
    metadata = read_image_metadata(image_path)
    if include_image_language:
        metadata["ai_language"] = image_to_ai_language(
            image_path,
            name=safe_name,
            description=description,
            include_data_uri=include_data_uri,
        )
    return VisualAnchor(
        name=safe_name,
        image_path=str(image_path),
        description=description,
        metadata=metadata,
    )


def _safe_name(value: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip()).strip("_")
    return safe or "anchor"


class PromptWorkflowPlanner:
    """Heuristic planner that turns a goal and visual anchors into a workflow."""

    def plan(self, goal: str, anchors: list[VisualAnchor], instruction: str = "") -> WorkflowSpec:
        text = "\n".join(part for part in [goal, instruction] if part).strip()
        planning_text = instruction.strip() or text
        steps = self._extract_explicit_steps(planning_text, anchors)
        if not steps:
            steps = self._default_steps(text, anchors)
        prompt = render_agent_prompt(goal, anchors, steps, instruction)
        return WorkflowSpec(goal=goal, anchors=anchors, steps=steps, agent_prompt=prompt)

    def _extract_explicit_steps(self, text: str, anchors: list[VisualAnchor]) -> list[WorkflowStep]:
        steps: list[WorkflowStep] = []
        anchor_by_lower = {anchor.name.lower(): anchor.name for anchor in anchors}
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            lower = line.lower()
            target = self._mentioned_anchor(lower, anchor_by_lower)
            clicked = False
            if any(word in lower for word in ["click", "คลิก", "คลิ๊ก", "กด"]):
                if target:
                    steps.append(WorkflowStep("assert_visible", target=target, reason="verify visual target before click"))
                    steps.append(WorkflowStep("click", target=target, reason=line))
                    clicked = True
            typed = self._quoted_text(line)
            if typed or any(word in lower for word in ["type", "พิมพ์", "กรอก"]):
                steps.append(WorkflowStep("type", text=typed or line, reason=line))
                continue
            wait_seconds = self._wait_seconds(lower)
            if wait_seconds is not None:
                steps.append(WorkflowStep("wait", seconds=wait_seconds, reason=line))
                continue
            if clicked:
                continue
        return steps

    def _default_steps(self, text: str, anchors: list[VisualAnchor]) -> list[WorkflowStep]:
        steps: list[WorkflowStep] = []
        for anchor in anchors:
            steps.append(WorkflowStep("assert_visible", target=anchor.name, reason="image anchor supplied by operator"))
            steps.append(WorkflowStep("click", target=anchor.name, reason="operator wants this screen image to be clickable"))
        if not steps:
            steps.append(WorkflowStep("prompt", text=text, reason="no visual anchor supplied; ask model to refine workflow"))
        return steps

    def _mentioned_anchor(self, line: str, anchor_by_lower: dict[str, str]) -> str | None:
        for lower_name, name in anchor_by_lower.items():
            if lower_name in line:
                return name
        return None

    def _quoted_text(self, line: str) -> str | None:
        match = re.search(r"[\"'“”‘’](.+?)[\"'“”‘’]", line)
        return match.group(1) if match else None

    def _wait_seconds(self, line: str) -> float | None:
        if not any(word in line for word in ["wait", "รอ"]):
            return None
        match = re.search(r"(\d+(?:\.\d+)?)", line)
        return float(match.group(1)) if match else 1.0


def render_agent_prompt(goal: str, anchors: list[VisualAnchor], steps: list[WorkflowStep], instruction: str = "") -> str:
    """Create a screen-agent prompt that can be sent to a vision-capable model."""

    anchor_lines = []
    for anchor in anchors:
        size = ""
        if "width" in anchor.metadata and "height" in anchor.metadata:
            size = f" ({anchor.metadata['width']}x{anchor.metadata['height']} {anchor.metadata.get('format', 'image')})"
        ai_language = anchor.metadata.get("ai_language", {})
        preview = ai_language.get("ascii_preview", [])
        preview_text = " | preview=" + "/".join(preview[:3]) if preview else ""
        anchor_lines.append(
            f"- {anchor.name}: match attached image `{anchor.image_path}`{size}; "
            f"click={anchor.click_policy}; confidence>={anchor.confidence_threshold}; "
            f"description={anchor.description or 'operator-provided visual target'}; "
            f"sha256={anchor.metadata.get('sha256', 'unknown')}{preview_text}"
        )
    step_lines = [f"{idx}. {step.to_dict()}" for idx, step in enumerate(steps, start=1)]
    return "\n".join([
        "You are a visual desktop workflow agent.",
        f"Goal: {goal}",
        "Rules: run dry-run first, never click until the visual anchor is visible, stop on uncertainty, and report every action.",
        "Visual anchors:",
        *(anchor_lines or ["- none supplied; ask the operator for screenshots or target crops."]),
        "Planned workflow:",
        *(step_lines or ["1. Ask the operator to clarify the workflow."]),
        "Operator instruction:",
        instruction or "(none)",
    ])


def dry_run_events(spec: WorkflowSpec) -> list[dict[str, Any]]:
    """Convert a workflow into safe preview events."""

    known_anchors = {anchor.name: anchor for anchor in spec.anchors}
    events: list[dict[str, Any]] = []
    max_steps = int(spec.safety.get("max_steps", 40))
    for index, step in enumerate(spec.steps[:max_steps], start=1):
        event = {"index": index, "action": step.action, "status": "preview", "detail": step.to_dict()}
        if step.target:
            anchor = known_anchors.get(step.target)
            event["anchor_found_in_spec"] = anchor is not None
            if anchor:
                event["image_path"] = anchor.image_path
                event["confidence_threshold"] = anchor.confidence_threshold
        events.append(event)
    if len(spec.steps) > max_steps:
        events.append({"action": "stop", "status": "blocked", "reason": f"max_steps {max_steps} exceeded"})
    return events
