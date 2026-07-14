---
title: Track Work Skill
issue: none
status: implemented
---

# Track Work Skill

## Problem

Work gets tracked ad-hoc across `issues_N.md` reports and hand-maintained lists, with no single status source of truth, and implementation starts before a tracking item exists. Each repo needs one live status ledger — GitHub Issues when it has GitHub, else a committed file-based backlog — that is the entry gate before any work starts.

## Goals

1. Track every bug/feature/enhancement/decision as one work item in one place: GitHub Issues (GitHub repo) or `.agents/issues/` (otherwise).
2. Detect the backend deterministically from explicit override then durable repository identity, without treating temporary service failure as a different ledger, and apply the repo's own label/taxonomy conventions.
3. Act as the entry gate: no implementation, spec edit, or test starts before a tracking item exists (or updates an existing one).
4. Link the detail layer (spec/plan/loop/research) from the item — never duplicate long-form narrative in the item body.
5. Drive a status lifecycle where close means the change landed on the default branch.

## Non-Goals

- Hold long-form narrative in the item body (link it instead).
- Auto-create a config or run an up-front setup wizard; detect conventions and use defaults. Ask only for explicit approval before repository mutations such as overrides, label seeding, or ledger retirement.
- Invent labels outside the repo's set; ask the user if a new one is genuinely needed.

## Constraints

- Backend selection: validated environment override > trusted-base config override > exact canonical GitHub origin identity > file for no-origin/non-GitHub repositories. `auto` falls through; invalid or ambiguous identity stops. `gh` availability, authentication, network/API access, permissions, and Issues enablement are capability checks, not identity checks.
- A known GitHub repository never silently creates or updates a file ledger when GitHub capability is unavailable; the operation stops with the failed probe and remediation. File use requires an explicit, confirmed override.
- Labels come from `gh label list` (GitHub) and always beat a config list; the config carries only what GitHub cannot expose. Creating a missing label taxonomy requires confirmation.
- IDs are immutable — never renumbered or reused; referenced from commits, specs, and other items.
- The file-backend issues dir is the shared team backlog and is committed; warn if gitignored.

## Scenarios

### Scenario S-001: The backend follows durable repository identity
- **Given** a repo starting work
- **When** backend selection runs
- **Then** a confirmed override wins, else a GitHub origin selects GitHub, else a no-origin or non-GitHub repository selects file; temporary `gh` capability does not change that identity

### Scenario S-002: GitHub capability failure stops instead of creating a second ledger
- **Given** a repository whose selected backend is GitHub
- **When** `gh` is missing, unauthenticated, unreachable, unauthorized, or the API probe otherwise fails
- **Then** no file item or config is written, and the result names the failed probe, preserves its error class, and offers retry/authentication or an explicitly confirmed file override

### Scenario S-003: Disabled GitHub Issues requires an explicit choice
- **Given** a GitHub repository whose Issues feature is disabled
- **When** an item would be read or written
- **Then** the operation stops and asks the user to enable Issues or explicitly confirm a file-backend override; it never falls back silently

### Scenario S-004: Repo conventions are read, GitHub labels discovered
- **Given** a first run
- **When** conventions are read
- **Then** a `.agents/track-work.config.md`, `AGENTS.md`, or `CLAUDE.md` block is used if present, else defaults; for GitHub, `gh label list` labels always beat any config list

### Scenario S-005: A tracking item is created before any work
- **Given** new work (bug/feature/enhancement/decision)
- **When** work is about to start
- **Then** a tracking item is created first (or an existing one updated) — no code/spec/test change precedes it

### Scenario S-006: Search before create avoids duplicates
- **Given** an incoming request
- **When** an item would be created
- **Then** existing items are searched first; a match is updated/cross-linked rather than duplicated

### Scenario S-007: Labels honor configured cardinality without surprise mutation
- **Given** a created item
- **When** labels are applied
- **Then** they come from the repo's actual set and honor configured cardinality (e.g. exactly one `type:`, one `priority:`, one `status:`); if core labels are missing, the proposed seed set is shown and created only after confirmation

### Scenario S-008: Detail files are linked, not duplicated
- **Given** a tracking item
- **When** the body is written
- **Then** spec/plan/loop/research paths are linked from it; long-form narrative is not duplicated in the body

### Scenario S-009: File-backend items use immutable IDs in a committed backlog
- **Given** the file backend
- **When** an item is created
- **Then** it gets an immutable ID under the committed `issues_dir` with a synced index; the skill warns and fixes if that dir is gitignored

### Scenario S-010: Close means landed on the default branch
- **Given** a code fix
- **When** the item is closed
- **Then** it is closed via a `Fixes #N`/`Closes #N` commit or PR that lands on the default branch (or file-backend `status: closed` after the commit), honoring any close-gate workflow and exempt labels

### Scenario S-011: Secrets and absolute paths are redacted before filing
- **Given** an item body
- **When** it is filed
- **Then** configured secrets and absolute local paths are redacted, tighter when the repo is public, and nothing is synced to `mirror_repos`

### Scenario S-012: Optional GitHub features apply when configured
- **Given** a `github.board` and/or `personas` config is present
- **When** a GitHub item is created or updated
- **Then** the issue's status is mirrored to the configured Project board field, and persona-weighted prioritization / a Personas body line is applied for applicable types

### Scenario S-013: Backend selection is observable
- **Given** any track-work operation
- **When** backend selection and capability probing complete
- **Then** the output reports the selected backend, the identity evidence or override that selected it, and capability status without inventing historical causes

### Scenario S-014: Ledger migration is journaled, resumable, and recoverable
- **Given** work items are being moved between reachable backends
- **When** migration is requested
- **Then** a committed journal outside both ledgers records source revisions and pending rows before mutation; the user confirms migration and overrides; idempotency markers and destination read-back advance rows to verified; partial failure preserves sources and resumes without duplicates; source retirement requires separate confirmation

### Scenario S-015: GitHub mutations are bound to canonical repository identity
- **Given** GitHub is the selected backend
- **When** an issue, label, status, close, or board operation runs
- **Then** an exact accepted origin or explicit `github.repo` yields one normalized `owner/repo`, every repo-scoped command receives it explicitly, ambient context cannot redirect the operation, and mutations are read back from that repository

### Scenario S-016: File operations are confined, serialized, and atomic
- **Given** the file backend
- **When** items or the index are read or mutated
- **Then** IDs and scalar inputs are validated, the issues path is repo-relative and non-symlinked, mutations share a lock, and same-directory temporary files atomically replace completed outputs without traversal or overwrite races

### Scenario S-017: Both backends implement the full lifecycle
- **Given** a tracked item on either backend
- **When** it moves among draft, backlog, in-progress, review, blocked, and closed
- **Then** exactly one lifecycle state is authoritative; block records the prior state, unblock restores it or an explicit valid target, open queries include every non-closed state, and close occurs only after landed evidence

### Scenario S-018: Issue creation uses private isolated content staging
- **Given** an issue body is ready to file
- **When** temporary storage is needed
- **Then** deterministic redaction runs first, a private uniquely named temporary file is used, cleanup is guaranteed, and concurrent agents cannot exchange bodies

### Scenario S-019: Unattended callers never prompt mid-run
- **Given** Backlog or another noninteractive caller invokes track-work
- **When** an operation would require confirmation or unavailable capability
- **Then** preflightable approvals are collected in the caller's sole authorization step and later discoveries return blocked with a reason rather than prompting or mutating silently

## Proposed Surface

### Inputs

| Input | Required | Description |
|---|:---:|---|
| Request | yes | The bug/feature/enhancement/decision to track, or a status query. |
| Repo conventions | no | `.agents/track-work.config.md` / `AGENTS.md` / `CLAUDE.md` block; else defaults. |

### Output

| Field | Description |
|---|---|
| `item` | The created/updated tracking item (GitHub issue # or file ID), with labels and status. |
| `links` | Detail files (spec/plan/loop/research) linked from the item. |
| `status` | Lifecycle status (draft / backlog / in-progress / review / closed; blocked toggle). |
| `backend` | Selected backend, identity evidence or confirmed override, and capability result or exact blocking probe. |

## Open Questions

None.
