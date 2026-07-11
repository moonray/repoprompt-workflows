# Spec Conformance — Test Quality Skill

- **Spec:** `docs/spec/test-quality.md` (Test Quality Skill)
- **Implementation:** `.agents/skills/test-quality/SKILL.md`
- **Audited:** 2026-07-10
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the skill; evidence = skill section / rule.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 keep only tests protecting a current contract with a named defect | Conformed | "Decide before writing" step 1 + Core rule 1 |
| G2 choose the lowest faithful layer | Conformed | "Layer selection" (6 layers, lowest-first) |
| G3 prefer exact observable outcomes | Conformed | Core rule 5 + Review checklist Q4 |
| G4 cover trust boundaries | Conformed | "Trust-boundary focus" (10 boundaries, higher blast radius list) |
| G5 avoid low-value tests | Conformed | "Avoid" list + Core rules 6–7 + "Mock guidance" |
| G6 diagnostics vs coverage; bug-fix regression fails first | Conformed | "Diagnostics vs coverage" + Core rule 8 |
| A test is added only when a plausible defect is named | Conformed | "Decide before writing" step 1 ("If you cannot name… do not add") |
| The lowest faithful layer is chosen | Conformed | "Layer selection" + step 4 |
| Exact observable outcomes are asserted | Conformed | Core rule 5 |
| Trust boundaries get coverage | Conformed | "Trust-boundary focus" |
| A bug-fix regression is proven to fail first | Conformed | Core rule 8 + "Decide" step (bug-fix note) |
| Diagnostics are not counted as coverage | Conformed | "Diagnostics vs coverage" |
| Low-value tests are consolidated or omitted on review | Conformed | "Review checklist" + "Avoid" |
| Mocks do not reimplement production logic | Conformed | "Mock guidance" |
| The commit gate refuses a test without a named failure mode | Conformed | "Commit gate" (4 conjunctive conditions) |
| Reporting states contract, layer, fixtures, validation, omissions | Conformed | "Reporting" |
| Surface: inputs (behavior, existing coverage, oracle) | Conformed | "Decide before writing" steps 1–3 |
| Surface: output (decision, layer, fixture_strategy, validation, omitted) | Conformed | "Reporting" + "Commit gate" |

## Coverage proof

- **audited:** Goals 1–6; all 10 scenarios; Proposed Surface (inputs; output fields)
- **unreconciled:** []

## Notes

Every Goal, scenario, and surface field is realized in the skill with matching evidence, including the trust-boundary list, the commit gate, and the reporting shape. No drift found.
