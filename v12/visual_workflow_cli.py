#!/usr/bin/env python3
"""CLI for v12 Visual Workflow Agent."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v12.visual_workflow_agent import (
    PromptWorkflowPlanner,
    WorkflowSpec,
    build_anchor,
    dry_run_events,
    image_to_ai_language,
    scan_workflow_targets,
)


def _read_text_argument(value: str | None, file_value: str | None) -> str:
    if file_value:
        return Path(file_value).read_text(encoding="utf-8")
    return value or ""


def cmd_create(args: argparse.Namespace) -> None:
    instruction = _read_text_argument(args.instruction, args.instruction_file)
    anchors = [
        build_anchor(
            item,
            base_dir=Path.cwd(),
            description=args.anchor_description,
            include_data_uri=args.embed_image_data_uri,
        )
        for item in args.image
    ]
    spec = PromptWorkflowPlanner().plan(args.goal, anchors, instruction)
    spec.save(Path(args.out))
    print(json.dumps({"status": "created", "out": args.out, "anchors": len(anchors), "steps": len(spec.steps)}, indent=2))


def cmd_prompt(args: argparse.Namespace) -> None:
    spec = WorkflowSpec.load(Path(args.workflow))
    print(spec.agent_prompt)


def cmd_dry_run(args: argparse.Namespace) -> None:
    spec = WorkflowSpec.load(Path(args.workflow))
    events = dry_run_events(spec)
    if args.json:
        print(json.dumps(events, indent=2, ensure_ascii=False))
        return
    print(f"Visual workflow dry-run: {spec.goal}")
    for event in events:
        target = event.get("detail", {}).get("target", "")
        print(f"[{event.get('index', '-')}] {event['action']} {target} -> {event['status']}")


def cmd_validate(args: argparse.Namespace) -> None:
    spec = WorkflowSpec.load(Path(args.workflow))
    missing = [anchor.image_path for anchor in spec.anchors if not Path(anchor.image_path).exists()]
    unknown_targets = [step.target for step in spec.steps if step.target and step.target not in {a.name for a in spec.anchors}]
    result = {
        "status": "ok" if not missing and not unknown_targets else "fail",
        "missing_images": missing,
        "unknown_targets": unknown_targets,
        "anchors": len(spec.anchors),
        "steps": len(spec.steps),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["status"] != "ok":
        sys.exit(1)


def cmd_describe_image(args: argparse.Namespace) -> None:
    payload = image_to_ai_language(
        Path(args.image),
        name=args.name or Path(args.image).stem,
        description=args.description or "",
        include_data_uri=args.embed_data_uri,
        max_data_uri_bytes=args.max_data_uri_bytes,
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def cmd_scan(args: argparse.Namespace) -> None:
    spec = WorkflowSpec.load(Path(args.workflow))
    matches = [match.to_dict() for match in scan_workflow_targets(Path(args.screen), spec)]
    result = {
        "status": "found" if matches else "not_found",
        "screen": args.screen,
        "matches": matches,
        "next_action": None,
    }
    if matches:
        first = matches[0]
        result["next_action"] = {
            "action": "click",
            "target": first["target"],
            "x": first["click"]["x"],
            "y": first["click"]["y"],
            "review_required": True,
        }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.require_match and not matches:
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Visual workflow agent CLI for image-anchored desktop workflows")
    sub = parser.add_subparsers(dest="cmd", required=True)

    create = sub.add_parser("create", help="create a workflow JSON from a goal, prompt, and attached target images")
    create.add_argument("--goal", required=True, help="workflow goal in natural language")
    create.add_argument("--image", action="append", default=[], help="visual anchor as NAME=PATH; may be repeated")
    create.add_argument("--instruction", help="extra workflow instructions or prompt text")
    create.add_argument("--instruction-file", help="read extra workflow instructions from a file")
    create.add_argument("--anchor-description", default="", help="description applied to supplied anchors")
    create.add_argument("--embed-image-data-uri", action="store_true", help="embed small image data URIs in AI-readable anchor payloads")
    create.add_argument("--out", required=True, help="output workflow JSON path")
    create.set_defaults(func=cmd_create)

    prompt = sub.add_parser("prompt", help="print the generated vision-agent prompt for a workflow")
    prompt.add_argument("workflow")
    prompt.set_defaults(func=cmd_prompt)

    dry = sub.add_parser("dry-run", help="preview workflow actions without clicking")
    dry.add_argument("workflow")
    dry.add_argument("--json", action="store_true")
    dry.set_defaults(func=cmd_dry_run)

    validate = sub.add_parser("validate", help="validate anchors and step targets")
    validate.add_argument("workflow")
    validate.set_defaults(func=cmd_validate)

    describe = sub.add_parser("describe-image", help="convert an attached image into AI-readable JSON")
    describe.add_argument("image")
    describe.add_argument("--name")
    describe.add_argument("--description")
    describe.add_argument("--embed-data-uri", action="store_true")
    describe.add_argument("--max-data-uri-bytes", type=int, default=262_144)
    describe.set_defaults(func=cmd_describe_image)

    scan = sub.add_parser("scan", help="scan a screenshot PNG for workflow image anchors and return click points")
    scan.add_argument("workflow")
    scan.add_argument("--screen", required=True, help="PNG screenshot/screen image to scan")
    scan.add_argument("--require-match", action="store_true", help="exit non-zero if no anchor is found")
    scan.set_defaults(func=cmd_scan)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
