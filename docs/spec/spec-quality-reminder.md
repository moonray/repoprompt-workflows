---
title: Spec Quality Reminder Hook
issue: none
status: implemented
---

# Spec Quality Reminder Hook

## Problem

When an agent edits a spec, an implementation plan, or a skill definition, nothing in the lifecycle confirms the matching quality discipline was applied — `spec-quality` vetting on specs, `spec-plan-readiness` gating on plans, `skill-creator` standards on SKILL.md files. These are Skills with no shell command a hook can observe, so a hard gate would force commits on mid-flight edits. A reminder nudge at the edit is the right enforcement level.

## Goals

1. Detect when an edit touches a spec file (`docs/spec/**/*.md` excluding index READMEs), a plan file (`docs/plans/*.md` excluding index READMEs), or a skill definition (`.agents/skills/**/SKILL.md`, recursive).
2. Nudge the matching skill per affected path, aggregating every matched rule into ONE reminder.
3. Recognize edited paths across runtimes — scalar path fields (Claude Code / MCP tools), list-valued inputs (files/edits/paths), move pairs (`new_path`+`old_path`), or an `apply_patch` command (Codex/opencode).
4. Suppress reminders for tool calls the runtime reports as failed (no change was made).

## Non-Goals

- Enforce a `Stop` gate (there is none); the downstream `spec-conformance` closeout gate is the backstop.
- Detect that a skill actually ran (unobservable from a hook).
- Gate files outside the three rule classes.
- Catch edits made through tools that report no path (e.g. raw shell redirects) — documented, accepted narrowness.

## Constraints

- Wired to `PostToolUse` on `Edit|Write|MultiEdit|apply_edits|file_actions` — native AND MCP-qualified names, with anchored matchers (bare `apply_edits` never matched `mcp__RepoPromptCE__apply_edits`).
- Reminder-only; one aggregated reminder per edit event, not one per path.
- A malformed input entry is skipped, never fatal — one bad input must not suppress reminders for the other paths in a batch.

## Scenarios

### Scenario: Editing a spec file nudges spec-quality
- **Given** a `PostToolUse` event editing `docs/spec/<feature>.md` where the basename is not `README.md`
- **When** the hook runs
- **Then** it emits a reminder to run the `spec-quality` skill on the spec

### Scenario: Editing the spec index is ignored
- **Given** an edit to `docs/spec/README.md`
- **When** the hook runs
- **Then** no reminder

### Scenario: Path outside every rule class is ignored
- **Given** an edit to a path under none of the three rule classes
- **When** the hook runs
- **Then** no reminder

### Scenario: Editing a plan nudges spec-plan-readiness
- **Given** an edit to `docs/plans/<plan>.md` (basename not `README.md`)
- **When** the hook runs
- **Then** it emits a `PLAN READINESS` reminder and no `SPEC QUALITY` reminder

### Scenario: Editing a nested SKILL.md nudges skill standards
- **Given** an edit to `.agents/skills/<group>/<nested>/SKILL.md` at any depth
- **When** the hook runs
- **Then** it emits a `SKILL STANDARDS` reminder

### Scenario: Multiple rule classes in one batch aggregate
- **Given** one edit event touching both a spec file and a plan file
- **When** the hook runs
- **Then** exactly one reminder carries both rule texts, deduplicated

### Scenario: Move edits are inspected on both paths
- **Given** a file move whose destination `new_path` is under `docs/spec/` and whose `old_path` is elsewhere
- **When** the hook runs
- **Then** it emits the spec-quality reminder

### Scenario: Failed edits are suppressed
- **Given** a `PostToolUse` event whose `tool_response` reports an error status
- **When** the hook runs
- **Then** no reminder is emitted for that call

### Scenario: apply_patch edits are recognized
- **Given** a Codex/opencode `apply_patch` command whose `*** Add/Update/Delete File:` path is under `docs/spec/`
- **When** the hook runs
- **Then** it emits the reminder

### Scenario: opencode plugin payload shape is recognized
- **Given** a `tool_input` carrying spread tool args plus an extracted `file_path` under `docs/spec/`
- **When** the hook runs
- **Then** it emits the reminder, ignoring the extra arg keys

### Scenario: Malformed payload exits cleanly
- **Given** stdin that is not valid JSON or is not a `PostToolUse` event
- **When** the hook runs
- **Then** it exits 0 with no output

## Proposed Surface

### Hook Payload

| Input | Required | Description |
|---|:---:|---|
| `hook_event_name` | yes | Must be `PostToolUse`. |
| `tool_input` | yes | Scalar path field(s) (`file_path`/`path`/`filePath`/`notebook_path`/`new_path`/`old_path`), list-valued `files`/`edits`/`paths` (strings or path-bearing objects), or a `command` containing an `apply_patch`. |
| `tool_response` | no | When present and error-shaped, the call made no change — reminders are suppressed. |

### Hook Output

| Field | Description |
|---|---|
| any rule matched | `hookSpecificOutput.additionalContext` carrying every matched rule text, joined, deduplicated. |
| otherwise | no output; exit 0. |

## Open Questions

None.
