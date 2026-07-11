# Spec Conformance — Maintainability Review Skill

- **Spec:** `docs/spec/maintainability-review.md` (Maintainability Review Skill)
- **Implementation:** `.agents/skills/maintainability-review/SKILL.md`
- **Audited:** 2026-07-10
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the skill; evidence = rubric rule / section.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 ambitious structural simplification (code judo) | Conformed | Non-Negotiable rule 0 + "Core Prompt" |
| G2 flag giant files (>1k lines) | Conformed | Non-Negotiable rule 1 |
| G3 flag spaghetti growth in unrelated flows | Conformed | Non-Negotiable rule 2 |
| G4 flag unearned indirection (wrappers/pass-throughs) | Conformed | Non-Negotiable rule 4 |
| G5 flag layer leaks and missing reuse of canonical helpers | Conformed | Non-Negotiable rule 6 |
| G6 flag unnecessary optionality/casts and avoidable orchestration | Conformed | Non-Negotiable rules 5 + 7 |
| G7 quality-only — correct behavior alone does not win approval | Conformed | "Intent" + Non-Negotiable rule 3 |
| Code-judo simplifications are proposed | Conformed | rule 0 + "Primary Review Questions" |
| A file crossing 1k lines is flagged | Conformed | rule 1 |
| Spaghetti growth in unrelated flows is flagged | Conformed | rule 2 |
| Unearned wrappers and pass-throughs are flagged | Conformed | rule 4 |
| Logic leaking across layers is flagged | Conformed | rule 6 |
| Type-boundary and orchestration smells are flagged | Conformed | Non-Negotiable rules 5 + 7 |
| Correct behavior alone does not win approval | Conformed | "Intent" (quality-only) + rule 3 |
| Rubric changes are re-synced, not hand-edited | Conformed | "Provenance" + BEGIN/END markers + sync script |
| Surface: inputs (change set, repo context) | Conformed | "When to use" + "Core Prompt" |
| Surface: output (structural_findings, category) | Conformed | "Output Expectations" + "Approval Bar" |

## Coverage proof

- **audited:** Goals 1–7; all 8 scenarios; Proposed Surface (inputs; output)
- **unreconciled:** []

## Notes

All seven Non-Negotiable rules, the quality-only intent, and the vendored-sync constraint (markers + sync script) match the spec. No drift found.
