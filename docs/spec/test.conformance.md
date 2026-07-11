# Spec Conformance — Test Generation Workflow

- **Spec:** `docs/spec/test.md` (Test Generation Workflow)
- **Implementation:** `.agents/workflows/Test.md`
- **Audited:** 2026-06-25
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the workflow; evidence = workflow phase / principle.
- **Status:** divergences resolved 2026-06-25 (Test workflow: +`test-quality` Core Principle 7, +`Layer` column & lowest-faithful-layer selection in Phase 3, +`deferred_or_omitted_coverage` in Phase 6). Matrix rows below reflect the pre-fix audit.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 generate tests from scenarios + Proposed Surface | Conformed | Phase 1 (read) → Phase 3 (map) → Phase 4 (write) |
| G2 cover every scenario with ≥1 traceable test, no out-of-spec behavior | Conformed | Core Principle 1 + Phase 3 ("every scenario has at least one test method") |
| G3 stop before generation when Spec Quality findings make spec insufficient | Conformed | Phase 1 steps 4–5 (`needs_revision` → stop) |
| G4 discover + follow repo conventions (framework/runner/layout/naming/fixture/helper/assertion) | Conformed | Phase 2 (Discover Test Infrastructure) |
| G5 apply shared Test Quality guidance (layers/fixtures/mocks/assertions) | **Diverged** | workflow references `spec-quality` (Core Principle 2) but never applies/references the shared **Test Quality** guidance when choosing layers/fixtures/mocks/assertions |
| G6 prefer lowest faithful test layer | **Diverged** | workflow has no lowest-faithful-layer selection; it defers to repo convention (Phase 4 Anti-Pattern: "match the repo's convention") with no step selecting the lowest layer or documenting reasons for a higher layer |
| G7 first-class tests: deterministic setup, realistic fixtures, exact assertions | Conformed | Core Principle 4 + Phase 4 ("focused assertions"; prefer specific over generic) |
| G8 report coverage, files/methods, validation status, unmapped scenarios | Conformed | Phase 6 summary table — see Completion Summary rows for field gaps |
| Explicit spec path is read | Conformed | Phase 1 steps 1–2 |
| Feature name resolves to a spec | Conformed | Phase 1 step 2 ("check docs/spec/ for matches") |
| Missing spec stops the workflow | Conformed | Phase 1 step 3 |
| Spec without scenarios stops the workflow | Conformed | Phase 1 step 9 |
| Spec surface and constraints extracted | Conformed | Phase 1 steps 6–8 |
| Spec quality findings stop test generation | Conformed | Phase 1 steps 4–5 |
| Shared test quality guidance shapes test design | **Diverged** | as G5 — workflow applies spec-quality but not the shared Test Quality guidance |
| Existing test infra discovered before editing | Conformed | Phase 2 |
| Repo conventions override defaults | Conformed | Phase 2 + Language-Specific Guidance ("always prefer what the repo actually uses") |
| No test infra → bootstrap recommendation | Conformed | Phase 2 ("If the repo has no test infrastructure… stop and suggest… bootstrap test") |
| Every scenario maps to tests | Conformed | Phase 3 mapping rules |
| Proposed Surface parameters covered | Conformed | Phase 3 ("every parameter… appears in at least one test") |
| Edge and error cases → dedicated tests | Conformed | Phase 3 + Phase 4 writing order |
| Lowest faithful layer is selected | **Diverged** | as G6 — no layer-selection step; defers to repo convention |
| Tests include exact observable assertions | Conformed | Phase 4 ("focused assertions"; Swift guidance: prefer specific assertions over generic) |
| Tests remain traceable to scenarios | Conformed | Phase 4 (comments linking to scenario ID) |
| Existing helpers/fixtures reused | Conformed | Phase 2 + Anti-Pattern ("work within what's there") |
| Production code is not modified | Conformed | Core Principle + Phase 5 + Anti-Pattern |
| Placeholder tests are rejected | Conformed | Phase 4 + Anti-Pattern |
| Tests compile before runtime evaluation | Conformed | Phase 5 ("build-only first") |
| Unimplemented feature may fail runtime tests | Conformed | Phase 5 (contract tests) |
| Implemented feature failures reported as defects | Conformed | Phase 5 (fix test bugs; report feature bugs) |
| Completion summary reports coverage + validation | **Diverged** | Phase 6 summary table omits `deferred_or_omitted_coverage` |
| Input: `spec` parameter | Conformed | workflow header `Spec: $ARGUMENTS` |
| Surface: Consumed Spec Content (path/scenarios/surface/constraints) | Conformed | Phase 1 steps 6–8 |
| Surface: Shared Spec Quality Gate (contract-level/testable/surface coverage) | Conformed | Phase 1 step 4 |
| Surface: Shared Test Quality Criteria (lowest layer/fixture-mock/observable) | **Diverged** | workflow neither realizes nor references these criteria (see G5/G6) |
| Surface: Scenario-to-Test Mapping incl. `layer` field | **Diverged** | Phase 3 mapping table has Scenario/Method/Setup/Assertions/Notes — no `layer` column (spec marks `layer` required); `test_file`/`action` also not explicit columns |
| Surface: Generated Test Artifacts (files/fixtures/traceability) | Conformed | Phase 4 |
| Surface: Completion Summary incl. `deferred_or_omitted_coverage` | **Diverged** | Phase 6 table lacks `deferred_or_omitted_coverage` field |

## Coverage proof

- **audited:** Goals 1–8; all 23 scenarios; Proposed Surface (Workflow Invocation `spec`; Consumed Spec Content; Shared Spec Quality Gate; Shared Test Quality Criteria; Scenario-to-Test Mapping; Generated Test Artifacts; Completion Summary)
- **unreconciled:** []

## Notes

**Resolved 2026-06-25** — the Test workflow now applies `test-quality` (Core Principle 7), has a `Layer` column + a lowest-faithful-layer selection step in Phase 3, and includes `deferred_or_omitted_coverage` in the Phase 6 summary. Original audit (for history): Test-quality / lowest-faithful-layer drift (G5, G6, "Shared test quality guidance", "Lowest faithful layer is selected", Shared Test Quality Criteria surface, Scenario-to-Test Mapping `layer`) — **decision needed**:
- (a) **implement**: add a layer-selection step to Phase 3 (lowest faithful layer per scenario, documented reason when higher), add a `layer` column to the mapping table, and reference the `test-quality` skill alongside `spec-quality`; or
- (b) **accept with reason**: if the workflow is intentionally convention-matching only, remove Goals 5–6, the "lowest faithful layer" scenario, the Shared Test Quality Criteria surface, and the `layer` mapping field from the spec.

Completion summary `deferred_or_omitted_coverage` (minor) — add the field to the Phase 6 summary table, or drop it from the spec.

Recommendation: (a) — the spec's test-quality discipline is the intended direction (see the spec's own Open Question on e2e vs lowest-faithful-layer native tests); the workflow should incorporate it rather than the spec being walked back.
