---
name: spec-quality
description: Use when drafting, reviewing, repairing, or validating scenario-based specs, product specs, implementation specs, Proposed Surface sections, Given/When/Then scenarios, Open Questions, or spec-quality checklists. Helps keep specs contract-level, observable, non-redundant, grounded in repo context, and free of implementation planning.
---

# Spec Quality

## Intent

Help agents draft and review specs that are contract-level, scenario-driven, testable, non-redundant, and grounded in existing repository context.

A good spec says **what** behavior should exist and **why** it matters. It does not become the implementation plan, architecture brief, task list, or test file design.

## When to use

Use this skill when working on any scenario-based spec or spec-like draft, including:

- product or implementation specs;
- `Problem`, `Goals`, `Non-Goals`, `Constraints`, `Scenarios`, `Proposed Surface`, or `Open Questions` sections;
- Given/When/Then scenarios;
- spec review, repair, validation, or quality checklists.

This skill can guide drafting or return a quality report. It does not replace a repo's explicit Spec workflow when that workflow is responsible for writing files, naming specs, or updating spec indexes.

## Inputs

Required:

- **Spec draft or source request**: readable spec content, proposed spec sections, scenarios, or a user request for a future spec.

Optional:

- **Repository context**: existing names, tools, commands, APIs, docs, schemas, or conventions that should ground the spec wording.

If no spec draft or source request is supplied, or the supplied input cannot be interpreted as spec-related content, report `input_error` and do not return `ready`.

## Non-goals

Do not use this skill to:

- replace an explicit Spec workflow that writes `docs/spec/` files or updates spec indexes;
- write `docs/spec/` files unless the user explicitly asks for file edits;
- update `docs/spec/README.md`;
- create implementation plans, architecture documents, code, or tests;
- decide feature implementation details that belong to planning or design;
- judge readiness of a Spec plus Deep Plan pair; use a dedicated `spec-plan-readiness` process for that.
- judge whether an implementation conforms to a spec (spec-vs-implementation); use `spec-conformance` for that, or `document` for doc-vs-code drift.

## Workflow

### 1. Check input

Determine whether you have a readable spec draft or source request.

- If missing or uninterpretable, set `input_error` to the exact problem and set `verdict: needs_revision`.
- If the user asked for drafting help from a source request, treat the request as valid input and use the checks as drafting guidance.
- Use the term **source request** for the user's requested behavior; avoid vague labels for the user's requested behavior.

### 2. Check contract-level scope

Specs stay at the what/why level. Put findings in `contract_level_findings` when content includes implementation-plan material that is not a predetermined constraint, such as:

- architecture choices;
- file locations or file organization;
- indexing, caching, storage, migration, or background processing strategy;
- code-level types, internal methods, or module names;
- phased delivery steps, task breakdowns, or sequencing;
- test file structure or implementation-specific test mechanics.

When possible, recommend either removing the material or rewriting it as an observable behavioral constraint.

### 3. Check scenario quality

Put findings in `scenario_findings` for any Given/When/Then scenario that is not:

- **Declarative**: describes behavior at the contract level, not internals;
- **Observable**: the Then step states a specific return value, state change, side effect, error, emitted output, persisted format, protocol behavior, or user-visible behavior;
- **Independent**: can be understood and tested without relying on another scenario's execution;
- **Focused**: covers one behavior rather than bundling unrelated concerns.
- **Identifiable**: carries a stable, unique ID (e.g., `S-001`) so tests and tasks can trace to it.

Flag vague Then steps such as "works correctly", "handles it", "shows the right result", or "does not break" unless the observable outcome is made explicit.

### 4. Check goal-to-scenario coverage

For each goal, verify that at least one scenario covers it.

- If a goal has no scenario, add a `scenario_findings` entry naming the uncovered goal.
- If all goals are covered, do not add a finding just to say so; the empty field is the clean result.

### 5. Check Proposed Surface-to-scenario coverage

If the spec lists tools, endpoints, commands, parameters, fields, return shapes, persisted formats, protocol behaviors, or other user-visible surfaces, verify each one appears in at least one scenario.

Put findings in `surface_findings` when:

- a surface element has no scenario coverage;
- a return field or error shape is listed but never exercised by a scenario;
- wording invents names, tools, APIs, commands, or conventions unsupported by available repository context.

Prefer existing repository terms and surfaces over invented names whenever repository context is available.

### 6. Check redundancy and section placement

Put findings in `redundancy_findings` when the same requirement appears across sections without adding precision.

Prefer the most specific section:

- scope exclusions belong in `Non-Goals`;
- predetermined environmental or policy constraints belong in `Constraints`;
- observable behavior belongs in `Scenarios`;
- public tools, endpoints, parameters, fields, and return shapes belong in `Proposed Surface`;
- unresolved decisions belong in `Open Questions`.

Recommend removing redundant copies rather than preserving duplicated text.

### 7. Check ambiguity and testability

Put findings in `ambiguity_findings` when text could be interpreted more than one way or cannot be tested as written, including:

- vague outcomes;
- undefined domain terms;
- implicit ordering or dependencies;
- missing defaults or omission behavior for optional parameters or optional behavior;
- unclear boundaries, permissions, ownership, or error conditions;
- placeholders such as `TBD`, `TODO`, question marks, or bracketed fill-ins.

State what decision or rewrite is needed to make the contract observable.

### 8. Check Open Questions

Put findings in `open_question_findings` when:

- unresolved decisions, placeholders, or unaccepted recommendations are hidden as assumptions in other sections;
- an Open Question lacks a recommendation or a clear reason no recommendation can be made.

Open Questions should be explicit and include recommendations so implementors can see the preferred path without mistaking unresolved decisions for accepted contract. If a decision has already been made, move it to the appropriate contract section instead of leaving it as a question.

### 9. Return the verdict

All findings are blocking. Do not emit advisory-only findings.

Use this deterministic rule:

- `verdict: ready` only when `input_error` and every findings field are empty.
- `verdict: needs_revision` otherwise.

## Output format

Return the quality report with these fields in this order:

```text
input_error
contract_level_findings
scenario_findings
surface_findings
redundancy_findings
ambiguity_findings
open_question_findings
verdict
```

Use empty strings or empty lists for fields with no findings. Keep findings specific enough that the user can revise the spec without guessing.

### Template

```text
input_error: []
contract_level_findings: []
scenario_findings: []
surface_findings: []
redundancy_findings: []
ambiguity_findings: []
open_question_findings: []
verdict: ready
```

If any field is non-empty, the verdict must be:

```text
verdict: needs_revision
```

## Drafting guidance

When drafting from a source request rather than reviewing an existing draft:

1. Capture the user's problem, goals, non-goals, constraints, scenarios, proposed surfaces, and open questions.
2. Keep implementation strategy, delivery sequencing, and file organization out of the spec unless the user states them as fixed constraints.
3. Make every scenario independently testable with a concrete observable Then outcome.
4. Make every goal and user-visible surface traceable to at least one scenario.
5. Put unresolved decisions in Open Questions with recommendations instead of silently choosing implementation details.
