#!/usr/bin/env python3
"""Claude Code hook: nudge the matching quality skill when a spec/plan/skill artifact is edited.

Wired to PostToolUse (Edit/Write/MultiEdit/apply_edits/file_actions — native AND RepoPrompt-CE
MCP-qualified names; matchers are anchored, so bare `apply_edits` never matched
`mcp__RepoPromptCE__apply_edits` — the 2026-10-07 #47 diagnosis) in ~/.claude/settings.json,
.codex/hooks.json, and the opencode plugin.

Rule table (per affected path, aggregated into ONE reminder):
  - docs/spec/**/*.md (except README.md)                 -> run spec-quality before relying on it
  - docs/plans/*.md (except README.md)                   -> run spec-plan-readiness before implementing from it
  - .agents/skills/**/SKILL.md (recursive — nested dirs) -> apply skill-creator standards
  - .agents/hooks/*.py with no spec (detection-gated)    -> a hook without a spec is tracked debt;
    silent when docs/spec/<stem>.md exists or the spec index names a covering spec (#12)

Reminder-only — no Stop gate. A Skill invocation is observable but "quality check passed" is not
provable from it; a gate would also obstruct legitimate mid-flight edits. Guarantee is NARROW:
supported edit tools only (Bash sed/python redirects bypass this — documented, accepted).

Source of truth: `.agents/hooks/spec-quality-reminder.py` in this repo; symlink it into your
runtime's hooks directory (e.g. `~/.claude/hooks/`). NOTE: the symlink deploys SCRIPT changes
only — matcher changes in the user-owned settings.json must be merged there separately.
"""
import json
import os
import re
import sys

RULES = [
    (
        re.compile(r"(^|/)docs/spec/.+\.md$"),
        "SPEC QUALITY: you edited a spec file (docs/spec/). Before declaring spec work done, "
        "run the spec-quality skill (Skill tool) on it and resolve findings: contract-level scope, "
        "observable/identifiable/independent/focused scenarios, goal- and surface-to-scenario "
        "coverage, redundancy, ambiguity/testability, Open Questions with recommendations.",
    ),
    (
        re.compile(r"(^|/)docs/plans/[^/]+\.md$"),
        "PLAN READINESS: you edited an implementation plan (docs/plans/). Before implementing "
        "from it, run the spec-plan-readiness skill on the Spec + plan pair and clear its gates "
        "(a blocked verdict authorizes no implementation).",
    ),
    (
        re.compile(r"(^|/)\.agents/skills/.+/SKILL\.md$"),
        "SKILL STANDARDS: you edited a SKILL.md. Apply the skill-creator standards to it "
        "(frontmatter shape, description budget and triggering, distinctness vs existing skills, "
        "progressive disclosure) AND confirm docs/spec/<skill-name>.md exists — a skill without a spec is tracked debt: create one per the spec conventions if missing.",
    ),
]

_EXCLUDE_BASENAMES = {"readme.md"}

_HOOK_SCRIPT_RE = re.compile(r"(^|/)\.agents/hooks/[^/]+\.py$")

_HOOK_SPEC_NUDGE = (
    "HOOK SPEC: you edited a hook script (.agents/hooks/). A hook without a spec is tracked "
    "debt: confirm docs/spec/<stem>.md exists for it, or the docs/spec/README.md index names "
    "its covering spec — otherwise author one via the Spec workflow and add the index row "
    "and conformance matrix."
)


def _hook_spec_missing(norm_path, cwd=None):
    """The hook-spec nudge when an edited hook script has neither its own spec
    (docs/spec/<stem>.md) nor a covering spec named in the index (docs/spec/README.md
    mentioning the stem — e.g. chrome-gate is covered by the chrome spec).
    Detection-gated like model-roster-reminder: silent when covered, so specced-hook
    edits cost zero context. None when the path is not a hook script or is covered.
    Coverage the hook cannot VERIFY also nudges (workspace-relative paths outside cwd,
    e.g. RPCE multi-root deliveries) — remind rather than stay silent on a guess.
    """
    if not _HOOK_SCRIPT_RE.search(norm_path):
        return None
    idx = norm_path.find("/.agents/hooks/")
    root = norm_path[:idx] if idx != -1 else os.path.dirname(os.path.dirname(norm_path))
    stem = os.path.basename(norm_path)[:-3]  # strip .py
    candidates = [root] if os.path.isabs(root) else ([os.path.join(cwd, root), root] if cwd else [root])
    for base in candidates:
        if os.path.isfile(os.path.join(base, "docs", "spec", stem + ".md")):
            return None
        index = os.path.join(base, "docs", "spec", "README.md")
        if os.path.isfile(index):
            try:
                if stem in open(index, encoding="utf-8", errors="ignore").read():
                    return None
            except OSError:
                pass
    return _HOOK_SPEC_NUDGE

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
    (one bad input must not suppress the reminders for the other paths in a batch).
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
    """Suppress reminders for tool calls that made no change, when the runtime says so."""
    tr = payload.get("tool_response")
    if not isinstance(tr, dict):
        return True  # unknown shape -> assume success (reminders are cheap; misses are not)
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


def classify(path, cwd=None):
    """All matching rule texts for one path (a path could theoretically match none)."""
    if not path:
        return []
    norm = path.replace("\\", "/")
    if os.path.basename(norm).lower() in _EXCLUDE_BASENAMES:
        return []
    hits = []
    for rule_re, text in RULES:
        if rule_re.search(norm):
            hits.append(text)
    hook_nudge = _hook_spec_missing(norm, cwd)
    if hook_nudge:
        hits.append(hook_nudge)
    return hits


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
    reminders = []
    for p in _paths_from_tool_input(payload.get("tool_input")):
        for text in classify(p, cwd):
            if text not in reminders:
                reminders.append(text)
    if reminders:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "\n".join(reminders),
            }
        }))
    sys.exit(0)


if __name__ == "__main__":
    main()
