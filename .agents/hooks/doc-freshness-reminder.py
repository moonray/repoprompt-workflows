#!/usr/bin/env python3
"""Claude Code hook: nudge a docs/spec drift audit when a tracked work item is closed.

PostToolUse reminder (fails open — a crashed hook never traps the agent). One nudge per
event, from either observed close signal:

  - shell close commands: tw.py close / $TW close / tw close / issue.sh close /
    close.sh <ref> / gh issue close   (gh pr close is NOT an item close)
  - file-backend close edits: a .agents/issues/*.md whose frontmatter now reads
    status: closed

Fills the issue-close half of closeout gating that spec-conformance-gate.py documents
as unhandled ("GitHub-issue-based closes that don't touch a spec file need a separate
issue-close hook"): that gate owns spec-vs-implementation on spec-file terminal flips;
this owns docs-vs-code freshness at item close. Reminder-only by design — "audit ran"
is not provable from a Skill invocation, and exempt-label closes change no code, so the
nudge names the skip condition instead of blocking. Escalation path if this proves weak:
a test-quality-style Stop gate.

Source: `.agents/hooks/doc-freshness-reminder.py` in this repo (symlink it into your
runtime's hooks directory, e.g. `~/.claude/hooks/`).
"""
import json
import os
import re
import sys

# Adjacency (close as the immediate subcommand/argument, not a long-range "…close…" anywhere
# in the string): a `.*` bridge matched PROSE mentioning close commands — observed live when
# the hook fired on its own introducing commit whose message named the close shapes.
_CLOSE_CMD_RES = [
    re.compile(r"\btw\.py\b['\"]?\s+close\b"),
    re.compile(r"\$\{?TW\}?['\"]?\s+close\b"),
    re.compile(r"\btw\s+close\b"),
    re.compile(r"\bissue\.sh\b['\"]?\s+close\b"),
    re.compile(r"\bclose\.sh\b"),
    re.compile(r"\bgh\s+issue\s+close\b"),
]

_ISSUE_FILE_RE = re.compile(r"(^|/)\.agents/issues/[^/]+\.md$")
_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)

NUDGE = (
    "DOC FRESHNESS: a tracked work item was just closed. Before declaring the work done, "
    "run the `document` skill in code mode — change-driven over the closed item's landed "
    "commit span (dry-run first) — and report the drift findings with the close; do not "
    "leave doc/spec reconciliation to a later user prompt. Apply doc-side edits only "
    "under an explicit grant. Skip with a stated reason only when the close changed no "
    "code, docs, or steering surfaces (exempt-label closes)."
)


def _paths_from_patch(command):
    """Codex/opencode deliver file edits as an apply_patch command (no path field)."""
    if not isinstance(command, str):
        return []
    return re.findall(r"^\*\*\*\s+(?:Add|Update|Delete)\s+File:\s*(.+?)\s*$", command, re.MULTILINE)


def _paths_from_payload(p):
    ti = p.get("tool_input")
    if not isinstance(ti, dict):
        return []
    paths = []
    for k in ("file_path", "path", "filePath", "notebook_path"):
        v = ti.get(k)
        if isinstance(v, str) and v:
            paths.append(v)
    paths.extend(_paths_from_patch(ti.get("command")))
    return paths


def _edit_succeeded(payload):
    """Suppress the nudge for tool calls that made no change, when the runtime says so."""
    tr = payload.get("tool_response")
    if not isinstance(tr, dict):
        return True  # unknown shape -> assume success (nudges are cheap; misses are not)
    if tr.get("is_error") is True or tr.get("isError") is True:
        return False
    err = tr.get("error")
    if err is True or (isinstance(err, (str, dict)) and err):
        return False
    if str(tr.get("status", "")).lower() == "error":
        return False
    if tr.get("ok") is False or tr.get("success") is False:
        return False
    return True


def _file_closed(path):
    """True when the edited issue file's frontmatter now reads status: closed."""
    if not path or not _ISSUE_FILE_RE.search(path.replace("\\", "/")):
        return False
    if not os.path.isfile(path):
        return False
    try:
        head = open(path, encoding="utf-8", errors="ignore").read(2000)
    except OSError:
        return False
    m = _FRONTMATTER_RE.match(head)
    if not m:
        return False
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        if k.strip().lower() == "status" and v.strip().strip('"').strip("'").lower() == "closed":
            return True
    return False


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if not isinstance(payload, dict):
        sys.exit(0)
    if payload.get("hook_event_name") != "PostToolUse":
        sys.exit(0)
    if not _edit_succeeded(payload):
        sys.exit(0)
    ti = payload.get("tool_input")
    command = ti.get("command") if isinstance(ti, dict) else None
    fired = any(r.search(command) for r in _CLOSE_CMD_RES if isinstance(command, str))
    if not fired:
        for p in _paths_from_payload(payload):
            if _file_closed(p):
                fired = True
                break
    if fired:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": NUDGE,
            }
        }))
    sys.exit(0)


if __name__ == "__main__":
    main()
