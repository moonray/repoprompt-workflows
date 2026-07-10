# Hooks

Canonical hook scripts that enforce the rules in [`../rules/global.md`](../rules/global.md) at the tool-call lifecycle. Each is runtime-agnostic Python that reads a Claude-Code-compatible JSON payload on stdin and emits either a hard `decision: block` (a gate) or a `hookSpecificOutput.additionalContext` nudge (a reminder). The guarantee logic lives once here; each runtime registers it against its own lifecycle events.

## Scripts

| Script | Kind | Event(s) | Guarantee |
|---|---|---|---|
| `test-quality-reminder.py` | reminder + Stop gate | PostToolUse:Bash, Stop | Records a run when a test command fires; at Stop, blocks if a test file was edited since the last run — edit→run→stop is allowed, edit→stop is not (committing/cleaning also clears it). Also nudges the `test-quality` skill. |
| `spec-quality-reminder.py` | reminder | PostToolUse:edit | Nudges the `spec-quality` skill when a `docs/spec/*.md` file (other than the index) is edited. |
| `spec-conformance-gate.py` | gate (block) | PostToolUse:edit | Blocks closing a spec (frontmatter `status` set to a terminal value) that has no conformance matrix; directs to the `spec-conformance` skill. |
| `delegation-reminder.py` | reminder | PostToolUse:delegation tools | Nudges independent verification when a delegated agent (`Task` / `TaskOutput` / `agent_run`) returns a report. |

Two are reminders rather than hard gates because the matching discipline is a Skill with no shell command a hook can observe run; the downstream closeout gates (review-quality revalidation, the conformance matrix) remain the backstops.

## Register per backend

The payload is Claude-Code-compatible, so the same `.py` runs nearly unchanged on backends whose payload matches; where a backend differs, a thin adapter translates.

- **Claude Code** — register in `~/.claude/settings.json` against `PostToolUse` / `Stop` (matchers in the table) and symlink each script into `~/.claude/hooks/`.
- **Codex** — `.codex/hooks.json` (repo) or `~/.codex/hooks.json`; file edits arrive as an `apply_patch` command, which the scripts parse for the target path.
- **opencode** — a `.mjs` plugin in `.opencode/plugins/` bridges to these scripts.
- **pi** — a `.ts` extension in `~/.pi/agent/extensions/` bridges to these scripts.

Example Claude Code wiring (one entry per hook; matchers vary):

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Bash", "hooks": [{ "type": "command", "command": "~/.claude/hooks/test-quality-reminder.py" }] },
      { "matcher": "Edit|Write|MultiEdit", "hooks": [{ "type": "command", "command": "~/.claude/hooks/spec-quality-reminder.py" }] },
      { "matcher": "Edit|Write|MultiEdit", "hooks": [{ "type": "command", "command": "~/.claude/hooks/spec-conformance-gate.py" }] },
      { "matcher": "^Task$|^TaskOutput$|mcp__RepoPromptCE__agent_run", "hooks": [{ "type": "command", "command": "~/.claude/hooks/delegation-reminder.py" }] }
    ],
    "Stop": [
      { "matcher": "*", "hooks": [{ "type": "command", "command": "~/.claude/hooks/test-quality-reminder.py" }] }
    ]
  }
}
```

Hooks are a guardrail, not an absolute enforcement boundary — a model can occasionally route around them. Treat them as strong default enforcement.

## Adding a hook

- Keep guarantee logic in Python here (runtime-agnostic, JSON on stdin).
- Register per backend; adapt the payload shape only where a backend differs.
- Prefer a reminder over a gate unless the guarantee is observably enforceable. A gate that can only be cleared by committing forces commits on mid-flight edits — avoid.
