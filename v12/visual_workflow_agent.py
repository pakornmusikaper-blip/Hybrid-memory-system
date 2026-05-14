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

import hashlib
import json
import re
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


def build_anchor(spec: str, base_dir: Path | None = None, description: str = "") -> VisualAnchor:
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
    return VisualAnchor(
        name=_safe_name(name),
        image_path=str(image_path),
        description=description,
        metadata=read_image_metadata(image_path),
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
        anchor_lines.append(
            f"- {anchor.name}: match attached image `{anchor.image_path}`{size}; "
            f"click={anchor.click_policy}; confidence>={anchor.confidence_threshold}; "
            f"description={anchor.description or 'operator-provided visual target'}"
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
