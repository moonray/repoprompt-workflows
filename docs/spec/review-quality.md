---
title: Review Quality Skill
issue: none
status: implemented
---

# Review Quality Skill

## Problem

Review findings can be vague, ungrounded, or closed on model opinion. Findings need structured evidence, grounding in the reviewed scope, a revalidation gate that refuses model-only "fixed", and stable signatures so repeats can be deduped and triaged.

## Goals

1. Require structured, resolvable evidence on every finding (`path`, line range, `symbol`, `quote`).
2. Keep findings grounded in the review scope; drop unresolvable ones while keeping valid siblings.
3. Report scope proof (`inspected`); an empty finding set is valid only with `inspected`.
4. Close a finding `fixed` only on a fresh review plus passing targeted validation — never on model opinion alone.
5. Give each finding a stable signature for dedup, rerank, and repeat detection.
6. Triage before acting: dedup, rerank, and classify repeats rather than looping.

## Non-Goals

- Write or apply fixes (the Loop workflow coordinates fixing); this skill judges findings.
- Replace a repo's own review tooling when it emits findings.
- Grade spec or test quality (`spec-quality`, `test-quality`).

## Constraints

- Input is a review scope (diff/task/files) and the findings, optionally validation commands.
- Findings without resolvable evidence are invalid.

## Scenarios

### Scenario: Every finding carries resolvable evidence
- **Given** a review finding
- **When** it is produced
- **Then** it carries `path`, `startLine`/`endLine`, `symbol`, and a `quote` of the offending code; a finding without resolvable evidence is invalid

### Scenario: Unresolvable findings are dropped, siblings kept
- **Given** a finding whose `path`/line range does not resolve in the review scope
- **When** findings are grounded
- **Then** that finding is dropped, but valid sibling findings are kept — one bad finding does not sink the batch

### Scenario: Scope proof is reported
- **Given** a completed review
- **When** findings are reported
- **Then** the `inspected` scope (files/symbols covered) is reported; an empty finding set is valid only as `{ findings: [], inspected: [...] }`

### Scenario: A finding is fixed only on fresh review plus passing validation
- **Given** a finding marked `fixed`
- **When** the revalidation gate runs
- **Then** a fresh review no longer finds it AND the targeted validation commands pass (results recorded); if validation cannot run, the status is `blocked` or `uncertain`, never `fixed`

### Scenario: Stable signatures support dedup
- **Given** a set of findings
- **When** signatures are computed
- **Then** each finding carries severity + normalized path + normalized summary + related scenario/task ID, used to detect repeats and dedup

### Scenario: Triage classifies repeats rather than looping
- **Given** repeated findings with the same signature
- **When** triage runs
- **Then** identical signatures are deduped, survivors reranked, and after two failed fix attempts or three observations the signature is classified `false_positive` / `core_issue` / `futility`

### Scenario: Output records evidence, scope, drops, and validation
- **Given** reported findings
- **When** the output is produced
- **Then** it states findings with evidence and signatures, the `inspected` scope, dropped findings and why, validation commands/results for any `fixed`, and any `blocked`/`uncertain` items

## Proposed Surface

### Inputs

| Input | Required | Description |
|---|:---:|---|
| Review scope | yes | The diff, task, or files under review. |
| Findings | yes | Existing findings, or a request to produce them. |
| Validation commands | no | Tests/lint/build available for the changed behavior. |

### Output

| Field | Description |
|---|---|
| `findings` | Each with evidence (`path`, lines, `symbol`, `quote`) and a signature. |
| `inspected` | Files/symbols covered. |
| `dropped` | Findings removed and why. |
| `validation` | Commands and results used for any `fixed` status. |
| `blocked`/`uncertain` | Items that cannot be closed, with blockage. |

## Open Questions

None.
