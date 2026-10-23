---
title: Test Quality Reminder Hook
issue: none
status: implemented
---

# Test Quality Reminder Hook

## Problem

Agents can edit test files and stop without running them, or run a suite and declare the work done without vetting the tests for meaning. No lifecycle event proves "tests were run and judged." A hook is needed that records when a real suite runs, blocks stopping while uncommitted test changes outrun the last run, and nudges the `test-quality` skill each time a suite executes.

The gate was built on Claude Code's lifecycle, where an actual Skill-tool invocation is observable and can be required. Runtimes differ: Codex routes `Stop` but emits no event for skill invocations, and opencode cannot route a blocking `Stop` at all. Per runtime the "vetted" half must either be clearable by an observable deliberate act or the runtime's lack of enforcement must be documented — a silent run-only clear is prohibited everywhere.

## Goals

1. Detect genuine test-run commands across languages/runners, ignoring runner words that appear only in comments, heredocs, strings, or non-run subcommands.
2. Record a per-repo last-run marker keyed by repo root so edit→run→stop ordering is observable.
3. Block a `Stop` while any uncommitted test file was edited after the later of the most recent run and the most recent vetting (skill invocation, or attestation where the runtime cannot observe skills) in that repo.
4. Nudge the `test-quality` skill each time a suite is run.
5. Treat documentation files as non-tests so a `docs/spec/` home is never misread as a test directory.
6. Degrade honestly per runtime: an observable skill marker where the runtime emits one; an explicit attestation step where `Stop` is routed but skill invocations are invisible; documented-unsupported where `Stop` is not routable as a gate. Never a silent run-only clear.

## Non-Goals

- Judge test quality directly; that is the `test-quality` skill's job (the hook only nudges it).
- Enforce coverage thresholds or mandate frameworks.
- Gate on committed test files — only uncommitted dirty files block `Stop`.
- Block `Stop` when no test files are dirty.
- Make a runtime that cannot route a blocking `Stop` enforce one anyway.

## Constraints

- Reads a Claude-Code-compatible JSON payload on stdin (`hook_event_name`, `cwd`, `tool_input.command`, `tool_name`).
- Per-runtime wiring:
  - **Claude Code** — `PostToolUse` matcher `Bash|Skill` (command + skill detection) and `Stop` (dirty-file gate) in `~/.claude/settings.json` via `scripts/install.sh`.
  - **Codex** — repo `.codex/hooks.json`: `PostToolUse` matcher `Bash` and `Stop`, both invoking the hook with `TQ_HOOK_RUNTIME=codex` in the environment (marks a runtime whose wiring cannot observe skill invocations).
  - **opencode** — repo `.opencode/plugins/repoprompt-hooks.mjs`: bash `tool.execute.after` feeds run detection; `session.idle` feeds `Stop` reactively and can only log (documented-unsupported; no blocking session-end channel exists).
- The last-run marker lives at `~/.cache/tq-hook/lastrun-<sha1(repo)[:12]>`; the vet marker at `~/.cache/tq-hook/tqskill-<sha1(repo)[:12]>`; mtimes are the event times.
- Attestation is honored only when `TQ_HOOK_RUNTIME` is set by the runtime's wiring: a deliberate, observable act (a Bash command invoking this hook's script with `--attest-vetted`) performed after applying the `test-quality` checklist. Where a runtime observes real skill invocations (no `TQ_HOOK_RUNTIME`), attestation is inert and the Skill-tool invocation remains the only way to stamp the vet marker.
- A "test file" matches the multi-language `TEST_FILE_RE` and is not a documentation file (`DOC_FILE_RE`).

## Scenarios

### Scenario: Running a suite records a run and nudges vetting
- **Given** a `PostToolUse:Bash` event whose command invokes a known runner at command position (e.g. `pytest`, `npm test`, `node --test`, `make test`), or a bare interpreter running a test-matching script (e.g. `python tests/test_foo.py`, `node tests/x.js`)
- **When** the hook runs
- **Then** it writes the repo's last-run marker and emits a reminder to vet added/modified tests with the `test-quality` skill

### Scenario: Non-run command does nothing
- **Given** a Bash command that does not invoke a runner at command position, or mentions a runner only inside a heredoc, comment, or string
- **When** the hook runs
- **Then** it writes no marker and emits no reminder

### Scenario: Help/version and install invocations are not runs
- **Given** a command like `pytest --help` or `npm install jest`
- **When** the hook runs
- **Then** it is not treated as a test run (no marker, no reminder)

### Scenario: Invoking the test-quality skill stamps the vet marker
- **Given** a `PostToolUse` event with `tool_name` `Skill` and `tool_input.skill` equal to `test-quality`
- **When** the hook runs
- **Then** it writes the repo's vet marker, writes no run marker, and emits no reminder; a `Skill` event for any other skill writes nothing

### Scenario: Stop is blocked when a test file is dirty since the last run or vetting
- **Given** an uncommitted test file modified after the repo's last recorded run or after the last vetting (or either not recorded)
- **When** a `Stop` event fires
- **Then** the hook blocks with a reason directing the agent to run the affected suite and vet the tests before stopping

### Scenario: edit→run→vet→stop is allowed
- **Given** a test file edited and then the suite run and the tests vetted (skill invocation, or attestation where the runtime cannot observe skills), so both marker mtimes are at least the edit mtime
- **When** a `Stop` event fires
- **Then** the hook does not block

### Scenario: edit→run→stop without vetting is blocked
- **Given** a test file edited and then the suite run, but no vetting after the edit (skill skipped or "applied from context")
- **When** a `Stop` event fires
- **Then** the hook blocks — a run alone never clears the gate

### Scenario: Attestation stamps the vet marker on a skill-invisible runtime
- **Given** `TQ_HOOK_RUNTIME` is set by the runtime's wiring, and a Bash command whose simple-command segment contains a standalone `--attest-vetted` token together with a `test-quality-reminder.py` token
- **When** the `PostToolUse` event for that command fires
- **Then** the hook writes the repo's vet marker as that runtime's deliberate vetting act, writes no run marker, and emits no output

### Scenario: Attestation is inert where skills are observable
- **Given** no `TQ_HOOK_RUNTIME` in the hook's environment (Claude Code wiring)
- **When** the same attestation command's `PostToolUse` event fires
- **Then** no marker is written — the actual Skill-tool invocation remains the only vetting act that clears the gate

### Scenario: Stop reason names the vetting act the runtime can perform
- **Given** `TQ_HOOK_RUNTIME` is set and uncommitted test files are dirty
- **When** a `Stop` event fires
- **Then** the block reason directs the agent to run the suite and perform the attestation command (not a Skill-tool invocation the runtime does not have); without `TQ_HOOK_RUNTIME` the reason names the `test-quality` Skill invocation

### Scenario: Committing or cleaning test changes clears the gate
- **Given** no uncommitted test files (they were committed or cleaned)
- **When** a `Stop` event fires
- **Then** the hook does not block

### Scenario: Documentation files are not counted as tests
- **Given** a dirty file under `docs/spec/` (a markdown spec)
- **When** a `Stop` event fires
- **Then** the file is excluded by the documentation filter and does not contribute to a block

### Scenario: Malformed payload exits cleanly
- **Given** stdin that is not valid JSON or lacks an event
- **When** the hook runs
- **Then** it exits 0 with no output (never raises)

### Scenario: opencode does not enforce the Stop gate (documented-unsupported)
- **Given** the opencode plugin wiring, where the `Stop` equivalent (`session.idle`) fires after the turn ends and cannot block
- **When** a turn ends with uncommitted test-file changes
- **Then** no block occurs; a reactive warning is logged; the runtime is documented (plugin mapping, hooks README, this spec) as not enforcing the gate rather than silently passing it

## Proposed Surface

### Hook Payload

| Input | Required | Description |
|---|:---:|---|
| `hook_event_name` | yes | `PostToolUse` (command/skill/attestation detection) or `Stop` (dirty-file gate). |
| `cwd` | no | Working dir; resolved to a repo root for the per-repo markers. Defaults to process cwd. |
| `tool_input.command` | PostToolUse:Bash | The Bash command string inspected for a test-run or attestation invocation. |
| `tool_name` | PostToolUse | `Bash` for commands; `Skill` for skill invocations. |
| `tool_input.skill` | PostToolUse:Skill | The invoked skill name; only `test-quality` stamps the vet marker. |
| env `TQ_HOOK_RUNTIME` | no | Set by wiring on runtimes that cannot observe skill invocations (Codex). Gates attestation honoring and the Stop reason text. Absent under Claude Code. |

### Hook Output

| Field | Description |
|---|---|
| PostToolUse run detected | `hookSpecificOutput.additionalContext` carrying the `test-quality` vet reminder. |
| PostToolUse skill or attestation | no output; the vet marker is stamped. |
| Stop dirty | `{"decision":"block","reason":…}` — the reason names the vetting act the runtime can perform (Skill invocation, or the attestation command under `TQ_HOOK_RUNTIME`). |
| otherwise | no output; exit 0. |

### Runtime support

| Runtime | Run detection | Vet half | Stop gate |
|---|---|---|---|
| Claude Code | `PostToolUse:Bash` | Skill-tool invocation (matcher `Bash\|Skill`) | enforced |
| Codex | `PostToolUse:Bash` | attestation (`--attest-vetted`, `TQ_HOOK_RUNTIME=codex`) | enforced (`decision:block` continuation) |
| opencode | `tool.execute.after` (bash) | none observable | **not enforced** — documented-unsupported, reactive warn at `session.idle` |

## Open Questions

None.
