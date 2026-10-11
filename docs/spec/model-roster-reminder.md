---
title: Model Roster Reminder Hook
issue: 10
status: implemented
---

# Model Roster Reminder Hook

## Problem
The model-routing skill's picks go stale silently: new model generations land every few months, but agents consult rosters (`app_settings`, `agent_manage`, oracle calls) without comparing what they see against the canonical table, and the skill's suggest duty depends on an agent noticing at all. An always-on reminder would be pure noise between releases — detection must be deterministic, file-based, and free unless something actually changed.

## Goals
1. Run the comparison exactly when a roster/oracle tool call happens (RPCE `app_settings` / `agent_manage` / `ask_oracle`).
2. Stay silent — zero model-context tokens — when every pick is present and no strictly newer provider generation exists.
3. Flag exactly two defect classes: a pick missing from its provider's available-model cache (roster drift), and a strictly newer provider generation than every same-provider pick.
4. Fail open: any error, missing skill, or unreadable cache means silence, never a broken tool call.
5. Register per backend: Claude Code (installer settings merge), Codex (`.codex/hooks.json`), opencode (plugin branch, warn-log bridge).

## Non-Goals
- Re-evaluating or re-pointing anything — the hook only surfaces drift and suggests the `model-routing` skill's re-evaluation.
- Network fetches, release monitoring, schedulers, or watchers — detection piggybacks on tool calls agents already make; the skill's quarterly staleness trigger is the backstop.
- Wired-settings drift (live `models.*` values vs the table) — a candidate future check, deliberately not built yet.

## Constraints
- Comparison sources are local files only: the model-routing SKILL.md table (via the global skill symlink, or the repo-relative path from the event's `cwd`) plus the runtimes' caches (`~/.codex/models_cache.json`, newest `*-cc.json` in `~/.claude/cache/model-catalog/`).
- Env overrides (`MODEL_ROUTING_SKILL`, `MODEL_ROSTER_CODEX_CACHE`, `MODEL_ROSTER_CC_CACHE`) exist so tests never touch real caches.
- The nudge names the `model-routing` skill and explicitly forbids silent re-routing.
- Pick normalization follows the two known naming shapes (`GPT-X.Y Name` → `gpt-X.Y-name`; `Claude Name X.Y` → `claude-name-X-Y`); unparsable names are skipped silently rather than guessed.

## Scenarios

### S-001: Trigger scope
- **Given** a PostToolUse event whose tool is not `mcp__RepoPromptCE__{app_settings|agent_manage|ask_oracle}`
- **When** the hook runs
- **Then** it emits nothing

### S-002: Silence when current
- **Given** a matching tool call, and caches containing every pick with no strictly newer provider generation
- **When** the hook runs
- **Then** it emits nothing — the common case costs zero model-context tokens

### S-003: Newer generation flagged
- **Given** a cache model whose provider version tuple strictly exceeds every same-provider pick's
- **When** the hook runs
- **Then** the reminder names that model, states the drift, and suggests the `model-routing` skill's re-evaluation with no silent re-routing

### S-004: Missing pick flagged
- **Given** a pick absent from its provider's available-model cache
- **When** the hook runs
- **Then** the reminder names the pick as roster drift with the same suggestion

### S-005: Fail open
- **Given** an absent model-routing skill, unreadable caches, or any internal error
- **When** the hook runs
- **Then** it exits silently with a zero status — detection never breaks the tool call

### S-006: Cross-backend registration
- **Given** the hook ships in this repo's hook infrastructure
- **When** a backend is wired
- **Then** Claude Code registers it via the installer's settings merge, Codex via `.codex/hooks.json`, and opencode via the plugin's `tool.execute.after` branch (warn-log bridge — opencode tool hooks have no model-visible injection, re-verified 2026-10-11)

## Proposed Surface

### Inputs
| Input | Required | Description |
|---|:---:|---|
| PostToolUse payload | yes | `tool_name` (matched against the roster/oracle set) and `cwd` (repo-relative skill fallback). |
| model-routing SKILL.md | yes | Source of the canonical picks; discovered via symlink, user-scope dir, or the event `cwd`. |
| Available-model caches | yes | Codex slugs and Claude ids; env-overridable for tests. |

### Output
Nothing (silent), or one `hookSpecificOutput.additionalContext` reminder: `MODEL ROUTING DRIFT: <findings>. Surface this to the user and suggest the model-routing skill's re-evaluation; do not silently re-route.`
