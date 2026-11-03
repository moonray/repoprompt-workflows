---
title: Spec-Accuracy Reminder Hook
issue: 13
status: implemented
---

# Spec-Accuracy Reminder Hook

## Problem

Operational docs (runbooks in `.agents/slash/`, procedures in `docs/procedures/`, operations docs in `docs/operations/`) and specs (`docs/spec/`) describe the same behavior from two sides — how we do it vs what the behavior contract is. When the operational side changes, nothing prompts a check of the spec side: the sibling hooks own every other direction (spec-quality-reminder: spec edited → writing quality; doc-freshness-reminder: item closed → drift audit; spec-conformance-gate: spec closed → matrix). Observed incident (private client workspace, 2026-10-30 → 11-02, recovered via operator-directed chat mining): a runbook was rewritten for a changed convention and its paired spec kept describing the old world for three days, silently, until the operator asked. The gap is a trigger gap at change time, not a knowledge gap — the fix existed in-session and was never applied to the paired doc.

## Goals

1. Detect an operational-doc edit at the moment it lands (`.agents/slash/*.md`, `docs/procedures/*.md`, `docs/operations/*.md`) via any supported edit-tool path form.
2. Nudge a same-session accuracy check: if the edit changed documented behavior, check whether any spec (or its conformance matrix) still describes the OLD behavior, and fix or flag the drift now, while the change context is fresh — with an explicit quick-no-op allowance when no spec pairs with the doc.
3. Stay silent where there is nothing to check: repos without a `docs/spec/` directory (positively verified), README index files, non-operational paths, and edits the runtime reported as failed.
4. Fail open — a malformed input or crash never traps the agent.

## Non-Goals

- No gate/blocking: the check is judgment (which specs pair with the doc), not an observable command; a gate would also obstruct legitimate mid-flight edits. Reminder-only, like the sibling reminder hooks.
- No verification that the check ran (no marker machinery).
- No reverse direction (spec edited → operational docs stale): spec-quality-reminder owns the spec-edit event; folding an accuracy clause into its nudge is a separate follow-up, not this hook's scope.
- No coverage of Bash-driven edits (sed/python redirects bypass edit-tool events — documented, accepted, same boundary as spec-quality-reminder).
- No coverage of human/out-of-band doc edits: hooks observe agent tool calls only.

## Constraints

- Watched paths are immediate `.md` children of `.agents/slash/`, `docs/procedures/`, and `docs/operations/` (recursive descent deliberately excluded — nested content is not a runbook; `README.md` basenames excluded). `docs/operations/` is a standard watch name even where only one repo currently has one — absent dirs simply never match.
- Spec-dir gate is three-valued: nudge when `docs/spec/` exists; silent only on POSITIVE absence (a resolvable base directory lacking it); nudge when unverifiable — verification failure is not evidence of absence.
- An explicit payload `cwd` is the sole resolution base for relative paths; the hook process's own cwd is consulted only when the payload carries none (an unrelated repo at the process cwd must not invent or mask the edited repo's specs — the defect the suite caught pre-fix).
- Path tolerance: scalar path keys (`file_path`/`path`/`filePath`/`notebook_path`/`new_path`/`old_path`), array forms (`files`/`edits`/`paths`, including dict items), and apply-patch headers (`Add`/`Update`/`Delete File`, `Move to`); a malformed entry is skipped, not fatal.
- Tool-response suppression recognizes explicit failure indicators only (`is_error`/`isError` true, truthy `error`, `status: "error"`, `ok`/`success` false); absent or unrecognized shapes are treated as success.
- Exactly one nudge per event even when several watched paths are present.
- The script never deliberately exits non-zero.

## Scenarios

### Scenario S-001: Runbook edit in a specs repo fires the nudge
- **Given** a PostToolUse edit event whose affected path is an immediate `.md` child of `.agents/slash/`, in a repo whose `docs/spec/` directory exists
- **When** the hook runs
- **Then** it emits the spec-accuracy nudge

### Scenario S-002: Procedure or operations-doc edit in a specs repo fires the nudge
- **Given** the same event shape with the path an immediate `.md` child of `docs/procedures/` or `docs/operations/`
- **When** the hook runs
- **Then** it emits the spec-accuracy nudge

### Scenario S-003: A positively spec-less repo stays silent
- **Given** an operational-doc edit whose repo root resolves on disk and carries no `docs/spec/` directory
- **When** the hook runs
- **Then** no nudge — a repo whose operational docs have no specs has nothing to drift against

### Scenario S-004: An unresolvable root nudges
- **Given** an operational-doc edit whose repo root cannot be verified (no candidate base exists on disk)
- **When** the hook runs
- **Then** it emits the nudge — remind rather than stay silent on a guess

### Scenario S-005: Relative paths resolve against the payload cwd, exclusively
- **Given** a relative operational-doc path with a payload `cwd` naming the repo
- **When** the hook runs
- **Then** the cwd is the only resolution base: nudge when that repo has `docs/spec/`, silence on its positive absence — and never a result derived from the hook process's own cwd

### Scenario S-006: README index files stay silent
- **Given** an edit to a `README.md` under a watched directory
- **When** the hook runs
- **Then** no nudge

### Scenario S-007: Non-operational paths stay silent
- **Given** edits to specs themselves, plans, source files, or other docs trees (`docs/plans/`, `docs/operations/`, source paths)
- **When** the hook runs
- **Then** no nudge

### Scenario S-008: Failed edits are suppressed; unknown outcomes nudge
- **Given** an operational-doc edit whose tool response carries an explicit failure indicator
- **When** the hook runs
- **Then** no nudge — while an absent or unrecognized response shape still nudges

### Scenario S-009: Batch, move, and apply-patch path forms are covered
- **Given** edit events whose watched paths arrive in array forms (`files`/`edits`/`paths`, dict items), as move sources/destinations, or in apply-patch command headers
- **When** the hook runs
- **Then** watched paths in any covered form trigger the nudge; malformed sibling entries never suppress it

### Scenario S-010: Exactly one nudge per event
- **Given** a single event carrying multiple watched operational-doc paths
- **When** the hook runs
- **Then** exactly one nudge is emitted

### Scenario S-011: Foreign events are ignored
- **Given** a hook event other than PostToolUse
- **When** the hook runs
- **Then** exit 0 with no output

### Scenario S-012: Malformed input exits cleanly
- **Given** stdin that is not valid JSON, or valid JSON that is not an object
- **When** the hook runs
- **Then** exit 0 with no output

### Scenario S-013: The nudge carries the full directive
- **Given** any nudge-emitting scenario
- **When** the nudge is emitted
- **Then** its text names: the same-session check while context is fresh, the OLD-behavior drift question, specs AND conformance matrices, fix-or-flag (not defer), and the quick-no-op allowance when no spec pairs with the doc

## Proposed Surface

### Hook Payload

| Input | Required | Description |
|---|:---:|---|
| `hook_event_name` | yes | Must be `PostToolUse`. |
| `tool_input` path forms | yes (one) | Scalar path keys, `files`/`edits`/`paths` arrays (string items or dicts with path keys), or an apply-patch `command` whose headers carry paths. |
| `cwd` | no | The runtime's working directory; the sole resolution base for relative paths when present. |
| `tool_response` | no | When present with an explicit failure indicator, the event is suppressed. |

### Spec-dir gate

An edited operational-doc path is nudged when the implied repo root has a `docs/spec/` directory, or when the root cannot be verified; it is silent only when a resolvable root positively lacks `docs/spec/`. Root derivation: the path prefix before the watched directory (absolute), the payload `cwd` (relative), or the process cwd only in the absence of a payload `cwd`.

### Hook Output

| Field | Description |
|---|---|
| watched path + specs exist/unverifiable | `hookSpecificOutput.additionalContext` carrying the spec-accuracy nudge; exit 0. |
| otherwise | no output; exit 0. |

## Open Questions

None.
