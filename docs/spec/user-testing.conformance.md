# Spec Conformance — User Testing Skill

- **Spec:** `docs/spec/user-testing.md` (User Testing Skill)
- **Implementation:** `.agents/skills/user-testing/SKILL.md`
- **Audited:** 2026-07-10
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the skill; evidence = workflow step / section.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 enumerate real user workflows from spec/intent | Conformed | Workflow step 1 |
| G2 drive the real rendered UI via automation | Conformed | Workflow step 2 (browser / platform UI automation) |
| G3 screenshot each step and inspect | Conformed | Workflow steps 3–4 |
| G4 flag the defects automated tests miss | Conformed | Workflow step 5 |
| G5 produce a record; human hand-off optional | Conformed | Workflow steps 6–7 + Output |
| G6 block (not skip) when it cannot run | Conformed | "When it can't run" + Workflow |
| Workflows come from spec/intent, not the test list | Conformed | step 1 |
| The real UI is driven end-to-end per workflow | Conformed | step 2 |
| Each step is screenshotted and inspected | Conformed | steps 3–4 (console + network) |
| The runtime is checked, not just the pixels | Conformed | step 4 |
| A human hand-off is optional, not required | Conformed | step 6 ("gold standard, not the only way") |
| Impossible user testing is blocked, not skipped | Conformed | "When it can't run" + smoke-is-floor note |
| Testing runs against throwaway data | Conformed | "Data isolation (hard rule)" |
| A user-test record is produced | Conformed | step 7 + Output |
| Surface: inputs (feature, spec scenarios) | Conformed | "Inputs" (feature; spec as workflow source) |
| Surface: output (workflows, issues, not_tested) | Conformed | Output section |

## Coverage proof

- **audited:** Goals 1–6; all 8 scenarios; Proposed Surface (inputs; output)
- **unreconciled:** []

## Notes

The data-isolation hard rule, the blocked-not-skipped policy, and the workflow/record shape all match the spec. No drift found.
