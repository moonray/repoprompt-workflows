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
| Constraints | Table entries verifiable in the runtime roster | Conformed | pre-restart probes 2026-10-10 19:52Z (catalog 516; gap found, reported, tracked) + post-restart probes 21:47–21:48Z (catalog 528, +12; `models.planning_model` = `codex_custom_gpt-6.1-sol-high` via get, matching the ratified pick) | Sol 6.1 and Fable 5.1 verified in catalog; Opus 5.5 verified by invocation — `claude_code__claude-opus-5-5:medium` answered a connectivity ping 2026-10-10. Wired and read back: `models.planning_model` = `codex_custom_gpt-6.1-sol-high`; `models.additional_oracle_models` = [opus-5-5:medium, fable-5-1:high]. Astra id still unconfirmed; roster slot remains (max 4) |
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
  - Constraints: roster verifiability (SKILL.md:26,45; verified post-restart 2026-10-10)
  - Constraints: workspace portability (full-text scan)
  - Constraints: roles-as-interface (SKILL.md:14,35)
  - S-001 .. S-007 (all scenarios)
  - Surface: recommendation table fields
  - Surface: re-evaluation triggers
  - Surface: report block
unreconciled: []
```

Every scenario, Proposed Surface element, and stated constraint was checked; none Diverged or Not-built. The former planning-mirror open question is resolved (post-restart verification above); the remaining Open Question (propose-only settings) is a recorded decision-pending, not a conformance gap.
