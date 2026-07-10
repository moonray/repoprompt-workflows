# Spec Conformance — Document

- **Spec:** `docs/spec/document.md` (Document Skill)
- **Implementation:** `.agents/skills/document/SKILL.md`
- **Audited:** 2026-06-25
- **Method:** each Goal + scenario mapped to its realization in the skill; evidence = skill step / output.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 sync identifies affected docs | Conformed | step 4 (sync) |
| G2 audit finds existing drift | Conformed | step 5 (audit) |
| G3 every edit traces to code basis | Conformed | step 3 (establish code basis) + apply rules |
| G4 scope-bounded + approval-gated | Conformed | scope input + apply rules (dry-run default) |
| G5 repo-agnostic discovery | Conformed | step 1 (Markdown + Gherkin) |
| G6 progressive-disclosure index | Conformed | step 6 (keep a docs index) — *note below* |
| Sync identifies affected docs | Conformed | step 4 |
| Sync proposes reconciliation edits | Conformed | step 4 |
| Sync excludes unaffected docs | Conformed | step 4 (exclude unrelated) |
| No fabricated content | Conformed | step 3 + apply rules |
| Audit detects existing drift | Conformed | step 5 |
| Audit catches value/enum mismatch | Conformed | step 5 |
| Audit flags removed/renamed reference | Conformed | step 5 (dangling references) |
| Contract-doc conflict surfaced, not edited | Conformed | step 2 classify + sync/audit (contract → report, no edit) |
| Scope limits the run | Conformed | scope input (step 1 apply scope) |
| Edits dry-run by default | Conformed | apply rules |
| Apply writes only approved edits | Conformed | apply rules |
| Repo-agnostic discovery (md + gherkin) | Conformed | step 1 |
| Instruction-artifact dirs can contain docs | Conformed | step 1 (constraint) |
| No drift → clean no-op | Conformed | output (empty result) |
| Sync keeps docs index in sync | Conformed | step 6 |

## Coverage proof

- **audited:** Goals 1–6 + all scenarios (sync / audit / contract / scope / dry-run / discovery / index)
- **unreconciled:** []

## Notes

- Minor: the skill's **Output format** section doesn't yet enumerate "Index updates" as an output, though step 6 implements the behavior. Add the row to match the spec's Outputs table (cosmetic; behavior conforms).
