- Preserve orchestrator context by delegating task-local exploration, test authoring, implementation, debugging, review, and refactor work while consuming compact evidence reports.
9. Support hands-off, unattended execution under an orchestrator by accepting an optional authorization scope and routing user-facing decisions back to the orchestrator, without changing standalone behavior.
title: Loop Workflow
issue: none
status: implemented
---

# Loop Workflow

## Problem

Loop is a delegation-heavy orchestrator that turns a Spec + Deep Plan into reviewed, tested code. Today it lives only as an operational workflow prompt that mixes the behavioral contract (what gates it enforces, what artifacts it produces, when it escapes) with implementation mechanics (which tool, which file path, which agent model). Because the contract is not separated from the mechanism, improvements discovered during use have no canonical home: this session found that Loop's final review can pass while missing live spec↔implementation value drift, and that Loop has no path for verifying already-implemented work after a rebase. A stable contract is needed so future changes are made against what Loop guarantees, independent of how each phase is realized.

## Goals

1. Define Loop's contract — gates, artifacts, escape conditions — independent of mechanism, as the single source of truth.
2. Guarantee no implementation begins until Spec + Plan pass deterministic and independent readiness checks using the shared `spec-plan-readiness` criteria.
3. Guarantee every task is contract-driven: a Spec scenario becomes a failing test before any production change, and green is reached before review.
4. Guarantee a persistent, resumable progress artifact so any run can resume after interruption.
5. Guarantee the final review catches spec↔implementation drift, including value/enum drift on response fields, not only field presence or behavioral claims.
6. Guarantee closeout includes a dry-run documentation sync/audit for changed code so documentation drift, unsupported claims, and contract-doc conflicts are reported before final handoff.
7. Support verifying already-implemented work (e.g., post-rebase audit) without forcing a red→green pass over existing code.
8. Preserve orchestrator context by delegating task-local exploration, test authoring, implementation, debugging, review, and refactor work while consuming compact evidence reports.

## Non-Goals

- Authoring or maintaining the Spec or Deep Plan. Loop consumes them; their creation and upkeep is a separate, referenced process.
- Choosing the specific agent model, delegation tool, file path, or validation lane for each phase — those are plan-level decisions.
- Replacing repo-specific CI or coordinated validation; Loop invokes whatever the repo prescribes.
- Judging the correctness of Spec or Plan content — only their structural readiness.
- Spec/doc maintenance workflows, skills, or slash commands themselves (referenced, not owned — see Open Questions).

## Constraints

- Tests are written at the lowest faithful layer, assert exact observable outcomes, and must not use mocks that recreate production logic or tests that only assert implementation details or coverage counts.
- Implementation, test authoring, review, and refactor are delegated; Loop owns coordination and evidence verification only.
- Loop treats delegated agents and workflows as context firebreaks: task-local details stay with the delegate unless narrow evidence is insufficient for a gate decision.
- The default working location is a non-main worktree; main is used only when explicitly requested.
- Refactor is strictly behavior-preserving and is followed by a re-run of targeted tests.
- A stable finding signature is severity + normalized file path + normalized finding summary + related scenario/task. Repeated P0/P1 findings escalate to a classify-or-stop decision (not another retry) after two failed fix attempts or three review observations with the same signature.
- Spec/Plan authoring and maintenance is a separate process that Loop references by name; Loop's contract stays free of doc-authoring mechanics.

## Scenarios

### Scenario S-001: Readiness gate blocks on unresolved questions
- **Given** the Spec has an unresolved Open Question or a scenario without an observable Then outcome, or the Plan lacks ordered work items, dependency order, validation commands, or task-to-scenario mapping
- **When** Loop begins
- **Then** it stops before creating any test or code and reports the exact blocking gaps

### Scenario S-002: Readiness gate applies shared readiness criteria
- **Given** Loop receives a Spec and Deep Plan before implementation begins
- **When** it evaluates readiness
- **Then** it applies the shared `spec-plan-readiness` criteria for observable scenarios, Proposed Surface completeness, ordered plan tasks, expected affected areas, dependencies, validation, test strategy, risks, rollback notes, task-to-scenario mapping, and spec-plan contradictions

### Scenario S-003: Spec Quality findings block implementation
- **Given** the Spec has contract-level drift, non-observable scenarios, uncovered Proposed Surface elements, ambiguity, redundancy that changes interpretation, or hidden unresolved decisions
- **When** Loop evaluates readiness
- **Then** it stops before creating tests or code and reports the Spec Quality gaps as readiness blockers

### Scenario S-004: Readiness gate proceeds only after independent verdict
- **Given** the Spec and Plan pass all deterministic checks
- **When** Loop requests an independent readiness verdict
- **Then** it proceeds to setup only if the verdict is implementable, mapping each scenario to a recommended test layer and naming a first safe task

### Scenario S-005: Worktree safety by default
- **Given** Loop is about to make changes and the current location is main
- **When** no explicit instruction to use main was given
- **Then** Loop switches to or creates an appropriate non-main worktree before any change

### Scenario S-006: Progress artifact is persistent and resumable
- **Given** a Loop run is in progress or interrupted
- **When** the run is resumed
- **Then** a progress artifact exists with metadata (branch, worktree, phase, current task, review-cycle counts, stable finding signatures), a task ledger, a review/escape ledger, and a validation/resume log sufficient to continue without chat context

### Scenario S-007: Tests precede implementation in implement mode
- **Given** a task derived from a Plan work item and its covering Spec scenario
- **When** Loop works the task
- **Then** a meaningful failing test asserting the scenario's observable outcome is produced and confirmed red before any production code is written

### Scenario S-008: No meaningful red test halts the task
- **Given** a task whose scenario cannot be expressed as a meaningfully failing test
- **When** Loop attempts to generate the red test
- **Then** it stops the task and pushes back for a Spec/Plan correction rather than writing a tautological test

### Scenario S-009: Work is delegated, gates are verified by the orchestrator
- **Given** implementation, review, or refactor work to perform
- **When** Loop advances a task
- **Then** the work is dispatched to a delegated agent/workflow and Loop records verifiable evidence (test results, review output) before advancing

### Scenario S-010: Delegation preserves orchestrator context
- **Given** a task requires task-local file exploration, test authoring, implementation debugging, review analysis, or refactor details
- **When** Loop coordinates the task
- **Then** delegated agents or workflows handle those details in their own contexts and return compact evidence summaries containing the task ID, scenario IDs, files changed or inspected, tests and validation results, review finding signatures, blockers, and recommended next step

### Scenario S-011: Orchestrator reads narrow context only when evidence is insufficient
- **Given** a delegated report lacks enough evidence for Loop to decide whether a gate passed
- **When** Loop needs more detail
- **Then** it asks the delegate for a focused follow-up or reads the narrowest relevant context needed for the gate decision, records why the report was insufficient, what context was read, and which gate decision it enabled, and does not absorb the full task-local working set

### Scenario S-012: Repeated findings escape rather than loop
- **Given** the same stable P0/P1 finding signature across two failed fix attempts or three review observations
- **When** the finding recurs
- **Then** Loop requests a classification (false positive, core issue, or futility) and either documents the false positive, returns a core issue to implementation, or stops — rather than retrying

### Scenario S-013: Refactor preserves behavior
- **Given** a task is green and review-clean
- **When** Loop refactors
- **Then** only behavior-preserving improvements are applied and targeted tests are re-run green; refactor never broadens scope

### Scenario S-014: Final review reconciles emitted values against the spec
- **Given** a task or whole-PR review where a Spec response field enumerates values or fixes a type
- **When** Loop runs the final review
- **Then** an actually emitted value (from a live run or a fixture assertion) is compared against the spec for that field, and a mismatch is reported — not merely that the field exists or that a behavioral claim holds

### Scenario S-015: Verification mode for already-implemented work
- **Given** the implementation for a scenario already exists (e.g., a post-rebase check) with a covering test
- **When** Loop is run over that work
- **Then** it confirms the test passes and records scenario coverage, and does not generate a new failing test or reimplement existing code

### Scenario S-016: Parallelization only when safe
- **Given** multiple candidate tasks
- **When** Loop decides whether to parallelize
- **Then** it parallelizes only when tasks share no expected files, have independent tests/fixtures, have no public-API dependency on each other, and share no build/test lane; otherwise it serializes

### Scenario S-017: Final review covers the whole diff and converts findings to test-backed tasks
- **Given** all task loops are complete
- **When** Loop runs the final review
- **Then** a delegated full-diff review reports stable P0/P1 finding signatures, files inspected, validation evidence, and value-conformance evidence for Spec-enumerated or typed emitted fields; worthwhile findings become follow-up tasks, and each finding has a failing or covering test before it is fixed

### Scenario S-018: Closeout runs repo-appropriate coordinated validation
- **Given** the final review is clean
- **When** Loop closes out
- **Then** it runs the validation the repo prescribes and records the results in the progress artifact before finalizing

### Scenario S-019: Closeout reports documentation drift before handoff
- **Given** implementation changes affect documented behavior, commands, parameters, schemas, or workflows
- **When** Loop closes out
- **Then** it runs a dry-run documentation sync or audit and records affected docs, proposed edits, unsupported claims, and contract conflicts before finalizing

### Scenario S-020: Authorization scope governs git-visible actions; default behavior preserved
- **Given** Loop is invoked, optionally with an authorization scope (`git_scope`, `doc_edits`)
- **When** Loop reaches a git-visible action (push/PR/merge) or a documentation-edit step
- **Then** it performs that action exactly when an explicit scope authorizes it (interactive ask, or orchestrator brief carrying a wizard grant); absent a scope, current behavior holds (separate explicit ask; doc sync stays dry-run). Destructive git is never authorized by any scope.

### Scenario S-021: Oracle-down degraded readiness under orchestrator authorization
- **Given** the oracle is unreachable and Loop is invoked orchestrated with `degraded_ok`
- **When** Loop evaluates readiness
- **Then** it proceeds with the inline deterministic gate authoritative and records degraded mode; standalone Loop with the oracle down stays blocked rather than proceeding ungated

### Scenario S-022: User-testing isolates data and blocks when no browser tool
- **Given** a user-facing change needs user-testing
- **When** Loop runs the user-testing step
- **Then** it runs a real browser against a throwaway/isolated data location (carried by the brief), never the user's real environment data; if no browser tool is reachable the closeout item is blocked with reason; a unit or contract test is never labeled as user-testing

### Scenario S-023: Amendments are acknowledged or declined with evidence, never silently skipped
- **Given** an amendment was requested during an approval
- **When** Loop closes out
- **Then** it records each amendment as applied (with grep/diff evidence) or explicitly declined (with reason); it never silently skips an amendment

### Scenario S-024: Conformance path defaults to canonical unless the invoker marks the spec contended
- **Given** Loop produces the spec-conformance matrix at closeout
- **When** more than one issue targets the same spec
- **Then** it writes the canonical `<spec>.conformance.md` by default, and uses a brief-supplied per-issue path only when the invoker marks the spec contended (Backlog serializes contended specs instead — see Backlog spec S-015)

### Scenario S-025: Orchestrated escalation routes to the orchestrator, never the end-user
- **Given** Loop is invoked orchestrated and reaches a surface that would normally ask the user (dirty worktree, no safe worktree, spec/plan not ready, documentation-edit approval, implementation ambiguity)
- **When** it cannot proceed autonomously
- **Then** it returns a structured blocked/escalation report to the orchestrator and waits for steer; it never surfaces a question to the end-user. Interactive invocations retain today's ask-the-user behavior.

### Scenario S-026: Closeout produces the spec-conformance matrix
- **Given** all task loops are complete and validation is green
- **When** Loop closes out
- **Then** it runs the `spec-conformance` skill and records the matrix path in the progress doc; the loop is not closed until the matrix exists and every Diverged/Not-built item is explicitly accepted with reason

### Scenario S-027: Orchestrated mode completes the authorized git flow
- **Given** Loop runs orchestrated with a `git_scope` covering push/PR/merge
- **When** the implementation is green and review-clean
- **Then** Loop completes the authorized flow (push → PR → merge within scope) rather than stopping at commits; standalone/interactive behavior is unchanged (push/PR/merge still require a separate explicit ask)

### Scenario S-028: Closeout close-keyword on GitHub merge
- **Given** the GitHub backend and a `git_scope` covering merge
- **When** Loop creates/merges the PR
- **Then** the squash-merge subject carries `(#<id>)` and the PR body carries `Closes #<id>`

### Scenario S-029: Repo hard-constraints loaded and non-negotiable
- **Given** the repo declares hard rules (e.g. `CLAUDE.md`/`AGENTS.md`)
- **When** Loop starts
- **Then** it loads them (from the brief's `constraints` field when orchestrated, else directly from the repo) and treats them as non-negotiable, superseding plan/scope preferences on conflict

## Proposed Surface

### Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Spec path | yes | Path to the behavioral contract document. |
| Plan path | yes | Path to the ordered, file-mapped deep plan. |
| Issue / PR / branch / worktree | no | Optional routing hints. |
| Authorization scope | no | `git_scope` + `doc_edits`; absent = today's separate-explicit-ask behavior (S-020). |
| Toolchain | no | Repo-specific test/build commands + env (absolute paths). |
| Oracle status | no | `up\|down` + `degraded_ok`; absent = oracle required (S-021). |
| User-testing target | no | Browser tool + throwaway data location (S-022). |
| Conformance path | no | Override only when the spec is contended (S-024). |
| Escalation principal | no | `orchestrator` routes user-facing decisions to the orchestrator (S-025). |
| Constraints | no | Repo hard-rules from `CLAUDE.md`/`AGENTS.md`; absent = Loop reads them directly (S-029). |

### Gates enforced

| Gate | When | Blocking condition |
|------|------|---------------------|
| Deterministic readiness | Phase 1, before any work | Unresolved open questions; scenarios without observable Then; missing Proposed Surface; Spec Quality findings that make the contract unreliable; plan missing ordered items/dependency order/validation commands/test strategy/task-to-scenario mapping; spec↔plan contradiction. |
| Independent readiness verdict | Phase 1, after deterministic checks | Shared `spec-plan-readiness` verdict or independent oracle verdict is not implementable. |
| Red-before-green | Per task, implement mode | No meaningful failing test confirmed. |
| Repeated-finding escalation | Per task and final review | Same stable signature at the retry/observation threshold. |
| Value conformance | Final review | Spec-enumerated/typed field's emitted value not reconciled. |
| Delegate evidence sufficiency | Per delegated step | Missing required report fields, transcript-style report, unbounded raw logs, broad pasted file contents, or insufficient evidence for a gate decision without focused follow-up or a narrow context read. |
| Coordinated validation | Closeout | Repo-prescribed validation not green. |
| Documentation sync/audit | Closeout | Documentation drift, unsupported claims, or contract conflicts are not reported before final handoff. |

### Shared Readiness Criteria

| Criterion | Description |
|---|---|
| Spec readiness | Open Questions are resolved, scenarios have observable outcomes, user-facing surfaces are specified enough to test and implement, and Spec Quality checks do not find contract-level, scenario, surface, redundancy, ambiguity, or hidden Open Question blockers. |
| Plan readiness | Work items are ordered and include expected affected areas, dependencies, validation commands, test strategy, risks, rollback notes, and task-to-scenario mapping. |
| Spec-plan consistency | Planned behavior, scope, sequencing, surfaces, and validation do not contradict the Spec. |

### Artifacts produced

| Artifact | Required content |
|----------|------------------|
| Progress doc | Structured state block (branch, worktree, phase, current task, review-cycle counts, stable finding signatures); Metadata; Task ledger; Review/escape ledger; Validation/resume log; documentation sync/audit results. |
| Delegated task report | Compact per-task evidence summary: task ID, scenario IDs, files changed or inspected, tests and validation results, review finding signatures, blockers, and recommended next step; excludes full transcripts, exploratory reasoning dumps, unbounded raw logs, and broad pasted file contents. |
| Context exception log | Reason a delegated report was insufficient, focused follow-up requested or narrow context read, file/range or diff slice inspected when applicable, and gate decision enabled by the extra context. |

### Modes

| Mode | Trigger | Behavior |
|------|---------|----------|
| Implement | Implementation does not yet exist | Scenario to failing test to red to implement to green to review to refactor. |
| Verify | Implementation already exists (rebase, audit) | Confirm covering tests pass; record scenario coverage; find spec/plan gaps; do not reimplement. |

## Open Questions

1. **Where does the Spec/Plan authoring and maintenance process live?** Loop references it but does not own it. Recommendation: a dedicated spec authoring skill and plan authoring skill (or a single doc-lifecycle slash command) that Loop references by name, keeping Loop's contract free of doc mechanics.
2. **Should a Spec/Plan open question that contains a recommendation be required to resolve to an implementing task or an explicit waiver before closeout?** Currently a recommendation can be silently absorbed as a documented gap. Recommendation: yes — require an explicit waiver-with-rationale so deferred recommendations are distinguishable from intentional non-goals.
3. **Should Verify mode be selected automatically (by detecting existing implementation) or require an explicit flag?** Recommendation: automatic detection with a logged mode decision, overridable by an explicit input.
