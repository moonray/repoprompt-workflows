---
name: review-depth
description: Use when deciding how much review effort a change warrants — quick, standard, or deep — picked from the change's size, spread, risk, and blast radius. Reach for it whenever someone asks how thoroughly to review a PR, branch, or diff, or whether a quick pass or a deep review fits a given change. It only sizes the effort — it does not perform the review, choose lenses, or triage findings. An explicit quick/standard/deep choice overrides detection.
---

# Review Depth

## Intent

Pick the cheapest review depth that is still safe for a change, so tokens are not wasted on small changes nor withheld from large or risky ones. Deterministic and auditable. An explicit user choice overrides detection.

## When to use

- A review workflow or agent needs to choose quick vs standard vs deep.
- Before fanning out review shots, to size the shot/lens matrix and decide on adversarial verification.
- Whenever someone asks "how thoroughly should I review this change?"

## Inputs

Required: the change set under review (a git comparison scope), enough to compute the signals below.

Optional: an explicit depth choice (`quick` / `standard` / `deep`) from the user, which overrides detection.

## Signals

Compute from the change — `git numstat` + diff paths + the review map:

| Signal | How measured | Bands |
|---|---|---|
| Size | total lines changed (added + deleted) | S ≤ 150 · M 151–800 · L > 800 |
| Spread | distinct top-level modules/directories touched | 1 · 2–3 · ≥ 4 |
| Severe risk flags | booleans (see below) | count 0 / 1 / ≥ 2 |
| Blast radius | in-repo callers of changed public/exported symbols (from the map) | low (≤ few, one subsystem) · high (many or cross-subsystem) |
| Doc-only | every changed file is documentation/markdown | true / false |

Severe risk flags — the presence of any is significant:

- Persisted data format, schema, migration, or wire-protocol change.
- Authn/authz, session, or secret/credential handling.
- Public API/SDK/contract change: new or changed exported surface, versioned endpoint, CLI flag/argument.

Other risk flags (build/CI/config/IaC, crypto, concurrency primitives, billing logic) raise scrutiny but are not severe for depth-floor purposes.

## Selection rule (deterministic)

```text
1. base    = { S: quick, M: standard, L: deep }[size]
2. severe  = number of severe risk flags present
3. depth   = base
4. if severe >= 1: depth = at least standard            # floor
5. depth   = escalate(depth, severe)                    # each severe flag bumps one level toward deep
6. if blast_radius == high: depth = escalate(depth, 1)
7. if doc_only and severe == 0: depth = quick           # docs don't need a multi-shot review
```

where `escalate(quick, 1) = standard`, `escalate(standard, 1) = deep`, `escalate(deep, _) = deep`.

**Override:** if the user explicitly chose `quick` / `standard` / `deep`, use it and skip steps 1–7. Record that detection was skipped.

## Output

Return the selected depth plus the signals and a one-line rationale, so the choice is auditable:

```text
depth: standard
signals: size M (412 lines) · spread 2 · severe 1 (public API) · blast_radius low · doc_only false
rationale: medium change with a public-API surface flag floors at standard.
```

## Non-goals

- Do not choose lenses, partition zones, or decide verification — those belong to the review workflow.
- Do not run tests or validation.
- Do not override an explicit user choice.
- Budget (`frugal`/`balanced`/`unlimited`) is orthogonal and enforced by the review workflow, not here — it can downgrade deep-mode shot and verification counts but does not change the selected depth.
