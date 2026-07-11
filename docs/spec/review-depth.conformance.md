# Spec Conformance — Review Depth Skill

- **Spec:** `docs/spec/review-depth.md` (Review Depth Skill)
- **Implementation:** `.agents/skills/review-depth/SKILL.md`
- **Audited:** 2026-07-10
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the skill; evidence = signals / selection rule / output.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 compute review signals | Conformed | "Signals" table (size/spread/severe/blast radius/doc-only) |
| G2 select depth deterministically | Conformed | "Selection rule" steps 1–7 |
| G3 explicit override wins, recorded | Conformed | "Override" line |
| G4 auditable output (depth + signals + rationale) | Conformed | "Output" block |
| Size sets the base depth | Conformed | Selection rule step 1 (`{S:quick,M:standard,L:deep}`) |
| A severe risk flag floors at standard and escalates | Conformed | steps 4–5 |
| High blast radius escalates | Conformed | step 6 |
| Doc-only with no severe risk is quick | Conformed | step 7 |
| An explicit user choice overrides detection | Conformed | "Override" + Output (records skip) |
| Output is auditable | Conformed | "Output" (depth/signals/rationale) |
| Lenses and verification are not chosen here | Conformed | "Non-goals" |
| Surface: inputs (change set, explicit depth) | Conformed | Inputs section |
| Surface: output (depth, signals, rationale) | Conformed | Output block |

## Coverage proof

- **audited:** Goals 1–4; all 7 scenarios; Proposed Surface (inputs; output)
- **unreconciled:** []

## Notes

The deterministic selection rule, override, and auditable output match the spec; budget is correctly left orthogonal (Non-goals). No drift found.
