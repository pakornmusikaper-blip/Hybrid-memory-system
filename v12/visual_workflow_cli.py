#!/usr/bin/env python3
"""CLI for v12 Visual Workflow Agent."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v12.visual_workflow_agent import PromptWorkflowPlanner, WorkflowSpec, build_anchor, dry_run_events


def _read_text_argument(value: str | None, file_value: str | None) -> str:
    if file_value:
        return Path(file_value).read_text(encoding="utf-8")
    return value or ""


def cmd_create(args: argparse.Namespace) -> None:
    instruction = _read_text_argument(args.instruction, args.instruction_file)
    anchors = [build_anchor(item, base_dir=Path.cwd(), description=args.anchor_description) for item in args.image]
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Visual workflow agent CLI for image-anchored desktop workflows")
    sub = parser.add_subparsers(dest="cmd", required=True)

    create = sub.add_parser("create", help="create a workflow JSON from a goal, prompt, and attached target images")
    create.add_argument("--goal", required=True, help="workflow goal in natural language")
    create.add_argument("--image", action="append", default=[], help="visual anchor as NAME=PATH; may be repeated")
    create.add_argument("--instruction", help="extra workflow instructions or prompt text")
    create.add_argument("--instruction-file", help="read extra workflow instructions from a file")
    create.add_argument("--anchor-description", default="", help="description applied to supplied anchors")
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
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
