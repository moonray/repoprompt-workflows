# Hooks

Canonical hook scripts that enforce the rules in [`../rules/global.md`](../rules/global.md) at the tool-call lifecycle. Each `.py` is runtime-agnostic Python that reads a Claude-Code-compatible JSON payload on stdin and emits either a hard `decision: block` (a gate) or a `hookSpecificOutput.additionalContext` nudge (a reminder). The guarantee logic lives once here; each runtime registers it against its own lifecycle events.

## Scripts

| Script | Kind | Event(s) | Guarantee |
|---|---|---|---|
| `test-quality-reminder.py` | reminder + Stop gate | PostToolUse:Bash\|Skill, Stop | Records a run when a test command fires and a vet marker when the `test-quality` Skill is actually invoked (Claude Code) or explicitly attested via `--attest-vetted` (Codex — see runtime support below); at Stop, blocks if a test file was edited since the later of {last run, last vetting} — edit→run→vet→stop is allowed, edit→run→stop (vetting skipped or "applied from context") is not. |
| `spec-quality-reminder.py` | reminder | PostToolUse:edit | Nudges the matching quality skill when a spec (`docs/spec/`), a plan (`docs/plans/`), or a skill definition (`.agents/skills/**/SKILL.md`, recursive) is edited — one aggregated reminder per edit event; suppressed when the runtime reports the edit failed. Also nudges (detection-gated, #12) when a hook script (`.agents/hooks/*.py`) is edited without a spec of its own or an index-named covering spec — a hook without a spec is tracked debt; unverifiable coverage nudges. The spec-file nudge also carries the reverse-direction clause (#14): a spec edit that changes documented behavior directs the same-session check of the implementing operational docs (`.agents/slash/`, `docs/procedures/`, `docs/operations/`). |
| `spec-conformance-gate.py` | gate (block) | PostToolUse:edit | Blocks closing a spec (frontmatter `status` set to a terminal value) that has no conformance matrix; directs to the `spec-conformance` skill. |
| `delegation-reminder.py` | reminder | PostToolUse:delegation tools | Nudges independent verification when a delegated agent (`Task` / `TaskOutput` / `agent_run`) returns a report. |
| `chrome-gate.py` | gate (one-shot deny) | PreToolUse:mcp__chrome-devtools__* | Denies the session's **first** chrome-devtools MCP tool call with a reason directing to the `chrome` skill (own-app UI excepted — proceed under user-testing); every later call in the session passes silently. Fails open — a broken gate never disables browsing. |
| `model-roster-reminder.py` | reminder (detection-gated) | PostToolUse:mcp__RepoPromptCE__(app_settings\|agent_manage\|ask_oracle) | On roster/oracle tool calls, compares the `model-routing` skill's picks against the runtimes' available-model caches (`~/.codex/models_cache.json`, `~/.claude/cache/model-catalog/`); nudges ONLY when a pick is missing or a strictly newer provider generation exists — silent (zero model-context tokens) otherwise. Fails open. |
| `doc-freshness-reminder.py` | reminder | PostToolUse:Bash\|edit | Nudges the `document`-skill drift audit when a tracked work item is closed — shell close shapes (`tw.py`/`$TW`/`issue.sh`/`close.sh`/`gh issue close`) or a file-backend frontmatter flip to `status: closed` — so doc freshness is part of closeout, not a later user prompt. Fails open. |
| `spec-accuracy-reminder.py` | reminder | PostToolUse:edit | Nudges a same-session spec-accuracy check when an operational doc (`.agents/slash/*.md` runbook, `docs/procedures/*.md`, `docs/operations/*.md`) is edited in a repo with a `docs/spec/` dir — fix or flag any spec (or conformance matrix) still describing the OLD behavior, now, while the change context is fresh; silent on positively spec-less repos, READMEs, non-watched paths, and failed edits. Fills the change-time direction the sibling hooks leave open (spec-quality owns spec-edit quality, doc-freshness owns item-close audits). Fails open. |

### Runtime support for the test-quality Stop gate (#2)

- **Claude Code — enforced, skill marker.** PostToolUse matcher `Bash|Skill`: a real Skill-tool invocation of `test-quality` stamps the vet marker.
- **Codex — enforced, explicit attestation.** Codex routes `Stop` but emits no hook event for skill invocations, so its wiring (`.codex/hooks.json`) invokes the hook with `TQ_HOOK_RUNTIME=codex`. The vetting act is the deliberate attestation: `python3 "$(git rev-parse --show-toplevel)/.agents/hooks/test-quality-reminder.py" --attest-vetted` (honored only under that env; the Stop reason names it). On runtimes without the env, attestation is inert — a real Skill invocation stays the only path.
- **opencode — documented-unsupported.** Its Stop equivalent (`session.idle`) fires after the turn ends and cannot block; the plugin logs a reactive warn only. The absence of the gate is documented here, in the plugin mapping, and in the spec — never a silent run-only clear.

Two are reminders rather than hard gates because the matching discipline is a Skill with no shell command a hook can observe run; the downstream closeout gates (review-quality revalidation, the conformance matrix) remain the backstops.

## Scope: repo-scoped vs global

The `.py` scripts are invoked three ways, and that decides their scope:

- **Claude Code — global (cross-repo).** `scripts/install.sh` symlinks the scripts into `~/.claude/hooks/` and registers them in `~/.claude/settings.json`. Because that config is global, the hooks then apply in every repo.
- **Codex — global user layer + optional project layer.** Codex discovers hooks from every active config layer: `~/.codex/hooks.json` / `~/.codex/config.toml` (user level — loads for EVERY project, even untrusted ones) merges with `<repo>/.codex/hooks.json` (project level, trust-gated). `scripts/install.sh` maintains the user-level file (scripts via `$HOME/.claude/hooks/`); review/trust it once via `/hooks` after the first write. Verified live 2026-11-03: the user-level file alone fires in a brand-new repo with no project wiring — discovery → dispatch → nudge injection. The committed `.codex/hooks.json` in this repo remains for consumers who have not installed the global layer (it resolves scripts repo-relative via `git rev-parse --show-toplevel`).
- **opencode — project plugin with global fallback; package dir + config entry.** opencode 2.x loads plugin PACKAGES (directories with package.json) declared in a config `plugin` array — bare `.mjs` paths are rejected ("configured plugin path must be a directory", verified live 2026-11-03) and 2.x requires the v2 `export default Plugin.define({ id, setup })` API. The committed `.opencode/plugins/repoprompt-hooks/` package resolves scripts repo-relative first, then falls back to the global `~/.claude/hooks/` symlinks. `scripts/install.sh` appends the package path to `~/.config/opencode/opencode.jsonc`'s `plugin` array — the verified global mechanism (server hot-reloads it). Reminder hooks surface as structured warn logs — opencode has no model-visible `additionalContext` injection (see the plugin header).

## Install

### Automatic (recommended)

`scripts/install.sh` symlinks every `.agents/hooks/*.py` into `~/.claude/hooks/`, idempotently merges the registrations into `~/.claude/settings.json` (Claude Code, global), writes the global Codex layer `~/.codex/hooks.json` (every repo — review/trust once via Codex's `/hooks`), and appends the plugin package to `~/.config/opencode/opencode.jsonc`'s `plugin` array (opencode 2.x global mechanism, verified live). Each merge is safe: JSON parsed with `python3`, backup written before changing anything, no duplicate entries, `--dry-run` / `--uninstall` honored. Restart Claude Code after the first install; trust the Codex layer once via `/hooks`.

Codex and opencode need no extra step in this repo — their adapters (`.codex/hooks.json`, `.opencode/plugins/repoprompt-hooks.mjs`) are committed here and load automatically; the installer additionally maintains the global layers for every OTHER repo.

### Manual (Claude Code)

Link each script, then merge the registration block into `~/.claude/settings.json`:

```bash
REPO="$(pwd)"   # run from the repo root
mkdir -p "$HOME/.claude/hooks"
for s in test-quality-reminder spec-quality-reminder spec-accuracy-reminder spec-conformance-gate delegation-reminder chrome-gate model-roster-reminder doc-freshness-reminder; do
  ln -sfh "$REPO/.agents/hooks/$s.py" "$HOME/.claude/hooks/$s.py"
done
```

Then ensure `~/.claude/settings.json` contains these registrations (merge into any existing `hooks` object — don't duplicate matchers you already have). The file-edit matcher is anchored and MCP-qualified so bare names never substring-match other tools; commands quote `$HOME` so homes with spaces work; `scripts/install.sh` is the canonical source — this example mirrors it exactly:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "^mcp__chrome-devtools__", "hooks": [{ "type": "command", "command": "python3 \"$HOME/.claude/hooks/chrome-gate.py\"" }] }
    ],
    "PostToolUse": [
      { "matcher": "Bash|Skill", "hooks": [{ "type": "command", "command": "python3 \"$HOME/.claude/hooks/test-quality-reminder.py\"" }] },
      { "matcher": "Bash", "hooks": [{ "type": "command", "command": "python3 \"$HOME/.claude/hooks/doc-freshness-reminder.py\"" }] },
      { "matcher": "^(?:Edit|Write|MultiEdit|apply_edits|file_actions|mcp__RepoPromptCE__(?:apply_edits|file_actions))$", "hooks": [{ "type": "command", "command": "python3 \"$HOME/.claude/hooks/spec-quality-reminder.py\"" }] },
      { "matcher": "^(?:Edit|Write|MultiEdit|apply_edits|file_actions|mcp__RepoPromptCE__(?:apply_edits|file_actions))$", "hooks": [{ "type": "command", "command": "python3 \"$HOME/.claude/hooks/spec-accuracy-reminder.py\"" }] },
      { "matcher": "^(?:Edit|Write|MultiEdit|apply_edits|file_actions|mcp__RepoPromptCE__(?:apply_edits|file_actions))$", "hooks": [{ "type": "command", "command": "python3 \"$HOME/.claude/hooks/spec-conformance-gate.py\"" }] },
      { "matcher": "^(?:Edit|Write|MultiEdit|apply_edits|file_actions|mcp__RepoPromptCE__(?:apply_edits|file_actions))$", "hooks": [{ "type": "command", "command": "python3 \"$HOME/.claude/hooks/doc-freshness-reminder.py\"" }] },
      { "matcher": "^Task$|^TaskOutput$|mcp__RepoPromptCE__agent_run", "hooks": [{ "type": "command", "command": "python3 \"$HOME/.claude/hooks/delegation-reminder.py\"" }] },
      { "matcher": "^mcp__RepoPromptCE__(?:app_settings|agent_manage|ask_oracle)$", "hooks": [{ "type": "command", "command": "python3 \"$HOME/.claude/hooks/model-roster-reminder.py\"" }] }
    ],
    "Stop": [
      { "matcher": "*", "hooks": [{ "type": "command", "command": "python3 \"$HOME/.claude/hooks/test-quality-reminder.py\"" }] }
    ]
  }
}
```

To remove: delete those eight symlinks and strip the matching entries from `settings.json`, or run `bash scripts/install.sh --uninstall` (does both, and leaves any entries you added yourself untouched).

Hooks are a guardrail, not an absolute enforcement boundary — a model can occasionally route around them. Treat them as strong default enforcement.

## Adding a hook

- Keep guarantee logic in Python here (runtime-agnostic, JSON on stdin).
- Wire it from each backend's adapter: add a matcher to `.codex/hooks.json` and a branch to `.opencode/plugins/repoprompt-hooks.mjs`; for Claude Code add a registration to `register_claude_settings`' `regs` list in `scripts/install.sh` **and** a `settings.json` entry in the manual block above. The installer symlinks any new `.py` automatically (it scans the dir).
- Prefer a reminder over a gate unless the guarantee is observably enforceable. A gate that can only be cleared by committing forces commits on mid-flight edits — avoid.
- Live-fire a newly registered hook without restarting: a fresh `agent_run` subagent session loads user-global registrations at its own start — run the control call (expect silence), inject a bounded drift probe into the hook's inputs, run again (expect the nudge), byte-compare against direct invocation, and revert the probe exactly (validated 2026-10-11 on the roster hook).
