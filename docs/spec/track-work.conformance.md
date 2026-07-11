# Spec Conformance — Track Work Skill

- **Spec:** `docs/spec/track-work.md` (Track Work Skill)
- **Implementation:** `.agents/skills/track-work/SKILL.md`
- **Audited:** 2026-07-10
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the skill; evidence = step / section.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 one work item per unit in one place (GitHub or file) | Conformed | "Intent" + "GitHub backend" / "File backend" |
| G2 detect backend and apply repo label/taxonomy conventions | Conformed | "Step 0 — detect the backend" + "Step 1 — read repo conventions" |
| G3 entry gate before any work | Conformed | "Intent" ("entry gate… no implementation… before the work has a tracking item") |
| G4 link the detail layer, never duplicate narrative | Conformed | "Step 4 — Link the detail files" + body template |
| G5 status lifecycle; close = landed on default branch | Conformed | "Status lifecycle" + "Closing" |
| The backend is detected deterministically | Conformed | Step 0 (override > GitHub > file; disabled-issues fallback) |
| Repo conventions read, GitHub labels discovered | Conformed | Step 1 (`gh label list` beats config) |
| A tracking item is created before any work | Conformed | "Intent" entry-gate statement + GitHub step 3 |
| Search before create avoids duplicates | Conformed | "Step 2 — Search before you create" |
| Labels honor configured cardinality | Conformed | Step 3 (cardinality) + config schema `labels.dimensions` |
| Detail files are linked, not duplicated | Conformed | Step 4 + body template "Detail / links" |
| File-backend items use immutable IDs in a committed backlog | Conformed | "File backend workflow" (immutable IDs; gitignore warning) |
| Close means landed on the default branch | Conformed | "Closing" (Fixes/Closes #N; close-gate; exempt labels) |
| Secrets and absolute paths redacted before filing | Conformed | "Privacy / redaction before filing" |
| Surface: inputs (request, repo conventions) | Conformed | Step 1 + classify request (Step 1 GitHub) |
| Surface: output (item, links, status) | Conformed | body template + status lifecycle |

## Coverage proof

- **audited:** Goals 1–5; all 9 scenarios; Proposed Surface (inputs; output)
- **unreconciled:** []

## Notes

Backend detection, the entry gate, label cardinality, immutable IDs, the close-on-default-branch rule, and redaction all match the spec. No drift found.
