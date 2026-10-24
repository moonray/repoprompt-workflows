# Spec Conformance — Track Work Skill

- **Spec:** `docs/spec/track-work.md` (Track Work Skill)
- **Implementation:** `.agents/skills/track-work/SKILL.md`, `scripts/issue.sh`, and `scripts/place_on_board.sh`
- **Audited:** 2026-10-22
- **Method:** each goal, stable scenario, and Proposed Surface element mapped to the skill; evidence names the implementing section.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 one work item per unit in one place | Conformed | Intent; Step 0 prevents capability failure from creating a second ledger |
| G2 deterministic backend identity and repo taxonomy | Conformed | Step 0 selects override/origin identity before capability; Step 1 and GitHub step 0 govern taxonomy |
| G3 entry gate before any work | Conformed | Intent entry-gate statement; GitHub and file workflows |
| G4 link detail rather than duplicate narrative | Conformed | GitHub step 4; issue body template |
| G5 lifecycle; close means landed on default | Conformed | Status lifecycle; Closing |
| S-001 backend follows durable repository identity | Conformed | Step 0 selection order: confirmed override, GitHub origin, file identity |
| S-002 GitHub capability failure stops | Conformed | Step 0 capability probes and stop-before-write rule |
| S-003 disabled Issues requires explicit choice | Conformed | Step 0 treats `hasIssuesEnabled=false` as blocked and requires confirmed override |
| S-004 conventions and GitHub labels discovered | Conformed | Step 1; `gh label list` authority |
| S-005 tracking item precedes work | Conformed | Intent entry gate; Do/Don't |
| S-006 search before create | Conformed | GitHub step 2 |
| S-007 label cardinality without surprise mutation | Conformed | GitHub step 0 requires showing labels and confirmation; step 3 applies cardinality |
| S-008 detail files linked, not duplicated | Conformed | GitHub step 4; body template |
| S-009 file items use immutable IDs in committed backlog | Conformed | File backend workflow |
| S-010 close means landed on default | Conformed | Closing |
| S-011 secrets and local paths redacted | Conformed | Privacy / redaction before filing |
| S-012 configured optional GitHub features | Conformed | GitHub step 5; persona handling |
| S-013 backend selection observable | Conformed | Step 0 requires compact backend, selected-by, and capability diagnostic; forbids invented historical causes |
| S-014 migration journaled and recoverable | Conformed | Ledger migration requires a pre-mutation external journal, source revisions, idempotency markers, row-level read-back, resumability, and separate retirement confirmation |
| S-015 GitHub operations bound to canonical repo | Conformed | Step 0 normalizes exact origin forms; every example uses `-R "$REPO"`; Project helper requires and verifies canonical issue URL |
| S-016 file operations confined/serialized/atomic | Conformed | `issue.sh` validates IDs/scalars/path, rejects symlinks, locks mutations, and atomically renames same-directory temporary files; `scripts/test_issue.sh` covers traversal, invalid input, lifecycle, creation, and index integrity |
| S-017 full lifecycle on both backends | Conformed | `issue.sh status/block/unblock/close/reopen`; open means every non-closed state; Closing requires landed evidence and read-back |
| S-018 private isolated body staging | Conformed | GitHub step 3 uses `umask 077`, `mktemp`, cleanup trap, redaction-before-write, and repository-bound read-back |
| S-019 unattended callers never prompt | Conformed | Caller mode section; Backlog invokes noninteractive and collects predictable taxonomy approval in its sole wizard |
| S-020 Tracked means explicitly owned | Conformed | `.agents/skills/track-work/SKILL.md:305` |
| S-021 Ledger rereads at commitment boundaries | Conformed | `.agents/skills/track-work/SKILL.md:310` |
| S-022 Mitigated is not fixed | Conformed | `.agents/skills/track-work/SKILL.md:311` |
| S-023 Local personal exposure requires confirmation | Conformed | `.agents/skills/track-work/SKILL.md:312` |
| G7 creation-time triage baseline | Conformed | Triage (creation-time rules) section: entry states, priority defaults, decision routing, signature dedup (added 2026-10-22) |
| S-025 decisions route to humans at creation | Conformed | Triage — "Decisions route to humans" bullet (added 2026-10-22) |
| S-026 birth states draft/backlog only | Conformed | Triage — "Birth states" bullet: other states appear only as negations; in-progress claimed by the starting actor (added 2026-10-22) |
| S-027 batch items carry parent link | Conformed | Triage — "Batch/summary items carry a parent link" bullet: Source/Detail link (added 2026-10-22) |
| S-028 priority defaults by finding kind | Conformed | Triage — priority defaults table + `triage.priority_defaults` config override (added 2026-10-22) |
| S-029 signature dedup before create | Conformed | Triage — "Dedup by signature before create" bullet; GitHub step 2 search upgraded to the review signature (added 2026-10-22) |
| S-030 atoms named not restated | Conformed | Triage intro names the four atoms with the `.agents/rules/global.md` pointer; no definition text copied (added 2026-10-22) |
| S-031 per-repo triage config override | Conformed | Config schema `triage:` block (`priority_defaults`, `entry_state` constrained to draft|backlog); "When to add a config" `triage` row (added 2026-10-22) |
| S-032 consumption triage unchanged | Conformed | Triage boundary sentence names Backlog Phase 1 + triage-work; section contains no consumption-time logic (added 2026-10-22) |
| Surface inputs | Conformed | Step 1 request and repo conventions |
| Surface outputs item, links, status, backend | Conformed | Body template; lifecycle; Step 0 diagnostic |

## Coverage proof

- **audited:** Goals 1–5, 7; S-001–S-023; S-025–S-032; Proposed Surface inputs and outputs; both helper scripts
(G7 and S-025–S-032 added 2026-10-22 together with the skill's Triage section; earlier scope unchanged from the prior re-audit. Pre-existing gap, disclosed not audited: the spec carries G6 and S-024 but the matrix has no rows for them — they predate this change and sit outside its surface, per plan scope)
- **unreconciled:** []

Scope disclosure (2026-10-23): the spec gained G8 and S-033–S-040 (CLI adapter, #1) after this audit; implementation is in progress (`scripts/tw.py`, T2–T3 landed locally) and the CLI rows land here at T7 closeout per `docs/plans/track-work-cli.md`. Until then this matrix covers the skill surface only, as audited 2026-10-22.

## Notes

The 2026-07-14 re-audit includes executable helpers after adversarial review. Repository identity is explicit, capability failures block without fallback, file mutations are confined/serialized/atomic, the lifecycle is implemented, issue bodies use private staging, and migration is journaled. Label seeding, persistent overrides, migration, and source retirement require authorization; unattended callers block instead of prompting.

The 2026-10-22 re-audit adds the creation-time Triage contract (G7; S-025–S-032), implemented as the skill's "Triage (creation-time rules)" section, the Config schema `triage:` block, and the upgraded search-before-create step; the shared atoms are named per `.agents/rules/global.md`, never restated. The G6/S-024 matrix gap predates this change and is disclosed above, not silently repaired.
