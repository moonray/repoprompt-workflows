---
title: Test Quality Skill
issue: none
status: implemented
---

# Test Quality Skill

## Problem

Tests get written to increase coverage or restate implementation details rather than to protect behavior. Agents need reusable discipline to decide whether a test is worth adding, choose the right layer, avoid low-value tests, and verify meaningful oracles — independent of the Test workflow that generates tests.

## Goals

1. Keep only tests that protect a current contract with a named, plausible defect.
2. Choose the lowest test layer that faithfully reproduces the risk.
3. Prefer exact observable outcomes over "does not crash", not-nil, or field-presence assertions.
4. Ensure coverage at trust boundaries (user-input, network, filesystem, secrets, process-exec, database, auth/permissions, concurrency, external-api, serialization).
5. Avoid low-value tests: coverage-padding, implementation-detail restatements, one-test-per-branch, mocks that reimplement production logic.
6. Distinguish diagnostics (no pass/fail oracle) from coverage; for bug fixes, prove the regression fails on known-bad code before trusting it.

## Non-Goals

- Write tests for the agent; this is guidance (the Test workflow generates tests).
- Mandate a framework, language, or coverage threshold.
- Grade spec quality (`spec-quality`) or review finding quality (`review-quality`).

## Constraints

- Applies to any language/stack.
- Committed fixtures are immutable/read-only; destructive tests operate on copies.
- Smoke/diagnostic tests needing network, credentials, or wall-clock dates must be labeled as such.

## Scenarios

### Scenario: A test is added only when a plausible defect is named
- **Given** a proposed test
- **When** the decide-before-writing step is applied
- **Then** a concrete defect (data loss, protocol break, race, persistence error, malformed input, costly operational failure) is named, or the test is omitted

### Scenario: The lowest faithful layer is chosen
- **Given** a behavior to cover
- **When** layer selection runs
- **Then** the lowest layer that faithfully reproduces the risk is picked (unit/core > component/service > fs/db/wire > raw fixtures > provider/adapter > end-to-end/smoke)

### Scenario: Exact observable outcomes are asserted
- **Given** a test under review
- **When** the core rules are applied
- **Then** it asserts an exact value, state, side effect, error, or wire/persisted format — not "does not crash" or field-presence

### Scenario: Trust boundaries get coverage
- **Given** behavior crosses a trust boundary
- **When** the test plan is finalized
- **Then** that boundary has coverage, with higher scrutiny on secrets/auth/permissions/user-input/serialization/concurrency

### Scenario: A bug-fix regression is proven to fail first
- **Given** a bug fix with a regression test
- **When** the test is evaluated
- **Then** it is shown to fail against the known-bad behavior and reproduce the reported symptom before the fix is trusted

### Scenario: Diagnostics are not counted as coverage
- **Given** a benchmark or probe without an acceptance threshold
- **When** it is classified
- **Then** it is committed as a labeled diagnostic, not a passing test; promoted to coverage only once it has a pass/fail oracle

### Scenario: Low-value tests are consolidated or omitted on review
- **Given** a test that is a non-nil check, implementation-detail restatement, one-per-branch, or coverage-driven with no named failure mode
- **When** the review checklist runs
- **Then** it is consolidated, moved to a lower layer, converted to a smoke/diagnostic, or deleted

### Scenario: Mocks do not reimplement production logic
- **Given** a test mock
- **When** mock guidance is applied
- **Then** it does not duplicate production filtering/sorting/parsing/permission/persistence/routing logic; if that logic matters it is tested directly

### Scenario: The commit gate refuses a test without a named failure mode
- **Given** a candidate test
- **When** the commit gate is evaluated
- **Then** the test is committed only if it protects a current contract, fails for a meaningful defect at the lowest faithful layer, and is deterministic and isolated; otherwise it is consolidated/redesigned/omitted

### Scenario: Reporting states contract, layer, fixtures, validation, and omissions
- **Given** completed test work
- **When** it is summarized
- **Then** the report states the protected contract and risk, the chosen layer and why, fixture strategy, validation commands run, and coverage intentionally omitted/consolidated/deferred

## Proposed Surface

### Inputs

| Input | Required | Description |
|---|:---:|---|
| Behavior under test | yes | The contract the test would protect. |
| Existing coverage | no | Direct tests / outcome assertions already protecting the behavior. |
| Oracle | no | An exact observable outcome distinguishing broken from fixed. |

### Output

| Field | Description |
|---|---|
| `decision` | add / consolidate / redesign / classify-as-diagnostic / omit. |
| `layer` | The chosen lowest-faithful layer and rationale. |
| `fixture_strategy` | Generated vs raw fixtures; immutability handling; secrets/PII/absolute-paths sanitized; minimal; fixture-encoded historical bugs documented. |
| `validation` | Commands run to validate. |
| `omitted` | Coverage intentionally not added, with reason. |

## Open Questions

None.
