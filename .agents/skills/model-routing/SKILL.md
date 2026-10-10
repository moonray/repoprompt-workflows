---
name: model-routing
description: Use when choosing an oracle model or effort level for spec, plan, or review consultations (ask_oracle, context_builder, RPCE models.* settings), or when re-evaluating the Recommended RepoPrompt Architecture after a new model release, roster change, or pricing change. Maintains the canonical role→model routing table and its refresh discipline.
---

# Model Routing

## Recommended RepoPrompt Architecture

Canonical as of 2026-10-10 (user-ratified; last re-evaluated 2026-10-10). Roles are the stable interface; models are data that re-evaluation replaces.

| Role | Consultations | Model | Effort | Why |
|---|---|---|---|---|
| Context & Discovery | repo analysis, spec/plan generation, context-heavy discovery and drafting | GPT-6.1 Sol | high | Cheapest deep cache reads (~$0.10/M cached input). RPCE planning re-reads large context prefixes, so cached-input price dominates run cost. |
| Review & Refine | cross-checking specs/plans, readiness and clarity verdicts, finding tie-breaks | Claude Opus 5.5 | medium | Communicates clearly and reliably catches logical gaps in long documents. Different model family than the drafter, so blind spots don't compound. |
| Escalation | one stuck sub-task after repeated failed attempts (fix loop, unmet complex constraint) | GPT-6 Astra, or Claude Fable 5.1 | low–medium, or high | Strongest raw problem-solving, spent only on the stuck piece. |

Invariants:

- **Cache-first economics.** Cached-input price, not nominal input price, is the primary cost criterion for the Context & Discovery role.
- **Cross-family review.** The Review & Refine model comes from a different model family than the Context & Discovery model.
- **Bounded escalation.** Escalate only the specific stuck sub-task — never re-run the whole task on a stronger model — and record what was escalated and why.
- **Availability is part of correctness.** A table entry naming a model absent from the runtime roster is a defect: verify against the roster before routing or publishing (RPCE: `app_settings` `models.*` options, `agent_manage` `list_agents`).

## Applying the routing

Route by consultation type, not by mode name:

- **Verdicts and critiques** — go/no-go readiness, issue clarity, spec cross-check, finding classification, tie-breaks → Review & Refine.
- **Generation** — drafting from a source request, deep-plan production, discovery synthesis → Context & Discovery.
- **Stuck twice on the same sub-task** → Escalation, at the repeat threshold the calling workflow already defines.

RPCE wiring: `models.planning_model` mirrors Context & Discovery; `models.additional_oracle_models` carries the Review & Escalation picks; `ask_oracle`'s model override takes the specific model id. Workflows and skills reference roles, not model names, so a re-evaluation rewrites this one table and no call sites.

## Re-evaluation

Re-evaluate when any trigger fires:

- a new major model release in any family, or a roster change in the runtime;
- a pricing change, especially cached-input price;
- observed quality or cost drift against the current picks;
- the as-of date is more than a quarter old the next time routing is applied.

Procedure:

1. Verify the roster first — recommend only models the runtime actually offers, at effort levels that exist for them.
2. Gather fresh published pricing (input, output, cached-input) for candidates. Cite what you fetched; never quote remembered prices as current.
3. Gather current benchmark signal for long-context/agentic coding and instruction adherence — e.g. repoprompt.com/bench (JS-rendered; fetch via browser automation or search when a plain fetch returns a shell) and public SWE/agentic leaderboards. Label anything you could not verify as unverified.
4. Apply the invariants: cache-first for Context & Discovery, cross-family for Review & Refine, strongest raw capability for Escalation.
5. Rewrite the table, bump the as-of date, and update every artifact quoting the block in the same change (this file is canonical; call sites quote roles only).
6. Propose, do not silently apply, changes to user-owned runtime settings — surface the exact `app_settings` keys and values.
7. Report the result in the canonical block format:

```text
Recommended RepoPrompt Architecture
- Context & Discovery: <model> (<effort>) — <one-line why>
- Review & Refine: <model> (<effort>) — <one-line why>
- Escalation: <model> (<effort>) — <one-line why>
```
