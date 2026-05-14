# v12 Visual Workflow Agent CLI

Status: Draft
Date: 2026-05-14

## Goal

Provide an agent CLI for building desktop workflows from natural language plus attached visual targets.  It is designed to feel like an auto-click workflow tool, but safer and more agent-friendly:

- Attach cropped images or screenshots as named **visual anchors**.
- Generate a reusable JSON workflow that says which image to find, verify, click, type into, or wait for.
- Generate a vision-agent prompt that can be sent to a multimodal model or screen automation runtime.
- Preview every action with `dry-run` before any future executor clicks the screen.

## Commands

### Create a workflow

```bash
python v12/visual_workflow_cli.py create \
  --goal "Login and open the dashboard" \
  --image login_button=/path/to/login-button.png \
  --instruction "Click login_button, wait 2 seconds" \
  --out /tmp/login-workflow.json
```

### Validate image anchors and step targets

```bash
python v12/visual_workflow_cli.py validate /tmp/login-workflow.json
```

### Preview the workflow

```bash
python v12/visual_workflow_cli.py dry-run /tmp/login-workflow.json
```

### Print the generated agent prompt

```bash
python v12/visual_workflow_cli.py prompt /tmp/login-workflow.json
```

## Workflow Model

A workflow contains:

| Field | Meaning |
|---|---|
| `goal` | Natural-language operator goal. |
| `anchors` | Named attached images with fingerprints, size metadata, matching confidence, and click policy. |
| `steps` | Safe actions such as `assert_visible`, `click`, `type`, `wait`, `hotkey`, and `prompt`. |
| `safety` | Dry-run-first policy, max step cap, and stop-on-missing-anchor behavior. |
| `agent_prompt` | Prompt text for a vision-capable screen agent. |

## Why This Is Better Than a Basic Auto Clicker

Basic clickers usually replay coordinates.  This CLI stores semantic visual anchors instead, so the workflow can say “click the image that looks like this button” rather than “click x=512 y=384”.  That makes the workflow easier to review, easier to regenerate from a prompt, and more resilient when windows move.

## Current Scope

The v12 CLI creates, validates, and dry-runs workflows.  It does not perform live OS clicks by default.  A future screen executor can consume the JSON spec, use the image metadata and confidence thresholds, and report observed screen matches before clicking.
