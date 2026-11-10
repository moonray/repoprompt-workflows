---
title: Backlog-Overseer Workflow
issue: none
status: implemented
---

# Backlog-Overseer Workflow

## Problem

Backlog-Overseer runs the Backlog pipeline on the RPCE overseer substrate. The v1 wizard asked a multi-part question at every launch even though the operator has never overridden a default; v1's same-turn flight-set polling exists only because RPCE historically delivered no completion notifications; and v1's deferred end-of-run cleanup conflicts with overseer scope guardrails, which count live lanes and worktrees. The first overseer run (2026-11-09) additionally showed that an app-side placement failure can poison an entire granted scope, and that a granted scope can exceed what was requested.

The workflow needs a precise contract for the launch-time settings model, substrate selection and its failure playbooks, lane coordination, capacity lifecycle, and teardown — while inheriting the Backlog pipeline contract unchanged where not superseded.

## Goals

1. Resolve every run's settings deterministically at launch from committed defaults plus explicit overrides, before any mutation.
2. Keep an explicit, immediately-prior ask for every git-visible action: an empty launch is non-publishing.
3. Keep authorization a persisted, user-owned revision that the orchestrator never mints to itself.
4. Select the coordination substrate from evidence: wake mode only with verified wake delivery and a lane-independent liveness backstop; otherwise a complete v1-semantics fallback.
5. Degrade safely from oversight infrastructure failures without retrying into a poisoned grant.
6. Verify granted authority against the request; unrequested capabilities are disclosed and never used.
7. Coordinate lanes only through confirmed oversight links, event-driven.
8. Release lane and worktree capacity per completed issue so scope guardrails bound concurrency, not queue depth.
9. Retain operator history: session dismissal is the terminal teardown state and deletion is never recommended.
10. Encode known RPCE routing limits instead of rediscovering them per run.

## Non-Goals

- Replacing or mutating the v1 Backlog workflow before wake mode is proven on real runs (v1 stays installed as the fallback substrate; deprecation marker only after 2–3 wake-mode runs complete without substrate fallback — operator decision recorded 2026-11-10).
- Zero-argument push/merge/auto-close: making git-visible actions the empty-launch default would be a standing delegation and is excluded.
- Deleting sessions, branches, or history automatically, or recommending deletion.
- Authorizing destructive git through any setting or grant.
- Implementing issue code, tests, debugging, review, or refactor inside the orchestrator (inherited Backlog non-goal).

## Constraints

- Exactly one coordination substrate per run: wake mode or fallback, never mixed.
- Wake mode requires oversight tools available, a granted tree scope, wake delivery probe-verified in the current grant, and a configured lane-independent idle-wake backstop.
- Scope guardrails cap the substrate: max depth 2 (lanes delegate roles), live sessions sized from the pre-flight delegation-topology call-test, live worktrees 3; the platform lane ceiling is 12 per overseer.
- Pace never exceeds 3 concurrent issues; the default is 1 (concurrent orchestration assumed unknown).
- `agent_run` worktree binding resolves from the primary root only (platform limit).
- This spec inherits every scenario of `docs/spec/backlog.md` except where explicitly superseded below; inherited scenarios carry over unchanged. Superseded: S-003 (exempt batch) and S-004 (wizard ask) by the launch contract (S-101–S-104, S-115); S-014 (flight ceiling) by pace plus guardrails (S-105, S-112); the deferred-cleanup limb of S-055 by S-112 (its resume/replacement limbs are inherited and extended by S-117).
- Scenario IDs occupy the S-101…S-1NN block, distinct from Backlog's S-001…S-059, so cross-spec citations stay unambiguous.

## Scenarios

### Scenario S-101: Settings resolve at launch, before any mutation
- **Given** the workflow is launched with `$ARGUMENTS` (possibly empty)
- **When** settings are resolved
- **Then** every argument key is one of the allowed override keys with a valid value, or the run blocks with the parse error before any issue, repository, or session mutation; an empty argument list resolves every setting to the committed defaults

### Scenario S-102: An empty launch is non-publishing
- **Given** a launch whose arguments name no git-visible setting
- **When** settings resolve
- **Then** completion is local-only, close is evidence-only, and the exempt-close batch is report-only; no push, PR, merge, or issue-status change occurs at any point in the run

### Scenario S-103: Authorization is persisted, user-owned, and never self-minted
- **Given** resolved settings
- **When** the run begins work
- **Then** an authorization revision (issuer, granted and effective timestamps, git scope of the triaged issue paths, stop flag) is persisted to the run progress doc before the first mutation, and later revisions arise only from an explicit user message, applied monotonically

### Scenario S-104: Zero routine asks
- **Given** a run in progress after launch
- **When** the orchestrator needs a decision
- **Then** no user question is initiated; the only user touchpoints are a required-tool pre-flight failure, the app-side scope approval card, the operator-attended wake probe, and explicit user messages — every other decision follows the escalation ladder or blocks the item

### Scenario S-105: Substrate selection is evidence-driven with a complete fallback
- **Given** oversight tools, a scope grant, and a probe record
- **When** the substrate is selected
- **Then** wake mode is used only when the tools are available, the scope is granted, wake delivery is probe-verified in the current grant, and the idle-wake backstop is configured; otherwise the run uses fallback mode with no oversight-scope calls, same-turn bounded waits, and v1 teardown, and the mode is recorded in the run doc

### Scenario S-106: The probe ends no turn before verification
- **Given** a first run for a scope lineage
- **When** the wake probe runs
- **Then** the probe lane's task completes within the turn before any wake test; the wake test ends a turn only with the operator-attended contract stated in advance (an operator re-invocation after the agreed window counts as wake failure); the resulting probe record states mode, verified channels, scope lineage, and date

### Scenario S-107: Placement-denied scopes degrade without in-grant retry
- **Given** an active scope whose lane creation is denied placement-unresolved while scope inventory shows only the orchestrator
- **When** the denial is handled
- **Then** the run degrades to fallback, releases the scope, records the denial evidence in the probe record, and discloses the operator recovery; lane creation is not retried inside the denied grant, and dispatch is re-tested only after release

### Scenario S-108: Grants are verified against the request
- **Given** a scope grant returns
- **When** the grant is recorded
- **Then** the granted capabilities and guardrails are recorded verbatim; any capability not requested (including destructive) is disclosed in the run doc and never exercised

### Scenario S-109: Lanes are link-confirmed before a turn ends
- **Given** a dispatched lane has reached a running state
- **When** the orchestrator considers ending its turn
- **Then** the lane is confirmed linked under the current scope before turn-end; a lane whose link cannot be confirmed is waited on same-turn instead

### Scenario S-110: Wake events route by type
- **Given** wake mode and an arrived lane update or backstop wake
- **When** the event is handled
- **Then** result events run verify, close, capacity release, then refill; decision events follow the escalation ladder with whitelisted-accept and scope-decline approvals; failure events verify the claimed blocker against ground truth first; backstop wakes check milestone rows; quiet check-ins with nothing actionable produce no work

### Scenario S-111: Live wake confirmation — backstop-only arrival is failure
- **Given** wake mode with a dispatched lane
- **When** the lane's first result arrives
- **Then** arrival via a lane update confirms wake delivery for the run; arrival only via the idle-wake backstop with the lane already terminal marks wake delivery failed, degrades the run to fallback, and rewrites the probe record

### Scenario S-112: Capacity is released per completed issue
- **Given** an issue has passed verification, closure, and landing
- **When** capacity is released
- **Then** the lane is unlinked and retired and the merged-path worktree is removed before the next dispatch; retained open-PR and local-only worktrees count against the worktree ceiling, and an exhausted ceiling stops new dispatch with a checkpoint disclosure in the rollup rather than a mid-allocation guardrail refusal

### Scenario S-113: Session history is retained
- **Given** completed lanes at teardown
- **When** teardown runs
- **Then** sessions are dismissed or archived only; the rollup never presents completed sessions as awaiting deletion, and deletion is neither performed nor recommended

### Scenario S-114: Non-primary-root issues route serialized in-checkout
- **Given** a queued issue whose target repository is not the primary root
- **When** it is dispatched
- **Then** it runs serialized branch-in-checkout with the orchestrator reading only and one branch per issue, disclosed in the rollup, instead of a worktree binding

### Scenario S-115: Triage excludes blocked, invalid, and decision items
- **Given** discovered open items
- **When** the work queue is built
- **Then** status-blocked and invalid items are excluded from both the queue and close candidates (restart-required rows rejoin only through the resume path), and decision-type items route to the rollup unresolved

### Scenario S-116: Conservative escalation blocks oracle-decidable ambiguity
- **Given** escalation=conservative in the resolved settings
- **When** an oracle-decidable ambiguity arises mid-run
- **Then** the item is blocked rather than decided; under the default autonomous setting the oracle decides and the decision with rationale is recorded in the run doc

### Scenario S-117: Resume re-probes a re-granted scope and re-checks the wedge
- **Given** a run resumed after restart
- **When** flight state is reconstructed
- **Then** settings come from the run doc without re-asking; a missing scope is re-granted with the same guardrails and the probe re-runs as a new scope lineage; restart-required rows rejoin only after the provisioning-wedge signature is confirmed absent with attempt counts preserved; the default branch is synced before any retroactive verification

## Proposed Surface

### Launch Contract
`$ARGUMENTS`: whitespace-separated `key=value`; allowed keys pace, concurrent_orchestration, completion, contract_publication_scope, close, role, escalation, max_issues, retain; unknown key or invalid value blocks (S-101). DEFAULTS table (committed): triage order, non-publishing completion/close/exempt defaults, pace 1, role pair, escalation autonomous, retain off, degraded_ok false, doc_edits false, browser isolation preference (S-102).

### Authorization Revision
Fields: revision, issuer (backlog-overseer-launch), granted_at, effective_at, git_scope (the triaged issue paths, filled when triage closes), stop (S-103).

### Oversight Grant
Requested capabilities (observe, organize, control, restructure, spawn, worktree) and guardrails (max depth 2, live-session sizing from the call-test, live worktrees 3); the granted set is recorded verbatim with extras disclosed (S-105, S-108).

### Probe Record
`docs/progress/backlog-overseer-probe.md`: probe mode (passed or fallback), verified channels, scope lineage, date, evidence lines; valid for its scope lineage only (S-106, S-107, S-111, S-117).

### Lane Brief
Fields per dispatch: progress path, lineage and epoch, contract tuple identity, base SHAs, authorization revision, responsibility map, toolchain, oracle status, user-testing target, amendments, siblings, repo constraints verbatim, and the notification policy (notify on result, failure, or decision; quiet otherwise) (S-110).

### Event Handler Table
Result, decision or approval, failure, backstop, quiet check-in (S-110).

### Capacity Release
Order: unlink lane, retire lane, remove merged-path worktree; retained-worktree ceiling checkpoint (S-112).

### Teardown Order
Lanes, then worktrees (completion-path gated, branches always kept), then scope release last (S-112, S-113).

### Run Progress Doc
`docs/progress/backlog-<run>.md`: resolved settings, authorization revision, pre-existing state snapshot, capability table, substrate record, triaged queue, ledger, rollup with the loaded authorization restated (S-103, S-104).

### Gates
Two-beat verify, conformance-passed-to-land, serial rebase-merge, CI-red parking, conflict policy — inherited from `docs/spec/backlog.md` Proposed Surface; the non-publishing defaults keep them landing-gated (S-102).

## Open Questions

1. **Agent-side wake configuration** — can the orchestrator configure auto-wake and the idle-wake interval via MCP, or are they UI-only per overseer session? *Recommendation:* determine in the next re-probe; if UI-only, Phase 0.4 gains an operator instruction to set wake controls before the probe (S-106's observable — backstop confirmed active before any turn-end — is unchanged either way).
2. **Tree-wide live-session counting** — do lane-internal delegated roles count against the live-session guardrail? *Recommendation:* keep call-test-driven sizing and record the observed behavior; if counting is tree-wide, size to pace × (1 + observed fan-out).
3. **Quiet check-in support** — does the Claude Code route classify self_noop quiet check-ins? *Recommendation:* verify in the re-probe; if unsupported, drop the quiet-check-in row from the event handler table (noise, not correctness).
