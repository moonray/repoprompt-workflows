# Spec Conformance — Spec-Plan Readiness Skill

- **Spec:** `docs/spec/spec-plan-readiness.md` (Spec-Plan Readiness Skill)
- **Implementation:** `.agents/skills/spec-plan-readiness/SKILL.md`
- **Audited:** 2026-06-25
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the skill; evidence = skill workflow step / output field / checklist item.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 evaluate Spec+Plan implementability before impl | Conformed | skill is a gate; steps 1–7 |
| G2 identify exact blocking gaps (spec/plan/both) | Conformed | steps 2–5 (`source: spec/plan/both`) |
| G3 every task traceable to observable scenarios + validation | Conformed | step 5 (task-to-scenario map) |
| G4 verdict authorizes impl or names resolutions | Conformed | step 7 + Output format |
| G5 scenario-to-test guidance + first safe task (no orchestration) | Conformed | step 6 (scenario-to-test map) + step 7 (first_safe_task) |
| Complete inputs → implementable verdict | Conformed | step 7 + readiness checklist |
| Missing spec blocks readiness | Conformed | step 1 (`source: spec`) + Inputs short-circuit |
| Missing plan blocks readiness | Conformed | step 1 (`source: plan`) + Inputs short-circuit |
| Open questions block readiness | Conformed | step 2 (unresolved Open Questions → spec gap) |
| Non-observable scenarios block readiness | Conformed | step 2 (missing observable Then → spec gap) |
| Missing Proposed Surface blocks tool/API work | Conformed | step 2 (insufficient surface → spec gap) |
| Repository context sharpens plan-concreteness checks | Conformed | step 4 (Apply repository context; plan gaps on divergence) |
| Plan without ordered tasks blocks readiness | Conformed | step 3 (ordered items + dependency order) |
| Plan without expected files/components blocks readiness | Conformed | step 3 (expected files/components/modules/surfaces) |
| Plan without validation blocks readiness | Conformed | step 3 (validation commands/test strategy/success criteria) |
| Plan without risk/rollback notes blocks readiness | Conformed | step 3 (risk rule: multi-module / persisted format / non-reversible) |
| Missing task-to-scenario mapping blocks readiness | Conformed | step 5 (`source: both` for unmapped task/scenario) |
| Spec and plan contradiction blocks readiness | Conformed | step 5 (`source: both` for contradictions) |
| First safe task requires dependency awareness | Conformed | step 7 (earliest ordered task, prerequisites satisfied, coverage/areas/validation/layer known) |
| Blocked verdict does not authorize implementation | Conformed | step 7 ("when blocked, do not include first_safe_task; authorizes no tests/code/delegation") |
| Input: Spec (req), Deep Plan (req), Repository context (opt) | Conformed | Inputs section |
| Surface: verdict (`implementable`/`blocked`) | Conformed | Output format |
| Surface: blocking_gaps (source/reason/required_resolution) | Conformed | steps 2–5 + Output format |
| Surface: scenario_to_test_map (layer + reason; empty when blocked) | Conformed | step 6 + Output rules |
| Surface: task_to_scenario_map (unmapped → blocking gaps) | Conformed | step 5 + Output rules |
| Surface: first_safe_task (only when implementable) | Conformed | step 7 + Output format |

## Coverage proof

- **audited:** Goals 1–5; all 15 scenarios; Proposed Surface (Skill Invocation inputs; Readiness Verdict fields: verdict, blocking_gaps, scenario_to_test_map, task_to_scenario_map, first_safe_task)
- **unreconciled:** []

## Notes

Clean result: every Goal, scenario, and verdict field is realized in the skill with matching evidence, including the short-circuit on missing inputs, the deterministic risk/rollback rule, and the "blocked authorizes nothing" guarantee. No drift found.
