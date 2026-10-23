# Plan — track-work creation-time triage rules (#4)

Derived from `docs/spec/track-work-triage.md` (blob recorded at commit time). Implementation branch: `backlog/4-track-work-triage`. **Route note (Backlog 2026-10-22):** no worktree — serialized branch-in-checkout dispatch per the wizard-authorized route change.

## Ordered tasks

- **T1 — Triage section (first safe task; pure addition).** Author the "Triage (creation-time rules)" section in `.agents/skills/track-work/SKILL.md`, placed after "Step 1 — read repo conventions" / before "Caller mode" (keep the skill's existing voice and formatting). Cover S-001–S-006, S-008: decision routing, draft|backlog entry states, parent links for batch items, priority defaults table, signature-based dedup-before-create (upgrade the existing "Search before you create" step to point at it), atom names with pointer to `.agents/rules/global.md`, explicit "creation-time only" boundary sentence.
- **T2 — config schema block.** Extend the Config schema section with the optional `triage:` block (`priority_defaults`, `entry_state`) per S-007; note in "When to add a config" that a repo drops the block only when it overrides defaults.
- **T3 — spec + conformance.** Update `docs/spec/track-work.md` in place with the triage contract (a Triage section consistent with this spec's scenarios; follow the file's existing format); re-audit `docs/spec/track-work.conformance.md` with a dated row for the new contract (existing rows keep their evidence; only add/re-audit what the triage surface touches).
- **T4 — verify.** Run the spec's grep oracles (a)–(d) and capture outputs; re-read the section for voice/format consistency; confirm no script changes (`git diff --stat` stays inside `.agents/skills/track-work/SKILL.md`, `docs/spec/track-work.md`, `docs/spec/track-work.conformance.md`).
- **T5 — closeout artifacts.** `docs/spec/track-work-triage.conformance.md` (S-001–S-008 + Proposed Surface + Constraints, grep-captured evidence; the keryx-copy divergence row carries the recorded acceptance); spec README index row (added at contract commit). Commit.

## Risks / rollback

- Section bloat: keep the triage section tight (the skill is 302 lines; target ≤40 new lines) — atoms named, not restated.
- Duplication risk with triage-work skill (consumption-time): the boundary sentence (S-008) and a one-line pointer to triage-work prevent overlap; do not copy its rubric.
- Rollback: revert the single implementation commit.

## Toolchain

- Read-only verification: grep oracles pinned in spec Constraints; no test suite applies (skill/spec prose).

## Toolchain note

`git -C /Users/bala/Sites/repoprompt-workflows diff --stat` must show only the three surfaced files (+ closeout artifacts).
