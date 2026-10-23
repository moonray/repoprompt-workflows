# Spec Conformance — track-work creation-time triage rules

- **Spec:** `docs/spec/track-work-triage.md` (blob `21614fc176d4ac43a27687fbf3b841cb38340303` @ `c0687fc`)
- **Implementation:** `.agents/skills/track-work/SKILL.md` (Triage section, Config schema `triage:` block, step-2 upgrade), `docs/spec/track-work.md`, `docs/spec/track-work.conformance.md`
- **Audited:** 2026-10-22 (Loop rpw4 / epoch L4-E1, issue moonray/repoprompt-workflows#4)
- **Method:** grep oracles (a)–(d) pinned in spec Constraints + verbatim section reading (prose repo — no test suite); outputs captured verbatim in `docs/progress/backlog-4-loop.md`

## Matrix

| Section | Item | Status | Evidence | Note |
|---|---|---|---|---|
| Overview | extension-not-standalone; atoms named never restated | Conformed | SKILL.md:134–150 (section lives inside track-work); :136 (atom discipline) | 2026-08-21 design decision honored |
| Proposed Surface | Triage section (decision routing, entry states, parent linkage, priority defaults, signature dedup) | Conformed | SKILL.md:134–150, placed between "When to add a config" and "Caller mode"; all five contents present | One canonical file: `~/.claude/skills/track-work` and `~/.agents/skills/track-work` observed as symlinks to this repo's copy (2026-10-22) |
| Proposed Surface | Config schema `triage:` block | Conformed | SKILL.md:88–90 (`priority_defaults`, `entry_state`) + "When to add a config" row SKILL.md:120 | Data-only schema documentation; "absent = built-in defaults" stated inline |
| Proposed Surface | `docs/spec/track-work.md` updated in place + matrix re-audited | Conformed | docs/spec/track-work.md:21 (G7), :36 (constraint), :160–195 (S-025–S-032); track-work.conformance.md `Audited: 2026-10-22` + dated rows | Scenarios follow the file's Given/When/Then idiom; IDs continue after S-024 (no renumbering) |
| Proposed Surface | no script changes | Conformed | `git diff --stat -- scripts/` = 0 lines (oracle d) | diff confined to the three surfaced files |
| S-001 | decisions route to humans at creation | Conformed | SKILL.md:138 — created for human triage, never auto-queued/auto-resolved at creation | names the Backlog/rollup convention without Phase-1 logic |
| S-002 | entry states draft\|backlog | Conformed | SKILL.md:139; oracle (a): `status:draft` ×1, `status:backlog` ×1 in section; other states appear only as negations ("Nothing is born `in-progress`, `review`, or `blocked`") | "review" at :150 is "review signature", not a birth state |
| S-003 | batch/summary items carry a parent link | Conformed | SKILL.md:140 — Source/Detail link to the originating batch item or run | never a free-floating duplicate |
| S-004 | priority defaults by finding kind | Conformed | SKILL.md:141–148 (live-failure bug → p1; gap blocking active work → p2 / cosmetic → p3; parked idea → p3) + override via `triage:` block | creation-time defaults; consumption triage may re-rank (stated) |
| S-005 | signature-based dedup-before-create | Conformed | SKILL.md:150 (search ledger for the review signature; match → update-not-create) + step 2 upgraded at SKILL.md:183 | atom named, not restated |
| S-006 | atoms named, not restated | Conformed | SKILL.md:136 — Stable Identifiers, Review Quality, Verifying Delegated Work, Git Safety + `.agents/rules/global.md` pointer; anti-copy grep: zero definition fragments ("severity + normalized", "normalized finding summary") in SKILL.md / track-work.md | oracle (b) |
| S-007 | config override block | Conformed | SKILL.md:88–90 + :120 | `entry_state` inline comment constrains to draft\|backlog — preserves the S-002 invariant through overrides |
| S-008 | consumption triage unchanged | Conformed | SKILL.md:136 boundary sentence (Backlog Phase 1 + `triage-work` keep consumption); section contains no re-ranking/flight-set language (verbatim read); Backlog workflow and triage-work skill untouched by the diff | — |
| Constraints | (a) birth-state grep oracle | Conformed | captured output: 1/1 counts; other-state mentions are negations only | see progress doc T4 entry |
| Constraints | (b) atom-name grep oracle | Conformed | captured output: four atom names + pointer present; no copied definitions | see progress doc T4 entry |
| Constraints | (c) canonical spec carries contract + dated matrix row | Conformed | 8 new scenario headings in track-work.md; `Audited: 2026-10-22`; 12 dated mentions in its matrix | — |
| Constraints | (d) `scripts/` diff empty | Conformed | 0 lines | — |
| Constraints | keryx historical copies not updated | Diverged (accepted) vs issue #4's original both-repos AC | this loop's writes confined to repoprompt-workflows (git status: three modified files + progress doc); keryxsolutions untouched | Accepted divergence: keryx#33 machinery-historical doctrine (keryxsolutions `docs/spec/README.md` — machinery specs are historical records, canonical lives here) supersedes the issue's 2026-08-21 pre-doctrine AC. Principal: Backlog orchestrator · auth_revision 1 · 2026-10-22. Conforms to the ratified spec text, which explicitly excludes the keryx half |
| Non-goals | no standalone triage skill / no shared-skill indirection | Conformed | no new skill dir in the diff; extension lives in track-work's SKILL.md | — |
| Non-goals | no changes to Backlog Phase-1, triage-work, or any other workflow/skill | Conformed | diff touches only track-work SKILL.md + docs/spec/track-work.md + its matrix | — |
| Non-goals | no script/code changes | Conformed | oracle (d) | — |

## Coverage proof

- **audited:** Overview discipline; Proposed Surface bullets 1–4; S-001–S-008; Constraints (a)–(d); the keryx-copies constraint; Non-goals 1–3
- **unreconciled:** one item — keryx-copy AC divergence, disposition **accepted-with-reason** (principal: Backlog orchestrator, auth_revision 1, 2026-10-22; rationale: keryx#33 machinery-historical doctrine supersedes the issue's both-repos AC; the ratified spec Constraints record the same acceptance). No other Diverged or Not-built items.

## Notes

Audited under Loop rpw4 / epoch L4-E1 (orchestrated). Verification lane: the spec's pinned grep oracles plus verbatim section reading; grep outputs are captured verbatim in `docs/progress/backlog-4-loop.md` (Validation log, 2026-10-22 T4 entry). Out of scope and disclosed: `docs/spec/track-work.conformance.md` carried no rows for G6/S-024 **before** this change — a pre-existing gap disclosed there, not audited here.
