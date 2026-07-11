# Loop Workflow — Conformance Matrix

Spec: [`loop.md`](loop.md) · Implementation: [`/.agents/workflows/Loop.md`](../../.agents/workflows/Loop.md)

> Regenerated after the S-NNN backfill (S-001…S-019) and the autonomy scenarios (S-020…S-026). The spec and its workflow were co-authored in the same change, so conformance is high by construction; an independent future audit (after one side is edited alone) is the real test.

## Matrix

| Scenario | Status | Evidence | Note |
|---|---|---|---|
| S-001 Readiness gate blocks on unresolved questions | Conformed | Loop.md §Phase 1 inline gate | — |
| S-002 Readiness gate applies shared readiness criteria | Conformed | Loop.md §Phase 1 inline gate (spec-plan-readiness criteria) | — |
| S-003 Spec Quality findings block implementation | Conformed | Loop.md §Phase 1 inline gate | — |
| S-004 Readiness gate proceeds only after independent verdict | Conformed | Loop.md §Phase 1 step 4 | — |
| S-005 Worktree safety by default | Conformed | Loop.md §Core principles (Git safety); §Phase 2 step 2 | — |
| S-006 Progress artifact is persistent and resumable | Conformed | Loop.md §Phase 2 + progress body sections | — |
| S-007 Tests precede implementation in implement mode | Conformed | Loop.md §Phase 4 implement steps 1–2 | — |
| S-008 No meaningful red test halts the task | Conformed | Loop.md §Phase 4 step 2 | — |
| S-009 Work is delegated, gates are verified by the orchestrator | Conformed | Loop.md §Phase 4 + §Delegation/evidence contract | — |
| S-010 Delegation preserves orchestrator context | Conformed | Loop.md §Delegation and evidence contract | — |
| S-011 Orchestrator reads narrow context only when evidence insufficient | Conformed | Loop.md §Delegation and evidence contract | — |
| S-012 Repeated findings escape rather than loop | Conformed | Loop.md §Phase 4 step 6 | — |
| S-013 Refactor preserves behavior | Conformed | Loop.md §Phase 4 step 7 | — |
| S-014 Final review reconciles emitted values against the spec | Conformed | Loop.md §Phase 5 step 2 | — |
| S-015 Verification mode for already-implemented work | Conformed | Loop.md §Phase 4 modes | — |
| S-016 Parallelization only when safe | Conformed | Loop.md §Phase 3 | — |
| S-017 Final review covers the whole diff and converts findings to test-backed tasks | Conformed | Loop.md §Phase 5 steps 1–6 | — |
| S-018 Closeout runs repo-appropriate coordinated validation | Conformed | Loop.md §Phase 5 step 7 | — |
| S-019 Closeout reports documentation drift before handoff | Conformed | Loop.md §Phase 5 step 9 | — |
| S-020 Authorization scope governs git-visible actions; default preserved | Conformed | Loop.md §Core principles (Git safety, authorization-scope edit); §Invocation mode | New (autonomy). |
| S-021 Oracle-down degraded readiness under orchestrator authorization | Conformed | Loop.md §Phase 1 step 4; §Phase 4 step 6 | New. Standalone-down stays blocked. |
| S-022 User-testing isolates data and blocks when no browser tool | Conformed | Loop.md §Phase 5 step 7; `user-testing/SKILL.md` data-isolation rule | New. |
| S-023 Amendments acknowledged or declined with evidence, never silently skipped | Conformed | Loop.md §Phase 5 step 11 (closeout-evidence contract); §Anti-patterns | New. |
| S-024 Conformance path defaults to canonical unless invoker marks spec contended | Conformed | Loop.md §Phase 5 step 8 (contended-path note) | New. |
| S-025 Orchestrated escalation routes to orchestrator, never end-user | Conformed | Loop.md §Core principles (Invocation mode) | New. Covers dirty-worktree / no-safe-worktree / doc-edit / ambiguity routing. |
| S-026 Closeout produces the spec-conformance matrix | Conformed | Loop.md §Phase 5 step 8 | New (closeout gate). |
| S-027 Orchestrated mode completes the authorized git flow | Conformed | Loop.md §Core principles (invocation mode) | New. Standalone unchanged. |
| S-028 Closeout close-keyword on GitHub merge | Conformed | Loop.md §Phase 5 step 10 | New. Backend-conditional. |
| S-029 Repo hard-constraints loaded and non-negotiable | Conformed | Loop.md §Phase 1 step 1 | New. |

## Proposed Surface — Inputs (optional brief fields)

| Input | Status | Evidence | Note |
|---|---|---|---|
| Authorization scope | Conformed | Loop.md §Core principles; §Invocation mode | S-020. |
| Toolchain | Conformed | Loop.md §Phase 2 step 6 | L1. |
| Oracle status | Conformed | Loop.md §Phase 1 step 4 | S-021. |
| User-testing target | Conformed | Loop.md §Phase 5 step 7 | S-022. |
| Conformance path | Conformed | Loop.md §Phase 5 step 8 | S-024. |
| Escalation principal | Conformed | Loop.md §Invocation mode | S-025. |
| Constraints | Conformed | Loop.md §Phase 1 step 1 (orchestrated) / repo rule docs (standalone) | S-029. |

## Coverage proof

- **audited:** S-001…S-029 (all scenarios) + Proposed Surface Inputs.
- **unreconciled:** []
