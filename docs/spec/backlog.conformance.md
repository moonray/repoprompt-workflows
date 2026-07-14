# Spec Conformance — Backlog Workflow

- **Spec:** `docs/spec/backlog.md` (Backlog Workflow)
- **Implementation:** `.agents/workflows/Backlog.md`
- **Audited:** 2026-07-13
- **Method:** each scenario + Proposed Surface element mapped to its realization in the workflow; evidence = workflow section.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| S-001 Discovery is backend-agnostic via track-work | Conformed | Backlog.md §Invariant (backend-agnostic); §Phase 1 |
| S-002 Triage order is bugs, then priority, then ease | Conformed | Backlog.md §Phase 1 (work queue sort) |
| S-003 Exempt items are a close-candidate batch, not silently dropped | Conformed | Backlog.md §Phase 1 (exempt-close batch); §Phase 2 item 2; §3e |
| S-004 The wizard is the only ask of the run | Conformed | Backlog.md §Invariant (single input point); §Phase 2; §Escalation |
| S-005 Git-visible actions never exceed the wizard authorization | Conformed | Backlog.md §Invariant (authorization boundary); §Phase 2 item 3; §3e — issue_scope bounded. |
| S-006 Capability gaps surface in the wizard or trigger a restart ask | Conformed | Backlog.md §Phase 2 (MCP + permissions pre-flight; required-tool restart prompt) — Updated; call-based check + restart ask. |
| S-007 Spec generation requires both clarity gates | Conformed | Backlog.md §3a (two-gate clarity check) |
| S-008 Oracle-down degrades existing-spec issues and blocks spec-needing ones | Conformed | Backlog.md §3a (Oracle-down policy, C1) |
| S-009 One unique worktree and branch per issue | Conformed | Backlog.md §Invariant; §3c step 1 |
| S-010 Pre-dispatch sweep reconciles orphans | Conformed | Backlog.md §3c step 3 — at-base verify included. |
| S-011 Dispatch calls are isolated in their own tool batch | Conformed | Backlog.md §Invariant (dispatch isolation); §3c step 4 — X2: verify/test excluded too. |
| S-012 Every dispatch attempt is reconciled, including starts that return no handle | Conformed | Backlog.md §Invariant (unknown outcome); §3c step 5 — deterministic identity, inventory/adopt-or-clean, 2-attempt block. |
| S-013 Concurrent issues are sibling-aware | Conformed | Backlog.md §3c step 6 |
| S-014 At most three issues are in flight | Conformed | Backlog.md §Invariant; §Phase 3 |
| S-015 Issues sharing a target spec serialize | Conformed | Backlog.md §3c step 2 — D7. |
| S-016 Closeout is verified independently, not trusted | Conformed | Backlog.md §3d (two-beat verify) |
| S-017 Verify overlaps next dispatch but never precedes close or cleanup | Conformed | Backlog.md §3d (non-blocking); §3f (cleanup after close) — X1. |
| S-018 CI failure on merge parks without asking | Conformed | Backlog.md §3e (E1 CI-red) |
| S-019 Merge conflicts regenerate derived docs or block | Conformed | Backlog.md §3e (E3 narrowed conflict rule) — Allowlist + regenerate. |
| S-020 Decision items are never auto-resolved | Conformed | Backlog.md §Phase 1 (decisions); §Escalation (never-autonomous set) |
| S-021 The ledger captures reconstructable flight state | Conformed | Backlog.md §3f (Ledger, F1) — session_id + worktree_id. |
| S-022 Resume reconstructs flight state without asking | Conformed | Backlog.md §Resume after restart (F2) |
| S-023 Escalation decides or blocks, never asks | Conformed | Backlog.md §Escalation (autonomous ladder) |
| S-024 The rollup records outcomes, divergences, and resume | Conformed | Backlog.md §Phase 4 |
| S-025 Browser user-testing is concurrent-safe via isolated profiles (or serialized) | Conformed | Backlog.md §Phase 2 (browser-concurrency pre-flight) — Updated: `--isolated` (or `--experimentalPageIdRouting`) is the mechanism. |
| S-026 Resume syncs the tree before retroactive verify | Conformed | Backlog.md §Resume (R1) — New. `--ff-only`, non-destructive. |
| S-027 Retroactive user-testing after a skipped frontend gate | Conformed | Backlog.md §3d (R2) — New. Recovery path. |
| S-028 Item status authoritative from track-work only | Conformed | Backlog.md §Phase 1 (R3) — New. |
| S-029 Orchestrator finishes an incomplete git flow | Conformed | Backlog.md §3e (R4) — New. |
| S-030 Close-keyword mandate on GitHub merge | Conformed | Backlog.md §3c brief + §3e (R5) — New. Backend-conditional. |
| S-031 Browser-isolation detected before concurrent UT | Conformed | Backlog.md §Phase 2 (R6) — New. Detect-or-serialize. |
| S-032 Repo hard-constraints ride in the brief | Conformed | Backlog.md §3c brief `constraints` (R7) — New. Repo-agnostic — pulls repo's own rules. |
| S-033 End-of-run doc sync | Conformed | Backlog.md §Phase 4 (R8) — New. `doc_edits`-gated. |
| S-034 End-of-run cleanup reaps worktrees/sessions, keeps branches | Conformed | Backlog.md §3f + §Phase 4 (R11) — New. Default-clean; `retain_for_inspection` opt-in. |
| S-035 Independent issues fly concurrently by default, gated by conflict risk | Conformed | Backlog.md §Invariant (default to parallel); §Phase 3 intro; §3c step 2 (conflict-risk gate); §3c pipeline — New. Fill the flight set; serialize only contended work. |
| S-036 Concurrent branches close via serial rebase-onto-default | Conformed | Backlog.md §3e (E3 ordered) — New. Most-independent first; rebase onto updated default. |
| S-037 Tool rejection text is not user intent and dispatch recovery stays autonomous | Conformed | Backlog.md §Invariant (unknown outcome); §3c step 5; §Anti-patterns — no attribution from harness text; no mid-run retry ask. |
| S-038 Cross-window orchestration risk is captured before dispatch | Conformed | Backlog.md §Invariant (per-run ceiling); §Phase 2 pre-flight + item 7 — active/unknown defaults local ceiling to 1. |
| S-039 Provisioning wedge stops dispatches and requires restart recovery | Conformed | Backlog.md §3c step 5; §Resume; §Anti-patterns — conservative signature; exact resource remains unproven. |
| S-040 Cleanup skip quarantines the dead session's branch binding | Conformed | Backlog.md §3c steps 3/5; §3f; §Anti-patterns — at-base is insufficient while a skipped session remains bound. |
| S-041 Dispatch diagnosis separates evidence from hypotheses | Conformed | Backlog.md §3c step 5; §Anti-patterns — no speculative attribution or remedy question. |

## Proposed Surface

| Item | Status | Evidence |
|---|---|---|
| Wizard fields (order, exempt batch, completion path default `branch+pr+merge`, close policy, role, escalation policy, max issues, concurrent orchestration) | Conformed | Backlog.md §Phase 2 — cross-window risk captured; local ceiling defaults to 1 when active/unknown. |
| Authorization scope (`git_scope`, `doc_edits`, `issue_scope`, `granted_at`) | Conformed | Backlog.md §Phase 2 (persist); §Invariant |
| Dispatch brief contract (authorization, toolchain, oracle, user_testing, escalation, amendments, siblings, constraints) | Conformed | Backlog.md §3c step 4 dispatch JSON — Atomic with Loop L6; `constraints` added (R7). |
| Gates enforced (single input, authorization, isolation, dispatch isolation, liveness, independent verify, conflict safety) | Conformed | Backlog.md §Invariants; §3c; §3d; §3e |
| Never-autonomous set | Conformed | Backlog.md §Escalation — Closed list. |
| Artifacts (run progress doc w/ ledger; rollup) | Conformed | Backlog.md §3f; §Phase 4 |

## Coverage proof

- **audited:** S-001…S-041 (all scenarios) + Proposed Surface (wizard fields, authorization scope, brief contract, gates, never-autonomous set, artifacts).
- **unreconciled:** []

## Notes

New spec + workflow, co-authored in the same change. Conformance is high by construction; an independent future audit (after one side is edited alone) is the real test.
