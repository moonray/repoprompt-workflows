---
title: Spec Quality Skill
issue: none
status: implemented
---

# Spec Quality Skill

## Problem

Spec-writing guidance currently lives inside the Spec workflow, so other agents and workflows cannot reliably reuse it when drafting, reviewing, or repairing specs. This creates drift: a workflow can keep the required file-writing steps while silently weakening scenario quality, Proposed Surface discipline, redundancy checks, or ambiguity checks. A reusable Spec Quality skill is needed so spec-like documents can be judged by the same behavioral standards wherever they are created or reviewed.

## Goals

1. Provide reusable quality criteria for drafting and reviewing implementation or product specs.
2. Ensure specs describe what and why, not implementation strategy, delivery phases, or file organization.
3. Ensure scenarios are declarative, observable, independent, and traceable to goals and user-visible surfaces.
4. Ensure Proposed Surface content is precise enough for tests or implementation planning without duplicating other sections.
5. Identify redundancy, gaps, ambiguity, placeholders, and unresolved decisions before a spec is treated as ready.

## Non-Goals

- Invoke or replace the Spec workflow that writes `docs/spec/` files and updates the spec index.
- Generate implementation plans, architecture documents, code, or tests.
- Decide how a feature should be implemented.
- Require every runtime to support automatic skill invocation.
- Define readiness criteria for a Spec plus Deep Plan pair; that belongs to Spec-Plan Readiness.

## Constraints

- The skill applies to scenario-based specs and spec drafts, including repo-local specs that use Problem, Goals, Non-Goals, Constraints, Scenarios, Proposed Surface, and Open Questions.
- Scenario outcomes must be observable as a return value, state change, side effect, error, emitted output, persisted format, protocol behavior, or user-visible behavior.
- Existing repository terms, surfaces, and conventions are preferred over invented names when the repository context is available.

## Scenarios

### Scenario: Draft guidance keeps specs at the contract level
- **Given** a user asks for help drafting a spec for a behavioral change
- **When** the skill's guidance is applied
- **Then** the resulting guidance emphasizes the user's problem, goals, non-goals, constraints, scenarios, proposed surfaces, and open questions without prescribing implementation strategy, delivery phases, or file organization

### Scenario: Review flags implementation planning in a spec
- **Given** a spec draft contains architecture choices, file locations, indexing strategy, code-level types, or phased delivery steps that are not predetermined constraints
- **When** the skill reviews the draft
- **Then** it reports those items as plan material that should be removed or rewritten as behavioral constraints

### Scenario: Scenario quality is checked
- **Given** a spec draft contains Given/When/Then scenarios
- **When** the skill reviews the scenarios
- **Then** it reports any scenario that is not declarative, not independently testable, or whose Then step lacks a specific observable outcome

### Scenario: Goals map to scenarios
- **Given** a spec draft contains one or more goals
- **When** the skill performs a gap check
- **Then** it reports each goal with no covering scenario, or confirms that every goal is covered by at least one scenario

### Scenario: Proposed Surface maps to scenarios
- **Given** a spec draft lists tools, endpoints, parameters, fields, return shapes, or other user-visible surfaces
- **When** the skill performs a gap check
- **Then** it reports each surface element that does not appear in at least one scenario, or confirms that every surface element is covered

### Scenario: Redundant content is removed from the recommendation
- **Given** a spec draft repeats the same requirement across Non-Goals, Constraints, Scenarios, or Proposed Surface
- **When** the skill reviews the draft
- **Then** it recommends keeping the requirement in the most specific section and removing the redundant copies

### Scenario: Ambiguity is identified
- **Given** a spec draft uses vague outcomes, undefined domain terms, implicit ordering, or missing defaults for optional behavior
- **When** the skill reviews the draft
- **Then** it reports the ambiguous text and states what decision or rewrite is needed to make the contract testable

### Scenario: Open questions are distinguished from decisions
- **Given** a spec draft contains unresolved decisions, placeholders, or recommendations that are not yet accepted
- **When** the skill reviews the draft
- **Then** it requires those items to appear as explicit Open Questions with recommendations rather than as silent assumptions

### Scenario: Existing repo context is respected
- **Given** repository context identifies existing names, tools, commands, APIs, or conventions relevant to the spec
- **When** the skill reviews proposed wording
- **Then** it prefers wording grounded in those existing surfaces and reports invented names or conventions that are unsupported by the repo context

### Scenario: No issues produces a clean result
- **Given** a spec draft is contract-level, scenario-driven, non-redundant, complete, and unambiguous
- **When** the skill reviews the draft
- **Then** it reports that no blocking spec-quality issues were found

### Scenario: Missing spec input is reported
- **Given** no spec draft or source request is supplied, or the supplied input cannot be interpreted as spec-related content
- **When** the skill evaluates the input
- **Then** it reports that a readable spec draft or source request is required and does not return a `ready` verdict

## Proposed Surface

### Skill Invocation

| Input | Required | Description |
|---|:---:|---|
| Spec draft or source request | yes | The draft spec, proposed spec content, or free-text user request for a future spec being evaluated for spec quality. |
| Repository context | no | Existing names, tools, APIs, docs, or conventions that should ground the spec language. |

### Quality Report

| Field | Description |
|---|---|
| `input_error` | Missing or uninterpretable required input; empty when a spec draft or source request is available. |
| `contract_level_findings` | Items that drift into implementation planning or lack what/why framing. |
| `scenario_findings` | Scenarios that are not declarative, observable, independent, or mapped to goals. |
| `surface_findings` | Proposed Surface elements missing scenario coverage or using unsupported names. |
| `redundancy_findings` | Requirements repeated across sections or represented in the wrong section. |
| `ambiguity_findings` | Vague outcomes, undefined terms, implicit ordering, missing defaults, or placeholders. |
| `open_question_findings` | Unresolved decisions that must become Open Questions with recommendations. |
| `verdict` | `ready` when `input_error` and all finding fields are empty; otherwise `needs_revision`. All findings are treated as blocking and the skill does not emit advisory-only findings. |

## Open Questions

None.
