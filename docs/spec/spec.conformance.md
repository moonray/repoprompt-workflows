# Spec Conformance — Spec Generation Workflow

- **Spec:** `docs/spec/spec.md` (Spec Generation Workflow)
- **Implementation:** `.agents/workflows/Spec.md`
- **Audited:** 2026-06-25
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the workflow; evidence = workflow phase / principle / Spec File Format.
- **Status:** the one divergence ("no open questions" empty-case) was resolved 2026-06-25 — the Spec File Format now directs an explicit `None.` when no open questions remain.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 produce one draft spec in required structure | Conformed | Phase 6 step 1 (write spec) + Spec File Format (required sections/order) |
| G2 ground in intent, issue context, repo context | Conformed | Phase 1 steps 1–2 + Core Principle 4 ("ground everything in what the repo has") |
| G3 confirm understood intent before writing | Conformed | Phase 1 step 4 (summarize 2–3 sentences, confirm) |
| G4 scenario-driven, non-redundant, testable, no impl planning | Conformed | Phases 3–5 + Anti-Patterns |
| G5 apply Spec Quality inline (no skill auto-load dependency) | Conformed | Core Principles note + Phases 3–5 ("self-contained…regardless of whether the skill is installed") |
| G6 maintain spec index + report counts/open questions | Conformed | Phase 6 steps 2–3 |
| Clear task → draft spec (frontmatter + sections in order) | Conformed | Phase 6 + Spec File Format |
| Referenced issue informs spec | Conformed | Phase 1 step 2 + frontmatter `issue` field |
| Vague task → one clarifying question | Conformed | Phase 1 step 3 |
| Intent confirmed before drafting | Conformed | Phase 1 step 4 |
| Shared spec-quality guidance applied | Conformed | Phases 3–5 + Core Principles |
| Clarification timeout halts (no write/index change) | Conformed | Phase 1 note (`timed_out: true` → halt) |
| Confirmation timeout halts (no write/index change) | Conformed | Phase 1 note (`timed_out: true` → halt) |
| Problem starts from user's pain point | Conformed | Phase 2 step 1 + Spec File Format (Problem) |
| Goals map to scenarios | Conformed | Phase 4 Gap step 1 |
| Proposed surface is testable | Conformed | Phase 4 Gap step 2 |
| Edge cases covered | Conformed | Phase 2 step 5 + Phase 4 step 4 |
| Redundant material removed | Conformed | Phase 3 Redundancy Check + Spec File Format ("do not add sections") |
| Implementation planning excluded | Conformed | Core Principle 1 + Anti-Patterns |
| Open questions explicit (numbered + recommendation) | Conformed | Spec File Format (Open Questions) + Phase 2 step 7 |
| No unresolved questions → "no open questions" statement | Conformed | Spec File Format now directs: if none remain, state `None.` explicitly (do not omit the section) |
| Spec index maintained (name, issue, draft row) | Conformed | Phase 6 step 2 |
| Completion summary (scenarios/tools/open questions) | Conformed | Phase 6 step 3 |
| Input: `task` parameter | Conformed | workflow header `Task: $ARGUMENTS` |
| Surface: Generated Spec Document fields (path/title/issue/status/H1/sections) | Conformed | Spec File Format |
| Surface: Shared Quality Criteria (contract-level/scenario/redundancy-gap-ambiguity) | Conformed | Phases 3–5 + Core Principles |
| Surface: Completion Summary (scenario_count/tools_or_endpoints_count/open_questions) | Conformed | Phase 6 step 3 |

## Coverage proof

- **audited:** Goals 1–6; all 17 scenarios; Proposed Surface (Workflow Invocation `task`; Generated Spec Document fields; Shared Quality Criteria; Completion Summary fields)
- **unreconciled:** []

## Disposition

Resolved (2026-06-25): the Spec File Format's Open Questions section now directs that when no open questions remain, the section states `None.` explicitly rather than being omitted — matching the spec contract and the rest of the `docs/spec/` set.
