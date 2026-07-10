---
name: spec-plan-readiness
description: Use before implementation when a Spec and Deep Plan must be checked for coding readiness. Applies a deterministic go/no-go gate for missing inputs, unresolved spec blockers, incomplete ordered plans, spec-plan contradictions, task-to-scenario traceability, scenario-to-test layer mapping, risk/rollback requirements, and first-safe-task selection; a blocked verdict authorizes no tests, code, or implementation delegation.
---

# Spec-Plan Readiness

## Intent

Decide whether a readable behavioral Spec plus readable Deep Plan is implementable before tests, code, or implementation delegation begin.

This skill is a gate. It reports exact blocking gaps and, only when all readiness conditions hold, identifies scenario test layers, task traceability, and the first safe implementation task.

## Inputs

Required:

- **Spec**: readable behavioral contract with scenarios, constraints, Proposed Surface, and Open Questions.
- **Deep Plan**: readable ordered implementation plan with tasks, affected areas, dependencies, validation, test strategy, risks, rollback notes, and task-to-scenario mapping.

Optional:

- **Repository context**: existing validation commands, test frameworks, surfaces, conventions, and test taxonomy.

If either required input is missing or unreadable, short-circuit: return `verdict: blocked`, report the missing `spec` and/or `plan` gap, leave maps empty, do not evaluate scenarios or tasks, and do not include `first_safe_task`.

## Non-goals

Do not use this skill to:

- write or revise the Spec or Deep Plan;
- create tests, production code, refactors, or implementation tasks;
- manage worktrees, progress ledgers, delegated agents, reviews, or closeout validation;
- replace full single-spec review by `spec-quality`;
- choose product scope beyond naming unresolved decisions, contradictions, and missing coverage.

## Workflow

### 1. Confirm readable inputs

Verify that both the Spec and Deep Plan were supplied and can be read.

Blocking gaps:

- `source: spec` when a readable behavioral spec is missing.
- `source: plan` when a readable ordered implementation plan is missing.

If any input gap exists, stop here.

### 2. Check spec blockers needed for implementation

Use `spec-quality` when available as supporting input, but do not require the Spec to pass a full single-spec review. Convert only findings that affect whether implementation may begin into `source: spec` gaps, then independently check the Spec conditions needed before implementation may begin:

- unresolved Open Questions affecting behavior, surface, constraints, validation, or scope;
- scenarios missing observable Then outcomes: return value, state change, side effect, error, emitted output, persisted format, protocol behavior, or user-visible behavior;
- user-facing tools, APIs, commands, fields, parameters, return shapes, persisted formats, or protocol behavior without enough Proposed Surface detail to implement and test;
- ambiguity, hidden decisions, or contradictions that prevent scenario/test mapping;
- contract-level drift or redundancy only when it makes behavior, surface, validation, task mapping, or scenario-to-test mapping unreliable.

Each finding is a `source: spec` gap with the specific rewrite or decision needed.

### 3. Check plan blockers

Verify the Deep Plan includes:

- ordered work items;
- dependency order or explicit independence between work items;
- expected files, components, modules, or user-facing surfaces for each work item;
- validation commands, test strategy, and success criteria;
- task-to-scenario mapping;
- risks, rollback notes, or failure-handling expectations when required.

Risk/rollback notes are required for any task that:

- touches more than one module;
- changes a persisted data format or protocol; or
- cannot be safely reversed by reverting one commit.

Each finding is a `source: plan` gap naming the affected task and missing plan detail.

### 4. Apply repository context

When repository context is available, judge the plan against it rather than generic assumptions.

Check whether planned validation commands, test frameworks, expected files/components, public surfaces, naming, layout, and conventions match the repository. Report `source: plan` gaps when the plan diverges from known repo commands or conventions without explanation.

### 5. Check spec-plan consistency and traceability

Build a task-to-scenario map from the Deep Plan and Spec.

Blocking gaps:

- `source: both` for any planned task not traceable to at least one Spec scenario;
- `source: both` for any Spec scenario without a planned task or explicit non-implementation rationale;
- `source: both` for contradictions in behavior, scope, sequencing, surfaces, dependencies, validation, or expected outcomes.

Do not treat unmentioned scope as allowed implementation work. The plan must either map it to the Spec or explicitly mark it out of scope.

### 6. Build the scenario-to-test map

For every mapped Spec scenario, recommend a test layer and reason.

Use the repository's test taxonomy when available, especially `docs/spec/test.md` and the `test-quality` skill. Prefer the lowest faithful layer:

- `unit/core` for pure logic, parsing, normalization, policy decisions, reducers, and state machines;
- `component/service` for public service behavior with controlled dependencies;
- `filesystem/database/wire-format integration` for persistence, schemas, migrations, file layout, query behavior, or wire compatibility;
- `provider/adapter/entrypoint` for command/tool/API argument conversion, routing, serialization, protocol behavior, UI event wiring, or adapter behavior;
- `end-to-end/smoke` only for critical user journeys or diagnostics that cannot be faithfully covered lower.

If readiness was blocked before mapping, return an empty `scenario_to_test_map`.

### 7. Select first safe task only when implementable

Set `verdict: implementable` only when all blocking gap lists are empty.

When implementable, select `first_safe_task` as the earliest ordered task whose prerequisites are satisfied and whose scenario coverage, expected affected areas, validation, and test layer are known.

When blocked, do not include `first_safe_task`. A blocked verdict authorizes no tests, production code, or implementation delegation.

## Output format

Return fields in this order:

```text
verdict: implementable | blocked
blocking_gaps:
  - source: spec | plan | both
    reason: ...
    required_resolution: ...
scenario_to_test_map:
  - scenario: ...
    recommended_layer: ...
    why: ...
task_to_scenario_map:
  - task: ...
    scenarios: [...]
    notes: ...
# Include only when verdict is implementable:
first_safe_task: ...
```

Rules:

- `blocking_gaps` is empty only when `verdict: implementable`.
- `scenario_to_test_map` is empty when missing inputs short-circuit evaluation or when blockers prevent reliable mapping.
- `task_to_scenario_map` includes mapped tasks when available; unmapped tasks or scenarios must also appear as `source: both` blocking gaps.
- `first_safe_task` appears only with `verdict: implementable`.

## Readiness checklist

Before returning `implementable`, confirm:

1. Spec and Deep Plan are both readable.
2. Spec Open Questions are resolved or explicitly non-blocking.
3. Every Spec scenario has an observable Then outcome.
4. Proposed Surface is sufficient for every user-facing tool, API, command, field, parameter, return shape, persisted format, or protocol behavior.
5. Plan tasks are ordered and dependency-aware.
6. Each task names expected affected files, components, modules, or surfaces.
7. Each task has validation, test strategy, and success criteria.
8. Risk/rollback notes exist for every task that triggers the deterministic risk rule.
9. Every task maps to Spec scenarios, and every scenario maps to a task or explicit non-implementation rationale.
10. The plan does not contradict Spec behavior, scope, sequencing, surfaces, dependencies, validation, or outcomes.
11. Scenario test layers are selected from repo taxonomy and `test-quality` guidance when available.
12. The first safe task is dependency-satisfied and fully mappable.
