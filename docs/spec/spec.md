---
title: Spec Generation Workflow
issue: none
status: implemented
---

# Spec Generation Workflow

## Problem
The Spec workflow defines how agents turn feature requests into rigorous scenario-based specs, but the workflow itself has no spec that future edits can be checked against. Without a behavioral contract, changes to `.agents/workflows/Spec.md` can silently weaken intent confirmation, scenario coverage, anti-scope-creep rules, or documentation updates that users rely on when asking for spec generation.

## Goals
1. Produce one draft spec document for a user-provided feature request using the required spec structure.
2. Ground the spec in the user's stated intent, referenced issue context, and relevant repository context before drafting.
3. Require confirmation of the understood intent before writing a spec.
4. Ensure the final spec is scenario-driven, non-redundant, complete enough to test, and free of implementation planning.
5. Apply the shared Spec Quality guidance when drafting and reviewing the spec without depending on skill auto-loading for the workflow to remain usable.
6. Maintain the spec index and report the completed spec's key counts and unresolved questions.

## Non-Goals
- Generate implementation plans, architecture documents, code, tests, or phased delivery schedules.
- Decide how the requested feature will be implemented.
- Guarantee that future implementations satisfy the generated spec.
- Define behavior for workflows other than Spec Generation Mode.
- Require every spec request to have a GitHub issue.

## Constraints
- Generated specs must use this exact section order: frontmatter, H1 title, Problem, Goals, Non-Goals, Constraints, Scenarios, Proposed Surface, Open Questions.
- Scenarios must use Given/When/Then steps and be declarative, observable, and independently testable.

## Scenarios

### Scenario: Clear task produces a draft spec
- **Given** a user provides a clear feature request with no referenced GitHub issue
- **When** the workflow is confirmed and completed
- **Then** it writes one draft spec document at `docs/spec/<feature-name>.md` whose frontmatter includes the feature title, `issue: none`, and `status: draft`, followed by the required sections in the required order

### Scenario: Referenced issue informs the spec
- **Given** a user provides a feature request that references an existing GitHub issue
- **When** the workflow is confirmed and completed
- **Then** the generated spec records the issue number and reflects relevant issue context in the Problem, Goals, Scenarios, or Open Questions sections

### Scenario: Vague task asks for clarification
- **Given** a user provides a request that does not identify a specific behavioral change
- **When** the workflow evaluates the request
- **Then** it asks one clarifying question grounded in the available task and repository context before drafting

### Scenario: Understood intent is confirmed before drafting
- **Given** the workflow has enough context to describe the requested spec
- **When** the workflow finishes intent discovery
- **Then** it summarizes the understood intent in two or three sentences and waits for user confirmation before writing the spec

### Scenario: Shared spec quality guidance is applied
- **Given** the workflow drafts or reviews a spec document
- **When** it checks the spec before writing or presenting it
- **Then** it applies the shared Spec Quality criteria for contract-level scope, scenario quality, Proposed Surface coverage, redundancy, gaps, ambiguity, and Open Questions while preserving the workflow's concrete file-writing and index-maintenance behavior

### Scenario: Clarification timeout halts the workflow
- **Given** the workflow asks the user a clarifying question
- **When** the clarification interaction times out
- **Then** the workflow stops without writing a spec document or changing the spec index

### Scenario: Confirmation timeout halts the workflow
- **Given** the workflow asks the user to confirm the understood intent
- **When** the confirmation interaction times out
- **Then** the workflow stops without writing a spec document or changing the spec index

### Scenario: Problem starts from the user's pain point
- **Given** the workflow drafts a spec
- **When** the Problem section is written
- **Then** it states what is broken or missing, why it matters, and which existing tools, workflows, or repository patterns fall short when that context is available

### Scenario: Goals map to scenarios
- **Given** the workflow drafts a spec with one or more goals
- **When** the gap check is complete
- **Then** every goal is covered by at least one scenario, or the goal is rewritten or removed

### Scenario: Proposed surface is testable
- **Given** the workflow drafts a Proposed Surface with parameters, endpoints, tools, fields, or return shapes
- **When** the gap check is complete
- **Then** every listed parameter appears in at least one scenario or is removed from the Proposed Surface

### Scenario: Edge cases are covered
- **Given** the requested feature includes empty results, large result sets, missing data, boundary conditions, invalid input, or cross-scope behavior
- **When** the gap check is complete
- **Then** the Scenarios section includes independently testable coverage for each relevant edge case

### Scenario: Redundant material is removed
- **Given** a draft repeats the same requirement across sections or includes sections outside the required format
- **When** the redundancy check is complete
- **Then** the final spec keeps each requirement in the most specific section and contains no extra sections

### Scenario: Implementation planning is excluded
- **Given** a draft contains implementation strategy, file organization, architecture, indexing approach, delivery phases, or code-level decisions
- **When** the ambiguity and redundancy checks are complete
- **Then** the final spec removes that material unless it is an existing constraint necessary to express the behavioral contract

### Scenario: Open questions are explicit
- **Given** an unresolved decision remains after drafting
- **When** the final spec is written
- **Then** the Open Questions section lists the decision as a numbered question with a recommendation

### Scenario: No unresolved questions remain
- **Given** no unresolved decisions remain after drafting
- **When** the final spec is written
- **Then** the Open Questions section states that there are no open questions

### Scenario: Spec index is maintained
- **Given** the workflow writes a spec document
- **When** the workflow completes
- **Then** the spec index contains a row for the spec name, issue value, and draft status

### Scenario: Completion summary is reported
- **Given** the spec document and spec index have been written
- **When** the workflow responds to the user
- **Then** it reports the number of scenarios, the number of proposed tools or endpoints, and any open questions needing user input

## Proposed Surface

### Workflow Invocation

| Parameter | Type | Required | Description |
|---|---:|:---:|---|
| `task` | string | yes | The user's feature or workflow request to turn into a spec. |

### Generated Spec Document

| Field or Section | Required | Description |
|---|:---:|---|
| Document path | yes | `docs/spec/<feature-name>.md`. |
| `title` | yes | Human-readable feature name in frontmatter. |
| `issue` | yes | Referenced GitHub issue number, or `none` when no issue applies. |
| `status` | yes | Always `draft` for newly generated specs. |
| `# <Feature Name>` | yes | H1 matching the feature name. |
| `Problem` | yes | The user pain point, existing gap, and why it matters. |
| `Goals` | yes | Numbered deliverables, each covered by at least one scenario. |
| `Non-Goals` | yes | Explicit scope exclusions. |
| `Constraints` | yes | Environmental realities and predetermined decisions not already self-evident from the surface. |
| `Scenarios` | yes | Given/When/Then behavioral contract. |
| `Proposed Surface` | yes | Tool schemas, API endpoints, parameters, return shapes, or other user-visible surfaces. |
| `Open Questions` | yes | Numbered unresolved decisions with recommendations, or a statement that there are no open questions. |

### Shared Quality Criteria

| Criterion | Description |
|---|---|
| Contract-level scope | Spec content states what and why; implementation strategy, architecture, file organization, and delivery phases are excluded unless they are predetermined constraints. |
| Scenario quality | Scenarios are declarative, observable, independent, and traceable to goals and Proposed Surface elements. |
| Redundancy, gap, and ambiguity checks | Repeated requirements, missing scenario coverage, undefined terms, vague outcomes, missing defaults, and unresolved decisions are corrected or reported before completion. |

### Completion Summary

| Field | Description |
|---|---|
| `scenario_count` | Number of scenarios in the written spec. |
| `tools_or_endpoints_count` | Number of proposed tools or endpoints in the written spec. |
| `open_questions` | Open questions that need user input, or an explicit statement that none remain. |

## Open Questions
None.
