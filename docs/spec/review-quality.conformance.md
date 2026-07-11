# Spec Conformance — Review Quality Skill

- **Spec:** `docs/spec/review-quality.md` (Review Quality Skill)
- **Implementation:** `.agents/skills/review-quality/SKILL.md`
- **Audited:** 2026-07-10
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the skill; evidence = core rule / output.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 structured, resolvable evidence on every finding | Conformed | Core rule 1 (path/lines/symbol/quote) |
| G2 ground in scope; drop unresolvable, keep siblings | Conformed | Core rule 2 |
| G3 report scope proof (inspected) | Conformed | Core rule 3 |
| G4 close fixed only on fresh review + passing validation | Conformed | Core rule 4 (revalidation gate) |
| G5 stable signatures for dedup/triage | Conformed | Core rule 5 |
| G6 triage before acting; classify repeats | Conformed | Core rule 6 |
| Every finding carries resolvable evidence | Conformed | Core rule 1 |
| Unresolvable findings dropped, siblings kept | Conformed | Core rule 2 |
| Scope proof is reported | Conformed | Core rule 3 |
| A finding is fixed only on fresh review plus passing validation | Conformed | Core rule 4 (blocked/uncertain, never fixed on opinion) |
| Stable signatures support dedup | Conformed | Core rule 5 |
| Triage classifies repeats rather than looping | Conformed | Core rule 6 (2 attempts / 3 observations) |
| Output records evidence, scope, drops, validation | Conformed | Output section |
| Surface: inputs (review scope, findings, validation commands) | Conformed | Inputs section |
| Surface: output (findings, inspected, dropped, validation, blocked) | Conformed | Output section |

## Coverage proof

- **audited:** Goals 1–6; all 7 scenarios; Proposed Surface (inputs; output)
- **unreconciled:** []

## Notes

All six core rules and the output shape match the spec, including the revalidation gate's refusal of model-only "fixed". No drift found.
