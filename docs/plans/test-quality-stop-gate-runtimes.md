# Plan — rpw#2: test-quality Stop gate under Codex/opencode

Issue: moonray/repoprompt-workflows#2 (bug, p2) · Spec: docs/spec/test-quality-reminder.md (exists; lacks runtime-gap coverage — amendment is in-scope work) · base 588676e

## Binding policy (decided, Backlog run 2026-10-16 — gate must not weaken)
Preference ladder, applied per runtime from investigation evidence:
1. **Route the skill marker** if the runtime emits an observable skill-invocation event.
2. **Explicit attestation step** if Stop is routed but skill invocations are not observable (the agent stamps the marker as a deliberate act after applying the checklist).
3. **Documented-unsupported** if Stop is not routed at all.
**Never ship a silent run-only clear** — a degradation that silently drops the skill half is prohibited.

## Ordered tasks

1. **Investigate Codex** (read-only): `.codex/hooks.json` wiring in this repo; codex hook-event model (≥0.148 carries the full hook system per keryx AGENTS.md runtime notes). Determine: (a) does codex emit an event the hook can match for skill/MCP-skill invocation? (b) does it route `Stop`?
2. **Investigate opencode** (read-only): `.opencode/plugins/repoprompt-hooks.mjs` + the opencode plugin API it uses. Same two questions.
3. **Record findings** per runtime in the progress doc with evidence (config lines/docs, not assumptions), then select the ladder rung per runtime.
4. **Implement** in `.agents/hooks/test-quality-reminder.py` + wiring: `scripts/install.sh`, `.codex/hooks.json`, `.opencode/plugins/repoprompt-hooks.mjs`, `.agents/hooks/README.md` table row — per the selected rung. Claude-Code behavior must remain unchanged (regression surface).
5. **Spec amendment:** `docs/spec/test-quality-reminder.md` gains the per-runtime behavior scenarios (follow the file's existing Scenario format); update `docs/spec/test-quality-reminder.conformance.md` for the new scenarios.
6. **Regression tests:** cover the chosen path(s) in the repo's existing hook test suite (discover it; if none exists for this hook, add minimal tests alongside the hook's existing test layout).
7. **Verify:** run the full hook test suite + any repo lint; confirm Claude-Code matcher unchanged.
8. **Commit(s):** `fix(#2): …` on this branch.

## Toolchain
Discover in task 1-2 (python3 for hooks; the repo's test invocation — check scripts/ and existing test files). Record exact commands in the closeout evidence.

## Risk / rollback
Hook-behavior risk contained by regression tests; rollback = revert branch commits. Biggest risk = weakening the Claude-Code path — the tests in task 6 must pin it.

## First safe task
Task 1 (read-only investigation).
