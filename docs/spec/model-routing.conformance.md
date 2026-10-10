---
title: Model Routing Skill — Conformance
issue: 7
spec: model-routing.md
audited: 2026-10-10
---

# Model Routing Skill — Conformance Matrix

Implementation audited: `.agents/skills/model-routing/SKILL.md` (canonical guidance artifact) plus the routing clauses at the oracle call sites in the workflows. Evidence = section/line citations.

## Matrix

| Section | Item | Status | Evidence | Note |
|---|---|---|---|---|
| Constraints | Table entries verifiable in the runtime roster | Diverged (accepted, pending refresh) | catalog probes 2026-10-10 (`app_settings models.planning_model` options, agent-filtered and unfiltered) | newest visible Codex generation GPT-5.6; no gpt-6.x/opus-5.x/astra entries visible; live setting is the unlisted custom id `codex_custom_gpt-6-sol-xhigh`. Ratified models postdate the local catalog — restart RepoPrompt CE to refresh, re-verify, then re-point per spec OQ-1 |
| Constraints | Workspace portability — no repo-specific paths, no live setting values baked in | Conformed | full-text scan of `model-routing/SKILL.md` | names setting keys (`:35`) but no current values; grep for repo paths: 0 matches |
| Constraints | Roles are the stable interface; models are replaceable data | Conformed | `model-routing/SKILL.md:14`, `:35` | call sites reference roles, never model names |
| Scenarios | S-001 Canonical dated block | Conformed | `model-routing/SKILL.md:12–19` | three roles with model/effort/rationale + as-of date on `:14` |
| Scenarios | S-002 Verdicts route to Review & Refine, cross-family | Conformed | `model-routing/SKILL.md:18`, `:24` (cross-family invariant), `:31` (verdict mapping); call sites: `Spec.md` Phase 6, `Backlog.md` §3a gate 2, `Loop.md` Phase 2 step 5 | |
| Scenarios | S-003 Generation routes to Context & Discovery | Conformed | `model-routing/SKILL.md:17`, `:32`, `:35` (`models.planning_model` mirror) | |
| Scenarios | S-004 Escalation bounded to the stuck sub-task | Conformed | `model-routing/SKILL.md:19`, `:25`, `:33`; call sites: `Loop.md` Escape hatches (Repeated P0/P1), `Deep-Review.md` Phase 4 | escalation only at the calling workflow's repeat threshold |
| Scenarios | S-005 Re-evaluation refreshes in place, proposes settings | Conformed | `model-routing/SKILL.md:37–50` | triggers `:37–42`; fresh-evidence + cite-or-label rule `:45–47`; same-change propagation `:49`; propose-only `:50` |
| Scenarios | S-006 Unavailable model reported as defect | Conformed | `model-routing/SKILL.md:26`, `:45` | routing never silently skips a roster mismatch; the invariant fired live on 2026-10-10 — the ratified generation's absence was reported and drove the refresh plan (OQ-1) instead of a silent guess-set |
| Scenarios | S-007 Canonical report block | Conformed | `model-routing/SKILL.md:51–58` | verbatim block template |
| Proposed Surface | Recommendation table fields | Conformed | `model-routing/SKILL.md:16–20` | Role/Model/Effort/Rationale columns; as-of date `:14` |
| Proposed Surface | Re-evaluation triggers | Conformed | `model-routing/SKILL.md:37–42` | all four trigger classes from the spec |
| Proposed Surface | Report block | Conformed | `model-routing/SKILL.md:54–58` | |

## Coverage proof

```yaml
audited:
  - Constraints: roster verifiability (SKILL.md:26,45) — Diverged, accepted pending catalog refresh (see unreconciled)
  - Constraints: workspace portability (full-text scan)
  - Constraints: roles-as-interface (SKILL.md:14,35)
  - S-001 .. S-007 (all scenarios)
  - Surface: recommendation table fields
  - Surface: re-evaluation triggers
  - Surface: report block
unreconciled:
  - item: Constraints — table entries verifiable in the runtime roster
    reason: ratified models (GPT-6.1 Sol, Opus 5.5, GPT-6 Astra) postdate the local RPCE catalog (probes 2026-10-10)
    waiver: accepted as environment lag; resolution recorded in spec OQ-1 (restart → re-verify → re-point); matrix to be refreshed when the roster catches up
```

Every scenario, Proposed Surface element, and stated constraint was checked. One constraint is Diverged with an accepted waiver (roster lag, OQ-1); everything else Conformed. Open Questions 1–2 are recorded decisions-pending, not conformance gaps (the spec's propose-only contract is what OQ-2 asks about changing).
