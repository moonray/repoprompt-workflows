# Spec Conformance — Spec Conformance Skill

- **Spec:** `docs/spec/spec-conformance.md` (Spec Conformance Skill)
- **Implementation:** `.agents/skills/spec-conformance/SKILL.md`
- **Audited:** 2026-07-10
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the skill; evidence = workflow step / output field.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 enumerate every auditable item (scenarios, surface, stated values) | Conformed | Workflow step 1 |
| G2 locate code/test evidence for each item | Conformed | Workflow step 2 |
| G3 classify Conformed/Diverged/Not-built with both sides | Conformed | Workflow step 3 |
| G4 emit coverage proof (audited + unreconciled) | Conformed | Workflow step 4 + Output |
| Every spec item is enumerated | Conformed | step 1 (scenarios S-NNN, surface elements, values/enums/constraints) |
| Evidence is located for each item | Conformed | step 2 (`file:symbol` or asserting test) |
| Items classified with both sides on divergence | Conformed | step 3 |
| A coverage proof is emitted | Conformed | step 4 + Output (`audited`, `unreconciled`) |
| An empty result requires positive evidence | Conformed | Output ("valid only as `{ audited: [...], unreconciled: [] }`") |
| Each unreconciled item carries a disposition | Conformed | step 4 (fix \| accepted-with-reason) |
| Surface: inputs (spec path, implementation scope) | Conformed | Inputs section |
| Surface: output (matrix rows, audited, unreconciled) | Conformed | Output section |

## Coverage proof

- **audited:** Goals 1–4; all 6 scenarios; Proposed Surface (inputs; output)
- **unreconciled:** []

## Notes

The enumerate→locate→classify→proof workflow and the empty-result rule match the spec exactly. No drift found.
