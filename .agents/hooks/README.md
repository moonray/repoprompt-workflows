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
- **Claude Code — global (cross-repo).** `scripts/install.sh` symlinks the scripts into `~/.claude/hooks/` and registers them in `~/.claude/settings.json`. Because that config is global, the hooks then apply in every repo.

## Install

### Automatic (recommended)

`scripts/install.sh` symlinks every `.agents/hooks/*.py` into `~/.claude/hooks/` **and** idempotently merges the registrations below into `~/.claude/settings.json` (Claude Code). The merge is safe: it parses the JSON with `python3`, backs `settings.json` up to `settings.json.bak` before writing, never duplicates an entry, and honors `--dry-run` / `--uninstall`. Restart Claude Code after the first install.

Codex and opencode need no extra step in this repo — their adapters (`.codex/hooks.json`, `.opencode/plugins/repoprompt-hooks.mjs`) are committed here and load automatically.

### Manual (Claude Code)

Link each script, then merge the registration block into `~/.claude/settings.json`:

```bash
REPO="$(pwd)"   # run from the repo root
mkdir -p "$HOME/.claude/hooks"
for s in test-quality-reminder spec-quality-reminder spec-conformance-gate delegation-reminder; do
  ln -sfh "$REPO/.agents/hooks/$s.py" "$HOME/.claude/hooks/$s.py"
done
```

Then ensure `~/.claude/settings.json` contains these registrations (merge into any existing `hooks` object — don't duplicate matchers you already have). The file-edit matcher covers both Claude Code's native tools and RepoPrompt CE's `apply_edits` / `file_actions` MCP tools:

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Bash", "hooks": [{ "type": "command", "command": "~/.claude/hooks/test-quality-reminder.py" }] },
      { "matcher": "Edit|Write|MultiEdit|apply_edits|file_actions", "hooks": [{ "type": "command", "command": "~/.claude/hooks/spec-quality-reminder.py" }] },
      { "matcher": "Edit|Write|MultiEdit|apply_edits|file_actions", "hooks": [{ "type": "command", "command": "~/.claude/hooks/spec-conformance-gate.py" }] },
      { "matcher": "^Task$|^TaskOutput$|mcp__RepoPromptCE__agent_run", "hooks": [{ "type": "command", "command": "~/.claude/hooks/delegation-reminder.py" }] }
    ],
    "Stop": [
      { "matcher": "*", "hooks": [{ "type": "command", "command": "~/.claude/hooks/test-quality-reminder.py" }] }
    ]
  }
}
```

To remove: delete those four symlinks and strip the matching entries from `settings.json`, or run `bash scripts/install.sh --uninstall` (does both, and leaves any entries you added yourself untouched).

Hooks are a guardrail, not an absolute enforcement boundary — a model can occasionally route around them. Treat them as strong default enforcement.

## Adding a hook

- Keep guarantee logic in Python here (runtime-agnostic, JSON on stdin).
- Wire it from each backend's adapter: add a matcher to `.codex/hooks.json` and a branch to `.opencode/plugins/repoprompt-hooks.mjs`; for Claude Code add a registration to `register_claude_settings`' `regs` list in `scripts/install.sh` **and** a `settings.json` entry in the manual block above. The installer symlinks any new `.py` automatically (it scans the dir).
- Prefer a reminder over a gate unless the guarantee is observably enforceable. A gate that can only be cleared by committing forces commits on mid-flight edits — avoid.
