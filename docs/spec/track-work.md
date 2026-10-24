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
6. Answer workspace-level status questions across every repo in the workspace — never just the primary — aggregating each repo's ledger into one repo-labeled result.
7. Triage items at creation — entry state, priority defaults, decision routing, signature dedup — so every item is born deterministic and consumption triage starts from a known baseline.
8. Deliver the tracked behavior through a deterministic CLI (`resolve`/`list`/`create`/`status`/`close`/`migrate`) so backend resolution, repository binding, redaction, lifecycle transitions, close evidence, and migrations execute identically across RPCE backend runtimes instead of depending on each agent interpreting the skill text and assembling shell commands.

## Non-Goals

- Hold long-form narrative in the item body (link it instead).
- Auto-create a config or run an up-front setup wizard; detect conventions and use defaults. Ask only for explicit approval before repository mutations such as overrides, label seeding, or ledger retirement.
- Invent labels outside the repo's set; ask the user if a new one is genuinely needed.
- MCP-server behavior in the CLI core: the core is runtime-agnostic; an MCP wrapper, if built, wraps the CLI without core changes. Deferred with #1 — revisit only when a workflow demonstrably needs MCP dispatch.

## Constraints

- Backend selection: validated environment override > trusted-base config override > exact canonical GitHub origin identity > file for no-origin/non-GitHub repositories. `auto` falls through; invalid or ambiguous identity stops. `gh` availability, authentication, network/API access, permissions, and Issues enablement are capability checks, not identity checks.
- A known GitHub repository never silently creates or updates a file ledger when GitHub capability is unavailable; the operation stops with the failed probe and remediation. File use requires an explicit, confirmed override.
- Labels come from `gh label list` (GitHub) and always beat a config list; the config carries only what GitHub cannot expose. Creating a missing label taxonomy requires confirmation.
- IDs are immutable — never renumbered or reused; referenced from commits, specs, and other items.
- The file-backend issues dir is the shared team backlog and is committed; warn if gitignored.
- Creation-time triage is contracted in the skill's Triage section: the shared atoms (Stable Identifiers, Review Quality signatures, Verifying Delegated Work, Git Safety) are named by reference to `.agents/rules/global.md`, never restated; consumption-time triage (Backlog Phase 1, triage-work) is untouched.
- The CLI is the mechanical executor of this spec: every command emits one machine-readable JSON envelope and an exit status (0 success, 2 usage, 1 other failures with a typed `error.code`); every mutation verifies itself by read-back before reporting success; noninteractive invocations return `blocked` instead of prompting. The CLI core requires no runtime-specific behavior — skills and workflows consume the envelope.

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

### Scenario S-020: Tracked means explicitly owned
- **Given** a defect or consequential finding is mentioned narratively in another item's body, a report, or a spec document
- **When** an agent claims the work is tracked
- **Then** the claim is valid only if an authoritative item carries it in its primary scope or a concrete acceptance criterion; otherwise a dedicated item is created (preferred for P0/P1) or an existing explicitly-owning item is updated, without duplicating an authoritative equivalent

### Scenario S-021: Ledger rereads at commitment boundaries
- **Given** the ledger is shared and mutable by other actors
- **When** an agent reaches a commitment boundary (assigning/dispatching, changing open/blocked/done state, closing/replacing/claiming completion, or detecting external change)
- **Then** authoritative item state is re-read rather than carried from discovery

### Scenario S-022: Mitigated is not fixed
- **Given** an incident's mitigations are complete and its causal defect remains unresolved (including defects that are not ours to fix)
- **When** tracking is reconciled
- **Then** the causal defect remains explicitly owned — the existing incident item stays open as owner, or a separate root item exists only because ownership or lifecycle genuinely differs (upstream defects mark blocked/external-owner with "report upstream" recorded as next action only where a channel exists and disclosure is authorized) — and mitigation completion alone cannot close it

### Scenario S-023: Local personal exposure requires confirmation
- **Given** a finding that is personal-only, untracked, not shared into team/client systems, shows no active compromise, and violates no repository/organization policy
- **When** tracking is requested
- **Then** an interactive caller confirms with the user before creating a standalone item; a noninteractive caller returns blocked/pending-confirmation with no item created; if the user declines an already-created item it is closed wontfix with the decision recorded, never deleted; shared credentials, repository exposure, client systems, or policy-governed secrets remain eligible for normal tracking

### Scenario S-024: Workspace-level questions fan out to every repo
- **Given** a workspace holding multiple repos (RPCE multi-root, or multiple checkouts elsewhere)
- **When** a workspace-level status question is asked ("what's open", "list open issues by priority")
- **Then** the repo set is enumerated before any ledger query (every loaded root that is a git repo, plus any repo the question names), backend selection and config discovery run per repo, each query is bound to its own repo, the aggregate labels every item with its repo, and an unreachable ledger appears as a reported gap rather than being omitted; only an explicit user narrowing reduces the set

### Scenario S-025: Decisions route to humans at creation
- **Given** a decision-type finding at intake
- **When** the tracking item is created
- **Then** it is created for human triage — never auto-queued or auto-resolved by an agent at creation time; the Backlog/rollup consumption convention is named, not duplicated

### Scenario S-026: Birth states are draft or backlog only
- **Given** a newly created tracking item
- **When** its initial status is assigned
- **Then** it enters `status:draft` (needs repro/decision) or `status:backlog` (triaged, acceptance clear) — never born `in-progress`, `review`, or `blocked`; `in-progress` is claimed only by the actor that starts work

### Scenario S-027: Batch/summary items carry a parent link
- **Given** an item filed from a batch or summary artifact
- **When** it is created
- **Then** its Source/Detail section carries a parent/reference link identifying the originating batch item or run — never a free-floating duplicate

### Scenario S-028: Priority defaults by finding kind
- **Given** a finding filed with no per-repo `triage:` override
- **When** its priority is assigned at creation
- **Then** the deterministic defaults table applies (live-failure bug → p1; process/doc gap → p2/p3; parked idea → p3); the table is creation-time defaults and consumption triage may re-rank

### Scenario S-029: Signature-based dedup before create
- **Given** an item about to be created
- **When** the ledger is searched first
- **Then** the search runs against the item's review signature (the Review Quality atom, named not restated); a match updates the existing item (comment/relabel) instead of creating

### Scenario S-030: Triage atoms are named, not restated
- **Given** the skill's Triage section
- **When** it touches Stable Identifiers, Review Quality signatures, Verifying Delegated Work, or Git Safety
- **Then** those atoms are named with a pointer to `.agents/rules/global.md` and no definition text is copied

### Scenario S-031: Per-repo triage config override
- **Given** a repo whose creation-time defaults differ
- **When** the config carries a `triage:` block (`priority_defaults`, `entry_state`)
- **Then** it overrides the built-in defaults — `entry_state` constrained to `draft`|`backlog` — and an absent block means built-in defaults

### Scenario S-032: Consumption triage unchanged
- **Given** Backlog's Phase-1 consumption triage and the triage-work skill
- **When** creation-time triage rules apply
- **Then** they govern creation only — no re-ranking rules or flight-set language appear, and consumption surfaces keep their own logic

### Scenario S-033: CLI commands emit one machine-readable envelope
- **Given** the CLI invoked with any supported command (`resolve`/`list`/`create`/`status`/`close`/`migrate`)
- **When** the command completes, successfully or not
- **Then** stdout carries exactly one JSON envelope with `ok`, `command`, `backend`, and the operation's result or a typed `error` (`code` + `message`); the process exits 0 on success, 2 on usage errors, and 1 on every other failure

### Scenario S-034: resolve reports identity and capability separately
- **Given** `resolve` invoked in a repository
- **When** identity inputs are read (validated environment override, trusted-base config, exact origin parse)
- **Then** the envelope reports `backend`, `selected_by`, and the normalized target (`owner/repo` or the repo-relative issues dir) — or fails `origin-rejected` with the remediation; capability probes appear as a separate `capability` field and never change the selected identity; identical inputs yield identical output on every invocation

### Scenario S-035: Mutations are bound and read back from one repository
- **Given** a mutating CLI command running against the GitHub backend
- **When** the mutation executes
- **Then** every underlying call is bound to the resolved `owner/repo` explicitly, ambient `GH_REPO` and working directory cannot redirect it, and the envelope names the repository the mutation was read back from; a read-back that resolves elsewhere fails `wrong-repository`

### Scenario S-036: Redaction is mechanical on the write path
- **Given** `create` receiving an item body
- **When** the body is staged for filing
- **Then** configured secret values and absolute local paths are replaced deterministically before the item exists on any backend, the envelope reports which redaction classes applied, and no unredacted copy persists after the command exits

### Scenario S-037: Label changes are cardinality-safe and verified
- **Given** `create` or `status` applying labels
- **When** labels are set
- **Then** they are validated against the repo's discovered label set — a label outside it fails `unknown-label` with the proposal shown, no label is created implicitly; on a status transition, conflicting labels in the same prefix are removed and the target added in one operation, and the resulting label set is read back into the envelope

### Scenario S-038: close refuses without landed evidence
- **Given** `close` invoked on an item whose implementing change is not verified as landed on the default branch
- **When** close runs
- **Then** no close mutation occurs and the envelope fails `landed-evidence`, naming the check that did not pass (commit ancestry on the default branch, merged PR, or the file backend's landed commit) — unless the item carries a configured exempt label, per S-010's semantics

### Scenario S-039: Noninteractive invocations block instead of prompting
- **Given** the CLI invoked in noninteractive mode
- **When** an operation would require a confirmation, or a capability probe fails (auth, network, permissions, disabled Issues)
- **Then** the process exits non-zero with `error.code` `blocked` and a reason, performs no mutation, and never prompts or hangs waiting for input

### Scenario S-040: Migration resumes from its journal without duplicates
- **Given** a migration journal whose rows sit in `pending`/`created`/`verified` states
- **When** `migrate` runs again (or `migrate --status` is queried)
- **Then** it resumes from the journal — already-verified rows are skipped, `created` rows are only re-checked (never re-created) via their idempotency marker, rows advance to `verified` only after destination read-back, a mid-run failure leaves sources intact and the journal resumable, and source retirement runs only as a separate confirmed step

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

### CLI (deterministic executor)

Invoked by the skill and workflows as the mechanical execution path; `<ref>` is a GitHub issue URL, `owner/repo#N`, or a file-backend `ISSUE-NNN`.

| Command | Arguments | Success envelope (beyond `ok`/`backend`) | Typed failures |
|---|---|---|---|
| `resolve` | — | `selected_by`, `repo` or `issues_dir`, `capability` | `origin-rejected`, `blocked` |
| `list` | `[--status ..] [--label ..]` | `items[]` (id, title, status, labels, repo) | `blocked`, `not-found` (bad scope) |
| `create` | `--title --type --priority [--label ..] [--body-file ..] [--noninteractive]` | `item` (number/ID + url/path), applied labels, redaction summary | `unknown-label`, `cardinality`, `blocked` |
| `status` | `<ref> <state> [--noninteractive]` | `item`, `from`→`to`, labels read back | `invalid-transition`, `not-found`, `blocked` |
| `close` | `<ref> [--reason ..] [--noninteractive]` | `item` closed + the landed-evidence check that passed | `landed-evidence`, `not-found`, `blocked` |
| `migrate` | `--to github\|file [--status] [--retire-source]` | journal path + row states | `blocked`, journal write failure |

## Open Questions

None.
