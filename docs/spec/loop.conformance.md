# Spec Conformance — Loop Workflow

- **Spec:** `docs/spec/loop.md` (Loop Workflow)
- **Implementation:** `.agents/workflows/Loop.md`
- **Audited:** 2026-07-14
- **Method:** one row per scenario and atomic Proposed Surface field/enum/constraint; evidence uses workflow line ranges.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| S-001 Readiness block occurs after durable initialization | Conformed | `.agents/workflows/Loop.md:28-74` |
| S-002 Readiness gate applies shared criteria and provenance | Conformed | `.agents/workflows/Loop.md:41-74` |
| S-003 Spec Quality findings block implementation | Conformed | `.agents/workflows/Loop.md:48-59` |
| S-004 Independent verdict is Loop-owned and keyed | Conformed | `.agents/workflows/Loop.md:59-74,108-113` |
| S-005 Worktree safety exempts only one owned operational path | Conformed | `.agents/workflows/Loop.md:16-39,76-93` |
| S-006 Progress initialization precedes readiness | Conformed | `.agents/workflows/Loop.md:28-39` |
| S-007 Tests precede implementation in Implement mode | Conformed | `.agents/workflows/Loop.md:130-145` |
| S-008 No meaningful red test halts the task | Conformed | `.agents/workflows/Loop.md:130-145,184-194` |
| S-009 Required work remains delegated | Conformed | `.agents/workflows/Loop.md:108-145` |
| S-010 Delegated evidence is lineage-aware | Conformed | `.agents/workflows/Loop.md:108-129` |
| S-011 Narrow inspection cannot substitute for delegation | Conformed | `.agents/workflows/Loop.md:108-129` |
| S-012 Repeated-finding classification is budgeted | Conformed | `.agents/workflows/Loop.md:108-113,140-145` |
| S-013 Refactor preserves behavior | Conformed | `.agents/workflows/Loop.md:140-145` |
| S-014 Final review reconciles emitted values against the Spec | Conformed | `.agents/workflows/Loop.md:147-161` |
| S-015 Verify mode excludes unaudited recovered work | Conformed | `.agents/workflows/Loop.md:130-145,178-180` |
| S-016 Parallelization only when safe | Conformed | `.agents/workflows/Loop.md:95-106` |
| S-017 Final review covers the whole diff | Conformed | `.agents/workflows/Loop.md:147-161` |
| S-018 Closeout runs repository validation | Conformed | `.agents/workflows/Loop.md:147-161` |
| S-019 Documentation has three edit classes | Conformed | `.agents/workflows/Loop.md:147-161,180-182` |
| S-020 Authorization revisions do not assign responsibility | Conformed | `.agents/workflows/Loop.md:16-26,176-182` |
| S-021 Oracle transport failure is not a verdict | Conformed | `.agents/workflows/Loop.md:59-74,108-113` |
| S-022 User testing isolates data and blocks when unavailable | Conformed | `.agents/workflows/Loop.md:147-161` |
| S-023 Amendments are durable ordered events | Conformed | `.agents/workflows/Loop.md:161-182` |
| S-024 Conformance path defaults to canonical unless contended | Conformed | `.agents/workflows/Loop.md:147-161` |
| S-025 Standalone and orchestrated blocks have distinct ownership | Conformed | `.agents/workflows/Loop.md:28-39,163-176` |
| S-026 Matrix generation is not acceptance | Conformed | `.agents/workflows/Loop.md:147-182` |
| S-027 Loop performs only assigned git actions | Conformed | `.agents/workflows/Loop.md:16-26,147-161` |
| S-028 Close metadata follows the landing owner | Conformed | `.agents/workflows/Loop.md:147-161` |
| S-029 Constraints are recorded during initialization | Conformed | `.agents/workflows/Loop.md:28-47` |
| S-030 Loop never authors its own contract | Conformed | `.agents/workflows/Loop.md:28-39,184-194` |
| S-031 A direct-fix request exits rather than weakens Loop | Conformed | `.agents/workflows/Loop.md:28-39,196-215` |
| S-032 Progress initialization precedes readiness work | Conformed | `.agents/workflows/Loop.md:28-39` |
| S-033 Readiness uses immutable committed contract identity | Conformed | `.agents/workflows/Loop.md:41-47` |
| S-034 Lifecycle states have non-overlapping resume semantics | Conformed | `.agents/workflows/Loop.md:163-176` |
| S-035 Partial maintenance never resumes implementation | Conformed | `.agents/workflows/Loop.md:176-182` |
| S-036 Delegation capability is a hard implementation gate | Conformed | `.agents/workflows/Loop.md:108-129` |
| S-037 Oracle attempts and verdicts have separate budgets | Conformed | `.agents/workflows/Loop.md:108-113` |
| S-038 Authorization revisions are ordered and prospective | Conformed | `.agents/workflows/Loop.md:176-182` |
| S-039 Responsibility governs Loop's completion boundary | Conformed | `.agents/workflows/Loop.md:16-26,147-161` |
| S-040 Recovered work is candidate WIP until audited | Conformed | `.agents/workflows/Loop.md:178-180` |
| S-041 Progress and conformance are mandatory operational artifacts | Conformed | `.agents/workflows/Loop.md:28-39,147-182` |
| S-042 Conformance acceptance requires authoritative item-specific decisions | Conformed | `.agents/workflows/Loop.md:180-182` |
| S-043 Contract-only commits have explicit disposition | Conformed | `.agents/workflows/Loop.md:180-182` |

## Proposed Surface and Constraints

| Item | Status | Evidence | Note |
|---|---|---|---|
| Input.Spec path/blob tracked clean at contract_commit | Conformed | `.agents/workflows/Loop.md:41-47` | — |
| Input.Plan path/blob tracked clean at same reachable contract_commit | Conformed | `.agents/workflows/Loop.md:41-47` | — |
| Input.invocation standalone|orchestrated | Conformed | `.agents/workflows/Loop.md:16-39` | — |
| Input.authorization ordered issuer/effective/scopes/acceptances/stop | Conformed | `.agents/workflows/Loop.md:28-39,176-182` | — |
| Input.responsibility actor ownership | Conformed | `.agents/workflows/Loop.md:16-26,176-182` | — |
| Input.progress exact lineage-owned path | Conformed | `.agents/workflows/Loop.md:28-39` | — |
| Input.oracle per-key attempts/verdicts + lineage ceilings | Conformed | `.agents/workflows/Loop.md:59-74,108-113` | — |
| Input.delegation call-based topology record | Conformed | `.agents/workflows/Loop.md:108-129` | — |
| Input.handoff predecessor/HEAD/manifest/authority/budget/next actor | Conformed | `.agents/workflows/Loop.md:28-39,163-180` | — |
| Input.toolchain + isolated user-testing target | Conformed | `.agents/workflows/Loop.md:76-93,147-161` | — |
| Authorization all 12 persisted fields | Conformed | `.agents/workflows/Loop.md:16-26,176-182` | — |
| Authorization latest revision rechecked before external action | Conformed | `.agents/workflows/Loop.md:16-26,147-182` | — |
| Responsibility standalone explicitly assigned actions | Conformed | `.agents/workflows/Loop.md:16-26,176-182` | — |
| Responsibility orchestrated Loop implementation/evidence; Backlog external actions | Conformed | `.agents/workflows/Loop.md:16-26,147-182` | — |
| Contract identity commit/paths/blobs/tuple/base/implementation base | Conformed | `.agents/workflows/Loop.md:28-47,76-93` | — |
| Contract identity implementation HEAD does not change key | Conformed | `.agents/workflows/Loop.md:41-47` | — |
| Oracle readiness 1 verdict/2 attempts; standalone 3/6; orchestrated 2/4 | Conformed | `.agents/workflows/Loop.md:59-74,108-113` | — |
| Oracle classification 1/2 per signature; 3/6 lineage | Conformed | `.agents/workflows/Loop.md:108-113,140-145` | — |
| Lifecycle.paused live same epoch retained | Conformed | `.agents/workflows/Loop.md:163-180` | — |
| Lifecycle.terminated no steer; new epoch | Conformed | `.agents/workflows/Loop.md:163-180` | — |
| Lifecycle.handed_off_outside_loop no steer; new audited epoch | Conformed | `.agents/workflows/Loop.md:163-180` | — |
| Lifecycle.replacement_required quarantine + proof/restart | Conformed | `.agents/workflows/Loop.md:163-180` | — |
| Lifecycle.blocked no steer; preserve/clean; new epoch | Conformed | `.agents/workflows/Loop.md:163-180` | — |
| Lifecycle.completed no steer; owner cleanup | Conformed | `.agents/workflows/Loop.md:163-180` | — |
| Maintenance request workflow/create|reconcile/paths/branch/start/counterpart | Conformed | `.agents/workflows/Loop.md:28-39,176-182` | — |
| Maintenance outcome complete|partial|dirty + range/identity/dirty/reason | Conformed | `.agents/workflows/Loop.md:176-182` | — |
| Mode.Implement | Conformed | `.agents/workflows/Loop.md:130-145` | — |
| Mode.Verify | Conformed | `.agents/workflows/Loop.md:130-145` | — |
| Mode.Recovery audit resolves Implement|Verify|blocked | Conformed | `.agents/workflows/Loop.md:178-180` | — |
| Artifact.progress full lineage/lifecycle/identity/authority/capability/budget/handoff/validation/conformance | Conformed | `.agents/workflows/Loop.md:28-39,76-93,147-182` | — |
| Artifact.matrix passed|blocked_unaccepted + item acceptance | Conformed | `.agents/workflows/Loop.md:147-182` | — |
| Constraint: Behavioral tests use lowest faithful layer and realistic fixtures | Conformed | `.agents/workflows/Loop.md:17-18,130-145` | — |
| Constraint: All implementation roles delegated; no size exception | Conformed | `.agents/workflows/Loop.md:19-20,108-145` | — |
| Constraint: Default location non-default-branch worktree | Conformed | `.agents/workflows/Loop.md:22-23,76-93` | — |
| Constraint: Refactor preserves behavior and is revalidated/reviewed | Conformed | `.agents/workflows/Loop.md:140-145` | — |
| Constraint: Stable signatures govern repeated findings | Conformed | `.agents/workflows/Loop.md:24-25,140-145` | — |
| Constraint: Mode standalone|orchestrated; responsibility controls actions | Conformed | `.agents/workflows/Loop.md:16-26,163-182` | — |
| Constraint: Readiness key is committed tuple, not later HEAD | Conformed | `.agents/workflows/Loop.md:41-47` | — |
| Constraint: Exact progress/conformance paths are operational artifacts | Conformed | `.agents/workflows/Loop.md:28-39,147-182` | — |
| Constraint: External maintenance normally new epoch; live transfer capability-proven only | Conformed | `.agents/workflows/Loop.md:28-39,163-182` | — |
| Authorization field: `revision` | Conformed | `.agents/workflows/Loop.md:16-26,176-182` | — |
| Authorization field: `issuer` | Conformed | `.agents/workflows/Loop.md:16-26,176-182` | — |
| Authorization field: `issued_at` | Conformed | `.agents/workflows/Loop.md:16-26,176-182` | — |
| Authorization field: `effective_at` | Conformed | `.agents/workflows/Loop.md:16-26,176-182` | — |
| Authorization field: `git_scope` | Conformed | `.agents/workflows/Loop.md:16-26,176-182` | — |
| Authorization field: `contract_maintenance` | Conformed | `.agents/workflows/Loop.md:16-26,176-182` | — |
| Authorization field: `contract_publication_scope` | Conformed | `.agents/workflows/Loop.md:16-26,176-182` | — |
| Authorization field: `doc_edits` | Conformed | `.agents/workflows/Loop.md:16-26,176-182` | — |
| Authorization field: `issue_scope` | Conformed | `.agents/workflows/Loop.md:16-26,176-182` | — |
| Authorization field: `conformance_acceptances` | Conformed | `.agents/workflows/Loop.md:16-26,176-182` | — |
| Authorization field: `stop` | Conformed | `.agents/workflows/Loop.md:16-26,176-182` | — |
| Authorization field: `granted_at` | Conformed | `.agents/workflows/Loop.md:16-26,176-182` | — |
| Contract identity field: `contract_commit` | Conformed | `.agents/workflows/Loop.md:28-47,76-93` | — |
| Contract identity field: `spec_path` | Conformed | `.agents/workflows/Loop.md:28-47,76-93` | — |
| Contract identity field: `spec_blob_sha` | Conformed | `.agents/workflows/Loop.md:28-47,76-93` | — |
| Contract identity field: `plan_path` | Conformed | `.agents/workflows/Loop.md:28-47,76-93` | — |
| Contract identity field: `plan_blob_sha` | Conformed | `.agents/workflows/Loop.md:28-47,76-93` | — |
| Contract identity field: `tuple_key` | Conformed | `.agents/workflows/Loop.md:28-47,76-93` | — |
| Contract identity field: `base_branch` | Conformed | `.agents/workflows/Loop.md:28-47,76-93` | — |
| Contract identity field: `base_sha` | Conformed | `.agents/workflows/Loop.md:28-47,76-93` | — |
| Contract identity field: `implementation_base_sha` | Conformed | `.agents/workflows/Loop.md:28-47,76-93` | — |
| Maintenance request field: `workflow` | Conformed | `.agents/workflows/Loop.md:28-39,176-182` | — |
| Maintenance request field: `operation` | Conformed | `.agents/workflows/Loop.md:28-39,176-182` | — |
| Maintenance request field: `authorized_paths` | Conformed | `.agents/workflows/Loop.md:28-39,176-182` | — |
| Maintenance request field: `branch` | Conformed | `.agents/workflows/Loop.md:28-39,176-182` | — |
| Maintenance request field: `starting_commit` | Conformed | `.agents/workflows/Loop.md:28-39,176-182` | — |
| Maintenance request field: `counterpart` | Conformed | `.agents/workflows/Loop.md:28-39,176-182` | — |
| Maintenance report field: `outcome` | Conformed | `.agents/workflows/Loop.md:176-182` | — |
| Maintenance report field: `commit_range` | Conformed | `.agents/workflows/Loop.md:176-182` | — |
| Maintenance report field: `final_contract_identity` | Conformed | `.agents/workflows/Loop.md:176-182` | — |
| Maintenance report field: `dirty_paths` | Conformed | `.agents/workflows/Loop.md:176-182` | — |
| Maintenance report field: `reason` | Conformed | `.agents/workflows/Loop.md:176-182` | — |
| Lifecycle value: `paused` | Conformed | `.agents/workflows/Loop.md:163-180` | — |
| Lifecycle value: `terminated` | Conformed | `.agents/workflows/Loop.md:163-180` | — |
| Lifecycle value: `handed_off_outside_loop` | Conformed | `.agents/workflows/Loop.md:163-180` | — |
| Lifecycle value: `replacement_required` | Conformed | `.agents/workflows/Loop.md:163-180` | — |
| Lifecycle value: `blocked` | Conformed | `.agents/workflows/Loop.md:163-180` | — |
| Lifecycle value: `completed` | Conformed | `.agents/workflows/Loop.md:163-180` | — |
| Progress field: `lineage` | Conformed | `.agents/workflows/Loop.md:28-39,76-93,147-182` | — |
| Progress field: `epoch` | Conformed | `.agents/workflows/Loop.md:28-39,76-93,147-182` | — |
| Progress field: `lifecycle` | Conformed | `.agents/workflows/Loop.md:28-39,76-93,147-182` | — |
| Progress field: `phase` | Conformed | `.agents/workflows/Loop.md:28-39,76-93,147-182` | — |
| Progress field: `initialization` | Conformed | `.agents/workflows/Loop.md:28-39,76-93,147-182` | — |
| Progress field: `dirty_snapshot` | Conformed | `.agents/workflows/Loop.md:28-39,76-93,147-182` | — |
| Progress field: `contract_identity` | Conformed | `.agents/workflows/Loop.md:28-39,76-93,147-182` | — |
| Progress field: `authorization` | Conformed | `.agents/workflows/Loop.md:28-39,76-93,147-182` | — |
| Progress field: `responsibility` | Conformed | `.agents/workflows/Loop.md:28-39,76-93,147-182` | — |
| Progress field: `capabilities` | Conformed | `.agents/workflows/Loop.md:28-39,76-93,147-182` | — |
| Progress field: `budgets` | Conformed | `.agents/workflows/Loop.md:28-39,76-93,147-182` | — |
| Progress field: `maintenance_outcome` | Conformed | `.agents/workflows/Loop.md:28-39,76-93,147-182` | — |
| Progress field: `handoff` | Conformed | `.agents/workflows/Loop.md:28-39,76-93,147-182` | — |
| Progress field: `validation` | Conformed | `.agents/workflows/Loop.md:28-39,76-93,147-182` | — |
| Progress field: `conformance` | Conformed | `.agents/workflows/Loop.md:28-39,76-93,147-182` | — |

## Coverage Proof

- **audited:** S-001…S-043, 83 atomic Proposed Surface/field/enum items, and all 9 constraints.
- **unreconciled:** none.
- **status:** `passed`.
