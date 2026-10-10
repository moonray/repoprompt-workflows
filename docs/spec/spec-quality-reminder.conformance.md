# Spec Conformance — Spec Quality Reminder Hook

- **Spec:** `docs/spec/spec-quality-reminder.md` (Spec Quality Reminder Hook)
- **Implementation:** `.agents/hooks/spec-quality-reminder.py` (+ unit suite `.agents/hooks/spec-quality-reminder.test.mjs`, 14 tests)
- **Audited:** 2026-10-10 (re-audited after porting the rule-table rewrite; prior audit 2026-07-10 covered the single-class version)
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the script; evidence = function / code branch; locking suite run green (`node --test`, 14/14).

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 detect edits touching spec / plan / nested SKILL.md files (indexes excluded) | Conformed | `RULES` table (`docs/spec/`, `docs/plans/`, `(^|/)\.agents/skills/` + `(^|/)SKILL\.md$`) + `_EXCLUDE_BASENAMES` in `classify` |
| G2 nudge the matching skill per path, aggregated into ONE reminder | Conformed | `main`: per-path `classify` hits appended when `text not in reminders`, emitted as one joined `additionalContext` |
| G3 recognize paths across runtimes (scalar fields, list inputs, move pairs, apply_patch) | Conformed | `_paths_from_tool_input` (`scalar_keys` incl. `new_path`/`old_path`; `files`/`edits`/`paths` lists of strings or path-bearing dicts) + `_paths_from_patch` (`_PATCH_FILE_RE`) |
| G4 suppress reminders for failed edits | Conformed | `_edit_succeeded` (`tool_response.is_error`/`error`/`status`) guard in `main` |
| Editing a spec file nudges spec-quality | Conformed | `RULES[0]` + `classify` → SPEC QUALITY text (test: relative apply_patch body; absolute path) |
| Editing the spec index is ignored | Conformed | `_EXCLUDE_BASENAMES` basename check in `classify` |
| Path outside every rule class is ignored | Conformed | `classify` returns `[]` when no rule matches |
| Editing a plan nudges spec-plan-readiness (and only that class) | Conformed | `RULES[1]`; a `docs/plans/` path misses `RULES[0]`'s dir regex |
| Editing a nested SKILL.md nudges skill standards | Conformed | regex search (not a one-level glob) — `(^|/)\.agents/skills/` + `(^|/)SKILL\.md$` match at any depth |
| Multiple rule classes in one batch aggregate | Conformed | `main` dedup loop + `"\n".join(reminders)` |
| Move edits are inspected on both paths | Conformed | `new_path` and `old_path` in `scalar_keys` |
| Failed edits are suppressed | Conformed | `_edit_succeeded` returns False on error-shaped `tool_response` |
| apply_patch edits are recognized | Conformed | `_PATCH_FILE_RE` finds `*** Add/Update/Delete File:` targets |
| opencode plugin payload shape is recognized | Conformed | `_paths_from_tool_input` reads every known key and ignores extras (test: spread args + `file_path`) |
| Malformed payload exits cleanly | Conformed | `try/except` on `json.load` + non-PostToolUse guard → `sys.exit(0)` |
| Surface: payload (hook_event_name, tool_input shapes, optional tool_response) | Conformed | `payload.get("hook_event_name")`; `tool_input` handled by `_paths_from_tool_input`; `tool_response` by `_edit_succeeded` |
| Surface: output (aggregated additionalContext / nothing) | Conformed | joined deduped rule texts via `hookSpecificOutput`; else exit 0 |

## Coverage proof

- **audited:** Goals 1–4; all 11 scenarios; Proposed Surface (payload inputs incl. optional `tool_response`; aggregated output)
- **unreconciled:** []

## Notes

Reminder-only design (no Stop gate) matches the spec's Non-Goals; the narrowness (no raw-shell-redirect detection) is stated in Non-Goals. Registration matchers (anchored, MCP-qualified) live in user-owned settings — carried by `scripts/install.sh` and the runtime wiring docs, not by the script. No drift found.
