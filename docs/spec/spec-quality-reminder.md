---
title: Spec Quality Reminder Hook
issue: none
status: implemented
---

# Spec Quality Reminder Hook

## Problem

When an agent edits a spec file, nothing in the lifecycle confirms the spec was checked against `spec-quality` discipline (contract-level scope, observable scenarios, goal/surface coverage, redundancy, ambiguity). Because `spec-quality` is a Skill with no shell command a hook can observe, a hard gate would force commits on mid-flight spec edits. A reminder nudge at the edit is the right enforcement level.

## Goals

1. Detect when an edit touches a spec file (`docs/spec/*.md` excluding the index).
2. Nudge the `spec-quality` skill on such edits.
3. Recognize edited paths across runtimes — a path field (Claude Code) or an `apply_patch` command (Codex/opencode).

## Non-Goals

- Enforce a `Stop` gate (there is none); the downstream `spec-conformance` closeout gate is the backstop.
- Detect that the skill actually ran (unobservable from a hook).
- Gate non-spec files.

## Constraints

- Wired to `PostToolUse` on `Write|Edit|MultiEdit|apply_edits|file_actions`.
- A spec file matches `docs/spec/`, ends in `.md`, and its basename is not `readme.md`.
- Reminder-only.

## Scenarios

### Scenario: Editing a spec file nudges spec-quality
- **Given** a `PostToolUse` event editing `docs/spec/<feature>.md` where the basename is not `README.md`
- **When** the hook runs
- **Then** it emits a reminder to run the `spec-quality` skill on the spec

### Scenario: Editing the spec index is ignored
- **Given** an edit to `docs/spec/README.md`
- **When** the hook runs
- **Then** no reminder

### Scenario: Non-spec file is ignored
- **Given** an edit to a path outside `docs/spec/`
- **When** the hook runs
- **Then** no reminder

### Scenario: apply_patch edits are recognized
- **Given** a Codex/opencode `apply_patch` command whose `*** Add/Update/Delete File:` path is under `docs/spec/`
- **When** the hook runs
- **Then** it emits the reminder

### Scenario: Malformed payload exits cleanly
- **Given** stdin that is not valid JSON or is not a `PostToolUse` event
- **When** the hook runs
- **Then** it exits 0 with no output

## Proposed Surface

### Hook Payload

| Input | Required | Description |
|---|:---:|---|
| `hook_event_name` | yes | Must be `PostToolUse`. |
| `tool_input` | yes | A path field (`file_path`/`path`/`filePath`/`notebook_path`) or a `command` containing an `apply_patch`. |

### Hook Output

| Field | Description |
|---|---|
| spec path edited | `hookSpecificOutput.additionalContext` carrying the `spec-quality` reminder. |
| otherwise | no output; exit 0. |

## Open Questions

None.
