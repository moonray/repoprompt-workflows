#!/usr/bin/env python3
"""Claude Code hook: nudge an oracle review when a session commits a substantial
change set without any oracle consultation.

PostToolUse reminder (fails open — a crashed hook never traps the agent).
Accumulates per-session state from tool events:

  - edit events (edit tools or apply_patch commands): distinct edited paths;
    any write under docs/spec|specs/plans sets the spec/plan flag
  - ask_oracle (MCP-qualified name ending in ask_oracle): stamps consulted
  - a successful `git commit` shell command: the trigger moment

At the commit, if the session edited >=3 distinct non-doc files OR wrote a
spec/plan doc, and never consulted the oracle, emit ONE nudge (per session)
directing a bounded ask_oracle review pass — or a reasoned skip. Silent on
everything else; never blocks.

Why commit-keyed rather than Stop: Stop fires every turn, so it would nudge
mid-flight work; the commit is the observable "declaring this change done"
moment (the same surface doc-freshness-reminder rides for closes). Evidence
base: 2026-11-05 chat-mining sweep — oracle compliance tracks enforcement, not
the harness's soft guidance line; ad-hoc sessions skipped oracle in ~all of
150+ sessions over two months, and the one ad-hoc session that consulted caught
6 verified defects. Spec: docs/spec/oracle-review-reminder.md.

Source of truth: `.agents/hooks/oracle-review-reminder.py` in this repo; symlink
it into your runtime's hooks directory (e.g. `~/.claude/hooks/`).
"""
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time

CACHE_DIR = os.environ.get("ORACLE_REVIEW_STATE_DIR") or os.path.expanduser(
    "~/.cache/oracle-review-hook"
)
_STATE_TTL = 7 * 24 * 3600  # prune session state older than a week on write

NUDGE = (
    "ORACLE REVIEW: this session is committing a substantial change set (>=3 files or a "
    "spec/plan write) with no oracle consultation observed. Before declaring the work "
    "done, run one `ask_oracle` review pass (mode:review) over the diff or change summary "
    "— routed per the `model-routing` skill (Review & Refine) — and fold confirmed "
    "findings; or state why an independent lane isn't warranted (trivial or mechanical "
    "change, review-depth quick band, user declined). One-time nudge for this session."
)

# review-depth's S/M boundary: at or below this many changed lines in the landed commit,
# the change sizes `quick` and an oracle lane is not worth premium tokens.
_SMALL_CHANGE_LINES = 150


def _commit_lines(command, cwd):
    """Changed lines of the just-landed commit when it ran in `cwd` (no -C/--git-dir).
    None when unmeasurable -> caller nudges (fail toward the reminder, not silence)."""
    if re.search(r"\s(?:-C\s|--git-dir|--work-tree)", command):
        return None  # commit landed elsewhere; cwd stats would be the wrong commit
    commit_at = _COMMIT_RE.search(command)
    if commit_at and re.search(
        r"\bcd\s+(?:\"[^\"]*\"|'[^']*'|\S+)\s*(?:&&|;)", command[: commit_at.start()]
    ):
        return None  # `cd <dir> && git commit …` — same blind spot as -C (observed live 2026-11-05)
    try:
        out = subprocess.run(
            ["git", "-C", cwd or ".", "show", "--shortstat", "--format=", "HEAD"],
            capture_output=True, text=True, timeout=5,
        ).stdout
        m_ins = re.search(r"(\d+) insertion", out)
        m_del = re.search(r"(\d+) deletion", out)
        if not m_ins and not m_del:
            return None
        return int(m_ins.group(1) if m_ins else 0) + int(m_del.group(1) if m_del else 0)
    except Exception:
        return None


# Oracle observation: the MCP-qualified tool name (any server prefix) or bare name.
_ORACLE_TOOL_RE = re.compile(r"(?:^|__)ask_oracle$")
# Commit adjacency: `git commit`, `git -C <path> commit`, &&-chained segments; flag forms
# like `git -c k=v commit` are covered by the (flag value)* group.
# `git commit` in command position: short global flags take a separate value token
# (-C path, -c k=v); long flags take =value only (--git-dir=X, --no-pager).
# commit(?![\w-]) keeps commit-tree/commit-graph from matching; --dry-run is a
# non-writing mode and is excluded separately in main().
_COMMIT_RE = re.compile(
    r"\bgit\s+(?:(?:(?:-[A-Za-z][\w-]*\s+(?:\"[^\"]*\"|'[^']*'|\S+))|(?:--[\w-]+(?:=\S+)?))\s+)*commit(?![\w-])"
)
_DOC_EXT_RE = re.compile(r"\.(md|markdown|mdx|txt|rst|adoc)$", re.IGNORECASE)
_SPEC_PLAN_RE = re.compile(r"(^|/)docs/(spec|specs|plans)/")
# Steering markdown is product, not prose: skills/workflows/rules/slash under .agents
# (or any SKILL.md) count as non-doc even though they carry a doc extension — in this
# repo those files ARE the behavior-defining surface (oracle review, 2026-11-05).
_STEERING_RE = re.compile(r"(^|/)\.agents/(skills|workflows|rules|slash)/|(^|/)SKILL\.md$")


def _norm(path):
    p = path.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    p = re.sub(r"/{2,}", "/", p)
    return p.rstrip("/") or p


def _is_doc(path):
    if _STEERING_RE.search(path):
        return False
    return bool(_DOC_EXT_RE.search(path))


def _is_spec_plan(path):
    return bool(_SPEC_PLAN_RE.search(path))


def _paths_from_patch(command):
    """Codex/opencode deliver file edits as an apply_patch command (no path field)."""
    if not isinstance(command, str):
        return []
    return re.findall(
        r"^\*\*\*\s+(?:Add|Update|Delete)\s+File:\s*(.+?)\s*$", command, re.MULTILINE
    )


def _paths_from_payload(ti):
    if not isinstance(ti, dict):
        return []
    paths = []
    for k in ("file_path", "path", "filePath", "notebook_path"):
        v = ti.get(k)
        if isinstance(v, str) and v:
            paths.append(v)
    paths.extend(_paths_from_patch(ti.get("command")))
    return paths


def _succeeded(payload):
    """Suppress contribution for calls the runtime reports as failed; unknown = success."""
    tr = payload.get("tool_response")
    if not isinstance(tr, dict):
        return True
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


def _state_path(payload):
    key_src = payload.get("session_id") or payload.get("cwd") or "default"
    key = hashlib.sha1(str(key_src).encode()).hexdigest()[:12]
    return os.path.join(CACHE_DIR, f"sess-{key}.json")


def _fresh(path):
    """Expired state resets (prune-on-write alone never clears an actively reused key)."""
    try:
        if time.time() - os.path.getmtime(path) > _STATE_TTL:
            return False
    except OSError:
        pass
    return True


def _load(path):
    if not _fresh(path):
        return {"files": [], "spec": False, "consulted": False, "nudged": False}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {"files": [], "spec": False, "consulted": False, "nudged": False}


def _save(path, state):
    """Atomic replace, under an flock held by the caller around load-modify-save."""
    fd = None
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=CACHE_DIR, prefix=".tmp-")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            fd = None
            json.dump(state, f)
        os.replace(tmp, path)
        # Opportunistic, bounded prune of stale session state (only our prefix).
        now = time.time()
        for name in os.listdir(CACHE_DIR):
            if not name.startswith("sess-"):
                continue
            fp = os.path.join(CACHE_DIR, name)
            try:
                if now - os.path.getmtime(fp) > _STATE_TTL:
                    os.unlink(fp)
            except OSError:
                pass
    except Exception:
        pass  # fail open


def _locked(path):
    """flock the state file's sidecar lock for the whole load-modify-save transaction."""
    lock = open(path + ".lock", "w")
    fcntl.flock(lock, fcntl.LOCK_EX)
    return lock


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if not isinstance(payload, dict):
        sys.exit(0)
    if payload.get("hook_event_name") != "PostToolUse":
        sys.exit(0)

    tool_name = str(payload.get("tool_name") or "")
    ti = payload.get("tool_input")
    ti = ti if isinstance(ti, dict) else {}
    sp = _state_path(payload)
    try:
        lock = _locked(sp)
    except Exception:
        lock = None  # fail open: proceed unlocked rather than trapping the agent
    try:
        _main_locked(payload, tool_name, ti, sp)
    finally:
        if lock:
            try:
                lock.close()
            except Exception:
                pass


def _main_locked(payload, tool_name, ti, sp):
    state = _load(sp)

    # 1. Oracle consultation observed — any outcome counts (transport failure != skip).
    if _ORACLE_TOOL_RE.search(tool_name):
        state["consulted"] = True
        _save(sp, state)
        return

    # 2. Edit events accumulate the session's change-set picture.
    paths = _paths_from_payload(ti)
    if paths:
        if _succeeded(payload):
            files = set(state.get("files") or [])
            for p in paths:
                np = _norm(p)
                files.add(np)
                if _is_spec_plan(np):
                    state["spec"] = True
            state["files"] = sorted(files)
            _save(sp, state)
        return

    # 3. Shell events: the commit is the trigger moment.
    command = ti.get("command")
    is_shell = tool_name.lower() in {"bash", "shell"}
    dry_run = isinstance(command, str) and "--dry-run" in command
    if (
        is_shell
        and isinstance(command, str)
        and not dry_run
        and _COMMIT_RE.search(command)
        and _succeeded(payload)
    ):
        if state.get("nudged") or state.get("consulted"):
            sys.exit(0)
        non_doc = [p for p in (state.get("files") or []) if not _is_doc(p)]
        if len(non_doc) >= 3 or state.get("spec"):
            # Token-economy gate: a spec/plan write always warrants the (cheap, document-
            # shaped) consultation; a code change at or below review-depth's quick band
            # does not — measure the landed commit when it ran in cwd, and stay silent.
            if not state.get("spec"):
                lines = _commit_lines(command, payload.get("cwd"))
                if lines is not None and lines <= _SMALL_CHANGE_LINES:
                    return
            state["nudged"] = True
            _save(sp, state)
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": NUDGE,
                }
            }))
    sys.exit(0)


if __name__ == "__main__":
    main()
