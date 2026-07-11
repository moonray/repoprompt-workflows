---
title: User Testing Skill
issue: none
status: implemented
---

# User Testing Skill

## Problem

A frontend feature is not done because its automated tests pass — automated tests assert code contracts (an element exists, a tab switches), not that the feature works or looks right for the user. Spec-conformance is not a substitute either, since the spec itself can be wrong. Only driving the real rendered UI through actual workflows catches these defects.

## Goals

1. Enumerate the real user workflows the feature serves (from spec scenarios / intent, not the test list).
2. Drive the real rendered UI via automation — browser tools for web/HTML, platform UI automation for non-HTML native UI — end-to-end as the user would.
3. Screenshot each step and inspect with a user's eyes; check console errors and failed network requests.
4. Flag the defects automated tests miss (empty columns, broken layouts, wrong copy, dead controls).
5. Produce a user-test record; treat a human hand-off as the optional gold standard, not the only path.
6. When user testing cannot run, mark the closeout item `blocked` with a reason — never silently skip it.

## Non-Goals

- Replace automated tests (`test-quality`), spec-conformance (`spec-conformance`), or code review (Deep Review / `maintainability-review`).
- Fix issues found; report them so they become follow-up tasks.

## Constraints

- **Data isolation (hard rule):** run against a throwaway/isolated data location, never the user's real environment data — browser automation on real data can destroy it, and unattended runs have nobody watching.
- A functional smoke ("it loads, tabs switch") is the floor, not a substitute, and must be labeled as such.

## Scenarios

### Scenario: Workflows come from spec/intent, not the test list
- **Given** a user-facing feature
- **When** workflows are enumerated
- **Then** they come from the spec's scenarios or the feature's intent, not from the automated test list

### Scenario: The real UI is driven end-to-end per workflow
- **Given** an enumerated workflow
- **When** the skill runs
- **Then** it drives the real rendered UI (browser automation for web/HTML; platform UI automation for native UI) through the workflow as the user would

### Scenario: Each step is screenshotted and inspected
- **Given** a driven workflow
- **When** steps execute
- **Then** each step is screenshotted and inspected with a user's eyes for empty columns, broken layouts, wrong copy, and dead controls

### Scenario: The runtime is checked, not just the pixels
- **Given** a driven UI
- **When** runtime state is checked
- **Then** console errors and failed/missing network requests are inspected for defects invisible to unit and contract tests

### Scenario: A human hand-off is optional, not required
- **Given** a completed tool-driven pass
- **When** the actual user is available
- **Then** the feature may be handed off and what they hit logged; tool-driven testing remains the scalable default

### Scenario: Impossible user testing is blocked, not skipped
- **Given** no UI runtime, headless/CI-only, or no user available
- **When** user testing cannot run
- **Then** the closeout item is `blocked` with a recorded reason, never silently skipped; a functional smoke is labeled as the floor, not a substitute

### Scenario: Testing runs against throwaway data
- **Given** a user-testing run
- **When** the target data location is chosen
- **Then** it is a throwaway/isolated location, never the user's real environment data

### Scenario: A user-test record is produced
- **Given** a completed run
- **When** the output is produced
- **Then** it records workflows exercised (steps, result, screenshot refs), issues found (severity, what/where, screenshot), and `not_tested` (what couldn't be tested + why)

## Proposed Surface

### Inputs

| Input | Required | Description |
|---|:---:|---|
| Feature | yes | The user-facing/frontend change to verify. |
| Spec scenarios | no | Source of the real user workflows. |

### Output

| Field | Description |
|---|---|
| `workflows` | Each: steps, result, screenshot references. |
| `issues` | Each: severity, what + where, screenshot. |
| `not_tested` | What couldn't be tested + why (blocked), or "handed to user — pending". |

## Open Questions

None.
