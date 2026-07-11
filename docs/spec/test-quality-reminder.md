---
title: Test Quality Reminder Hook
issue: none
status: implemented
---

# Test Quality Reminder Hook

## Problem

Agents can edit test files and stop without running them, or run a suite and declare the work done without vetting the tests for meaning. No lifecycle event proves "tests were run and judged." A hook is needed that records when a real suite runs, blocks stopping while uncommitted test changes outrun the last run, and nudges the `test-quality` skill each time a suite executes.

## Goals

1. Detect genuine test-run commands across languages/runners, ignoring runner words that appear only in comments, heredocs, strings, or non-run subcommands.
2. Record a per-repo last-run marker keyed by repo root so edit→run→stop ordering is observable.
3. Block a `Stop` while any uncommitted test file was edited after the most recent run in that repo.
4. Nudge the `test-quality` skill each time a suite is run.
5. Treat documentation files as non-tests so a `docs/spec/` home is never misread as a test directory.

## Non-Goals

- Judge test quality directly; that is the `test-quality` skill's job (the hook only nudges it).
- Enforce coverage thresholds or mandate frameworks.
- Gate on committed test files — only uncommitted dirty files block `Stop`.
- Block `Stop` when no test files are dirty.

## Constraints

- Reads a Claude-Code-compatible JSON payload on stdin (`hook_event_name`, `cwd`, `tool_input.command`).
- Wired to `PostToolUse:Bash` (command detection) and `Stop` (dirty-file gate) in `~/.claude/settings.json`.
- The last-run marker lives at `~/.cache/tq-hook/lastrun-<sha1(repo)[:12]>`; its mtime is the run time.
- A "test file" matches the multi-language `TEST_FILE_RE` and is not a documentation file (`DOC_FILE_RE`).

## Scenarios

### Scenario: Running a suite records a run and nudges vetting
- **Given** a `PostToolUse:Bash` event whose command invokes a known runner at command position (e.g. `pytest`, `npm test`, `node --test`, `make test`)
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

### Scenario: Stop is blocked when a test file is dirty since the last run
- **Given** an uncommitted test file modified after the repo's last recorded run (or no run recorded)
- **When** a `Stop` event fires
- **Then** the hook blocks with a reason directing the agent to run the affected suite and vet tests before stopping

### Scenario: edit→run→stop is allowed
- **Given** a test file edited and then the suite run (so the run marker mtime is at least the edit mtime)
- **When** a `Stop` event fires
- **Then** the hook does not block

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

## Proposed Surface

### Hook Payload

| Input | Required | Description |
|---|:---:|---|
| `hook_event_name` | yes | `PostToolUse` (command detection) or `Stop` (dirty-file gate). |
| `cwd` | no | Working dir; resolved to a repo root for the per-repo marker. Defaults to process cwd. |
| `tool_input.command` | PostToolUse | The Bash command string inspected for a test-run invocation. |

### Hook Output

| Field | Description |
|---|---|
| PostToolUse run detected | `hookSpecificOutput.additionalContext` carrying the `test-quality` vet reminder. |
| Stop dirty | `{"decision":"block","reason":...}` with the stop reason. |
| otherwise | no output; exit 0. |

## Open Questions

None.
