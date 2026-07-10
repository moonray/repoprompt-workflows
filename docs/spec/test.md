---
title: Test Generation Workflow
issue: none
status: implemented
---

# Test Generation Workflow

## Problem

The Test workflow defines how agents turn a scenario-based spec into repository-native tests, but the workflow itself has no behavioral spec that future edits can be checked against. Without a stable contract, changes to `.agents/workflows/Test.md` can silently weaken scenario coverage, repository-convention discovery, test quality, or the guardrail that production code is not modified during test generation.

## Goals

1. Generate tests from a provided spec's Given/When/Then scenarios and Proposed Surface.
2. Cover every spec scenario with at least one traceable, meaningful test and avoid adding behavior outside the spec.
3. Stop before test generation when Spec Quality findings make the spec insufficiently contract-level, observable, unambiguous, or surface-complete to test.
4. Discover and follow the repository's existing test framework, runner, layout, naming, fixture, helper, and assertion conventions before writing tests.
5. Apply the shared Test Quality guidance when choosing test layers, fixtures, mocks, and assertion strategy.
6. Prefer the lowest faithful test layer that protects the scenario's observable contract while respecting the repository's existing conventions.
7. Write first-class tests with deterministic setup, realistic fixtures where needed, and exact observable assertions.
8. Verify that generated tests compile, and run them when the feature appears implemented.
7. Report scenario coverage, files and test methods written, validation status, and any unmapped scenarios.

## Non-Goals

- Implement production features or modify production code to make tests pass.
- Replace or redesign the repository's test framework, runner, or fixture architecture.
- Generate tests without a scenario-based spec.
- Guarantee that generated tests pass when the feature has not been implemented yet.
- Maximize coverage metrics or create tests that only restate implementation details.
- Decide the feature's implementation strategy beyond what is necessary to express expected observable behavior in tests.

## Constraints

- The workflow consumes specs from `docs/spec/` or an explicit spec path supplied by the user.
- The source spec must include Given/When/Then scenarios; without scenarios, the workflow stops instead of inventing tests.
- Tests must protect observable behavior from the spec: return values, state changes, side effects, errors, persisted format, emitted output, protocol behavior, or user-visible behavior.
- Tests must use the lowest faithful layer for the risk: unit, service/component, filesystem/database/wire-format integration, adapter/entrypoint, or end-to-end/smoke.
- End-to-end tests are used sparingly for critical journeys and are not the default when a lower layer faithfully covers the scenario.
- Mocks must simplify setup and must not reimplement production filtering, sorting, parsing, routing, permissions, persistence, or other logic under test.
- Fixtures must be minimal, deterministic, privacy-safe, and shaped like real persisted, wire, runtime, UI, or filesystem data when that shape is part of the contract.
- The workflow must not modify production code; if expected production surface is missing, tests may compile-fail and the workflow reports that as implementation work, not a test-authoring reason to change production.
- The repository's existing test conventions override language-specific defaults in the workflow prompt.

## Scenarios

### Scenario: Explicit spec path is read
- **Given** the user invokes the workflow with an explicit spec path
- **When** the workflow begins
- **Then** it reads that spec and uses its scenarios, Proposed Surface, and Constraints as the testing contract

### Scenario: Feature name resolves to a spec
- **Given** the user invokes the workflow with a feature name instead of a path
- **When** a matching spec exists in `docs/spec/`
- **Then** the workflow resolves the feature name to that spec and continues from the resolved file

### Scenario: Missing spec stops the workflow
- **Given** the user invokes the workflow with no resolvable spec path or feature name
- **When** the workflow searches `docs/spec/`
- **Then** it stops without writing tests and reports that a scenario-based spec is required

### Scenario: Spec without scenarios stops the workflow
- **Given** the resolved spec contains no Given/When/Then scenarios
- **When** the workflow completes spec analysis
- **Then** it stops without writing tests and reports that tests cannot be generated without scenarios

### Scenario: Spec surface and constraints are extracted
- **Given** the resolved spec includes scenarios, Proposed Surface entries, and Constraints
- **When** the workflow analyzes the spec
- **Then** it records the tested surfaces, required inputs, expected outputs, edge conditions, and environmental constraints that shape the test design

### Scenario: Spec quality findings stop test generation
- **Given** the resolved spec has contract-level drift, non-observable scenarios, uncovered Proposed Surface elements, ambiguity, redundancy that changes interpretation, or hidden unresolved decisions
- **When** the workflow applies Spec Quality checks before scenario mapping
- **Then** it stops without writing tests and reports the exact spec gaps that must be fixed before test generation

### Scenario: Shared test quality guidance shapes test design
- **Given** the workflow is choosing test layers, fixture strategy, mock boundaries, or assertions for mapped scenarios
- **When** it designs the tests
- **Then** it applies the shared Test Quality criteria so tests protect plausible behavioral risks at the lowest faithful layer with realistic deterministic fixtures and exact observable assertions

### Scenario: Existing test infrastructure is discovered before editing
- **Given** a valid scenario-based spec is available
- **When** the workflow prepares to write tests
- **Then** it identifies the repository's test framework, runner or validation command, test directories, file naming, suite naming, method naming, assertion style, helpers, fixtures, setup and teardown patterns, and representative similar tests before creating or editing test files

### Scenario: Repository conventions override defaults
- **Given** the repository's existing tests use conventions different from the workflow's language-specific examples
- **When** the workflow writes tests
- **Then** the generated tests follow the repository conventions rather than the generic language examples

### Scenario: No test infrastructure produces a bootstrap recommendation
- **Given** the repository has no discoverable test infrastructure
- **When** the workflow finishes discovery
- **Then** it stops broad test generation, recommends an ecosystem-appropriate minimal framework and directory structure, and may write only a minimal bootstrap test if the user has requested setup

### Scenario: Every scenario maps to tests
- **Given** the spec contains one or more scenarios
- **When** the workflow creates the scenario-to-test mapping
- **Then** every scenario is mapped to at least one test method with setup derived from Given, action derived from When, assertions derived from Then, and notes for dependencies or edge cases

### Scenario: Proposed Surface parameters are covered
- **Given** the spec's Proposed Surface lists parameters, endpoints, tools, fields, or return shapes
- **When** the workflow completes the scenario-to-test mapping
- **Then** every listed surface element appears in at least one mapped test or is reported as unmapped because the spec has no scenario covering it

### Scenario: Edge and error cases become dedicated tests
- **Given** the spec scenarios or Constraints identify empty results, missing data, invalid input, boundary values, large sets, cross-scope behavior, or error paths
- **When** the workflow writes tests
- **Then** those cases receive dedicated, independently diagnosable tests unless they are intentionally consolidated into an equivalent table-driven test

### Scenario: Lowest faithful layer is selected
- **Given** a scenario can be tested at multiple layers
- **When** the workflow chooses where to test it
- **Then** it selects the lowest layer that faithfully reproduces the risk and documents any reason for choosing a higher layer such as persisted shape, protocol behavior, adapter routing, UI wiring, or a critical smoke journey

### Scenario: Tests include exact observable assertions
- **Given** the workflow writes a test for a scenario
- **When** the Then outcome is encoded
- **Then** the test asserts exact observable values, state, side effects, errors, emitted output, or persisted/wire format rather than only non-null, field-present, or does-not-crash conditions

### Scenario: Tests remain traceable to scenarios
- **Given** the workflow creates or edits a test file
- **When** each test method is written
- **Then** the test name or nearby comment identifies the covered scenario clearly enough for future maintainers to trace coverage back to the spec

### Scenario: Existing helpers and fixtures are reused
- **Given** existing test helpers, factories, mocks, or fixtures cover the needed setup style
- **When** the workflow writes tests
- **Then** it reuses those conventions instead of inventing a parallel helper or fixture system

### Scenario: Production code is not modified
- **Given** generated tests expose a missing production API, compile error, or failing implementation behavior
- **When** the workflow is running in Test Generation Mode
- **Then** it does not modify production code and instead reports the missing or failing implementation surface separately from test-authoring issues

### Scenario: Placeholder tests are rejected
- **Given** a scenario cannot yet be expressed as a meaningful deterministic test
- **When** the workflow reaches that scenario
- **Then** it leaves no TODO or placeholder test and reports the scenario as unmapped with the specific blocker

### Scenario: Tests compile before runtime evaluation
- **Given** test files have been written
- **When** a compile-only or equivalent validation command is available
- **Then** the workflow runs that validation first and fixes test-authoring compile errors without changing production code

### Scenario: Unimplemented feature may fail runtime tests
- **Given** generated tests compile but the feature under test is not implemented
- **When** runtime tests are run or considered
- **Then** the workflow treats failing contract tests as expected implementation work and reports them without attempting production changes

### Scenario: Implemented feature failures are reported as defects
- **Given** the feature appears implemented and generated tests compile
- **When** the workflow runs the relevant tests
- **Then** failures caused by behavior mismatches are reported as feature defects, while failures caused by test mistakes are fixed in the tests

### Scenario: Completion summary reports coverage and validation
- **Given** the workflow has finished writing and validating tests
- **When** it responds to the user
- **Then** it reports the scenario count, test files created or modified, test method count, covered scenarios, uncovered scenarios with reasons, compile status, runtime status, validation commands run, and any intentionally deferred coverage

## Proposed Surface

### Workflow Invocation

| Parameter | Type | Required | Description |
|---|---:|:---:|---|
| `spec` | string | yes | Spec path or feature name identifying the scenario-based contract to test. |

### Consumed Spec Content

| Field or Section | Required | Description |
|---|:---:|---|
| Spec path | yes | Explicit path, or a file resolved from `docs/spec/`. |
| Scenarios | yes | Given/When/Then scenarios that define required tests. |
| Proposed Surface | yes | Tools, endpoints, parameters, return shapes, fields, or user-visible surfaces to exercise. |
| Constraints | no | Environmental realities that affect test layer, fixture shape, validation, or scope. |

### Shared Spec Quality Gate

| Criterion | Description |
|---|---|
| Contract-level spec | The spec must be free of implementation planning that prevents tests from targeting observable behavior. |
| Testable scenarios | Scenarios must have observable Then outcomes and enough independence to map to tests. |
| Surface coverage | Proposed Surface elements that tests must exercise are covered by scenarios and are not ambiguous. |

### Shared Test Quality Criteria

| Criterion | Description |
|---|---|
| Lowest faithful layer | Tests use the lowest layer that reproduces the scenario's real risk without defaulting to broad end-to-end coverage. |
| Fixture and mock quality | Fixtures are deterministic and realistic where shape matters; mocks simplify setup without recreating production logic. |
| Observable assertions | Assertions check exact values, state, side effects, errors, emitted output, or persisted/wire format rather than weak presence or non-crash checks. |

### Scenario-to-Test Mapping

| Field | Required | Description |
|---|:---:|---|
| `scenario` | yes | Scenario name from the spec. |
| `test_file` | yes | Repository-native test file that will cover the scenario. |
| `test_method` | yes | Test method, function, case, or table row covering the scenario. |
| `setup` | yes | Preconditions and fixtures derived from Given. |
| `action` | yes | Operation under test derived from When. |
| `assertions` | yes | Exact observable outcomes derived from Then. |
| `layer` | yes | Selected test layer and, when not the lowest apparent layer, the reason. |
| `notes` | no | Dependencies, edge cases, blockers, or consolidation details. |

### Generated Test Artifacts

| Artifact | Required content |
|---|---|
| Test files | Repository-native tests following discovered framework, layout, naming, imports, setup, and assertion style. |
| Fixtures or helper edits | Only when consistent with existing conventions and necessary for realistic deterministic setup. |
| Traceability comments or names | Scenario names or equivalent references linking each test back to the spec. |

### Completion Summary

| Field | Description |
|---|---|
| `scenario_count` | Number of scenarios found in the spec. |
| `test_files_created_or_modified` | Paths of generated or edited test files. |
| `test_method_count` | Number of test methods, cases, or table rows written. |
| `covered_scenarios` | Scenarios with at least one mapped test. |
| `uncovered_scenarios` | Scenarios not covered, each with a specific reason. |
| `compile_status` | Compile-only or equivalent validation result, including command used. |
| `runtime_status` | Runtime test result, skipped status, or expected failing-contract status. |
| `deferred_or_omitted_coverage` | Any intentionally deferred, consolidated, smoke-only, or unmapped coverage with rationale. |

## Open Questions

1. **Should the workflow promise end-to-end tests specifically, or repository-native tests at the lowest faithful layer?** The current workflow metadata mentions e2e tests, while the body describes native tests and infrastructure discovery. Recommendation: treat the behavioral contract as repository-native, lowest-faithful-layer test generation, and update workflow metadata in a future change to avoid implying that all generated tests must be e2e.
