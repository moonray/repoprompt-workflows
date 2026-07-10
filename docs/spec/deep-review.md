---
title: Deep Review Workflow
issue: none
status: implemented
---

# Deep Review Workflow

## Problem

Deep Review turns a change set into governed, revalidatable findings through a multi-shot, context-grounded process: explore agents map the area, parallel pair agents each fire `context_builder` across multiple lenses, and findings are aggregated under the `review-quality` discipline. It is named **Deep Review** because RPCE already ships a built-in `Review` workflow; reusing that name collides in the workflows picker. Today Deep Review lives only as an operational workflow prompt that mixes the behavioral contract (what it guarantees) with implementation mechanics (`context_builder`, pair/explore agents, zones). Separating the contract from the mechanism gives future improvements a canonical home.

The workflow also resolves two tensions its inputs create. First, thermo-nuclear review produces high-conviction structural *opinions* with no resolvable evidence, while `review-quality` *demands* resolvable structured evidence — the contract must guarantee that every finding, regardless of lens, carries resolvable evidence and a stable signature, and that nothing is closed on model opinion alone. Second, a fixed depth either wastes tokens on small changes or under-reviews large ones — the contract must guarantee depth auto-selects from the change unless the user overrides. Finally, the thermo-nuclear lens is vendored from a living upstream skill, so its version must be recorded and re-syncable without hand-editing the contract.

## Goals

1. Define Deep Review's contract — phases, gates, finding shape, revalidation — independent of mechanism, as the single source of truth.
2. Guarantee no review proceeds without a confirmed comparison scope and recorded author intent.
3. Guarantee the change is mapped (zones + blast radius) before any review shot fans out.
4. Guarantee every finding is context-grounded (not from memory or the raw diff) and carries resolvable structured evidence plus a stable signature.
5. Guarantee multi-lens coverage — correctness and thermo-nuclear maintainability both run on standard-or-deeper changes, not a single generic pass.
6. Guarantee findings are aggregated under the shared `review-quality` discipline: evidence gate, dedup by signature, rerank, and an inspected-scope proof.
7. Guarantee a finding is closed `fixed` only when a fresh review no longer finds it and targeted validation passes; model opinion alone never closes a finding.
8. Guarantee high-severity or contested findings can be adversarially verified (deep), and that repeated findings escalate to a classify-or-stop decision.
9. Guarantee depth auto-selects from the change's size, spread, risk, and blast radius, and that an explicit user choice overrides detection.
10. Guarantee the thermo-nuclear lens is a version-tracked canonical skill, re-syncable from upstream without hand-editing the contract.
11. Guarantee the author can dismiss findings with intent-grounded rationale, and that dismissals are recorded.

## Non-Goals

- Implementing fixes. Deep Review produces governed findings; fixing is delegated (e.g., to `Loop`).
- Choosing the specific agent model, delegation tool, file path, or partition granularity — those are plan/mechanism decisions.
- Judging spec or test quality directly. Deep Review surfaces test and doc gaps as findings but defers to `test-quality` and `document`.
- Owning the thermo-nuclear, `review-quality`, or `review-depth` skills. Deep Review inlines their discipline; the skills are the canonical standalone versions.

## Constraints

- Every finding carries structured evidence (`path`, `startLine`/`endLine`, `symbol`, `quote`) and a stable signature (severity + normalized file path + normalized finding summary + area ID). Findings whose evidence does not resolve to a reviewed location are dropped while valid sibling findings are kept.
- Deep Review treats delegated shots and agents as context firebreaks: review detail stays with the shot; the orchestrator keeps signatures and evidence, not transcripts.
- A finding is `fixed` only when a fresh review no longer finds it **and** targeted validation (tests/lint/build) passes; otherwise its status is `blocked` or `uncertain`. Manual confirmation or model opinion alone does not close a finding.
- Depth auto-selects via the `review-depth` matrix; an explicit user choice skips detection. Severe risk flags (persisted data format/migration/protocol, authn/authz/secret, public API/contract) floor depth at standard and escalate.
- The thermo-nuclear lens is the canonical `maintainability-review` skill, vendored from upstream and recorded with a source URL, retrieval date, and content digest; it is re-synced via `scripts/sync-maintainability-review.mjs`, never hand-edited inside the contract.
- Author intent, recorded at intake, is the ground truth for false-positive dismissal; every dismissal carries rationale.
- Base SHA is recorded; a mutating review does not begin on a dirty worktree.

## Scenarios

### Scenario S-001: Scope confirmation is mandatory before review
- **Given** a review begins
- **When** no comparison scope has been confirmed by the user
- **Then** review stops and requests confirmation (`uncommitted`/`staged`/`back:N`/`main`/`<branch>`) before any mapping or shot runs

### Scenario S-002: Author intent is captured before review
- **Given** review begins
- **When** intake runs
- **Then** the change's intent, known tradeoffs, and focus/skip areas are recorded, and later serve as the ground truth for false-positive dismissal

### Scenario S-003: Map precedes review shots
- **Given** a confirmed change set
- **When** review proceeds to shots
- **Then** a review map (zones + blast radius) exists before any review shot is dispatched

### Scenario S-004: Findings are context-grounded, not from memory or the raw diff
- **Given** a review shot runs on a zone
- **When** it produces findings
- **Then** it reviewed via context-grounded context rather than the raw diff or recalled code, and any finding produced without that grounding is invalid

### Scenario S-005: Multi-lens coverage on non-trivial changes
- **Given** a standard-or-deeper change
- **When** shots run
- **Then** both the correctness and thermo-nuclear maintainability lenses run (not a single generic pass), with security/tests/docs added where the surface warrants

### Scenario S-006: Thermo-nuclear lens is quality-only
- **Given** the thermo-nuclear lens reviews a change whose behavior is correct but whose structure regresses
- **When** it reports
- **Then** it flags the structural regression and does not approve merely because behavior is correct

### Scenario S-007: Structured-evidence gate drops unresolvable findings
- **Given** an aggregated finding whose `path`/`line`/`quote` does not resolve to a reviewed location
- **When** aggregation runs
- **Then** that finding is dropped while valid sibling findings are kept

### Scenario S-008: Findings carry stable signatures and dedup across shots
- **Given** the same defect surfaced by multiple shots, zones, or lenses
- **When** aggregation runs
- **Then** they collapse into one finding with a stable signature, and cross-lens corroboration is recorded as a confidence boost

### Scenario S-009: Empty result requires inspected-scope proof
- **Given** a review that produces no findings
- **When** its report is produced
- **Then** it includes the set of files/symbols inspected; "no findings" without an inspected scope is not a pass

### Scenario S-010: High-severity findings are adversarially verified in deep mode
- **Given** deep mode, or a contested P0 finding
- **When** verification runs
- **Then** a skeptic attempts to refute the finding and it is kept only if it survives

### Scenario S-011: Revalidation gate refuses model-only fixed
- **Given** a finding marked fixed
- **When** it is closed
- **Then** a fresh review no longer finds it **and** targeted validation (tests/lint/build) passes; if validation cannot run, the status is `blocked` or `uncertain`, never `fixed`, and model opinion alone does not close it

### Scenario S-012: Author dismissal is intent-grounded and recorded
- **Given** the author dismisses a finding
- **When** it is dismissed
- **Then** the dismissal is recorded with rationale grounded in the recorded intent

### Scenario S-013: Depth auto-selects from change signals
- **Given** no explicit depth was chosen at intake
- **When** review selects depth
- **Then** it computes size, spread, severe-risk flags, blast radius, and doc-only, and picks quick/standard/deep by the `review-depth` rule, recording the signals and rationale

### Scenario S-014: Severe risk flags floor and escalate depth
- **Given** a change that touches a persisted data format/migration/protocol, authn/authz/secret handling, or a public API/contract
- **When** depth is auto-selected
- **Then** the depth is at least standard and escalates one level per severe flag present, regardless of raw size

### Scenario S-015: Explicit depth overrides detection
- **Given** the user explicitly chooses quick, standard, or deep at intake
- **When** review selects depth
- **Then** that depth is used, detection is skipped, and the override is recorded

### Scenario S-016: Thermo-nuclear lens is version-tracked and re-syncable
- **Given** the thermo-nuclear lens is in use
- **When** its provenance is inspected
- **Then** a source URL, retrieval date, and upstream content digest are recorded, and a re-sync command reproduces the inlined lens from upstream without hand-editing the contract

### Scenario S-017: Report is bounded and actionable
- **Given** review completes
- **When** the report is produced
- **Then** must-fix/suggestions/skipped each carry a signature, `[File:line]`, and remedy, the inspected scope and coverage are stated, and validation results back any `fixed` status

### Scenario S-018: Repeated findings escalate rather than loop
- **Given** the same stable finding signature across two failed fix attempts or three review observations
- **When** the finding recurs
- **Then** review requests a classification (`false_positive`, `core_issue`, `futility`) rather than retrying

### Scenario S-019: Git safety before a mutating review
- **Given** a review that will mutate the worktree
- **When** the tree is dirty
- **Then** review asks the user to stash or commit and records the base SHA before proceeding

### Scenario S-020: Budget tier caps deep-mode cost
- **Given** a budget tier is supplied (`frugal`/`balanced`/`unlimited`; default `balanced`) and depth is deep
- **When** review plans shots and adversarial verification
- **Then** a `frugal` budget coarsens the zone partition (fewer parallel shots) and limits verification to contested P0s (not all high-severity), and any reduction from the depth-default plan is recorded; `balanced`/`unlimited` leave the depth-default plan unchanged

## Proposed Surface

### Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Comparison scope | yes | `uncommitted`/`staged`/`back:N`/`main`/`<branch>`; confirmed before review. |
| Author intake | yes | Intent, known tradeoffs, focus/skip areas. |
| Change set (diff/PR/branch) | yes | The code under review. |
| Depth | no | `quick`/`standard`/`deep`; auto-selected from the change if omitted, per `review-depth`. |
| Budget tier | no | `frugal`/`balanced`/`unlimited`; caps deep-mode shot + verification scope (no-op at quick/standard). |

### Gates enforced

| Gate | When | Blocking condition |
|------|------|---------------------|
| Scope confirmation | Phase 0, before mapping | No confirmed comparison scope. |
| Map-before-shots | Phase 1, before shots | No review map (zones + blast radius). |
| Context grounding | Per shot | Findings produced from the raw diff or memory, not context-grounded. |
| Multi-lens coverage | Phase 2, standard+ | Correctness and thermo-nuclear not both run on a non-trivial change. |
| Structured-evidence gate | Phase 3 | Finding evidence does not resolve to a reviewed location. |
| inspected-scope proof | Phase 3 / 6 | "No findings" without an inspected scope. |
| Revalidation gate | Phase 5 | `fixed` claimed without fresh-review-absent and validation-pass. |
| Adversarial verification | Phase 4, deep/P0 | High-severity or contested finding not surviving refutation. |
| Depth scaling | Phase 0 | Depth mismatched to change size/risk when not explicitly overridden. |
| Repeated-finding escalation | Cross-cycle | Same stable signature at the retry/observation threshold. |

### Depth selection

| Preset | Trigger | Behavior |
|--------|---------|----------|
| Quick | Small change (≤150 lines, one module), no severe flag, or doc-only | One zone; correctness + thermo-nuclear; no verification. |
| Standard | Medium change (151–800 lines), 2–3 modules, or any severe risk flag | Partitioned zones; correctness + thermo-nuclear + surface lenses; verification only for a contested P0. |
| Deep | Large change (>800 lines), ≥4 modules, or high blast radius | Fine-grained zones; full lens matrix; adversarial verification of all P0/high-severity findings. |

### Lenses

| Lens | Scope | Note |
|-------|-------|------|
| Correctness | Logic errors, error handling, edge cases, API contract | Default lens. |
| Thermo-nuclear maintainability | Structure, abstraction, file size, layers, types, orchestration | Quality-only; the versioned `maintainability-review` skill; must emit structured evidence. |
| Security | Injection, authn/authz, secrets, unsafe deserialization | Surface-warranted only. |
| Tests | Meaningful behavioral test coverage at the lowest faithful layer | Ties to `test-quality`. |
| Docs | Documented-behavior, command, parameter, schema drift | Dry-run; ties to `document`. |

### Artifacts produced

| Artifact | Required content |
|----------|------------------|
| Aggregated finding set | Findings with signature + structured evidence + severity/confidence/remedy; inspected-scope union; coverage map. |
| Shot report | Zone, lens, inspected set, findings (signature + evidence), assumptions. |
| Review report | Summary (incl. depth + signals); must-fix/suggestions/skipped (signature + `[File:line]` + remedy); coverage; validation results; open questions. |
| Dismissal log | Dismissed findings with intent-grounded rationale. |

## Open Questions

1. **Should lens selection be automatic (by surface detection) or author-chosen at intake?** Recommendation: automatic, with the selected lens set logged, overridable by explicit intake.
2. **Should the thermo-nuclear lens run on every change, or skip below a threshold (e.g., config-only)?** Recommendation: always available, auto-skip for trivial/doc-only changes with the skip logged.
3. **Should accepted findings auto-hand-off to `Loop`, or require explicit author conversion?** Recommendation: explicit conversion via a one-action hand-off.
4. **Should adversarial verification default on for every P0 regardless of depth, or only in deep?** Recommendation: on for all P0 (cheap relative to a false alarm that drives a wasted fix); deep adds broader lens-matrix coverage.
5. **Are the `review-depth` thresholds (150/800 lines, severe-flag set) the right defaults, or should they be per-repo tunable?** Recommendation: ship as defaults, allow a repo-local override file if experience shows a stack needs different bands.
