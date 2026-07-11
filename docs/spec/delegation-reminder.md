---
title: Delegation Reminder Hook
issue: none
status: implemented
---

# Delegation Reminder Hook

## Problem

When a delegated agent (subagent, oracle, peer agent) returns a report, its summary is a claim of completion, not evidence. Without a checkpoint at the hand-off, a delegating agent may accept "done"/"fixed" without verifying the artifact. A reminder at the delegation-tool return enforces independent verification.

## Goals

1. Detect when a delegation tool returns (`Task`, `TaskOutput`, `mcp__RepoPromptCE__agent_run`).
2. Remind the delegating agent to verify the report against ground truth (read the diff/files, run tests, exercise behavior, spot-check a load-bearing claim) before accepting.
3. Avoid false emits on similarly named non-delegation tools (e.g. `TaskCreate`/`TaskUpdate`).

## Non-Goals

- Enforce a hard gate (there is none); downstream closeout gates (review-quality revalidation, the test-quality run requirement, the spec-conformance matrix) are the backstops.
- Parse the report to confirm a follow-up read (brittle, false-positive prone).
- Fire on non-delegation events.

## Constraints

- Wired to `PostToolUse` on delegation tools; the `settings.json` matcher is the first filter, the in-script tool set is the precise gate.
- Reminder-only.

## Scenarios

### Scenario: Delegation tool return triggers the reminder
- **Given** a `PostToolUse` event with `tool_name` in {`Task`, `TaskOutput`, `mcp__RepoPromptCE__agent_run`}
- **When** the hook runs
- **Then** it emits the delegation-verification reminder

### Scenario: Non-delegation tools are ignored
- **Given** a `PostToolUse` event with `tool_name` such as `TaskCreate`, `TaskUpdate`, `TaskList`, or `Bash`
- **When** the hook runs
- **Then** no reminder

### Scenario: Non-PostToolUse events are ignored
- **Given** a `Stop` or other event
- **When** the hook runs
- **Then** no output

### Scenario: Malformed payload exits cleanly
- **Given** stdin that is not valid JSON
- **When** the hook runs
- **Then** it exits 0 with no output

## Proposed Surface

### Hook Payload

| Input | Required | Description |
|---|:---:|---|
| `hook_event_name` | yes | Must be `PostToolUse`. |
| `tool_name` | yes | The tool that returned; matched against the delegation-tool set. |

### Hook Output

| Field | Description |
|---|---|
| delegation tool | `hookSpecificOutput.additionalContext` carrying the verification reminder. |
| otherwise | no output; exit 0. |

## Open Questions

None.
