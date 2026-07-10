# Hooks

Canonical hook scripts that enforce the rules in [`../rules/global.md`](../rules/global.md) at the tool-call lifecycle. Each `.py` is runtime-agnostic Python that reads a Claude-Code-compatible JSON payload on stdin and emits either a hard `decision: block` (a gate) or a `hookSpecificOutput.additionalContext` nudge (a reminder). The guarantee logic lives once here; each runtime registers it against its own lifecycle events.

## Scripts

| Script | Kind | Event(s) | Guarantee |
|---|---|---|---|
| `test-quality-reminder.py` | reminder + Stop gate | PostToolUse:Bash, Stop | Records a run when a test command fires; at Stop, blocks if a test file was edited since the last run — edit→run→stop is allowed, edit→stop is not. Also nudges the `test-quality` skill. |
| `spec-quality-reminder.py` | reminder | PostToolUse:edit | Nudges the `spec-quality` skill when a `docs/spec/*.md` file (other than the index) is edited. |
| `spec-conformance-gate.py` | gate (block) | PostToolUse:edit | Blocks closing a spec (frontmatter `status` set to a terminal value) that has no conformance matrix; directs to the `spec-conformance` skill. |
| `delegation-reminder.py` | reminder | PostToolUse:delegation tools | Nudges independent verification when a delegated agent (`Task` / `TaskOutput` / `agent_run`) returns a report. |

Two are reminders rather than hard gates because the matching discipline is a Skill with no shell command a hook can observe run; the downstream closeout gates (review-quality revalidation, the conformance matrix) remain the backstops.

## Scope: repo-scoped vs global

The `.py` scripts are invoked two ways, and that decides their scope:

- **Codex / opencode — repo-scoped.** Bundled adapters call the scripts relative to the repo root, so they are active **only when working in this repo** (or any repo that ships `.agents/hooks/`):
  - `.codex/hooks.json` — Codex loads it from the project when trusted; it runs the scripts via `$(git rev-parse --show-toplevel)/.agents/hooks/`.
  - `.opencode/plugins/repoprompt-hooks.mjs` — opencode auto-loads it from the project plugin dir; it `execFileSync`-es the scripts.
- **Claude Code — global (cross-repo).** `scripts/install.sh` symlinks the scripts into `~/.claude/hooks/`, and you register them once in `~/.claude/settings.json`. Because that config is global, the hooks then apply in every repo.

## Install

`scripts/install.sh` symlinks every `.agents/hooks/*.py` into `~/.claude/hooks/` (Claude Code). To activate them in Claude Code, add this to `~/.claude/settings.json` (the installer prints this reminder too):

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

Codex and opencode need no extra step in this repo — their adapters are committed here and load automatically.

Hooks are a guardrail, not an absolute enforcement boundary — a model can occasionally route around them. Treat them as strong default enforcement.

## Adding a hook

- Keep guarantee logic in Python here (runtime-agnostic, JSON on stdin).
- Wire it from each backend's adapter: add a matcher to `.codex/hooks.json` and a branch to `.opencode/plugins/repoprompt-hooks.mjs`; for Claude Code add a `settings.json` entry. The installer symlinks any new `.py` automatically (it scans the dir).
- Prefer a reminder over a gate unless the guarantee is observably enforceable. A gate that can only be cleared by committing forces commits on mid-flight edits — avoid.
