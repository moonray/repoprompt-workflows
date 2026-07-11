---
title: Review Depth Skill
issue: none
status: implemented
---

# Review Depth Skill

## Problem

Reviews waste tokens over-reviewing small changes and under-review large or risky ones. A deterministic, auditable rule is needed to pick the cheapest review depth (quick / standard / deep) that is still safe for a change.

## Goals

1. Compute review signals (size, spread, severe risk flags, blast radius, doc-only) from the change set.
2. Select depth deterministically — base on size, floored/escalated by severe flags and blast radius, with a doc-only shortcut.
3. Let an explicit user choice override detection, recorded as such.
4. Return depth plus signals and a one-line rationale so the choice is auditable.

## Non-Goals

- Choose lenses, partition zones, or decide verification (the review workflow's job).
- Run tests or validation.
- Override an explicit user choice.
- Enforce budget (`frugal`/`balanced`/`unlimited`); that is orthogonal and handled by the review workflow.

## Constraints

- Signals come from `git numstat`, diff paths, and the review map (in-repo callers of changed public/exported symbols).
- Severe risk flags: persisted data format/schema/migration/wire-protocol change; authn/authz/session/secret handling; public API/SDK/contract change.
- Size bands: S ≤ 150 · M 151–800 · L > 800 lines.

## Scenarios

### Scenario: Size sets the base depth
- **Given** a change of known size
- **When** the selection rule runs
- **Then** base depth is quick (S), standard (M), or deep (L)

### Scenario: A severe risk flag floors at standard and escalates
- **Given** one or more severe risk flags
- **When** the rule runs
- **Then** depth is at least standard, and each severe flag escalates one level toward deep

### Scenario: High blast radius escalates
- **Given** many or cross-subsystem in-repo callers of changed public symbols
- **When** blast radius is high
- **Then** depth escalates one level toward deep

### Scenario: Doc-only changes with no severe risk are quick
- **Given** every changed file is documentation/markdown and there are no severe flags
- **When** the rule runs
- **Then** depth is quick

### Scenario: An explicit user choice overrides detection
- **Given** the user explicitly chose quick / standard / deep
- **When** the skill runs
- **Then** that depth is used, detection is skipped, and the output records that detection was skipped

### Scenario: Output is auditable
- **Given** a selected depth
- **When** the result is returned
- **Then** it includes depth, the signals, and a one-line rationale

### Scenario: Lenses and verification are not chosen here
- **Given** a selected depth
- **When** downstream review is planned
- **Then** the skill does not choose lenses, partition zones, or verification, and does not run tests

## Proposed Surface

### Inputs

| Input | Required | Description |
|---|:---:|---|
| Change set | yes | A git comparison scope, enough to compute the signals. |
| Explicit depth | no | `quick` / `standard` / `deep`; overrides detection. |

### Output

| Field | Description |
|---|---|
| `depth` | `quick` \| `standard` \| `deep`. |
| `signals` | size band + lines, spread, severe count + kinds, blast radius, doc-only. |
| `rationale` | One-line justification; notes when detection was skipped (override). |

## Open Questions

None.
