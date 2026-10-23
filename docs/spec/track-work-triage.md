# track-work creation-time triage rules

**Status:** Active · **Created:** 2026-10-22 · **Tracking:** [#4](https://github.com/moonray/repoprompt-workflows/issues/4) · **Implements:** `.agents/skills/track-work/SKILL.md` (Triage section + config schema), `docs/spec/track-work.md` (in-place update)

## Overview

track-work classifies items at intake (type labels, dedup-by-keyword-search) but has no creation-time **triage policy** — nothing governs the priority a filed finding gets, the state new items enter, or how batch/summary items route. Backlog triages at consumption (Phase 1); this spec contracts the rules governing the moment items are **born**. Design decision (2026-08-21, recorded in the issue): a track-work extension, not a standalone triage skill; the shared triage atoms are canonized in `global.md` and are **named, never restated**.

## Proposed Surface

- `.agents/skills/track-work/SKILL.md` gains a **Triage (creation-time rules)** section covering: decision-type routing, entry states, batch/summary parent linkage, priority-mapping defaults, and signature-based dedup-before-create. One canonical file — the runtime discovery copies (`~/.claude/skills/track-work`, `~/.agents/skills/track-work`) are symlinks, so both update by construction.
- The skill's **Config schema** section gains an optional `triage:` block (per-repo overrides of the priority defaults and entry-state policy; data-only schema documentation).
- `docs/spec/track-work.md` (canonical, this repo) is updated in place with the triage contract; its conformance matrix is re-audited.
- Prose/schema/spec only — no script changes (`scripts/issue.sh`, `place_on_board.sh` untouched).

## Scenarios

- **S-001 decisions route to humans at creation.** The triage rules state that a `type:decision` finding is created for human triage and is never auto-queued or auto-resolved by an agent at creation time (naming the Backlog/rollup consumption convention without duplicating its Phase-1 logic).
- **S-002 entry states are draft|backlog.** The rules state new items enter `status:draft` (needs repro/decision) or `status:backlog` (triaged, acceptance clear) — never born `in-progress`, `review`, or `blocked`; `in-progress` is claimed only by the actor that starts work.
- **S-003 batch/summary items carry a parent link.** Items filed from a batch/summary artifact (e.g. document-skill alignment summaries) enter with a parent/reference link in the body (Source/Detail section) identifying the originating batch item or run — never as free-floating duplicates.
- **S-004 priority defaults by finding kind.** A small deterministic defaults table maps finding kind/work state → default priority (e.g. live-failure bug → p1; process/doc gap → p2/p3; parked idea → p3), overridable per-repo via the `triage:` config block. The table is defaults for creation time — consumption-time triage may re-rank.
- **S-005 signature-based dedup-before-create.** The dedup step upgrades from keyword search to signature matching (normalized finding summary + target path/symbol, per the Review Quality signature atom): before create, search the ledger for the signature; on match, update the existing item (comment/relabel) instead of creating; the skill names the atom rather than restating its definition.
- **S-006 atoms are named, not restated.** The triage section references the global atoms (Stable Identifiers; Review Quality signatures; Verifying Delegated Work; Git Safety) **by name** with a pointer to `.agents/rules/global.md` — no copied definitions.
- **S-007 config override block.** The Config schema documents an optional `triage:` block (e.g. `priority_defaults`, `entry_state`) that overrides the defaults per repo; absent block = built-in defaults.
- **S-008 consumption triage unchanged.** Backlog's Phase-1 consumption triage is untouched — the triage section governs creation only and contains no consumption-time logic (no re-ranking rules, no flight-set language).

## Constraints

- Grep oracles: (a) the Triage section contains `status:draft` and `status:backlog` and does not prescribe any other birth state; (b) the section names `Stable Identifiers` and `Review Quality` and does not copy their definition text; (c) `docs/spec/track-work.md` carries the triage contract and its matrix is re-audited with a dated row; (d) `scripts/` diff is empty.
- Keryx historical copies (`keryxsolutions/docs/spec/track-work*.md`) are **not** updated: per keryxsolutions `docs/spec/README.md` (machinery specs are historical records since keryx#33, canonical lives here), the issue's "both repos" AC (written 2026-08-21, pre-doctrine) is superseded for the keryx half. Disclosed as an accepted Diverged item — principal: Backlog orchestrator (auth rev 1, autonomous), 2026-10-22.

## Non-goals

- No standalone triage skill; no referenced-shared-skill indirection (rejected 2026-08-21).
- No changes to Backlog's Phase-1, triage-work, or any workflow/skill other than track-work's SKILL.md and spec.
- No script/code changes.

## Open questions

None.
