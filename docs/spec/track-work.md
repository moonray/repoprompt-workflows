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
2. Detect the backend deterministically (override > GitHub > file) and apply the repo's own label/taxonomy conventions.
3. Act as the entry gate: no implementation, spec edit, or test starts before a tracking item exists (or updates an existing one).
4. Link the detail layer (spec/plan/loop/research) from the item — never duplicate long-form narrative in the item body.
5. Drive a status lifecycle where close means the change landed on the default branch.

## Non-Goals

- Hold long-form narrative in the item body (link it instead).
- Auto-create a config or run a wizard; detect and fall back to defaults.
- Invent labels outside the repo's set; ask the user if a new one is genuinely needed.

## Constraints

- Backend detection: override (config `backend:` / `TRACK_WORK_BACKEND`) > GitHub (`gh auth` + GitHub origin + `gh repo view`) > file.
- Labels come from `gh label list` (GitHub) and always beat a config list; the config carries only what GitHub cannot expose.
- IDs are immutable — never renumbered or reused; referenced from commits, specs, and other items.
- The file-backend issues dir is the shared team backlog and is committed; warn if gitignored.

## Scenarios

### Scenario: The backend is detected deterministically
- **Given** a repo starting work
- **When** backend detection runs
- **Then** override wins, else GitHub when `gh` is authed and the origin is a GitHub repo, else the file backend; GitHub-with-issues-disabled falls back to file

### Scenario: Repo conventions are read, GitHub labels discovered
- **Given** a first run
- **When** conventions are read
- **Then** a `.agents/track-work.config.md` / `AGENTS.md` block is used if present, else defaults; for GitHub, `gh label list` labels always beat any config list

### Scenario: A tracking item is created before any work
- **Given** new work (bug/feature/enhancement/decision)
- **When** work is about to start
- **Then** a tracking item is created first (or an existing one updated) — no code/spec/test change precedes it

### Scenario: Search before create avoids duplicates
- **Given** an incoming request
- **When** an item would be created
- **Then** existing items are searched first; a match is updated/cross-linked rather than duplicated

### Scenario: Labels honor configured cardinality
- **Given** a created item
- **When** labels are applied
- **Then** they come from the repo's actual set and honor configured cardinality (e.g. exactly one `type:`, one `priority:`, one `status:`)

### Scenario: Detail files are linked, not duplicated
- **Given** a tracking item
- **When** the body is written
- **Then** spec/plan/loop/research paths are linked from it; long-form narrative is not duplicated in the body

### Scenario: File-backend items use immutable IDs in a committed backlog
- **Given** the file backend
- **When** an item is created
- **Then** it gets an immutable ID under the committed `issues_dir` with a synced index; the skill warns and fixes if that dir is gitignored

### Scenario: Close means landed on the default branch
- **Given** a code fix
- **When** the item is closed
- **Then** it is closed via a `Fixes #N`/`Closes #N` commit or PR that lands on the default branch (or file-backend `status: closed` after the commit), honoring any close-gate workflow and exempt labels

### Scenario: Secrets and absolute paths are redacted before filing
- **Given** an item body
- **When** it is filed
- **Then** configured secrets and absolute local paths are redacted, tighter when the repo is public, and nothing is synced to `mirror_repos`

## Proposed Surface

### Inputs

| Input | Required | Description |
|---|:---:|---|
| Request | yes | The bug/feature/enhancement/decision to track, or a status query. |
| Repo conventions | no | `.agents/track-work.config.md` / `AGENTS.md` block; else defaults. |

### Output

| Field | Description |
|---|---|
| `item` | The created/updated tracking item (GitHub issue # or file ID), with labels and status. |
| `links` | Detail files (spec/plan/loop/research) linked from the item. |
| `status` | Lifecycle status (draft / backlog / in-progress / review / closed; blocked toggle). |

## Open Questions

None.
