# Spec Conformance — Deep Review

- **Spec:** `docs/spec/deep-review.md` (Deep Review Workflow)
- **Implementation:** `.agents/workflows/Deep-Review.md` (+ `review-depth`, `maintainability-review`, `review-quality` skills)
- **Audited:** 2026-06-25
- **Method:** each scenario + Proposed Surface input mapped to its realization; evidence = workflow section / skill.
- **Status:** S-020 diverged at audit; resolved 2026-06-25 (qualitative budget tier implemented).

## Matrix

| Item | Status | Evidence |
|---|---|---|
| S-001 scope confirmation mandatory | Conformed | Phase 0 (MANDATORY scope confirm) |
| S-002 author intent captured | Conformed | Phase 0 intake (intent, tradeoffs, focus/skip) |
| S-003 map precedes shots | Conformed | Phase 1 (explore agents) |
| S-004 findings context-grounded | Conformed | Phase 2 shot brief (`context_builder`, not raw diff); Anti-patterns |
| S-005 multi-lens coverage | Conformed | Phase 2 lenses (correctness + thermo-nuclear minimum) |
| S-006 thermo-nuclear quality-only | Conformed | `maintainability-review` skill (quality-only), inlined |
| S-007 structured-evidence gate | Conformed | Phase 3 + evidence contract |
| S-008 stable signatures + dedup | Conformed | Phase 3 dedup by signature |
| S-009 inspected-scope proof | Conformed | Phase 3 |
| S-010 adversarial verification | Conformed | Phase 4 |
| S-011 revalidation gate | Conformed | Phase 5 |
| S-012 author dismissal intent-grounded | Conformed | Phase 5 reconciliation |
| S-013 depth auto-selects | Conformed | "Depth selection" section |
| S-014 severe flags floor/escalate | Conformed | Depth rule |
| S-015 explicit override | Conformed | Depth override |
| S-016 thermo-nuclear version-tracked | Conformed | `maintainability-review` provenance + `sync-maintainability-review.mjs` |
| S-017 report bounded/actionable | Conformed | Phase 6 |
| S-018 repeated findings escalate | Conformed | Phase 4 classify-or-stop |
| S-019 git safety before mutating | Conformed | Git safety section + Phase 0 base SHA |
| S-020 budget tier caps deep-mode cost | Conformed | Depth selection "Budget (cost ceiling)" + Phase 4 `frugal` limit + Phase 0 budget intake |
| Input: Budget tier | Conformed | Phase 0 author intake (frugal/balanced/unlimited) |

## Coverage proof

- **audited:** S-001…S-020 (all 20 scenarios) + Inputs (comparison scope, author intake, change set, depth, token-budget directive)
- **unreconciled:** []

## Notes

S-020 resolved (2026-06-25): implemented as a qualitative budget tier (`frugal`/`balanced`/`unlimited`) scoped to deep — `frugal` coarsens the zone partition and limits Phase 4 verification to contested P0s; wired into Phase 0 intake, the Depth-selection "Budget (cost ceiling)" rule, and Phase 4. Chosen over exact-token accounting (users can't gauge token amounts) and over dropping (deep on an expensive model is a real cost case).
