---
title: Backlog Workflow
issue: none
status: implemented
---

# Backlog Workflow

## Problem

Backlog coordinates many tracked issues through isolated Loop runs. Recent runs exposed contract gaps at the Backlog–Loop seam: uncommitted contract inputs, ambiguous action ownership, unbounded oracle calls, inline implementation after delegation failure, stacked issue branches, missing progress initialization, and unsafe recovery of dead sessions with dirty work.

Backlog needs a precise orchestration contract that preserves Loop's standalone guarantees while making Backlog the sole principal for contract preparation, deterministic re-gating, publication, landing, status, close, replacement, and cleanup.

## Goals

1. Preserve backend-agnostic tracked-work discovery, triage, and status ownership.
2. Keep the Phase-2 wizard as the only solicited input point while persisting direct amendments.
3. Separate action authorization from actor responsibility.
4. Require committed, reachable Spec/Deep Plan inputs before Loop dispatch.
5. Keep independent issues concurrent while dispatching only from refreshed default.
6. Reconcile unknown starts and provisioning wedges without blind retries or invented user intent.
7. Verify Loop work independently before landing or closing.
8. Recover dead Loop work through preservation and audited replacement, never inline implementation.
9. Bound oracle and delegation capabilities durably across restart and replacement.
10. Distinguish contract maintenance, contract-only publication, general docs, and mandatory operational artifacts.
11. Separate conformance generation from item-specific acceptance.

## Non-Goals

- Implementing issue code, tests, debugging, review, or refactor in the Backlog coordinator.
- Supporting stacked issue branches or parent-based PR chains.
- Assuming nested delegation, dirty-worktree transfer, existing-path replacement, or worktree reclaim without capability proof.
- Allowing oracle advice to create authorization or accept divergence.
- Deleting branches automatically.

## Constraints

- Discovery, status mutation, and close use track-work noninteractively; unavailable identity/capability blocks without fallback ledger.
- At most three Loop issues are in flight, with a lower local ceiling when other orchestrators may share RPCE resources.
- Each issue has a unique branch/worktree rooted directly on refreshed default.
- Backlog owns publication, landing, issue status, close, replacement, and cleanup in orchestrated mode.
- Contract preparation uses external `Spec` and RPCE core `Deep Plan` workflows; Backlog and Loop never author contract content inline.
- Readiness identity is the committed Spec/Plan blob tuple, not later implementation HEAD.
- Dirty predecessor work stays on its original branch/worktree and never uses suffix fallback.
- Authorization revisions are prospective, ordered, and rechecked before externally visible actions.

## Scenarios

### Scenario S-001: Discovery is backend-agnostic via track-work
- **Given** Backlog needs to discover, read, block, update, or close work
- **When** it invokes tracking behavior
- **Then** it uses track-work in noninteractive caller mode, accepts track-work backend identity/capability as authoritative, and blocks without reading or writing a fallback ledger when unavailable

### Scenario S-002: Triage order is bugs, then priority, then ease
- **Given** discovered open non-exempt items
- **When** Backlog triages
- **Then** bugs come first, then priority p0 through p3, then ease with unlabeled effort last

### Scenario S-003: Exempt items form a confirmed close batch
- **Given** `wontfix` or `duplicate` items already carry the human-decision label
- **When** discovery completes
- **Then** they are shown once in the wizard and never receive Loop sessions; duplicate closes cross-link canonical items

### Scenario S-004: The wizard is the only solicited ask
- **Given** the Phase-2 wizard completed
- **When** Backlog later needs a decision or receives a direct unambiguous user amendment
- **Then** it never initiates another question; policy/oracle decisions are decided or blocked, while unsolicited amendments are persisted and applied only within existing issue scope

### Scenario S-005: Authorization is a ceiling, not responsibility
- **Given** the latest revision permits git, documentation, contract-maintenance, or issue actions
- **When** an actor reaches an action
- **Then** the action must be permitted and assigned to that actor; broader scope never transfers Backlog's landing, status, close, replacement, or cleanup ownership

### Scenario S-006: Capability gaps surface before dispatch
- **Given** a run depends on tracking, oracle, browser, worktree, Loop dispatch, or Loop delegated roles
- **When** Backlog preflights
- **Then** it records call-based results, exposes actionable gaps in the single wizard, and blocks affected work rather than inferring capability or implementing inline

### Scenario S-007: Contract generation requires clear committed outputs
- **Given** an issue lacks Spec or Deep Plan
- **When** deterministic and oracle clarity gates pass
- **Then** Backlog invokes external `Spec` and/or exact `Deep Plan` and treats preparation complete only when required paths are tracked, clean, blob-identified, committed, and reachable from the issue branch

### Scenario S-008: Oracle-down degrades only preauthorized existing-contract work
- **Given** oracle is unavailable
- **When** Backlog processes issues
- **Then** existing ready contracts proceed only under original `degraded_ok`, contract creation blocks, and no call retry or scope decision is invented

### Scenario S-009: One unique worktree and branch per issue
- **Given** an issue is dispatched
- **When** Backlog allocates execution state
- **Then** no two Loop sessions share a branch or worktree and branch naming derives from immutable item identity

### Scenario S-010: Predecessor reconciliation preserves work
- **Given** an earlier session/worktree may be live, dead, clean, or dirty
- **When** Backlog reconciles it
- **Then** it resumes only a live provider, cleans only attributable disposable state, and preserves dirty or ambiguous work for audited replacement rather than reusing, copying, or suffixing it

### Scenario S-011: Dispatch calls are isolated
- **Given** Backlog starts Loop
- **When** it invokes `agent_run start`
- **Then** the start is alone in its tool batch

### Scenario S-012: Provisioning attempts and replacement epochs are distinct
- **Given** a fresh start may have unknown outcome while an executing Loop may later die
- **When** Backlog reconciles failure
- **Then** fresh starts use the two-attempt provisioning budget, while post-start recovery creates a new lineage epoch and preserves predecessor work

### Scenario S-013: Concurrent issues are sibling-aware
- **Given** multiple Loops are in flight
- **When** each is briefed
- **Then** each receives sibling issue IDs and source areas

### Scenario S-014: At most three issues are in flight
- **Given** more than three independent issues
- **When** Backlog dispatches
- **Then** it keeps the persisted local ceiling and queues excess work without another ask

### Scenario S-015: Contended issues serialize
- **Given** issues share target contract or source function/concern
- **When** Backlog schedules them
- **Then** they do not fly concurrently; adjacent disjoint-function work may fly and merges last

### Scenario S-016: Independent closeout verifies both ranges
- **Given** Loop reports assigned work complete
- **When** Backlog verifies
- **Then** it separately verifies contract-preparation and implementation ranges, rejects pre-initialization evidence, reruns tests, validates operational artifacts, and closes only with conformance `passed`

### Scenario S-017: Verification may overlap dispatch but precedes close
- **Given** a Loop landed
- **When** Backlog verifies
- **Then** another independent slot may be filled, but close and cleanup never precede verification

### Scenario S-018: CI failure parks without asking
- **Given** merge is authorized
- **When** close-gate or CI is red
- **Then** the issue remains review-blocked and is not merged or presented as an override question

### Scenario S-019: Merge conflicts regenerate only derived outputs
- **Given** serial landing conflicts
- **When** conflict is limited to allowlisted derived docs
- **Then** Backlog regenerates them; any source/spec/plan/test conflict aborts and blocks

### Scenario S-020: Decision items are never auto-resolved
- **Given** an item is `type:decision`
- **When** Backlog processes it
- **Then** it routes to human triage and never specs, implements, or closes it automatically

### Scenario S-021: Ledger captures authority and lineage
- **Given** issue state changes
- **When** Backlog persists the ledger
- **Then** it records contract identity, implementation base, authorization revision, responsibility, lineage/epoch, capabilities, oracle counters, dirty/maintenance state, conformance/acceptance, and predecessor/replacement handoff

### Scenario S-022: Resume restores authority without replay
- **Given** a run resumes
- **When** ledger joins current sessions, worktrees, branches, and blobs
- **Then** it restores latest authority, responsibility, counters, epoch, ownership, and rejects stale reports without repeating oracle calls for unchanged keys

### Scenario S-023: Escalation cannot invent conformance acceptance
- **Given** a decision exceeds authority, weakens a gate, or accepts an unlisted divergence
- **When** Backlog escalates
- **Then** it blocks unless item-specific acceptance exists in current authorization; oracle advice never creates authority

### Scenario S-024: Rollup includes contract and recovery disposition
- **Given** the run ends or pauses
- **When** Backlog rolls up
- **Then** it reports contract/implementation ranges, contract-only publication, authority/responsibility, capability/oracle exhaustion, lifecycle/dirty disposition, conformance status, and resume instructions

### Scenario S-025: Browser testing is concurrency-safe
- **Given** concurrent UI issues
- **When** user testing runs
- **Then** isolated profiles/page routing are proven or browser testing serializes

### Scenario S-026: Resume syncs default before retroactive verify
- **Given** merged work needs retroactive verification
- **When** Backlog resumes
- **Then** it fetches and fast-forwards default non-destructively and confirms the fix is present before testing

### Scenario S-027: Retroactive UI testing uses synced merged tree
- **Given** a merged UI item missed testing
- **When** Backlog recovers
- **Then** it tests the synced tree with throwaway data and records the result

### Scenario S-028: Track-work status is authoritative
- **Given** another note claims item status
- **When** Backlog triages
- **Then** it rechecks track-work and ignores conflicting informal claims

### Scenario S-029: Backlog finishes only verified mechanical git flow
- **Given** Loop stops before an action assigned to Backlog
- **When** Backlog considers completion
- **Then** it performs only mechanical git actions for committed clean Loop-finalized independently verified work and never authors or repairs unfinished implementation

### Scenario S-030: Close metadata follows landing ownership
- **Given** GitHub merge is authorized
- **When** Backlog as landing owner creates or merges PR
- **Then** subject carries `(#N)` and body carries `Closes #N`

### Scenario S-031: Browser isolation is detected
- **Given** concurrent browser testing is considered
- **When** Backlog preflights
- **Then** it proves isolation/page routing or serializes

### Scenario S-032: Brief carries immutable authority and lineage
- **Given** Backlog dispatches Loop
- **When** it constructs the brief
- **Then** it includes authorization revision, responsibility, contract identity, implementation base, progress path, oracle budgets, delegation capability, predecessor handoff, epoch, and repository constraints

### Scenario S-033: Documentation permission is not contract permission
- **Given** documentation sync runs
- **When** Backlog interprets `doc_edits`
- **Then** it applies only to general docs and neither authorizes contract maintenance nor controls mandatory progress/conformance output

### Scenario S-034: Cleanup follows lifecycle and ownership
- **Given** finalization
- **When** Backlog evaluates disposable state
- **Then** it cleans only completed, closed, or safely disposable rows and preserves paused, replacement-required, dirty-partial, local-only, and restart-required work

### Scenario S-035: Independent issues fly by default
- **Given** capacity and independent queued work
- **When** a slot opens
- **Then** Backlog dispatches the highest-priority independent issue and does not starve contended work

### Scenario S-036: Concurrent branches land serially
- **Given** multiple issues flew
- **When** Backlog lands
- **Then** it lands one at a time from most independent to most overlapping against updated default

### Scenario S-037: Harness rejection text is not user intent
- **Given** a start result contains generic rejection text without explicit user stop
- **When** Backlog handles it
- **Then** it treats it as technical outcome and reconciles autonomously

### Scenario S-038: Cross-window risk is captured
- **Given** other RPCE orchestration may share resources
- **When** the wizard runs
- **Then** it records `none|yes|unknown` and defaults local dispatch ceiling to one for yes/unknown unless explicitly raised

### Scenario S-039: Provisioning wedge requires restart recovery
- **Given** read-only RPCE calls work while provisioning hangs or zero-turn artifacts accumulate
- **When** Backlog detects the signature
- **Then** it stops starts, preserves attempts/counters/authority/epoch, checkpoints live work, marks restart-required, and resumes only after restart sweep

### Scenario S-040: Cleanup skip quarantines clean dead-session branch bindings
- **Given** cleanup skips a dead clean session
- **When** Backlog retries provisioning
- **Then** it quarantines the bound branch and may use a suffix only for clean half-provisioning; dirty predecessor work remains on original state

### Scenario S-041: Diagnosis separates evidence from hypotheses
- **Given** dispatch fails ambiguously
- **When** Backlog explains or recovers
- **Then** it separates observed state from hypotheses and never asks the user to choose speculative remedies

### Scenario S-042: Backlog owns external contract preparation
- **Given** inputs are missing/blocking or Loop reports gaps
- **When** Backlog prepares contracts
- **Then** it invokes external `Spec`/`Deep Plan`, records `committed_complete|committed_partial|dirty_partial`, runs deterministic readiness only for committed complete tuples, and dispatches a new epoch only after pass

### Scenario S-043: Failure never authorizes Backlog implementation
- **Given** Loop cannot start/delegate or dies
- **When** Backlog recovers
- **Then** it reconciles, replaces, preserves, restarts, or blocks without writing tests/code/refactors/reviews or unfinished commits

### Scenario S-044: Oracle ownership and accounting are durable
- **Given** clarity, conflict, or readiness decisions may use oracle
- **When** an operation occurs
- **Then** transport attempts and substantive verdicts are persisted separately under ceilings, and Backlog never performs Loop's independent verdict

### Scenario S-045: Authorization and responsibility are independent
- **Given** a brief has both
- **When** action is permitted
- **Then** only named owner acts; Backlog owns preparation, deterministic gate, publication, landing, status, close, replacement, cleanup

### Scenario S-046: Explicit amendments revise authority without another wizard
- **Given** wizard completed and user sends direct amendment
- **When** classifiable within issue scope
- **Then** Backlog records monotonic revision, prospective expansion, next-action reduction/stop, forwards it, rejects stale actions, and defers ambiguous/scope-expanding requests

### Scenario S-047: Issue branches start from refreshed default
- **Given** dependency is unmerged or default stale
- **When** branch preparation occurs
- **Then** issue waits, default refreshes non-destructively, and branch starts directly from refreshed default

### Scenario S-048: Contract inputs have immutable provenance
- **Given** Loop dispatch is imminent
- **When** inputs are validated
- **Then** both are tracked clean blobs at reachable contract commit with tuple key and separate implementation base

### Scenario S-049: Only post-initialization evidence is accepted
- **Given** Loop reports evidence
- **When** Backlog evaluates
- **Then** expected progress path, lineage, epoch, initialization checkpoint, and chronology must precede accepted changes

### Scenario S-050: Dirty predecessor work is preserved and audited
- **Given** an epoch dies with work
- **When** recovery occurs
- **Then** exact worktree/branch/HEAD/manifest/epoch are preserved; replacement on existing path needs exclusive capability proof else restart-required; replacement audits and re-establishes red evidence or blocks

### Scenario S-051: Mechanical publication requires verified-complete work
- **Given** Backlog owns external git action
- **When** it acts
- **Then** work is clean, committed, finalized, independently verified, conformance passed, and latest authorization rechecked

### Scenario S-052: Delegation capability is proven before dispatch
- **Given** Loop needs delegated roles
- **When** Backlog preflights
- **Then** each role is call-tested available/unavailable/unproven and implementation dispatch occurs only when all required roles are available

### Scenario S-053: Conformance generation and acceptance are separate
- **Given** matrix contains Diverged/Not-built
- **When** status is evaluated
- **Then** conformance is blocked-unaccepted unless each item has preauthorized reasoned acceptance; generation/oracle advice never accepts

### Scenario S-054: Contract-only commits remain visible
- **Given** preparation commits exist but implementation cancels/blocks/local-only
- **When** rollup occurs
- **Then** exact range/state is reported and publication requires separate contract publication scope

### Scenario S-055: Lifecycle controls resume/replacement/cleanup
- **Given** epoch lifecycle state
- **When** Backlog considers steer/replace/clean
- **Then** only live paused is steerable, terminal states need new epoch, dirty replacement work is preserved, outside handoff is not completion, and only safely disposable state cleans

## Proposed Surface

### Wizard

Existing fields remain. Add `contract_maintenance: deny|workflow-only` (default workflow-only), `contract_publication_scope: with-issue-only|branch+pr|branch+pr+merge` (default with-issue-only), item-specific `conformance_acceptances`, delegation capability summary, and explicit oracle degraded policy. Track-work mutation confirmation remains part of the single wizard.

### Authorization

Persist revision, issuer, issued/effective times, implementation git scope, contract-maintenance scope, contract-publication scope, general-doc permission, immutable issue scope, item-specific conformance acceptances, stop state, and original grant timestamp. Recheck latest revision before delegate start, push, PR, merge, or issue mutation.

### Responsibility

Backlog-issued values assign contract preparation, deterministic readiness, publication, landing, status/close, replacement, and cleanup to Backlog; independent readiness and delegated implementation/evidence belong to Loop.

### Contract Identity

Record reachable `contract_commit`, Spec/Plan paths and blob SHAs, tuple key, refreshed base branch/SHA, and separate `implementation_base_sha`.

### Maintenance

Requests name exact workflow (`Spec` or `Deep Plan`), `create|reconcile`, paths, branch, starting commit, and counterpart. Reports return committed-complete, committed-partial, or dirty-partial, commit range, final identity, dirty paths, reason.

### Delegation Capability

For test authoring, implementation/debugging, independent review, and refactor, record available/unavailable/unproven, call evidence, tested topology, timestamp, reason.

### Oracle Budget

Readiness: Loop one substantive verdict/two attempts per tuple, standalone lineage 3/6 and orchestrated 2/4. Backlog clarity/conflict use separate keyed budgets; deterministic readiness consumes none. Counters survive restart/replacement.

### Lifecycle and Ledger

Persist `paused|terminated|handed_off_outside_loop|replacement_required|blocked|completed`, lineage/epoch, phase, authority/responsibility, capabilities, contract identity, dirty snapshot/manifest, maintenance outcome, oracle counters, handoff, validation, conformance/acceptance, and contract/implementation ranges.

### Gates

Tracking capability, single wizard, authority+responsibility, contract provenance, default-parent branch, dispatch/liveness, progress initialization, delegation, oracle budgets, independent verification, conformance acceptance, verified mechanical landing, conflict safety, lifecycle-safe cleanup.

### Artifacts

Run progress ledger, per-Loop progress, immutable contract inputs, maintenance report, dirty handoff manifest, delegated evidence, conformance matrix/status/acceptances, rollup.

## Open Questions

None.
