---
name: test-quality
description: Use when creating, modifying, reviewing, or deciding whether to add tests, fixtures, mocks, integration tests, end-to-end tests, smoke tests, or test plans in any codebase or language, including regression tests for bug fixes. Guides agents to choose the right test layer, avoid low-value tests, and verify meaningful behavioral oracles.
---

# Test Quality

## Goal

Write tests that protect important behavior, not tests that merely increase coverage or restate implementation details.

A good test should answer:

> If this plausible bug happened, would this test fail for a clear reason?

## Decide before writing

Before adding a test, work through this in order:

1. **Name the behavior and a plausible defect** — a user failure, data loss, protocol or security break, race, persistence error, malformed input, or costly operational failure. If you cannot name a concrete defect, do not add the test.
2. **Search existing coverage** — direct tests and outcome-level assertions that already protect this behavior.
3. **Define an oracle that covers the bug population.** It must distinguish broken from fixed behavior (an exact observable outcome, not "does not crash") and be drawn from the population where the bug actually manifests. Validating a fix only against inputs that *don't* exhibit the bug — e.g. a decoder checked only against rows that already carry the decoded text, when the bug lives in rows that don't — proves nothing about the fix. If no oracle exists for the bug population, say so explicitly; sampling it by eye is investigation, not verification (see Diagnostics vs coverage).
4. **Choose the lowest layer** that faithfully reproduces the risk (see Layer selection).
5. **Decide**: add, consolidate into an existing test, redesign, classify as a diagnostic (see Diagnostics vs coverage), or omit.

For a bug fix, prefer a test that fails against the known-bad behavior before the fix.

## Core rules

1. Test current contracts with plausible user, data, protocol, security, reliability, or operational impact.
2. Prefer the lowest test layer that faithfully reproduces the risk.
3. Do not make everything end-to-end. End-to-end tests are valuable but should be few, stable, and high-signal.
4. Use realistic fixtures where persisted, wire, runtime, UI, or filesystem shape matters.
5. Prefer exact observable outcomes over “does not crash”, “not nil”, or field-presence-only assertions.
6. Consolidate equivalent branch cases into table-driven tests.
7. Avoid mocks that reimplement production logic unless the mock behavior itself is the point.
8. For bug fixes, prove the regression test fails on the current buggy code and reproduces the reported symptom before trusting it.
9. Keep tests deterministic, isolated, and easy to diagnose.
10. For a bug fix, the oracle must cover the **bug population** — the inputs/rows/states where the bug manifests — not just the easy cases where behavior is already correct. A test that passes only on non-bug inputs protects the status quo, not the fix.

## Layer selection

Use the lowest layer that faithfully reproduces the risk:

1. **Unit/core tests**
   - Pure logic, parsing, normalization, reducers, policy decisions, state machines, metadata derivation.
   - Best for exact edge cases and fast regression tests.

2. **Component/service tests**
   - Public service behavior with controlled dependencies.
   - Good for filtering, sorting, grouping, formatting, validation, and error responses.

3. **Filesystem/database/wire-format integration tests**
   - Use when persistence, schema compatibility, migrations, query behavior, or real file layout matters.

4. **Raw real-shape fixtures**
   - Use a few sanitized fixtures when generated fixtures may hide real persisted/wire data drift.
   - Keep them minimal, privacy-safe, and paired with clear expected outcomes.

5. **Provider/adapter/entrypoint tests**
   - Use at least one test through the public integration boundary when argument conversion, schema, routing, serialization, protocol behavior, UI event wiring, or adapter behavior matters.

6. **End-to-end/smoke tests**
   - Use sparingly for critical user journeys.
   - Do not rely on end-to-end tests as the only protection for deterministic logic.
   - Keep smoke checks short, opt-in if they need credentials/network/live services, and clear about prerequisites.

## Trust-boundary focus

Before finalizing what to test, identify the **trust boundaries** the behavior crosses and make sure each one has coverage. A trust boundary is a place where data or control passes between trust levels or external systems:

- **user-input** — untrusted input parsing, validation, sanitization, or parsing of query/path/body/CLI arguments;
- **network** — outbound or inbound HTTP, webhooks, retries, timeouts, partial responses;
- **filesystem** — paths, permissions, temp files, atomic writes, symlinks;
- **secrets** — credentials, tokens, keys, logging and redaction;
- **process-exec** — spawning subprocesses, shell interpolation, argument escaping;
- **database** — transactions, migrations, query safety, constraint handling;
- **auth** / **permissions** — identity, authorization, privilege checks;
- **concurrency** — races, locking, ordering, shared mutable state;
- **external-api** — third-party contracts, rate limits, downtime, failure modes;
- **serialization** — encode/decode of untrusted or persisted data.

Behavior crossing `secrets`, `auth`, `permissions`, `user-input`, `serialization`, or `concurrency` boundaries carries higher blast radius. Prefer exact-outcome tests at the lowest faithful layer, and do not let a missing test leave a boundary uncovered. When it aids diagnosis, tag the test with the boundary it protects.

## Diagnostics vs coverage

A benchmark, performance probe, or exploratory harness without an acceptance threshold is a **diagnostic**, not behavioral coverage — it informs investigation but does not protect a contract. Commit it as a diagnostic (clearly labeled, with an entry point and cleanup) rather than counting it as a passing test. Promote it to coverage only when it has a concrete pass/fail oracle.

## Fixture guidance

- Treat committed fixtures as immutable and read-only. Tests that mutate fixture data (write tags, edit files, transform records) operate on copies in a temp directory — destructive tests copy; they never overwrite the committed source.
- Use generated fixtures for readability and precise edge cases.
- Use raw fixtures for compatibility with persisted, external, or wire-format data.
- Do not check in large, private, or noisy production artifacts.
- Sanitize secrets, personal data, proprietary content, absolute paths, tokens, credentials, and unrelated payloads.
- Prefer small fixtures that preserve only fields needed to reproduce the contract.
- If a fixture encodes a historical bug, document the bug and the expected observable behavior in the test name or comments.

## Mock guidance

Mocks should simplify setup, not recreate the implementation under test.

Avoid mocks that duplicate production filtering, sorting, parsing, permission, persistence, or routing logic. If that logic matters, test it directly or use an integration fixture at the appropriate layer.

## Avoid

Avoid adding tests that are mainly:

- non-nil checks;
- field-presence checks without meaningful values;
- implementation-detail restatements;
- one test per trivial branch;
- broad omnibus end-to-end tests with unclear failure causes;
- mocks that duplicate production logic;
- coverage-driven tests with no named failure mode;
- arbitrary sleeps or timing assumptions;
- tests requiring network, credentials, local user state, or wall-clock dates unless explicitly classified as smoke/diagnostic.

## Review checklist

Before keeping a test, ask:

1. What behavior contract does this protect?
2. What realistic bug would make it fail?
3. Is this the lowest faithful layer?
4. Does it assert an exact observable outcome, state, side effect, error, or wire/persisted format?
5. Is it deterministic and isolated?
6. Is it redundant with stronger coverage elsewhere?
7. Would a future maintainer understand the fixture and expected result?
8. If this is a bug fix, does the oracle cover the bug population (where the bug manifests), not just cases that already work?

If the answer is weak, consolidate, move to a lower layer, convert to a smoke/diagnostic, or delete it.

## Commit gate

Commit a test only when it:

- protects a current contract with plausible impact;
- fails for a meaningful defect and asserts an exact observable outcome (value, state, error, side effect, cleanup, wire format, or bounded performance);
- adds distinct coverage at the lowest faithful layer;
- is deterministic, isolated, failure-focused, and maintainable relative to the risk.

Otherwise consolidate, redesign, classify as a diagnostic, or omit it.

## Reporting

When summarizing test work, state:

- the protected contract and plausible risk;
- the chosen layer and why;
- any raw or generated fixture strategy;
- validation commands run;
- coverage intentionally omitted, consolidated, moved to smoke/diagnostics, or deferred.
