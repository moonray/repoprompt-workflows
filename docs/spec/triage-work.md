# Spec: triage-work — multi-ledger review, cleanup, and ranking

**Status:** Active · **Created:** 2026-10-16 · **Tracking:** #11 · **Skill:** `.agents/skills/triage-work/SKILL.md`

## Context

Teams accumulate tracked work items across several ledgers — per-repo GitHub Issues or committed file backlogs, plus external ledgers a workspace acts on (a client's or upstream's repo). Recurring triage sessions review those items, verify them against current reality, clean the ledger, route what is not agent work, and rank what remains. Today that ritual is improvised session-by-session, and its failure modes are observed and repeatable: scoping to the primary repo only, trusting the last ticket comment instead of current state, forcing gated work into an effort ranking, auto-resolving decisions, items that have outlived the repo's intent lingering because nothing re-asks whether they are still a good idea, and leaving "why is this still open?" unanswered.

The `triage-work` skill contracts the ritual. It is the interactive analyst layer: it discovers via **track-work** (backend-agnostic, multi-repo fan-out), verifies, cleans, routes, ranks, and hands off. It does not implement (the **Backlog** workflow is the execution consumer) and it does not govern item birth (creation-time triage rules are a track-work concern, #4).

Provenance: derived from observed triage sessions across two multi-repo workspaces (2026-07 → 2026-10) — ease-ranked review, cross-ledger cleanup, parallel-safe selection against in-flight work, and comms-grounded verification of external-dependency claims — generalized to repo-independent behavior.

## Goals

1. One repeatable triage ritual over every ledger in scope, replacing per-session improvisation.
2. Ledger mutations are evidence-driven: no close, relabel, or comment happens without fresh ground-truth verification.
3. Every item ends the run with an explicit disposition — closed, cleaned, routed, ranked, or intent-questioned — carrying an autonomy classification, and items that no longer serve the repo's intent are surfaced rather than silently queued.
4. Human authority is preserved: decision items and judgment calls route to the user, never auto-resolved.
5. Output is decision-ready: a default priority rubric (or a requested axis for list outputs), a quick-wins callout, a recommended pick, and a hand-off offer.

## Non-Goals

- Executing any work item — spec, code, or tests (Backlog's job); triage-work only prepares and hands off.
- Creation-time intake triage — what priority/state a newborn item gets (track-work's concern, #4).
- Replacing standing status/briefing reports — triage-work is the periodic deep review those reports feed on, not a scheduler.
- Mail or message triage (a different domain, separately skilled).
- A new ledger, cache, or storage format — every ledger read/write flows through track-work.

## Proposed Surface

| Element | Contract |
|---|---|
| `.agents/skills/triage-work/SKILL.md` | The procedure (trigger, discover, verify, clean, route, rank, record, hand-off). Model-invoked. |
| Ledger operations | All via track-work: per-repo backend selection, `gh`/`issue.sh` binding, re-read at commitment boundaries. No direct ledger writes. |
| Report (chat-delivered) | Per-repo labeled aggregate; ledger diagnostics (backend + capability per repo, gaps reported); verified closures with evidence; taxonomy changes; autonomy-classified ranked list (or requested-axis list) with gated section; decision rollup; quick wins + recommended pick; hand-off offer. |
| Audit-trail comments | Posted on triaged items: what was checked, when, and the verdict — so the next run (or human) sees the evidence, not just the outcome. |

## Scenarios

### Scenario S-001: triage-shaped requests trigger the skill; adjacent requests do not
- **Given** the available-skills listing and a user request
- **When** the request asks to review/triage/prioritize open tracked items, list them by an axis (ease, priority), ask what is open or what to work on next, ask which items are safe alongside in-flight work, or ask to clean up needlessly open items
- **Then** the triage-work skill is loaded and followed; filing one new item (track-work), autonomous execution of the queue (Backlog), and mail/message triage do NOT trigger it

### Scenario S-002: scope fans out to every ledger, cross-ledger included, gaps reported
- **Given** a triage request in a multi-repo workspace
- **When** scope is resolved
- **Then** every workspace repo's ledger is included plus any external ledger the user names or a repo config pins; backend selection runs per repo through track-work (workspaces may mix GitHub and file backends); each repo's items are labeled by repo in the aggregate; an unreachable or missing ledger appears in the report as a stated gap, never a silent omission; only an explicit user narrowing reduces the set

### Scenario S-003: gathering is body-grounded
- **Given** the ledgers in scope
- **When** items are gathered
- **Then** open items are fetched with their full bodies (labels alone are insufficient for disposition), and each repo's label taxonomy dimensions are discovered from that repo's actual labels/config

### Scenario S-004: ground-truth verification precedes any mutation
- **Given** an item whose state is suspicious or decision-relevant (possibly closeable, possibly stale, possibly blocked)
- **When** triage assesses it
- **Then** the item's state is verified against current reality before anything is written — landed-commit ancestry on the default branch, gate/CI history, elapsed time-boxes, live-system or infra checks where the item names a system — and a prior ticket comment or transcript claim is treated as a claim, never as evidence; claims that depend on an external party are grounded in the authoritative communications/record source where one exists, and the verification result (not the prior comment) is what the disposition cites

### Scenario S-005: closures are evidence-verified against the item's own gate
- **Given** an item whose acceptance criteria or close gate appears satisfied
- **When** triage proposes closing it
- **Then** closure happens only after the gate evidence is freshly verified and recorded in the close-out (e.g. landing SHA, green-gate run list, soak evidence, elapsed time-box); the ledger is re-read at the commitment boundary so concurrent closure by another actor is detected and reconciled rather than duplicated

### Scenario S-006: dedup folds the nuance before closing the duplicate
- **Given** two items covering the same scope
- **When** triage treats one as a duplicate
- **Then** any unique detail, acceptance criterion, or open comment in the duplicate is first folded into the canonical item, then the duplicate is closed cross-linking the canonical — never a bare close that loses content

### Scenario S-007: taxonomy repair is applied or flagged, never skipped
- **Given** items with missing or drifted labels (unlabeled type/priority/status, priority no longer matching reality, backlog items actually blocked)
- **When** triage repairs taxonomy
- **Then** clear-cut fixes are applied directly with a comment recording why; fixes that are judgment calls are flagged to the user in the report and not applied until confirmed; after repair every remaining open item carries the repo's required label dimensions

### Scenario S-008: reserved follow-ups are filed; speculative stubs are not
- **Given** a closure whose close-out plan explicitly reserves a follow-up, or future work that has not materialized yet (details expected from an external party)
- **When** triage records it
- **Then** the reserved follow-up is filed as its own tracking item; unmaterialized future work gets a trigger note on the relevant existing item (create-the-item-when-details-arrive) instead of a speculative stub item

### Scenario S-009: every reported item carries an autonomy classification
- **Given** the items surviving cleanup
- **When** the run reports them
- **Then** each carries exactly one of: `autonomous` (an agent can start now), `needs-decision` (a human call is required), `human-only` (the work is human-executed; an agent can at most prepare), `blocked-external` (waiting on an outside party; an agent can chase or prep only) — and only `autonomous` items enter any ranking; the classification is derived from verified state, not assumed from labels

### Scenario S-010: decision items route to a human rollup, never auto-resolved
- **Given** `type:decision` items (or items whose disposition reduces to an unmade human decision)
- **When** triage handles them
- **Then** they appear in a separate human-decision rollup with any verified context that would inform the call, and are never spec'd, implemented, relabeled out of decision type, or closed by triage

### Scenario S-011: the default ranking rubric mirrors the execution consumer
- **Given** autonomous items and no user-requested ranking axis
- **When** the run orders them
- **Then** the order is `type:bug` first, then priority p0 → p1 → p2 → p3, then ease (labeled effort before unlabeled) — the same order the Backlog workflow's Phase 1 uses, so triage output and execution intake never disagree

### Scenario S-012: a requested ease axis separates gated from sized work
- **Given** the user asks for a list/ranking output by ease (or implementation effort)
- **When** the run ranks
- **Then** autonomous items are ordered easiest-first using effort labels grounded by body assessment (label absent → assess from the body and say so), and items that are gated rather than sized — blocked, human-only, time-gated, open-ended design — are listed separately below the ranking, each with its gating reason rather than a forced effort position

### Scenario S-013: a requested parallel-safety axis ranks around in-flight work
- **Given** the user asks what can be tackled while other named/observed work is in flight
- **When** the run ranks
- **Then** it defines the overlap zone (items touching the same files, themes, or physical checkouts as the in-flight work; single-shared-checkout repos count as fully contended for file edits), excludes items already owned by the in-flight sessions, ranks external-system work (no repo edits) as safest, marks cross-cutting coordination points (e.g. production-affecting steps to time around the other session), and lists blocked items as not-tackleable with their blocker

### Scenario S-014: the report is decision-ready and hands off
- **Given** a completed triage pass
- **When** the run reports
- **Then** it presents ledger diagnostics with per-repo backend/capability and stated gaps, verified closures with their evidence, taxonomy changes applied vs flagged, the autonomy-classified ranked list (default rubric or requested axis) with the gated section and decision rollup, a quick-wins callout, one recommended pick (or pairing) with its reasoning, and an offer either to start the pick or hand the cleaned queue to an execution run; triage findings and comms-derived facts are written back as audit-trail comments on the affected items

### Scenario S-015: surviving items are validated against repo intent
- **Given** an item that passes the staleness/closure checks, and the repo's intent anchor — an explicit intent/mission document where one exists, else the repo's stated-purpose docs (README/AGENTS), with whichever source was used named in the report
- **When** triage assesses whether the item is still applicable, still needed, and still a good idea
- **Then** every surviving item carries an intent verdict (aligned / questionable / no-longer-applicable) derived from the item's scope against the anchor's mission and non-goals; questionable or no-longer-applicable items appear in a dedicated report section stating the specific conflict and a recommended resolution (keep with reason, narrow, or close), are excluded from ranking and the recommended pick until the user resolves them, and are never auto-closed by triage

## Traceability

| Goal / Surface | Scenarios |
|---|---|
| G1 repeatable ritual over full scope | S-001, S-002, S-003 |
| G2 evidence-driven mutation | S-004, S-005, S-006 |
| G3 explicit disposition + autonomy | S-007, S-008, S-009, S-015 |
| G4 human authority preserved | S-007 (judgment calls), S-010, S-015 |
| G5 decision-ready output | S-011, S-012, S-013, S-014 |
| skill trigger/exclusions | S-001 |
| ledger-operations surface | S-002, S-005 |
| report surface | S-009, S-014 |
| audit-trail surface | S-004, S-006, S-007, S-014 |
