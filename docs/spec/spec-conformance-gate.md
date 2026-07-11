---
title: Spec Conformance Gate Hook
issue: none
status: implemented
---

# Spec Conformance Gate Hook

## Problem

A spec can be marked `implemented`/`shipped` without a conformance audit, closing a spec-driven feature on assertion ("tests pass") rather than coverage proof. A gate is needed that blocks a spec file from being set to a terminal lifecycle status unless a conformance matrix exists for it.

## Goals

1. Detect spec files broadly — path under `spec`/`specs`/`specifications`, a `*.spec.md` name, or frontmatter `type` in {spec, specification, contract, feature-spec, featurespec}.
2. Block an edit that sets a spec's frontmatter `status` to a terminal value when no conformance matrix exists.
3. Treat a matrix as satisfied by a sibling file whose name starts with `<stem>.conformance` OR a frontmatter key (`conformance`/`conformed`/`audited`/`conformance_matrix`).
4. Evaluate each file in a multi-file `apply_patch` independently.

## Non-Goals

- Close GitHub issues that don't edit a spec file (needs a separate issue-close hook).
- Judge the correctness of the conformance matrix; the `spec-conformance` skill authors it.
- Gate non-terminal `status` edits.

## Constraints

- Wired to `PostToolUse` on file edits.
- Terminal statuses: `implemented`, `shipped`, `done`, `closed`, `complete`, `completed`, `resolved`, `final`, `released`, `verified`, `approved`.
- Reads only the first ~4000 characters of the edited file for frontmatter.

## Scenarios

### Scenario: Closing a spec without a matrix is blocked
- **Given** a `PostToolUse` edit to a spec file whose frontmatter `status` is set to a terminal value and no conformance sibling or frontmatter reference exists
- **When** the hook runs
- **Then** it blocks with a reason directing the agent to run the `spec-conformance` skill to produce `<stem>.conformance.md`

### Scenario: A sibling conformance matrix allows the close
- **Given** the spec is set to a terminal status and a sibling `<stem>.conformance.md` exists
- **When** the hook runs
- **Then** no block

### Scenario: A frontmatter conformance reference allows the close
- **Given** the spec frontmatter carries a non-empty `conformance`/`conformed`/`audited` key
- **When** the hook runs
- **Then** no block

### Scenario: Non-terminal status is not gated
- **Given** a spec file edited with `status: draft`
- **When** the hook runs
- **Then** no block

### Scenario: Non-spec file is not gated
- **Given** a non-spec file set to `status: implemented`
- **When** the hook runs
- **Then** no block

### Scenario: One tripping file in a multi-file edit blocks
- **Given** an `apply_patch` touching several files where at least one is a terminal-status spec with no matrix
- **When** the hook runs
- **Then** it blocks on the first tripping file

### Scenario: Missing/unreadable file no-ops
- **Given** an edited path that does not exist on disk
- **When** the hook runs
- **Then** no block (the gate cannot evaluate a missing file)

### Scenario: Malformed payload exits cleanly
- **Given** stdin that is not valid JSON or is not a `PostToolUse` event
- **When** the hook runs
- **Then** it exits 0 with no output

## Proposed Surface

### Hook Payload

| Input | Required | Description |
|---|:---:|---|
| `hook_event_name` | yes | Must be `PostToolUse`. |
| `tool_input` | yes | A path field or an `apply_patch` command naming the edited file(s). |

### Hook Output

| Field | Description |
|---|---|
| tripping spec close | `{"decision":"block","reason":...}` naming the file, its status, and the required matrix. |
| otherwise | no output; exit 0. |

## Open Questions

None.
