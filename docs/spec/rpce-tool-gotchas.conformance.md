---
title: RPCE Tool Gotchas Skill — Conformance
issue: none
spec: rpce-tool-gotchas.md
audited: 2026-10-10
---

# RPCE Tool Gotchas Skill — Conformance Matrix

Implementation audited: `.agents/skills/rpce-tool-gotchas/SKILL.md` (guidance artifact; evidence = section/line citations), verified present on disk and symlinked into both runtime discovery dirs (`~/.claude/skills/`, `~/.agents/skills/`).

## Matrix

| Section | Item | Status | Evidence | Note |
|---|---|---|---|---|
| Goals | G1–G2 proactive trigger + Bash-first routing | Conformed | `SKILL.md:2–4` (description), `SKILL.md:10–14` | description demands proactive triggering ("not only after errors"); §1 Do-rule names heredoc/anchored-python with read-back |
| Goals | G3 boundary error ≠ missing file | Conformed | `SKILL.md:14` | "the failure reads as 'file does not exist' and invites recreating content that was never lost, or losing content that was never written" |
| Goals | G4 read-back is the state of record | Conformed | `SKILL.md:20` | "Treat the read-back, not the edit tool's success message, as the state of record" + cheapest-syntax-check list |
| Goals | G5 repair from observed state + full re-verify | Conformed | `SKILL.md:18, 20` | compounding-defects rationale; "repairing three stacked defects costs a full verification re-run" |
| Non-Goals | No editing of app-managed files | Conformed | `SKILL.md` (whole body) | no instruction anywhere to edit managed files; the skill itself was created by re-homing per the Externally Managed Files rule |
| Constraints | Runtime-generic, provenance-free | Conformed | `SKILL.md:9` | provenance line cites cross-workspace mining generically; no workspace names, session IDs, or incident specifics in the body |
| Constraints | Two facts only | Conformed | `SKILL.md:10, 16` | exactly two numbered sections |
| Scenarios | S-001 out-of-root plan routes through Bash | Conformed | `SKILL.md:14` | Bash-first, read-back verified, "no workspace-tool attempt precedes" implied by "Don't first try the workspace tool" |
| Scenarios | S-002 boundary error is not data loss | Conformed | `SKILL.md:14` | both failure-misreadings named (recreate-what-wasn't-lost; assume-what-wasn't-written) |
| Scenarios | S-003 read-back is the state of record | Conformed | `SKILL.md:20` | re-read changed regions + syntax check before the next file or conclusion |
| Scenarios | S-004 partial outcomes repaired from observed state | Conformed | `SKILL.md:18, 20` | duplicate definition / partial write / premature reference enumerated; verification re-run priced |
| Proposed Surface | Description triggers | Conformed | `SKILL.md:3–4` | both trigger families (out-of-root failure/plan; chained edits over fresh files) present, pushy per skill-creator guidance |

## Coverage

audited: Goals 1–5, Non-Goals (3), Constraints (2), Scenarios S-001–S-004, Proposed Surface (2 items)
unreconciled: []
