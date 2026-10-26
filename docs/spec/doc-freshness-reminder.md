---
title: Doc-Freshness Reminder Hook
issue: 12
status: implemented
---

# Doc-Freshness Reminder Hook

## Problem

Closing a tracked work item verifies landed code evidence (the referencing commit/PR on the default branch) but never doc/spec freshness. Across workspaces, a recurring pattern (2026-08→2026-10, 7 observed instances) shows the user prompting for a docs/spec drift audit after issue closeout — and the prompts caught real drift in at least five instances. Agents name the `document` skill as the designated drift-audit path and still run it only when asked: a trigger gap, not a knowledge gap. Autonomous backlog runs already close this loop with an end-of-run doc sync; interactive closes had no trigger. The sibling `spec-conformance-gate` hook explicitly documents the unhandled half this hook fills: closes that don't touch a spec file.

## Goals

1. Detect a tracked-work-item close at the moment it happens — a recognized close shell command, or a file-edit event on a ledger item whose status is `closed`.
2. Nudge the closing agent to run the change-driven drift audit (the `document` skill, code mode, over the closed item's landed span; dry-run default; findings reported with the close) before the work is declared done.
3. Stay silent on non-close activity: non-adjacent prose that names close commands, PR closes, failed tool calls, and ledger/doc edits that do not signal a close.
4. Fail open — a malformed input never traps the agent.

## Non-Goals

- No gate/blocking: "audit ran" is not provable from a Skill invocation, and exempt-label closes change no code; the nudge names the skip condition instead of blocking. A test-quality-style Stop gate is a documented escalation path if the reminder proves weak.
- No verification that the audit actually ran (no marker machinery).
- No autonomy over doc edits — the nudge pins dry-run default and an explicit apply grant.
- No coverage of runtimes whose tool events never reach the hook (documented-unsupported per runtime, like the opencode Stop gate).

## Constraints

- Wired to PostToolUse on shell and file-edit events; the runtime matcher is the first filter, the in-script detection is the precise gate.
- Reminder-only; the script never deliberately exits non-zero. A crash mid-execution is tolerated by the runtime's fail-open hook handling, not by this contract.
- Command recognition is adjacency-based (close as the immediate subcommand/argument after the script name or variable). `close.sh` additionally requires a ref-shaped argument (issue ID, URL, number, or `owner/repo#N`) so bare prose mentions stay silent.
- Accepted residual: an exact close-subcommand sequence embedded in prose (e.g. `gh issue close` inside a quoted commit message) fires — fixed neither by adjacency nor ref-shape; brittle command-position parsing would cost more than the residual.
- Ledger detection is state-based, not transition-based: the event carries no prior content, so an edit to an item whose status already reads `closed` also nudges.
- Exactly one nudge per event even when several signals match.
- Tool-response suppression recognizes explicit failure indicators only: `is_error`/`isError` true, a truthy `error`, `status: "error"`, `ok`/`success` false. Absent or unrecognized response shapes are treated as success (nudges are cheap; misses are not); a bare nonzero exit code in the response is not a recognized indicator.

## Scenarios

### Scenario S-001: Canonical variable-form close command fires the nudge
- **Given** a PostToolUse shell event whose command closes an item through the track-work CLI variable form (`python3 "$TW" close <ref>`, where the script path lives in a shell variable — no literal script name in the command)
- **When** the hook runs
- **Then** it emits the doc-freshness nudge

### Scenario S-002: All other recognized close shapes fire the nudge
- **Given** a PostToolUse shell event whose command is an explicit-path `tw.py close`, a bare `tw close`, an `issue.sh close`, a `close.sh <ref>` invocation with a ref-shaped argument, or a `gh issue close`
- **When** the hook runs
- **Then** it emits the doc-freshness nudge

### Scenario S-003: A ledger edit whose item reads closed fires the nudge
- **Given** a PostToolUse file-edit event whose edited file is a ledger item (`.md`, immediate child of the issues dir) whose frontmatter status is `closed` — including a re-edit of an item already closed
- **When** the hook runs
- **Then** it emits the doc-freshness nudge

### Scenario S-004: The nudge directs a bounded, granted audit, exactly once
- **Given** any single recognized close signal (S-001–S-003)
- **When** the hook emits
- **Then** exactly one nudge is emitted, directing to the `document` skill in code mode, change-driven over the closed item's landed span, dry-run first, with doc-side edits applied only under an explicit grant, findings reported with the close before the work is declared done, and the skip condition named (exempt closes that changed no code, docs, or steering surfaces, skipped with a stated reason)

### Scenario S-005: Non-adjacent prose naming close commands stays silent
- **Given** a PostToolUse shell event whose command contains a close-script name and the word "close" but not as an adjacent subcommand (e.g. a commit message naming the supported close shapes), or names `close.sh` with no ref-shaped argument after it
- **When** the hook runs
- **Then** no nudge

### Scenario S-006: An exact close-subcommand sequence in prose still fires (accepted residual)
- **Given** a PostToolUse shell event whose command embeds a literal close subcommand sequence (e.g. `gh issue close` inside a quoted commit message)
- **When** the hook runs
- **Then** it emits the nudge

### Scenario S-007: A PR close is not an item close
- **Given** a PostToolUse shell event whose command is `gh pr close <n>`
- **When** the hook runs
- **Then** no nudge

### Scenario S-008: A tool call that reports failure stays silent; unknown outcomes nudge
- **Given** a PostToolUse event for a recognized close command or ledger edit whose tool response carries an explicit failure indicator (the Constraints list)
- **When** the hook runs
- **Then** no nudge — while an absent or unrecognized response shape still nudges

### Scenario S-009: Non-closing edits stay silent
- **Given** a PostToolUse file-edit event on a ledger item whose frontmatter status is an open state, on a ledger item with absent or malformed frontmatter, on an unreadable or missing file, or on any non-ledger document
- **When** the hook runs
- **Then** no nudge

### Scenario S-010: Foreign events are ignored
- **Given** a hook event other than PostToolUse (e.g. Stop)
- **When** the hook runs
- **Then** exit 0 with no output

### Scenario S-011: Malformed input exits cleanly
- **Given** stdin that is not valid JSON, or valid JSON that is not an object
- **When** the hook runs
- **Then** exit 0 with no output

## Proposed Surface

### Hook Payload

| Input | Required | Description |
|---|:---:|---|
| `hook_event_name` | yes | Must be `PostToolUse`. |
| `tool_input.command` | shell events | The full command string; matched against the recognized close forms (adjacency; ref shape for `close.sh`). |
| `tool_input.file_path` / `path` / `filePath` / `notebook_path` | edit events | Scalar edited path. Path arrays, batch edit lists, and move destinations are not covered — an event carrying only those forms is treated as carrying no path (silent). |
| `tool_input.command` apply-patch forms | edit events | `*** Add/Update/Delete File: <path>` header lines are parsed for paths (same ledger-status check). |
| `tool_response` | no | When present with an explicit failure indicator, the event is suppressed. |

### Ledger file check

An edited path signals a close when it is a `.md` immediate child of an `.agents/issues/` directory, the file is readable, its frontmatter parses, and its `status` key reads `closed` (case-insensitive value). Anything else on that path — unreadable file, absent frontmatter, other status, index README without frontmatter — is silent.

### Hook Output

| Field | Description |
|---|---|
| close signal detected | `hookSpecificOutput.additionalContext` carrying the doc-freshness nudge; exit 0. |
| otherwise | no output; exit 0. |

## Open Questions

None.
