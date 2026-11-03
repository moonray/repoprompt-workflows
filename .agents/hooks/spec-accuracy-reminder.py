#!/usr/bin/env python3
"""Claude Code hook: nudge a same-session spec-accuracy check when an operational doc changes.

PostToolUse reminder (fails open — a crashed hook never traps the agent). Fires when an edit
lands on an operational doc — `.agents/slash/*.md` (runbooks/commands) or
`docs/procedures/*.md` — in a repo that has a `docs/spec/` directory, nudging: if the edit
changed documented behavior, check NOW whether any spec (or its conformance matrix) still
describes the OLD behavior, and fix or flag the drift in the same session.

Fills the change-time direction the sibling hooks leave open (#13):
spec-quality-reminder owns spec-edit -> writing quality; doc-freshness-reminder owns
item-close -> drift audit; spec-conformance-gate owns spec-close -> matrix. None fire when
the operational doc the spec describes is the thing that changed (observed: a runbook
rewritten for a new convention while its paired spec kept the dead constraint for days —
private client workspace, 2026-10-30 -> 11-02, recovered via chat mining).

Detection-gated on the repo's spec dir: silent when `docs/spec/` is positively absent (a
repo whose operational docs have no specs has nothing to drift against); nudges when
existence cannot be verified (unresolvable root — remind rather than stay silent on a
guess, same philosophy as spec-quality-reminder's hook-spec coverage check).

Reminder-only by design. Guarantee is NARROW, same boundary as spec-quality-reminder:
supported edit tools only (Bash sed/python redirects bypass this — documented, accepted).

Source of truth: `.agents/hooks/spec-accuracy-reminder.py` in this repo; symlink it into
your runtime's hooks directory (e.g. `~/.claude/hooks/`). NOTE: the symlink deploys SCRIPT
changes only — matcher changes in the user-owned settings.json must be merged there
separately (scripts/install.sh does that).
"""
import json
import os
import re
import sys

_OPDOC_RES = [
    re.compile(r"(^|/)\.agents/slash/[^/]+\.md$"),
    re.compile(r"(^|/)docs/procedures/[^/]+\.md$"),
]

_EXCLUDE_BASENAMES = {"readme.md"}

NUDGE = (
    "SPEC ACCURACY: you edited an operational doc (a .agents/slash/ runbook or a "
    "docs/procedures/ procedure) — the documented reality of how things work. If this edit "
    "changes documented behavior, check NOW, in this session while the context is fresh, "
    "whether any spec in docs/spec/ (or its conformance matrix) still describes the OLD "
    "behavior, and fix or flag the drift — a rewritten operational doc whose spec keeps a "
    "dead constraint drifts silently for days otherwise. If no spec pairs with the doc, "
    "this check is a quick no-op: say so and move on."
)

_PATCH_FILE_RE = re.compile(r"^\*\*\*\s+(?:Add|Update|Delete)\s+File:\s*(.+?)\s*$", re.MULTILINE)
_PATCH_MOVE_RE = re.compile(r"^\*\*\*\s+Move to:\s*(.+?)\s*$", re.MULTILINE)


def _paths_from_patch(command):
    """Codex/opencode deliver file edits as an apply_patch command (no path field)."""
    if not isinstance(command, str):
        return []
    return _PATCH_FILE_RE.findall(command) + _PATCH_MOVE_RE.findall(command)


def _paths_from_tool_input(ti):
    """Every affected path in the tool input — sources AND destinations, all file kinds.

    One adapter, deliberately per-key tolerant: a malformed entry is skipped, not fatal
    (one bad input must not suppress the nudge for the other paths in a batch).
    """
    if not isinstance(ti, dict):
        return []
    paths = []
    scalar_keys = ("file_path", "path", "filePath", "notebook_path", "new_path", "old_path")
    for key in scalar_keys:
        v = ti.get(key)
        if isinstance(v, str) and v:
            paths.append(v)
    for key in ("files", "edits", "paths"):
        v = ti.get(key)
        if isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    paths.append(item)
                elif isinstance(item, dict):
                    for sub in ("path", "file_path", "new_path", "old_path"):
                        sv = item.get(sub)
                        if isinstance(sv, str) and sv:
                            paths.append(sv)
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
        return False  # MCP/JSON-RPC errors arrive as strings or {code,message} objects
    if str(tr.get("status", "")).lower() == "error":
        return False
    if tr.get("ok") is False or tr.get("success") is False:
        return False
    return True


def _is_opdoc(norm):
    if os.path.basename(norm).lower() in _EXCLUDE_BASENAMES:
        return False
    return any(r.search(norm) for r in _OPDOC_RES)


def _repo_root(norm):
    """The repo root an operational-doc path implies: '' (cwd-relative) or the prefix
    before the watched directory; None when the path matches no known layout (an
    explicitly relative `.agents/slash/x.md` has no leading slash to anchor on)."""
    for prefix in (".agents/slash/", "docs/procedures/"):
        if norm.startswith(prefix):
            return ""
    for marker in ("/.agents/slash/", "/docs/procedures/"):
        idx = norm.find(marker)
        if idx != -1:
            return norm[:idx]
    return None


def _spec_dir_state(root, cwd):
    """True (docs/spec/ exists) / False (positively absent — a resolvable base dir
    exists but carries no docs/spec/) / None (unverifiable — no base resolves)."""
    if root is None:
        return None
    # An explicit payload cwd is THE resolution — never triangulate with the hook
    # process's incidental cwd (a different repo there poisons both outcomes: it can
    # invent a specs dir the edited repo lacks, or mask one it has).
    if root == "":
        bases = [cwd] if cwd else [os.getcwd()]
    elif os.path.isabs(root):
        bases = [root]
    else:
        bases = [os.path.join(cwd, root)] if cwd else [root]
    for base in bases:
        if os.path.isdir(os.path.join(base, "docs", "spec")):
            return True
    for base in bases:
        if os.path.isdir(base):
            return False
    return None


def should_nudge(path, cwd=None):
    """True when the edited path is a watched operational doc in a repo whose specs
    exist or cannot be ruled out (None-state reminds; only positive absence silences)."""
    if not path:
        return False
    norm = path.replace("\\", "/")
    if not _is_opdoc(norm):
        return False
    return _spec_dir_state(_repo_root(norm), cwd) is not False


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if not isinstance(payload, dict):
        sys.exit(0)  # valid JSON of another shape (list/null/string) is not an event
    if payload.get("hook_event_name") != "PostToolUse":
        sys.exit(0)
    if not _edit_succeeded(payload):
        sys.exit(0)
    cwd = payload.get("cwd") if isinstance(payload.get("cwd"), str) else None
    if any(should_nudge(p, cwd) for p in _paths_from_tool_input(payload.get("tool_input"))):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": NUDGE,
            }
        }))
    sys.exit(0)


if __name__ == "__main__":
    main()
