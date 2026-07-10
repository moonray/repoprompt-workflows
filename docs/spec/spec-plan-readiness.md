---
title: Spec-Plan Readiness Skill
issue: none
status: implemented
---

# Spec-Plan Readiness Skill

## Problem

Spec-driven implementation workflows need a reusable way to decide whether a Spec plus Deep Plan is ready for coding. Today the readiness criteria are embedded inside Loop, so other workflows can start work with unresolved spec questions, unobservable scenarios, missing plan dependencies, missing validation commands, or contradictions between the spec and plan. A dedicated Spec-Plan Readiness skill is needed to produce a consistent go/no-go verdict before tests, code, or delegation begin.

## Goals

1. Evaluate whether a Spec plus Deep Plan is implementable before implementation work starts.
2. Identify exact blocking gaps in the spec, the plan, or the relationship between them.
3. Confirm that every planned task is traceable to observable spec scenarios and expected validation.
4. Produce a readiness verdict that either authorizes implementation or names the required resolutions.
5. Provide enough scenario-to-test guidance to choose the first safe task without performing implementation orchestration.

## Non-Goals

- Write or revise the Spec or Deep Plan.
- Create tests, write production code, refactor code, or run implementation loops.
- Manage worktrees, progress ledgers, delegated agents, reviews, or closeout validation.
- Decide product scope beyond reporting unresolved questions, contradictions, and missing plan coverage.
- Replace the Spec Quality skill's review of a single spec draft.

## Constraints

- The skill evaluates readiness only from the supplied Spec, supplied Deep Plan, and available repository context.
- Missing or unreadable Spec or Deep Plan input short-circuits to missing-input gap reporting and stops per-scenario or per-task evaluation; if both inputs are missing, both `spec` and `plan` gaps are reported.
- A ready verdict requires every applicable readiness condition in the scenarios below to hold.
- A blocked verdict must identify the source of each gap as `spec`, `plan`, or `both` and state the resolution needed before implementation can begin.
- The skill may recommend test layers for scenarios, but it does not create tests; recommended layers must be drawn from the repo's test taxonomy, including `docs/spec/test.md` and the Test Quality skill when available.
- The skill independently re-checks only the Spec conditions needed to decide whether implementation may begin; full single-spec drafting and review quality remains the responsibility of Spec Quality.

## Scenarios

### Scenario: Complete inputs produce implementable verdict
- **Given** a Spec with observable scenarios and Proposed Surface and a Deep Plan with ordered tasks, expected files or components, dependencies, validation commands, test strategy, risks, rollback notes, and task-to-scenario mapping
- **When** the skill evaluates readiness
- **Then** it returns `implementable`, includes no blocking gaps, maps scenarios to recommended test layers, and names a first safe task

### Scenario: Missing spec blocks readiness
- **Given** no Spec is supplied or the supplied Spec cannot be read
- **When** the skill evaluates readiness
- **Then** it returns `blocked` with a `spec` gap stating that a readable behavioral spec is required

### Scenario: Missing plan blocks readiness
- **Given** no Deep Plan is supplied or the supplied Deep Plan cannot be read
- **When** the skill evaluates readiness
- **Then** it returns `blocked` with a `plan` gap stating that a readable ordered implementation plan is required

### Scenario: Open questions block readiness
- **Given** the Spec contains unresolved Open Questions that affect behavior, surface, constraints, or validation
- **When** the skill evaluates readiness
- **Then** it returns `blocked` with `spec` gaps naming each unresolved decision and the required resolution

### Scenario: Non-observable scenarios block readiness
- **Given** a Spec scenario has a Then step that does not state a verifiable return value, state change, side effect, error, emitted output, persisted format, protocol behavior, or user-visible behavior
- **When** the skill evaluates readiness
- **Then** it returns `blocked` with a `spec` gap identifying the scenario that must be rewritten

### Scenario: Missing Proposed Surface blocks tool or API work
- **Given** the Spec describes user-facing tools, APIs, commands, fields, parameters, or return shapes without enough Proposed Surface detail to implement or test them
- **When** the skill evaluates readiness
- **Then** it returns `blocked` with a `spec` gap naming the missing surface detail

### Scenario: Repository context sharpens plan-concreteness checks
- **Given** repository context is supplied with validation commands, test frameworks, existing surfaces, or repo conventions
- **When** the skill judges whether the plan is concrete enough
- **Then** it evaluates the plan against those concrete commands, frameworks, surfaces, and conventions and reports gaps where the plan diverges from repo context

### Scenario: Plan without ordered tasks blocks readiness
- **Given** the Deep Plan does not list ordered work items or does not identify dependencies between work items
- **When** the skill evaluates readiness
- **Then** it returns `blocked` with a `plan` gap requiring ordered tasks and dependency order

### Scenario: Plan without expected files or components blocks readiness
- **Given** the Deep Plan does not identify the expected files, components, modules, or surfaces affected by each work item
- **When** the skill evaluates readiness
- **Then** it returns `blocked` with a `plan` gap requiring the missing implementation scope for each affected work item

### Scenario: Plan without validation blocks readiness
- **Given** the Deep Plan lacks validation commands, test strategy, or success criteria for planned work
- **When** the skill evaluates readiness
- **Then** it returns `blocked` with a `plan` gap requiring validation and test strategy before implementation begins

### Scenario: Plan without risk or rollback notes blocks readiness
- **Given** the Deep Plan lacks risks, rollback notes, or failure-handling expectations for a task that touches more than one module, changes a persisted data format or protocol, or is not reversible by reverting a single commit
- **When** the skill evaluates readiness
- **Then** it returns `blocked` with a `plan` gap requiring risk or rollback notes for that task

### Scenario: Missing task-to-scenario mapping blocks readiness
- **Given** one or more Deep Plan tasks cannot be traced to a Spec scenario, or one or more Spec scenarios have no planned task or explicit non-implementation rationale
- **When** the skill evaluates readiness
- **Then** it returns `blocked` with a `both` gap identifying the unmapped task or scenario

### Scenario: Spec and plan contradiction blocks readiness
- **Given** the Deep Plan proposes behavior, scope, sequencing, surfaces, or validation that contradicts the Spec
- **When** the skill evaluates readiness
- **Then** it returns `blocked` with a `both` gap describing the contradiction and the decision needed to resolve it

### Scenario: First safe task requires dependency awareness
- **Given** the Spec and Deep Plan are otherwise implementable but some tasks depend on earlier tasks or shared surfaces
- **When** the skill names the first safe task
- **Then** it selects a task whose prerequisites are satisfied and whose scenario coverage and validation are known

### Scenario: Blocked verdict does not authorize implementation
- **Given** the skill returns one or more blocking gaps
- **When** a workflow consumes the verdict
- **Then** the verdict does not include a first safe task and does not authorize tests, production code, or implementation delegation to begin

## Proposed Surface

### Skill Invocation

| Input | Required | Description |
|---|:---:|---|
| Spec | yes | Behavioral contract containing goals, scenarios, constraints, Proposed Surface, and Open Questions. |
| Deep Plan | yes | Ordered implementation plan containing tasks, expected affected areas, dependencies, validation, test strategy, risks, rollback notes, and task-to-scenario mapping. |
| Repository context | no | Existing repo conventions, validation commands, test frameworks, or surfaces used to judge whether the plan is concrete enough. |

### Readiness Verdict

| Field | Required | Description |
|---|:---:|---|
| `verdict` | yes | `implementable` or `blocked`. |
| `blocking_gaps` | yes | Empty when implementable; otherwise a list of gaps with `source`, `reason`, and `required_resolution`. |
| `scenario_to_test_map` | yes | Scenario names mapped to a recommended test layer drawn from the repo's test taxonomy (`docs/spec/test.md` and the Test Quality skill when available), with the reason for the layer choice; empty list when readiness is blocked before mapping. |
| `task_to_scenario_map` | yes | Planned tasks linked to covered scenarios, with unmapped tasks or scenarios listed as blocking gaps. |
| `first_safe_task` | no | First implementation task safe to start when the verdict is `implementable`. |

## Open Questions

None.
