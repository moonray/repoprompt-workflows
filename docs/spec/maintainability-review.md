---
title: Maintainability Review Skill
issue: none
status: implemented
---

# Maintainability Review Skill

## Problem

Reviews tend to accept working code that leaves the codebase messier. A strict, quality-only structural lens is needed that hunts for dramatic simplifications ("code judo") — behavior-preserving restructurings that delete complexity — rather than local cleanup.

## Goals

1. Push for ambitious structural simplification: prefer the solution that makes the code feel inevitable in hindsight, and delete complexity rather than rearrange it.
2. Flag giant files: do not let a change push a file from under 1k lines to over 1k without a strong reason.
3. Flag spaghetti growth: ad-hoc conditionals, special cases, or one-off branches inserted into unrelated flows.
4. Flag unearned indirection: thin wrappers, identity pass-throughs, and generic mechanisms hiding simple data shapes.
5. Flag logic leaking across layers and failure to reuse existing canonical helpers.
6. Flag unnecessary optionality/casts and avoidable sequential/non-atomic orchestration.
7. Remain quality-only — do not approve merely because behavior is correct.

## Non-Goals

- Hunt behavior/correctness bugs (pair with a correctness lens).
- Discover findings or size the review (`review-depth`).
- Enforce local style nits.

## Constraints

- Use as one lens in a multi-lens review (e.g., Deep Review), or standalone.
- The rubric is vendored from upstream and sync-managed between `BEGIN`/`END` markers; re-sync with `scripts/sync-maintainability-review.mjs`, never hand-edit between markers.

## Scenarios

### Scenario: Code-judo simplifications are proposed
- **Given** a change under structural review
- **When** the lens is applied
- **Then** it searches for restructurings that preserve behavior while making the implementation dramatically simpler, smaller, and more direct

### Scenario: A file crossing 1k lines is flagged
- **Given** a diff that would push a file over 1000 lines
- **When** the lens reviews it
- **Then** it treats the crossing as a strong smell, preferring extraction/decomposition, and waives only with a compelling structural reason

### Scenario: Spaghetti growth in unrelated flows is flagged
- **Given** new ad-hoc conditionals or one-off branches inserted into unrelated flows
- **When** the lens reviews it
- **Then** it treats the addition as a design problem and prefers a dedicated abstraction/helper/state machine/module

### Scenario: Unearned wrappers and pass-throughs are flagged
- **Given** a thin abstraction, identity wrapper, or pass-through helper adding indirection without clarity
- **When** the lens reviews it
- **Then** it flags it and prefers direct, boring, maintainable code

### Scenario: Logic leaking across layers is flagged
- **Given** feature logic leaking into shared paths or implementation details leaking through APIs
- **When** the lens reviews it
- **Then** it calls out the leak and prefers the existing canonical utility and the right layer

### Scenario: Type-boundary and orchestration smells are flagged
- **Given** unnecessary optionality/casts/`any` that obscure the real invariant, or avoidable sequential/non-atomic orchestration
- **When** the lens reviews it
- **Then** it flags them per rules 5 (type/boundary cleanliness) and 7 (sequential/non-atomic orchestration), preferring explicit typed models and a simpler, more atomic flow

### Scenario: Correct behavior alone does not win approval
- **Given** a change that works but leaves the codebase messier
- **When** the lens evaluates it
- **Then** it does not approve merely because behavior is correct; it pushes for the cleaner structure

### Scenario: Rubric changes are re-synced, not hand-edited
- **Given** an upstream rubric change
- **When** the lens is maintained
- **Then** the skill is updated via the sync script, not by hand-editing between the markers

## Proposed Surface

### Inputs

| Input | Required | Description |
|---|:---:|---|
| Change set | yes | The diff/branch under structural review. |
| Repo context | no | Surrounding architecture to judge layering and reuse. |

### Output

| Field | Description |
|---|---|
| `structural_findings` | Each with evidence and a proposed simplification (prefer delete-over-rearrange). |
| `category` | giant-file \| spaghetti \| unearned-wrapper \| layer-leak \| type-boundary \| orchestration \| code-judo. |

## Open Questions

None.
