---
title: Model Routing Skill
issue: 7
status: implemented
---

# Model Routing Skill

## Problem
Oracle consultations during spec, plan, and review work choose models ad hoc: cached-input economics and cross-family diversity are ignored, escalation quietly becomes "redo everything on a stronger model", and whatever picks were made go stale as models, rosters, and pricing change. The ratified Recommended RepoPrompt Architecture needs one canonical home so every oracle call site routes by role and refreshes in one place.

## Goals
1. Keep one dated, canonical Recommended RepoPrompt Architecture mapping each role to model, effort, and rationale.
2. Route oracle consultations by role at the spec/plan/review call sites, with workflows referencing roles rather than model names.
3. Bound escalation to the specific stuck sub-task.
4. Re-evaluate the table on defined triggers, from fresh roster/pricing/benchmark evidence, updating every quoting artifact in the same change.

## Non-Goals
- Executing application code generation, or ranking consumer chat products.
- Benchmark-scraping infrastructure beyond bounded fetches during re-evaluation.
- Silently mutating user-owned runtime settings; `app_settings` changes are proposed, and the user applies them.

## Constraints
- A table entry must name a model verifiably present in the runtime roster at publication time.
- The skill is workspace-portable: no repo-specific paths, and no live setting values baked in (they go stale).
- Roles are the stable interface; model identities are data that re-evaluation may replace.

## Scenarios

### S-001: Canonical dated block
- **Given** an agent needing the current model routing
- **When** the model-routing skill is read
- **Then** it contains one Recommended RepoPrompt Architecture table with three roles (Context & Discovery, Review & Refine, Escalation), each naming model, effort, and rationale, plus an as-of date

### S-002: Verdict consultations route to Review & Refine
- **Given** an agent about to ask the oracle a verdict question (go/no-go readiness, issue clarity, spec cross-check, finding tie-break)
- **When** it selects the oracle model
- **Then** it uses the Review & Refine role's model and effort, whose model family differs from the Context & Discovery role's

### S-003: Generation consultations route to Context & Discovery
- **Given** an agent consulting the oracle to generate or synthesize (draft from a source request, deep plan, discovery synthesis)
- **When** it selects the oracle model
- **Then** it uses the Context & Discovery role's model and effort as published in the current table

### S-004: Escalation is bounded
- **Given** a sub-task has failed repeatedly or an unmet complex constraint has the run stuck
- **When** escalation is considered
- **Then** only that sub-task is re-consulted on an Escalation-role model, the escalation and its reason are recorded, and the rest of the run continues on its routed models

### S-005: Re-evaluation refreshes the table in place
- **Given** any trigger has fired (new major model release, roster change, pricing change, observed drift, or as-of date more than a quarter old when routing is next applied)
- **When** re-evaluation runs
- **Then** the table is rebuilt from roster, pricing (including cached-input), and benchmark evidence gathered fresh — cited, or labeled unverified — the as-of date is bumped, every artifact quoting the block is updated in the same change, and runtime-setting changes are proposed to the user rather than applied

### S-006: Unavailable model is a defect
- **Given** the table names a model
- **When** it is absent from the runtime roster
- **Then** routing does not silently skip it: the mismatch is reported and re-evaluation is triggered

### S-007: Canonical report block
- **Given** a (re-)evaluation completes
- **When** the result is reported
- **Then** the report contains the three-role Recommended RepoPrompt Architecture block with model, effort, and a one-line rationale per role

## Proposed Surface

### Recommendation table
| Field | Description |
|---|---|
| Role | One of Context & Discovery, Review & Refine, Escalation. |
| Model | Model identity as verifiable in the runtime roster. |
| Effort | Effort/reasoning level offered for that model. |
| Rationale | One-line why (economics, cross-family, capability). |
| As-of date | Publication date of the current picks. |

### Re-evaluation triggers
New major model release or roster change; pricing change (especially cached-input); observed quality or cost drift; as-of date more than a quarter old when routing is next applied.

### Report block
The three-role block (role: model (effort) — rationale) produced on every (re-)evaluation.

## Open Questions
1. Effort mismatch on the planning mirror: the ratified block specifies GPT-6.1 Sol at High effort, but the live RPCE `models.planning_model` is `codex_custom_gpt-6-sol-xhigh`. Recommendation: re-point the setting to the High-effort variant — planning consultations are the cache-heavy majority, and xhigh inflates their cost without ratified benefit — or ratify xhigh as deliberate and update the table.
2. Should re-evaluation auto-apply runtime-setting changes when the user has pre-approved the exact keys? Recommendation: no — keep propose-only; settings are user-owned and a proposal diff is cheap to apply.
