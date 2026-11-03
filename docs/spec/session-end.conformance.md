# Spec Conformance — Session-End Command

- **Spec:** `docs/spec/session-end.md` (Session-End Command)
- **Implementation:** `.agents/slash/session-end.md`; deployed by `scripts/install.sh` (commands scan)
- **Audited:** 2026-11-03
- **Method:** each Goal + scenario + Proposed Surface element mapped to the command text that carries it; evidence = section + rule line. Guidance-artifact conformance is textual, as with skills; runtime verification is the command's next real invocation.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 intent-to-end is a gate, not a farewell | Conformed | intro: "The session is NOT declared over … push back"; S-005 loop: re-verify before "declaring the session ended" |
| G2 evidence-first answers with verdict lines | Conformed | "Evidence or explicit 'nothing to do'"; Format rules: "one-glance verdict line first (`✅ …` / `⚠️ N items: <gist>`)" applying to every section |
| G3 numbered open items with lettered options | Conformed | section 6: numbered block shape, 2-4 lettered options, "operator may answer with letters or words, e.g. `1 a, 2 c, 4 ignore`" |
| G4 routing by size and relatedness | Conformed | Option rules: small/closely-related → finish-now recommended; large/separable → tracking issue recommended; reason clause required |
| S-001 gate semantics | Conformed | intro + closing: "wait for the operator's picks, execute them, and re-verify" |
| S-002 verdict lines, evidence citations | Conformed | Format rules block; per-section "Verdict line, then …" phrasing in sections 1-5 |
| S-003 numbered items, options, ignore path | Conformed | section 6 block template; "defer … and ignore … always available"; "Never silently drop an item; never pre-decide" |
| S-004 option routing with reason | Conformed | Option rules with "(recommended — say why in a clause)" |
| S-005 execute then re-verify | Conformed | closing paragraph: re-verify affected sections; "If picks create new loose ends, they join the list" |
| S-006 empty path renders summary | Conformed | section 6 final paragraph: `✅ nothing to do` + one-paragraph summary |
| Surface: command file | Conformed | frontmatter description carries trigger + reply grammar; six sections per spec |
| Surface: output grammar | Conformed | verdict lines, numbered items, lettered options all defined as format rules in the command text |
| Surface: deployment | Conformed | installer commands scan links `.agents/slash/*.md` into `~/.claude/commands` + `~/.agents/slash` (existing mechanism; live symlinks verified at first deploy, 2026-11-03) |

## Coverage proof

- **audited:** Goals 1–4; all 6 scenarios (S-001–S-006); Proposed Surface (command file; output grammar; deployment)
- **unreconciled:** []

## Notes

First spec for a slash command (commands were previously outside the coverage policy); promoted to specced because the operator redesign gave it a real behavioral contract (the push-back gate and the reply grammar). Recorded in the spec index with its issue (#15, reopened for the redesign).
