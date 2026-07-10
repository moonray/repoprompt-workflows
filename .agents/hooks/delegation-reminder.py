#!/usr/bin/env python3
"""Claude Code hook: nudge independent verification when a delegated agent reports.

Wired to PostToolUse (Task / TaskOutput / mcp__RepoPromptCE__agent_run) in ~/.claude/settings.json.
When a delegation tool returns, emit a reminder that the subagent's report is a claim, not
evidence — the delegating agent must read the committed diff/files, run the affected tests, or
exercise the rendered behavior, and spot-check at least one load-bearing claim before accepting
'done'/'fixed'/'complete'.

Reminder-only — there is NO Stop gate. A true gate would require parsing the report to learn
which files were claimed and confirming a follow-up read of them, which is brittle and
false-positive prone. The downstream gates (review-quality revalidation, the test-quality run
requirement, the spec-conformance matrix) remain the backstops that refuse to close on opinion
alone; this hook adds the first checkpoint at the hand-off.

This is the inbound companion to global.md's closeout gates; see "Verifying Delegated Work
(acceptance gate)" in rules/global.md.

The matcher in settings.json (^Task$|^TaskOutput$|mcp__RepoPromptCE__agent_run) is the first
filter; the set below is the precise gate (so a too-broad matcher can never cause a false emit,
e.g. on the unrelated TaskCreate/TaskUpdate/... todo tools that merely contain "Task").

Source of truth: `.agents/hooks/delegation-reminder.py` in this repo; symlink it into your runtime's hooks directory (e.g. `~/.claude/hooks/`).
"""
import json
import sys

REMINDER = (
    "DELEGATION VERIFICATION: a delegated agent just returned a report. Its summary is a "
    "claim of completion, not evidence — reports can be optimistic, partial, or hallucinated, "
    "and 'done'/'fixed'/'complete' in a return value does not make the underlying work so. "
    "Before accepting the task as complete, independently verify the actual artifact against the "
    "claim: read the committed diff or files, run the affected tests, or exercise the rendered "
    "behavior. Spot-check at least one load-bearing claim against ground truth rather than "
    "trusting the narrative. See 'Verifying Delegated Work (acceptance gate)' in rules/global.md."
)

# Tools that hand back a delegated agent's work/report.
#   Task                          — Claude Code built-in subagent dispatch (vanilla CC)
#   TaskOutput                    — retrieval of a background agent's output
#   mcp__RepoPromptCE__agent_run  — RepoPrompt CE delegation (start/poll/wait/steer)
_DELEGATION_TOOLS = {"Task", "TaskOutput", "mcp__RepoPromptCE__agent_run"}


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if payload.get("hook_event_name") != "PostToolUse":
        sys.exit(0)
    if payload.get("tool_name", "") in _DELEGATION_TOOLS:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": REMINDER,
            }
        }))
    sys.exit(0)


if __name__ == "__main__":
    main()
