# Spec Conformance — Spec Quality Skill

- **Spec:** `docs/spec/spec-quality.md` (Spec Quality Skill)
- **Implementation:** `.agents/skills/spec-quality/SKILL.md`
- **Audited:** 2026-06-25
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the skill; evidence = skill workflow step / output field.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 reusable quality criteria for drafting/reviewing | Conformed | Workflow steps 1–9 |
| G2 specs describe what/why, not impl strategy/phases/file org | Conformed | step 2 (Check contract-level scope) |
| G3 scenarios declarative/observable/independent/traceable | Conformed | step 3 (scenario quality) + step 4 (goal traceability) |
| G4 Proposed Surface precise, no duplication | Conformed | step 5 (surface→scenario coverage) + step 6 (section placement) |
| G5 identify redundancy, gaps, ambiguity, placeholders, unresolved decisions | Conformed | steps 4/5 (gaps), 6 (redundancy), 7 (ambiguity/placeholders), 8 (Open Questions) |
| Draft guidance keeps specs contract-level | Conformed | step 2 + Drafting guidance |
| Review flags implementation planning | Conformed | step 2 (architecture, file locations, indexing, code types, phased delivery) |
| Scenario quality is checked | Conformed | step 3 (declarative/observable/independent/focused/identifiable; flags vague Then) |
| Goals map to scenarios | Conformed | step 4 |
| Proposed Surface maps to scenarios | Conformed | step 5 |
| Redundant content removed from recommendation | Conformed | step 6 |
| Ambiguity is identified | Conformed | step 7 |
| Open questions distinguished from decisions | Conformed | step 8 |
| Existing repo context respected | Conformed | step 5 ("prefer existing repository terms") + Inputs (repo context optional) |
| No issues produces a clean result | Conformed | step 9 + Output format (`verdict: ready` when all empty) |
| Missing spec input is reported | Conformed | step 1 (`input_error`; do not return `ready`) + Inputs section |
| Input: Spec draft or source request (req), Repository context (opt) | Conformed | Inputs section |
| Surface: Quality Report fields (input_error/contract_level/scenario/surface/redundancy/ambiguity/open_question/verdict) | Conformed | Output format (8 fields, in order) |
| Surface: verdict rule (ready iff all empty; all findings blocking) | Conformed | step 9 + Output format rules |

## Coverage proof

- **audited:** Goals 1–5; all 11 scenarios; Proposed Surface (Skill Invocation inputs; Quality Report fields + verdict rule)
- **unreconciled:** []

## Notes

Clean result: every Goal, scenario, and report field is realized in the skill with matching evidence, including the deterministic verdict rule and the all-findings-blocking policy. No drift found.
