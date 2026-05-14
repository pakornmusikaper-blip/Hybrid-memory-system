#!/usr/bin/env python3
"""Browser interface for chatting with the visual workflow agent."""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v12.visual_workflow_agent import PromptWorkflowPlanner, VisualAnchor, build_anchor, dry_run_events


HTML_PAGE = r"""<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Visual Workflow Agent</title>
  <style>
    :root { color-scheme: dark; --bg: #0f172a; --panel: #111827; --soft: #1f2937; --line: #334155; --text: #e5e7eb; --muted: #94a3b8; --accent: #38bdf8; --ok: #34d399; }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: radial-gradient(circle at top left, #123251, var(--bg) 38rem); color: var(--text); }
    header { padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--line); background: rgba(15, 23, 42, 0.82); backdrop-filter: blur(12px); position: sticky; top: 0; z-index: 1; }
    h1 { margin: 0 0 .25rem; font-size: clamp(1.35rem, 3vw, 2.2rem); }
    header p { margin: 0; color: var(--muted); }
    main { display: grid; grid-template-columns: minmax(20rem, 1fr) minmax(22rem, 1.15fr); gap: 1rem; padding: 1rem; max-width: 1240px; margin: 0 auto; }
    section { background: rgba(17, 24, 39, .9); border: 1px solid var(--line); border-radius: 18px; overflow: hidden; box-shadow: 0 20px 70px rgba(0,0,0,.24); }
    .section-head { padding: 1rem; border-bottom: 1px solid var(--line); display: flex; align-items: center; justify-content: space-between; gap: .75rem; }
    .section-head h2 { margin: 0; font-size: 1rem; }
    .chat { min-height: 27rem; max-height: 46rem; overflow: auto; padding: 1rem; display: flex; flex-direction: column; gap: .75rem; }
    .bubble { padding: .8rem .9rem; border-radius: 14px; max-width: 95%; line-height: 1.45; white-space: pre-wrap; }
    .user { align-self: flex-end; background: #075985; }
    .agent { align-self: flex-start; background: var(--soft); border: 1px solid var(--line); }
    form { padding: 1rem; border-top: 1px solid var(--line); display: grid; gap: .75rem; }
    label { color: var(--muted); font-size: .9rem; display: grid; gap: .35rem; }
    input[type="text"], textarea { width: 100%; color: var(--text); background: #020617; border: 1px solid var(--line); border-radius: 12px; padding: .75rem; }
    textarea { min-height: 7rem; resize: vertical; }
    input[type="file"] { width: 100%; color: var(--muted); border: 1px dashed var(--line); border-radius: 12px; padding: .75rem; background: #020617; }
    button { border: 0; color: #00111d; background: linear-gradient(135deg, var(--accent), var(--ok)); padding: .8rem 1rem; border-radius: 12px; font-weight: 750; cursor: pointer; }
    button:disabled { opacity: .6; cursor: wait; }
    .preview { display: flex; flex-wrap: wrap; gap: .55rem; }
    .thumb { width: 92px; border: 1px solid var(--line); border-radius: 12px; overflow: hidden; background: #020617; }
    .thumb img { display: block; width: 100%; height: 68px; object-fit: contain; background: #020617; }
    .thumb span { display: block; padding: .35rem; color: var(--muted); font-size: .72rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .tabs { display: flex; gap: .5rem; flex-wrap: wrap; }
    .tab { color: var(--text); background: #020617; border: 1px solid var(--line); padding: .45rem .65rem; border-radius: 999px; font-size: .78rem; }
    .tab.active { border-color: var(--accent); color: var(--accent); }
    pre { margin: 0; padding: 1rem; min-height: 36rem; max-height: 51rem; overflow: auto; background: #020617; color: #dbeafe; font-size: .82rem; line-height: 1.45; }
    .hint { padding: .75rem 1rem; color: var(--muted); border-top: 1px solid var(--line); font-size: .88rem; }
    @media (max-width: 900px) { main { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <h1>Visual Workflow Agent Interface</h1>
    <p>แนบรูปปุ่ม/หน้าจอ แล้ว chat เพื่อให้ agent สร้าง flow การคลิ๊กแบบ review ก่อนใช้งานจริง</p>
  </header>
  <main>
    <section>
      <div class="section-head"><h2>Chat + Attach Images</h2><span id="status">พร้อมใช้งาน</span></div>
      <div id="chat" class="chat">
        <div class="bubble agent">สวัสดีครับ แนบรูปปุ่มหรือ crop ของหน้าจอ แล้วพิมพ์สิ่งที่ต้องการ เช่น “คลิ๊กปุ่ม login แล้วรอ 2 วินาที” ผมจะสร้าง workflow JSON, dry-run และ prompt ให้ครับ</div>
      </div>
      <form id="composer">
        <label>Goal / ชื่อ flow
          <input id="goal" type="text" placeholder="เช่น Login เข้า dashboard" />
        </label>
        <label>แนบรูปปุ่มหรือ screenshot crop
          <input id="files" type="file" accept="image/*" multiple />
        </label>
        <div id="preview" class="preview"></div>
        <label>Chat กับ agent
          <textarea id="message" placeholder="เช่น คลิ๊ก login_button แล้วพิมพ์ email จากนั้นกด submit"></textarea>
        </label>
        <button id="send" type="submit">ส่งให้ Agent สร้าง Flow</button>
      </form>
    </section>
    <section>
      <div class="section-head">
        <h2>Generated Flow</h2>
        <div class="tabs">
          <button type="button" class="tab active" data-view="workflow">workflow</button>
          <button type="button" class="tab" data-view="dryRun">dry-run</button>
          <button type="button" class="tab" data-view="prompt">prompt</button>
        </div>
      </div>
      <pre id="output">ยังไม่มี workflow</pre>
      <div class="hint">หมายเหตุ: interface นี้สร้างและ preview flow เท่านั้น ยังไม่คลิ๊ก OS จริงจนกว่าจะต่อ executor ภายนอก</div>
    </section>
  </main>
<script>
const chat = document.getElementById('chat');
const form = document.getElementById('composer');
const filesInput = document.getElementById('files');
const preview = document.getElementById('preview');
const output = document.getElementById('output');
const statusEl = document.getElementById('status');
let lastPayload = null;
let selectedView = 'workflow';

function addBubble(text, kind) {
  const node = document.createElement('div');
  node.className = `bubble ${kind}`;
  node.textContent = text;
  chat.appendChild(node);
  chat.scrollTop = chat.scrollHeight;
}

function readFileAsDataUri(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve({ file_name: file.name, name: file.name.replace(/\.[^.]+$/, ''), data_uri: reader.result });
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

filesInput.addEventListener('change', () => {
  preview.innerHTML = '';
  [...filesInput.files].forEach(file => {
    const item = document.createElement('div');
    item.className = 'thumb';
    const img = document.createElement('img');
    img.src = URL.createObjectURL(file);
    const label = document.createElement('span');
    label.textContent = file.name;
    item.append(img, label);
    preview.appendChild(item);
  });
});

function renderOutput() {
  if (!lastPayload) return;
  if (selectedView === 'prompt') output.textContent = lastPayload.prompt || '';
  else output.textContent = JSON.stringify(lastPayload[selectedView], null, 2);
}

document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    selectedView = tab.dataset.view;
    renderOutput();
  });
});

form.addEventListener('submit', async event => {
  event.preventDefault();
  const message = document.getElementById('message').value.trim();
  const goal = document.getElementById('goal').value.trim();
  if (!message && filesInput.files.length === 0) {
    addBubble('กรุณาพิมพ์ข้อความหรือแนบรูปก่อน', 'agent');
    return;
  }
  addBubble(message || '(แนบรูปอย่างเดียว)', 'user');
  statusEl.textContent = 'กำลังสร้าง flow...';
  document.getElementById('send').disabled = true;
  try {
    const attachments = await Promise.all([...filesInput.files].map(readFileAsDataUri));
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ goal, message, attachments })
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || 'request failed');
    lastPayload = payload;
    addBubble(payload.reply, 'agent');
    selectedView = 'workflow';
    document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.view === selectedView));
    renderOutput();
    document.getElementById('message').value = '';
    filesInput.value = '';
    preview.innerHTML = '';
  } catch (error) {
    addBubble(`เกิดข้อผิดพลาด: ${error.message}`, 'agent');
  } finally {
    statusEl.textContent = 'พร้อมใช้งาน';
    document.getElementById('send').disabled = false;
  }
});
</script>
</body>
</html>
"""


@dataclass
class WorkflowChatSession:
    """Stateful chat session that turns messages and image attachments into workflows."""

    workspace: Path
    planner: PromptWorkflowPlanner = field(default_factory=PromptWorkflowPlanner)
    anchors: list[VisualAnchor] = field(default_factory=list)
    messages: list[dict[str, str]] = field(default_factory=list)
    turn_count: int = 0

    def __post_init__(self) -> None:
        (self.workspace / "uploads").mkdir(parents=True, exist_ok=True)
        (self.workspace / "workflows").mkdir(parents=True, exist_ok=True)

    def handle_chat(self, message: str, attachments: list[dict[str, str]], goal: str = "") -> dict[str, Any]:
        self.turn_count += 1
        new_anchors = [self._save_attachment(item) for item in attachments]
        self.anchors.extend(new_anchors)
        effective_goal = goal.strip() or self._derive_goal(message, new_anchors)
        instruction = message.strip() or "คลิ๊กตำแหน่งตามรูปที่แนบโดยตรวจสอบจาก visual anchor ก่อน"
        spec = self.planner.plan(effective_goal, self.anchors, instruction)
        workflow_path = self.workspace / "workflows" / f"workflow-{self.turn_count:03d}.json"
        spec.save(workflow_path)
        events = dry_run_events(spec)
        self.messages.append({"role": "user", "content": message})
        reply = self._reply(spec, new_anchors, workflow_path)
        self.messages.append({"role": "agent", "content": reply})
        return {
            "reply": reply,
            "workflow_path": str(workflow_path),
            "workflow": spec.to_dict(),
            "dryRun": events,
            "prompt": spec.agent_prompt,
            "anchors_added": [anchor.to_dict() for anchor in new_anchors],
        }

    def _derive_goal(self, message: str, anchors: list[VisualAnchor]) -> str:
        if message.strip():
            return message.strip().splitlines()[0][:120]
        if anchors:
            return "Click attached visual target safely"
        return "Build a visual workflow"

    def _save_attachment(self, item: dict[str, str]) -> VisualAnchor:
        data_uri = item.get("data_uri", "")
        header, encoded = _split_data_uri(data_uri)
        suffix = _suffix_from_header(header, item.get("file_name", "image.png"))
        safe_name = _safe_file_stem(item.get("name") or item.get("file_name") or f"anchor_{self.turn_count}")
        upload_path = self.workspace / "uploads" / f"{self.turn_count:03d}-{len(self.anchors):03d}-{safe_name}{suffix}"
        upload_path.write_bytes(base64.b64decode(encoded))
        return build_anchor(
            f"{safe_name}={upload_path}",
            description=item.get("description", "uploaded from browser interface"),
            include_data_uri=True,
        )

    def _reply(self, spec: Any, new_anchors: list[VisualAnchor], workflow_path: Path) -> str:
        anchor_names = ", ".join(anchor.name for anchor in new_anchors) or "ใช้รูปที่เคยแนบไว้"
        return "\n".join([
            f"สร้าง workflow แล้ว: {workflow_path}",
            f"Anchors: {anchor_names}",
            f"Steps: {len(spec.steps)} action(s)",
            "เปิดแท็บ workflow/dry-run/prompt ทางขวาเพื่อตรวจสอบก่อนนำไปต่อ executor คลิ๊กจริง",
        ])


def _split_data_uri(data_uri: str) -> tuple[str, str]:
    if "," not in data_uri:
        raise ValueError("attachment must be a data URI")
    header, encoded = data_uri.split(",", 1)
    if ";base64" not in header:
        raise ValueError("attachment data URI must be base64")
    return header, encoded


def _suffix_from_header(header: str, file_name: str) -> str:
    original = Path(file_name).suffix.lower()
    if original:
        return original
    if "image/png" in header:
        return ".png"
    if "image/jpeg" in header or "image/jpg" in header:
        return ".jpg"
    if "image/gif" in header:
        return ".gif"
    return ".img"


def _safe_file_stem(value: str) -> str:
    stem = Path(value).stem or value
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", stem.strip()).strip("_")
    return safe or "anchor"


class WorkflowInterfaceHandler(BaseHTTPRequestHandler):
    session: WorkflowChatSession

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            self._send_html(HTML_PAGE)
            return
        if parsed.path == "/api/state":
            self._send_json({
                "anchors": [anchor.to_dict() for anchor in self.session.anchors],
                "messages": self.session.messages,
            })
            return
        self.send_error(HTTPStatus.NOT_FOUND, "not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/chat":
            self.send_error(HTTPStatus.NOT_FOUND, "not found")
            return
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        result = self.session.handle_chat(
            message=payload.get("message", ""),
            goal=payload.get("goal", ""),
            attachments=payload.get("attachments", []),
        )
        self._send_json(result)

    def log_message(self, format: str, *args: Any) -> None:
        sys.stderr.write("[visual-workflow-interface] " + format % args + "\n")

    def _send_html(self, body: str) -> None:
        data = body.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def build_server(host: str, port: int, workspace: Path) -> ThreadingHTTPServer:
    session = WorkflowChatSession(workspace)

    class Handler(WorkflowInterfaceHandler):
        pass

    Handler.session = session
    return ThreadingHTTPServer((host, port), Handler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Visual Workflow Agent browser interface")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--workspace", default="/tmp/visual-workflow-interface")
    args = parser.parse_args()
    server = build_server(args.host, args.port, Path(args.workspace))
    print(f"Visual Workflow Agent interface: http://{args.host}:{args.port}")
    print(f"Workspace: {args.workspace}")
    server.serve_forever()


if __name__ == "__main__":
    main()
