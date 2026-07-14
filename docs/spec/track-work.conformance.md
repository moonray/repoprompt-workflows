# Spec Conformance — Track Work Skill

- **Spec:** `docs/spec/track-work.md` (Track Work Skill)
- **Implementation:** `.agents/skills/track-work/SKILL.md`, `scripts/issue.sh`, and `scripts/place_on_board.sh`
- **Audited:** 2026-07-14
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
| Surface inputs | Conformed | Step 1 request and repo conventions |
| Surface outputs item, links, status, backend | Conformed | Body template; lifecycle; Step 0 diagnostic |

## Coverage proof

- **audited:** Goals 1–5; S-001–S-019; Proposed Surface inputs and outputs; both helper scripts
- **unreconciled:** []

## Notes

The 2026-07-14 re-audit includes executable helpers after adversarial review. Repository identity is explicit, capability failures block without fallback, file mutations are confined/serialized/atomic, the lifecycle is implemented, issue bodies use private staging, and migration is journaled. Label seeding, persistent overrides, migration, and source retirement require authorization; unattended callers block instead of prompting.
