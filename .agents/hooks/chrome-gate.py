#!/usr/bin/env python3
"""chrome-gate — one-shot PreToolUse nudge for the chrome skill.

Denies the FIRST mcp__chrome-devtools__* tool call of a session with a reason
directing the agent to load the chrome skill (root-first warm-up protocol);
every later call in that session passes silently. Fails open on any error —
a broken or missing gate must never disable browsing (spec constraint, S-013).
"""
import json
import os
import sys
import tempfile

# Both runtime namings: Claude Code keeps the server's hyphen
# (mcp__chrome-devtools__), Codex normalizes it to an underscore
# (mcp__chrome_devtools__) — observed in a live payload 2026-10-10.
MATCH = ("mcp__chrome-devtools__", "mcp__chrome_devtools__")
REASON = (
    "chrome skill gate (one-time): before driving an external site with "
    "chrome-devtools, load the chrome skill (root-first warm-up, challenge "
    "discipline, escalation ladder), then retry this call. If this is your "
    "own app's UI (user-testing scope), proceed as you were."
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # unparseable input — allow silently
    tool = str(payload.get("tool_name") or "")
    if not tool.startswith(MATCH):
        return 0  # not our tool — allow silently
    session = str(payload.get("session_id") or "").strip()
    if not session:
        return 0  # no session identity — allow silently
    marker = os.path.join(tempfile.gettempdir(), f"chrome-gate-{session}")
    try:
        if os.path.exists(marker):
            return 0  # already nudged this session — allow
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY)  # atomic once-only claim
        os.write(fd, tool.encode())
        os.close(fd)
    except FileExistsError:
        return 0  # raced a concurrent call — it issued the nudge; allow
    except Exception:
        return 0  # cannot establish once-only state — fail open
    json.dump(
        {
            "decision": "block",  # legacy/bridge schema shape
            "reason": REASON,
            "hookSpecificOutput": {  # current Claude Code schema
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": REASON,
            },
        },
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
