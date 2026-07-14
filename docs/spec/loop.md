---
title: Loop Workflow
issue: none
status: implemented
---

# Loop Workflow

## Problem

Loop is a delegation-heavy orchestrator that turns a committed Spec + Deep Plan into reviewed, tested code. Its current contract does not fully distinguish standalone from Backlog-orchestrated ownership, creates progress only after readiness, and leaves missing or blocked contracts without a durable maintenance/resume path. It also conflates authorization with action ownership and cannot safely describe recovery from a dead session with uncommitted work.

A stable standalone-first contract is needed so Loop remains useful on its own while Backlog can orchestrate multiple Loop runs without weakening readiness, delegation, conformance, or git-safety gates.

## Goals

1. Define Loop's gates, artifacts, lifecycle, ownership, and escape conditions independently of mechanism.
2. Guarantee no implementation begins until committed Spec + Deep Plan inputs pass deterministic and independent readiness checks.
3. Guarantee every implement-mode task starts with a meaningful failing test for mapped Spec scenarios and reaches green before review.
4. Guarantee durable progress initialization before full contract reading, oracle calls, delegation, or other repository writes.
5. Guarantee final review catches spec-to-implementation drift, including emitted value and type drift.
6. Guarantee closeout reports documentation drift and produces a conformance matrix before handoff.
7. Support Verify mode for trustworthy existing implementation without manufacturing a red-green history.
8. Preserve coordinator context by delegating test authoring, implementation/debugging, review, and refactor work and consuming compact evidence.
9. Support standalone and orchestrated execution through explicit authorization and responsibility, durable pause/handoff/resume state, and external Spec/Deep Plan maintenance without weakening readiness.
10. Identify readiness by immutable committed Spec/Plan blobs and bound oracle calls across resume and replacement.
11. Require capability-grounded delegation and safe auditing of recovered predecessor work.
12. Distinguish contract maintenance, general documentation, and mandatory progress/conformance artifacts.

## Non-Goals

- Authoring or maintaining the Spec or Deep Plan inside the Loop coordinator. The external `Spec` workflow and RPCE core `Deep Plan` workflow own those documents.
- Providing a weaker direct-stabilization mode that bypasses readiness or conformance.
- Assuming nested workflow dispatch, same-live-session worktree transfer, suspend/rebind/reclaim, or existing-path replacement without recorded capability proof.
- Choosing repository-specific models, validation lanes, or implementation architecture.
- Replacing repository CI or coordinated validation.

## Constraints

- Tests use the lowest faithful layer, exact observable outcomes, and realistic fixtures; no coverage-padding or mocks that recreate production logic.
- Test authoring, implementation/debugging, independent review, and refactor are delegated. No issue-size exception exists.
- The default working location is a non-default-branch worktree.
- Refactor is behavior-preserving and followed by targeted validation and review.
- Stable review signatures govern repeated-finding handling.
- Invocation mode is `standalone` or `orchestrated`; responsibility, not authorization breadth, determines which actor performs an action.
- Readiness identity is `contract_commit` plus Spec/Plan path and blob tuple; later branch `HEAD` is not a new readiness key.
- The exact lineage-owned progress path and final conformance path are mandatory operational artifacts, not general documentation or contract edits.
- External maintenance normally ends the current epoch and resumes through durable progress in a new epoch. Same-live-session maintenance is optional only after capability proof.

## Scenarios

### Scenario S-001: Readiness block occurs after durable initialization
- **Given** the Spec or Deep Plan is missing or readiness-blocking
- **When** Loop begins
- **Then** it first records the run-owned progress path and exact gaps, then stops before tests, production changes, or contract edits

### Scenario S-002: Readiness gate applies shared criteria and provenance
- **Given** Loop receives Spec and Deep Plan paths
- **When** it evaluates deterministic readiness
- **Then** it applies shared readiness criteria and verifies committed provenance, immutable blob identity, task-to-scenario traceability, and a separate implementation base

### Scenario S-003: Spec Quality findings block implementation
- **Given** the Spec has contract-level drift, non-observable scenarios, uncovered Proposed Surface, ambiguity, or hidden unresolved decisions
- **When** Loop evaluates readiness
- **Then** it records the exact gaps and blocks before tests, production code, or contract edits

### Scenario S-004: Independent verdict is Loop-owned and keyed
- **Given** deterministic readiness passes for a committed Spec/Plan tuple
- **When** Loop requests its independent readiness verdict
- **Then** it records the attempt before the call, uses the tuple key and persisted allowance, and proceeds only on one substantive `implementable` verdict or an explicitly authorized orchestrated degraded path

### Scenario S-005: Worktree safety exempts only one owned operational path
- **Given** Loop has snapshotted pre-existing dirtiness and created its progress path
- **When** it checks worktree safety
- **Then** only that exact lineage-owned progress path is exempt and every pre-existing or unrelated dirty path blocks mutation

### Scenario S-006: Progress initialization precedes readiness
- **Given** a Loop invocation starts
- **When** it performs full contract reading, oracle calls, delegation, or another repository write
- **Then** durable progress already records lineage, epoch, invocation mode, worktree/base, pre-existing dirtiness, constraints, authorization, responsibility, and `initialization_complete`

### Scenario S-007: Tests precede implementation in Implement mode
- **Given** a delegated task mapped to Spec scenarios
- **When** Loop works the task in Implement mode
- **Then** a test delegate produces and confirms a meaningful failure for the observable outcome before a production delegate changes code

### Scenario S-008: No meaningful red test halts the task
- **Given** a scenario cannot be expressed as a meaningful failing test
- **When** the test delegate reports that gap
- **Then** Loop blocks and requests contract/plan maintenance rather than accepting a tautological test or implementing anyway

### Scenario S-009: Required work remains delegated
- **Given** test authoring, implementation/debugging, independent review, or refactor work is required
- **When** Loop advances the task
- **Then** the appropriate delegate performs it and unavailable delegation blocks instead of causing coordinator implementation

### Scenario S-010: Delegated evidence is lineage-aware
- **Given** a delegate reports work
- **When** Loop evaluates the report
- **Then** it requires lineage, epoch, authorization revision, role, task/scenario IDs, changed or inspected paths, tests, validation, stable findings, blockers, and recommended next step

### Scenario S-011: Narrow inspection cannot substitute for delegation
- **Given** delegated evidence is insufficient
- **When** the coordinator needs more context
- **Then** it requests focused follow-up or reads the narrowest relevant slice and logs the exception, but never uses focused inspection as a substitute for a required delegate

### Scenario S-012: Repeated-finding classification is budgeted
- **Given** the same stable P0/P1 signature reaches the repeat threshold
- **When** Loop requests classification
- **Then** one substantive classification is allowed for that signature within the lineage ceiling; exhaustion leaves the finding unresolved and blocks closeout

### Scenario S-013: Refactor preserves behavior
- **Given** a task is green and review-clean
- **When** a refactor delegate improves it
- **Then** behavior remains unchanged and targeted tests plus post-refactor review pass

### Scenario S-014: Final review reconciles emitted values against the Spec
- **Given** a Spec fixes emitted values or types
- **When** Loop runs final delegated review
- **Then** actual emitted values from a live run or faithful fixture are compared to the contract and mismatches are reported

### Scenario S-015: Verify mode excludes unaudited recovered work
- **Given** implementation already exists
- **When** Loop selects Verify mode
- **Then** it requires trustworthy provenance, scenario coverage, and green tests; recovered predecessor work first enters Recovery audit and cannot qualify merely because implementation files exist

### Scenario S-016: Parallelization only when safe
- **Given** multiple candidate tasks
- **When** Loop schedules them
- **Then** it parallelizes only with disjoint expected files, independent fixtures, no public-API dependency, and no shared validation lane

### Scenario S-017: Final review covers the whole diff
- **Given** task loops are complete
- **When** Loop runs final review
- **Then** delegated full-diff evidence includes stable findings, inspected files, validation, and value conformance, and worthwhile findings become test-backed follow-up tasks

### Scenario S-018: Closeout runs repository validation
- **Given** final review is clean
- **When** Loop closes out
- **Then** repository-prescribed validation and required user testing run and are recorded before completion

### Scenario S-019: Documentation has three edit classes
- **Given** Loop reaches contract maintenance, documentation sync, or operational-artifact work
- **When** it interprets authority
- **Then** external Spec/Plan maintenance uses `contract_maintenance`, general docs use `doc_edits`, and exact progress/conformance outputs are mandatory operational artifacts covered by neither field

### Scenario S-020: Authorization revisions do not assign responsibility
- **Given** authority expands, reduces, or stops
- **When** Loop receives a revision
- **Then** it persists monotonic ordering and issuer, applies expansion prospectively, applies reduction or stop before the next action, rejects stale actors, rechecks before external actions, and leaves responsibility unchanged

### Scenario S-021: Oracle transport failure is not a verdict
- **Given** oracle readiness is required
- **When** transport fails, service is unavailable, or output is malformed
- **Then** the transport attempt is consumed but no substantive verdict is recorded; standalone blocks after bounded exhaustion and orchestrated degradation requires original authorization

### Scenario S-022: User testing isolates data and blocks when unavailable
- **Given** a user-facing change needs user testing
- **When** Loop closes out
- **Then** it drives a real workflow against throwaway data and blocks when no browser tool is reachable; unit tests are never labeled user testing

### Scenario S-023: Amendments are durable ordered events
- **Given** an amendment is received
- **When** Loop records or applies it
- **Then** it persists ID, issuer, scope, classification, before/after authorization revision, status, and evidence/reason, and duplicate IDs are idempotent

### Scenario S-024: Conformance path defaults to canonical unless contended
- **Given** Loop produces a matrix
- **When** no invoker-marked contention exists
- **Then** it writes canonical `<spec>.conformance.md`; a supplied per-issue path is used only for explicitly contended contracts

### Scenario S-025: Standalone and orchestrated blocks have distinct ownership
- **Given** Loop cannot proceed
- **When** it records the block
- **Then** orchestrated mode terminates that epoch with a structured report to Backlog, while standalone may remain live only in `paused`; external maintenance normally resumes through a new epoch and reusing progress does not imply the same session

### Scenario S-026: Matrix generation is not acceptance
- **Given** closeout generates a conformance matrix
- **When** any item is `Diverged` or `Not-built`
- **Then** Loop reports `blocked_unaccepted` until an authoritative item-specific acceptance exists; generation and oracle advice never accept findings

### Scenario S-027: Loop performs only assigned git actions
- **Given** implementation and closeout gates pass
- **When** Loop reaches publication or landing
- **Then** it performs only actions both authorized and assigned by responsibility; Backlog-orchestrated Loop returns committed clean `merge_ready` evidence and Backlog retains publication, landing, status, close, replacement, and cleanup

### Scenario S-028: Close metadata follows the landing owner
- **Given** GitHub merge is authorized
- **When** the actor assigned landing creates or merges the PR
- **Then** the subject carries `(#<id>)` and the body carries `Closes #<id>`

### Scenario S-029: Constraints are recorded during initialization
- **Given** repository hard rules exist
- **When** Loop initializes
- **Then** it records the constraints and source before readiness and treats them as non-negotiable across every epoch

### Scenario S-030: Loop never authors its own contract
- **Given** standalone Loop has a missing or readiness-blocking Spec or Deep Plan
- **When** contract maintenance is needed
- **Then** it writes a durable handoff for external `Spec` and/or RPCE core `Deep Plan` and does not edit either input; default resume is a new epoch after committed maintenance, while same-live-session maintenance requires recorded nested-dispatch and exclusive-worktree capability proof

### Scenario S-031: A direct-fix request exits rather than weakens Loop
- **Given** readiness or provenance is blocked
- **When** the user asks to bypass the contract and fix directly
- **Then** Loop records `handed_off_outside_loop`, makes no tests or production changes, states that outside work cannot claim Loop completion, and requires a later epoch to validate or audit it

### Scenario S-032: Progress initialization precedes readiness work
- **Given** Loop is invoked
- **When** it starts
- **Then** it snapshots pre-existing dirtiness, selects one owned progress path, persists `initialization_complete`, and only afterward performs full contract reads, oracle calls, delegation, or other writes

### Scenario S-033: Readiness uses immutable committed contract identity
- **Given** Spec and Deep Plan paths are supplied
- **When** Loop validates them
- **Then** both are tracked, clean, and present at reachable `contract_commit`; Loop records paths, blob IDs, tuple key, and separate `implementation_base_sha`

### Scenario S-034: Lifecycle states have non-overlapping resume semantics
- **Given** an epoch records `paused`, `terminated`, `handed_off_outside_loop`, `replacement_required`, `blocked`, or `completed`
- **When** further work is considered
- **Then** only live `paused` remains steerable and owns its worktree; every other state requires a new epoch, preserves disposition explicitly, and never equates handoff or block with completion

### Scenario S-035: Partial maintenance never resumes implementation
- **Given** external maintenance fails before its first commit, after only one contract commits, or with dirty contract edits
- **When** Loop receives the result
- **Then** it records `committed_partial` for a clean incomplete prefix or `dirty_partial` for uncommitted edits, preserves work, consumes no readiness verdict for that incomplete tuple, and emits an exact resume instruction; only `committed_complete` re-enters readiness

### Scenario S-036: Delegation capability is a hard implementation gate
- **Given** a required role is needed
- **When** call-based capability is unavailable or unproven
- **Then** Loop records the role and blocks or hands off without performing that role itself

### Scenario S-037: Oracle attempts and verdicts have separate budgets
- **Given** Loop requests readiness or review classification
- **When** oracle returns a verdict or transport outcome
- **Then** it persists the matching key before retry, permits at most two transport attempts and one substantive verdict per key, enforces lineage ceilings, and reports per-key versus lineage exhaustion distinctly

### Scenario S-038: Authorization revisions are ordered and prospective
- **Given** the authoritative principal expands, reduces, or revokes authority
- **When** Loop receives the revision
- **Then** it accepts only direct standalone-user or orchestrator-issued authority, persists the next revision, applies future expansion only prospectively, applies reduction or stop before the next action, and rejects stale reports

### Scenario S-039: Responsibility governs Loop's completion boundary
- **Given** authorization permits more actions than Loop owns
- **When** Loop finishes validation
- **Then** it performs only assigned actions and reports `merge_ready`; Backlog retains publication, landing, status, close, replacement, and cleanup in orchestrated mode

### Scenario S-040: Recovered work is candidate WIP until audited
- **Given** a replacement epoch inherits predecessor changes
- **When** it chooses Implement or Verify mode
- **Then** it audits all recovered work, re-establishes meaningful red evidence in isolated context from `implementation_base_sha` when chronology is not durable, and blocks rather than inferring chronology

### Scenario S-041: Progress and conformance are mandatory operational artifacts
- **Given** Loop runs without general documentation permission
- **When** it initializes or closes out
- **Then** it may create/update only the disclosed exact progress and conformance outputs without permission to edit contract or general docs; blocked progress remains unstaged unless authorized and merge-ready work commits final operational artifacts

### Scenario S-042: Conformance acceptance requires authoritative item-specific decisions
- **Given** the matrix contains `Diverged` or `Not-built`
- **When** Loop determines status
- **Then** it remains `blocked_unaccepted` unless every item records ID, rationale, accepting principal, authorization revision, and timestamp; standalone requires direct user amendment and orchestrated mode requires Backlog preauthorization

### Scenario S-043: Contract-only commits have explicit disposition
- **Given** external maintenance commits exist but implementation does not complete
- **When** standalone Loop pauses, terminates, or hands off
- **Then** progress records the exact contract range and whether it is local, pushed, in PR, or landed, and no contract-only publication occurs without `contract_publication_scope`

## Proposed Surface

### Inputs

| Input | Required | Description |
|---|---|---|
| Spec path and blob | yes | Tracked clean Spec at `contract_commit`. |
| Deep Plan path and blob | yes | Tracked clean Plan at the same reachable contract commit. |
| Invocation mode | yes | `standalone` or `orchestrated`. |
| Authorization revision | yes | Ordered issuer, effective time, scopes, acceptances, and stop state. |
| Responsibility | orchestrated yes | Actor ownership for readiness, implementation, publication, landing, status, replacement, and cleanup. |
| Progress path | yes | Exact lineage-owned operational path initialized before readiness. |
| Oracle budget | yes | Per-key attempts/verdicts and lineage ceilings. |
| Delegation capability record | yes | Call-based role availability for the actual topology. |
| Handoff | no | Predecessor epoch, HEAD, dirty manifest, authority, budget, and required next actor. |
| Toolchain and user-testing target | no | Repository commands/environment and isolated browser target. |

### Authorization

`revision`, `issuer`, `issued_at`, `effective_at`, `git_scope`, `contract_maintenance`, `contract_publication_scope`, `doc_edits`, `issue_scope`, `conformance_acceptances`, `stop`, and original `granted_at` are persisted. Latest revision is rechecked before delegate start, push, PR, merge, or metadata mutation.

### Responsibility

Standalone defaults ownership to Loop only for explicitly authorized actions. Orchestrated defaults implementation/evidence to Loop and publication, landing, status, close, replacement, and cleanup to the orchestrator.

### Contract Identity

`contract_commit`, Spec/Plan paths and blob SHAs, tuple key, `base_branch`, `base_sha`, and separate `implementation_base_sha` are recorded. Changed implementation HEAD with unchanged blobs does not create a new readiness key.

### Oracle Budget

Readiness allows one substantive verdict and two transport attempts per tuple, with standalone lineage ceiling three verdicts/six attempts and orchestrated ceiling two/four. Classification allows one verdict/two attempts per stable signature and three verdicts/six attempts per lineage.

### Lifecycle

| State | Steer | Worktree | Resume |
|---|---|---|---|
| `paused` | Same live epoch | Retained exclusively | Same epoch while live |
| `terminated` | No | Preserved or disposable by recorded state | New epoch |
| `handed_off_outside_loop` | No | Preserved per handoff | New audited epoch |
| `replacement_required` | No predecessor steer | Dirty work quarantined | Replacement after capability proof, else restart |
| `blocked` | No | Preserve/clean according to dirtiness | New epoch after resolution |
| `completed` | No | Cleanup by owner | New lineage only |

### External Maintenance

Requests name `Spec` or exact `Deep Plan`, `create|reconcile`, authorized paths, branch, starting commit, and linked counterpart. Reports return `committed_complete`, `committed_partial`, or `dirty_partial`, resulting commit range, final contract identity, dirty paths, and reason.

### Modes

`Implement`, `Verify`, and `Recovery audit`. Recovery audit resolves to Implement, Verify, or blocked.

### Artifacts

Progress contains lineage/epoch, lifecycle/phase, initialization, dirty snapshot, contract identity, authorization/responsibility, capabilities, budgets, maintenance outcome, handoff, validation, and conformance. Matrix status is `passed|blocked_unaccepted` with item-specific acceptance records.

## Open Questions

None.
