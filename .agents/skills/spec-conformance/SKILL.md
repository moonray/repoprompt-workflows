---
name: spec-conformance
description: Use when closing a spec-driven feature/issue or auditing whether an implementation actually matches its spec. Given a spec path, emits a section-by-section conformance matrix mapping every scenario and Proposed Surface element to Conformed (with file:line/test evidence), Diverged (what + why + both sides), or Not-built, plus an audited/unreconciled coverage proof. Distinct from document (doc-vs-code drift) and spec-quality (spec well-formedness) — this is spec-vs-implementation, independent of test pass/fail.
---

# Spec Conformance

## Intent

Prove the implementation conforms to the spec, section by section. Green tests are not proof — they assert code contracts (an element exists, an endpoint returns 200), not that behavior matches the spec's requirements. This skill is the audit that closes that gap and produces the artifact the closeout gate requires.

## When to use

- Before closing a spec-driven issue or feature (the closeout gate requires the matrix).
- When asked "does the implementation match the spec?" or "what diverges from the spec?"
- To produce `docs/spec/<spec>.conformance.md`.

## Inputs

- **spec path** (required): the spec document to audit.
- **implementation scope** (optional): defaults to the repo / working tree.

## Workflow

1. **Enumerate** every auditable item in the spec: each scenario (`S-NNN`), each Proposed Surface element (tool / endpoint / parameter / field / return shape), and each stated value, enum, or constraint.
2. **Locate evidence** for each item in the implementation: a code location (`file:symbol`) or a test that asserts the requirement.
3. **Classify** each item: **Conformed** (evidence matches the requirement) | **Diverged** (evidence conflicts — state both the spec side and the code side) | **Not-built** (no evidence found).
4. **Coverage proof**: emit the `audited` set (every item checked) and the `unreconciled` set (Diverged + Not-built). Each unreconciled item is either to-fix or accepted-with-reason; nothing is silently dropped.

## Output

Write `docs/spec/<spec>.conformance.md` containing the matrix and the coverage proof:

- matrix rows: `{ section, item, status: Conformed|Diverged|Not-built, evidence, note }`
- `audited`: every spec section and item checked
- `unreconciled`: Diverged + Not-built items, each with a disposition (fix | accepted-with-reason)

An empty result is valid only as `{ audited: [...], unreconciled: [] }` — "no divergence" requires positive evidence that the whole spec was checked.

## Non-goals

- Do not fix divergences; report them.
- Do not judge spec well-formedness (`spec-quality`) or doc drift (`document`).
- Do not write tests; do flag where a spec invariant lacks a covering test.
