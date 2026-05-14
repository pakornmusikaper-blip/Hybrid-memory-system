# v12 Visual Workflow Agent CLI

Status: Draft
Date: 2026-05-14

## Goal

Provide an agent CLI for building desktop workflows from natural language plus attached visual targets. It is designed to feel like an auto-click workflow tool, but safer and more agent-friendly:

- Attach cropped images or screenshots as named **visual anchors**.
- Convert each attached image into **AI-readable language JSON**: dimensions, hash, format, dominant color buckets, ASCII visual preview, and optional `data:image/...;base64,...` payload for multimodal agents.
- Generate a reusable JSON workflow that says which image to find, verify, click, type into, or wait for.
- Scan a PNG screenshot/screen image for the attached target image and return a reviewed click point.
- Generate a vision-agent prompt that can be sent to a multimodal model or screen automation runtime.
- Preview every action with `dry-run` before any future executor clicks the screen.

## Browser Interface

Run the local interface when you want to attach images and chat with the agent instead of writing CLI flags manually:

```bash
python v12/visual_workflow_cli.py interface --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765`, attach one or more button/screen images, then chat in Thai or English. The page sends the images as browser data URIs to the local agent, stores them in the workspace, converts them into AI-readable anchor payloads, and returns:

- workflow JSON
- dry-run events
- vision-agent prompt
- saved workflow path

The interface is intentionally review-first: it does not click the OS directly. Use the generated workflow with a separate executor after inspection.

## Commands

### Create a workflow

```bash
python v12/visual_workflow_cli.py create \
  --goal "Login and open the dashboard" \
  --image login_button=/path/to/login-button.png \
  --instruction "Click login_button, wait 2 seconds" \
  --out /tmp/login-workflow.json
```

Use `--embed-image-data-uri` if the workflow JSON should include small base64 image attachments for a multimodal model:

```bash
python v12/visual_workflow_cli.py create \
  --goal "Click the same button shown in the image" \
  --image target=/path/to/button.png \
  --embed-image-data-uri \
  --out /tmp/click-target-workflow.json
```

### Convert an attached image into AI-readable JSON

```bash
python v12/visual_workflow_cli.py describe-image /path/to/button.png \
  --name target_button \
  --description "Button crop supplied by the operator" \
  --embed-data-uri
```

The output includes stable metadata and language-like visual hints that an AI can read without guessing from a raw filename.

### Validate image anchors and step targets

```bash
python v12/visual_workflow_cli.py validate /tmp/login-workflow.json
```

### Preview the workflow

```bash
python v12/visual_workflow_cli.py dry-run /tmp/login-workflow.json
```

### Scan a screenshot for the attached image and produce click coordinates

```bash
python v12/visual_workflow_cli.py scan /tmp/login-workflow.json \
  --screen /path/to/current-screen.png
```

Example result:

```json
{
  "status": "found",
  "matches": [
    {
      "target": "login_button",
      "score": 1.0,
      "box": {"x": 420, "y": 312, "width": 96, "height": 32},
      "click": {"x": 468, "y": 328}
    }
  ],
  "next_action": {
    "action": "click",
    "target": "login_button",
    "x": 468,
    "y": 328,
    "review_required": true
  }
}
```

The scanner currently supports common non-interlaced 8-bit PNG target/screen images. It returns click coordinates but does not perform a live OS click by default.

### Print the generated agent prompt

```bash
python v12/visual_workflow_cli.py prompt /tmp/login-workflow.json
```

## Workflow Model

A workflow contains:

| Field | Meaning |
|---|---|
| `goal` | Natural-language operator goal. |
| `anchors` | Named attached images with fingerprints, size metadata, matching confidence, AI-readable image language, and click policy. |
| `steps` | Safe actions such as `assert_visible`, `click`, `type`, `wait`, `hotkey`, and `prompt`. |
| `safety` | Dry-run-first policy, max step cap, and stop-on-missing-anchor behavior. |
| `agent_prompt` | Prompt text for a vision-capable screen agent. |

## Why This Is Better Than a Basic Auto Clicker

Basic clickers usually replay coordinates. This CLI stores semantic visual anchors instead, so the workflow can say “click the image that looks like this button” rather than “click x=512 y=384”. The `scan` command then looks for that image in the current screenshot and produces a click point from the matched visual box. That makes the workflow easier to review, easier to regenerate from a prompt, and more resilient when windows move.

## Current Scope

The v12 CLI creates, validates, scans, and dry-runs workflows. It does not perform live OS clicks by default. A future screen executor can consume the JSON spec, use the image metadata and confidence thresholds, and report observed screen matches before clicking.
