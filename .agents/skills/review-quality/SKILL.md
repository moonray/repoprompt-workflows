---
name: review-quality
description: Use when producing, consuming, triaging, or revalidating code-review findings — review artifacts, P0/P1 findings, fix loops, and "is this finding real or fixed?" decisions, in any repo. Enforces structured evidence, prompt-grounding, a revalidation gate that refuses model-only "fixed", and stable-signature triage/dedup/rerank. This governs findings you already have — it does not discover them or size the review.
---

# Review Quality

## Intent

Make review findings precise, grounded, traceable, and honestly closable. A good finding names a real defect, points at exact evidence in the reviewed code, and is marked fixed only when the defect is gone *and* the targeted checks pass.

## When to use

Use when an agent is:

- producing a code-review artifact (findings on a diff, task, or feature);
- consuming findings to decide what to fix;
- triaging, deduplicating, or prioritizing findings;
- re-checking whether a finding is still open after a fix;
- coordinating a review/fix loop; the Loop workflow carries its own inline copy of this discipline.

## Inputs

Required: a review scope — the diff, task, or files under review — and the findings (or a request to produce them).

Optional: the validation commands available for the changed behavior (tests/lint/build).

## Core rules

1. **Structured evidence.** Every finding carries `path`, `startLine`/`endLine`, `symbol`, and a `quote` of the offending code. A finding without resolvable evidence is invalid.
2. **Prompt-grounded.** Evidence must reference files actually in the review scope. Drop a finding whose `path`/line range does not resolve, but keep valid sibling findings — one bad finding does not sink the batch.
3. **Scope proof.** A review must report what it `inspected` (files/symbols covered). An empty finding set is valid only as `{ findings: [], inspected: [...] }`. "No findings" without `inspected` is not a pass.
4. **Revalidation gate.** A finding is `fixed` only when a fresh review no longer finds it *and* the targeted validation commands (tests/lint/build for the changed behavior) pass; record the command results. If validation cannot run because of missing infrastructure or environment, the status is `blocked` or `uncertain`, never `fixed`. Manual confirmation or model opinion alone does not close a finding.
5. **Stable signatures.** Each finding carries a signature = severity + normalized file path + normalized finding summary + related scenario/task ID. Use it to detect repeats and dedup.
6. **Triage before acting.** Dedup identical signatures; rerank survivors by severity, confidence, reachability, test coverage, and patchability. After two failed fix attempts or three review observations of the same signature, classify it `false_positive`, `core_issue`, or `futility` rather than looping.

## Non-goals

- Do not write or apply fixes; this skill judges findings. The Loop workflow coordinates fixing.
- Do not replace a repo's own review tooling when it is responsible for emitting findings.
- Do not grade spec or test quality; use [`spec-quality`](../spec-quality/SKILL.md) and [`test-quality`](../test-quality/SKILL.md) for those.

## Output

When reporting on findings, state: the findings with evidence and signatures; the `inspected` scope; any dropped findings and why; the validation commands and results used for any `fixed` status; and any `blocked`/`uncertain` items with their blockage.
