---
title: Spec Conformance Skill
issue: none
status: implemented
---

# Spec Conformance Skill

## Problem

Green tests are not proof of spec conformance — they assert code contracts (an element exists, an endpoint returns 200), not that behavior matches the spec. Closing a spec-driven feature needs a section-by-section audit mapping every spec item to its implementation, plus a coverage proof that the whole spec was checked.

## Goals

1. Enumerate every auditable spec item: each scenario (`S-NNN`), each Proposed Surface element, and each stated value/enum/constraint.
2. Locate code or test evidence for each item.
3. Classify each item Conformed / Diverged / Not-built, stating both sides on divergence.
4. Emit a coverage proof — the `audited` set (everything checked) and `unreconciled` set (Diverged + Not-built), with no item silently dropped.

## Non-Goals

- Fix divergences (report them only).
- Judge spec well-formedness (`spec-quality`) or doc drift (`document`).
- Write tests; only flag where a spec invariant lacks a covering test.

## Constraints

- Input is a spec path (required); implementation scope defaults to the repo / working tree.
- Output is written to `docs/spec/<spec>.conformance.md`.
- An empty result is valid only as `{ audited: [...], unreconciled: [] }`.

## Scenarios

### Scenario: Every spec item is enumerated
- **Given** a spec path
- **When** the audit enumerates auditable items
- **Then** it lists each scenario (`S-NNN`), each Proposed Surface element (tool/endpoint/parameter/field/return shape), and each stated value, enum, or constraint

### Scenario: Evidence is located for each item
- **Given** an enumerated item
- **When** evidence is located
- **Then** a code location (`file:symbol`) or an asserting test is recorded for it

### Scenario: Items are classified with both sides on divergence
- **Given** located evidence
- **When** items are classified
- **Then** each is Conformed (evidence matches), Diverged (evidence conflicts — spec side and code side both stated), or Not-built (no evidence)

### Scenario: A coverage proof is emitted
- **Given** a completed classification
- **When** the output is produced
- **Then** it emits the `audited` set (every item checked) and the `unreconciled` set (Diverged + Not-built)

### Scenario: An empty result requires positive evidence
- **Given** a spec with no divergences
- **When** the audit completes
- **Then** the result is `{ audited: [...], unreconciled: [] }` — "no divergence" requires evidence the whole spec was checked

### Scenario: Each unreconciled item carries a disposition
- **Given** an unreconciled item
- **When** it is recorded
- **Then** it is marked to-fix or accepted-with-reason, never silently dropped

## Proposed Surface

### Inputs

| Input | Required | Description |
|---|:---:|---|
| Spec path | yes | The spec document to audit. |
| Implementation scope | no | Defaults to the repo / working tree. |

### Output

| Field | Description |
|---|---|
| matrix rows | `{ section, item, status: Conformed\|Diverged\|Not-built, evidence, note }`. |
| `audited` | Every spec section and item checked. |
| `unreconciled` | Diverged + Not-built items, each with a disposition (fix \| accepted-with-reason). |

## Open Questions

None.
