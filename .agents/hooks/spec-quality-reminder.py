#!/usr/bin/env python3
"""Claude Code hook: nudge spec-quality vetting when a spec file is edited.

Wired to PostToolUse (Write/Edit/MultiEdit/apply_edits/file_actions) in ~/.claude/settings.json.
When a docs/spec/*.md file (other than the index README) is edited, emit a reminder to run the
spec-quality skill on it.

Reminder-only — there is NO Stop gate. Unlike the test-quality hook (which detects test commands
via Bash and can gate edit->run->stop), spec-quality is a Skill with no shell command, so the hook
cannot detect that vetting ran. A gate that could only be cleared by committing would force commits
on mid-flight spec edits, so we nudge instead.

Source of truth: `.agents/hooks/spec-quality-reminder.py` in this repo; symlink it into your runtime's hooks directory (e.g. `~/.claude/hooks/`).
"""
import json
import os
import re
import sys

REMINDER = (
    "SPEC QUALITY: you just edited a spec file (docs/spec/). Before declaring spec work done, "
    "run the spec-quality skill (Skill tool) and resolve any findings on the spec you added or "
    "modified: contract-level scope (no implementation planning), observable/identifiable/"
    "independent/focused scenarios, goal- and surface-to-scenario coverage, redundancy, "
    "ambiguity/testability, and Open Questions that each carry a recommendation."
)


_PATCH_FILE_RE = re.compile(
    r"^\*\*\*\s+(?:Add|Update|Delete)\s+File:\s*(.+?)\s*$", re.MULTILINE
)


def _paths_from_patch(command):
    """Codex/opencode deliver file edits as an apply_patch command (no path field)."""
    if not isinstance(command, str):
        return []
    return _PATCH_FILE_RE.findall(command)


def _paths_from_payload(payload):
    """All edited paths in the payload — a path field (Claude) or an apply_patch (Codex)."""
    ti = payload.get("tool_input")
    if not isinstance(ti, dict):
        return []
    paths = []
    for key in ("file_path", "path", "filePath", "notebook_path"):
        v = ti.get(key)
        if isinstance(v, str) and v:
            paths.append(v)
    paths.extend(_paths_from_patch(ti.get("command")))
    return paths


_SPEC_DIR_RE = re.compile(r"(^|/)docs/spec/")


def is_spec_file(path):
    if not path:
        return False
    norm = path.replace("\\", "/")
    if os.path.basename(norm).lower() == "readme.md":
        return False
    # (^|/) so it matches both absolute (Claude: /abs/docs/spec/x.md)
    # and relative (Codex apply_patch: docs/spec/x.md) paths.
    return bool(_SPEC_DIR_RE.search(norm)) and norm.endswith(".md")


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if payload.get("hook_event_name") != "PostToolUse":
        sys.exit(0)
    if any(is_spec_file(x) for x in _paths_from_payload(payload)):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": REMINDER,
            }
        }))
    sys.exit(0)


if __name__ == "__main__":
    main()
