# Spec Conformance — Spec Quality Reminder Hook

- **Spec:** `docs/spec/spec-quality-reminder.md` (Spec Quality Reminder Hook)
- **Implementation:** `.agents/hooks/spec-quality-reminder.py` (+ unit suite `.agents/hooks/spec-quality-reminder.test.mjs`, 22 tests)
- **Audited:** 2026-10-26 (re-audited after adding the hook-script spec-debt rule (#12); prior audits: 2026-10-10 rule-table rewrite, 2026-07-10 single-class version)
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the script; evidence = function / code branch; locking suite run green (`node --test`, 29/29 at the 2026-10-26 audit; 22/22 after the 2026-10-23 fixture hardening (#8)).

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 detect edits touching spec / plan / nested SKILL.md files (indexes excluded) | Conformed | `RULES` table (`docs/spec/`, `docs/plans/`, `(^|/)\.agents/skills/` + `(^|/)SKILL\.md$`) + `_EXCLUDE_BASENAMES` in `classify` |
| G2 nudge the matching skill per path, aggregated into ONE reminder | Conformed | `main`: per-path `classify` hits appended when `text not in reminders`, emitted as one joined `additionalContext` |
| G3 recognize paths across runtimes (scalar fields, list inputs, move pairs, apply_patch) | Conformed | `_paths_from_tool_input` (`scalar_keys` incl. `new_path`/`old_path`; `files`/`edits`/`paths` lists of strings or path-bearing dicts) + `_paths_from_patch` (`_PATCH_FILE_RE`) |
| G4 suppress reminders for failed edits | Conformed | `_edit_succeeded` (`tool_response.is_error`/`error`/`status`) guard in `main` |
| G5 detect hook-script edits with missing/unverifiable spec coverage and nudge the debt | Conformed | `_HOOK_SCRIPT_RE` + `_hook_spec_missing()` (own-spec check, index-mention check, candidate-root chain, nudge-on-unverifiable) wired into `classify` |
| Editing a spec file nudges spec-quality | Conformed | `RULES[0]` + `classify` → SPEC QUALITY text (tests: absolute path via `path` field; apply_patch Add/Update body) |
| Editing the spec index is ignored | Conformed | `_EXCLUDE_BASENAMES` basename check in `classify` |
| Path outside every rule class is ignored | Conformed | `classify` returns `[]` when no rule matches |
| Editing a plan nudges spec-plan-readiness (and only that class) | Conformed | `RULES[1]`; a `docs/plans/` path misses `RULES[0]`'s dir regex |
| Editing a nested SKILL.md nudges skill standards | Conformed | regex search (not a one-level glob) — `(^|/)\.agents/skills/` + `(^|/)SKILL\.md$` match at any depth |
| Multiple rule classes in one batch aggregate | Conformed | `main` dedup loop + `"\n".join(reminders)` |
| Move edits are inspected on both paths | Conformed | `new_path` and `old_path` in `scalar_keys` |
| Failed edits are suppressed | Conformed | `_edit_succeeded` returns False on error-shaped `tool_response` |
| apply_patch edits are recognized | Conformed | `_PATCH_FILE_RE` finds `*** Add/Update/Delete File:` targets |
| opencode plugin payload shape is recognized | Conformed | `_paths_from_tool_input` reads every known key and ignores extras (test: spread args + `file_path`) |
| Malformed payload exits cleanly | Conformed | `try/except` on `json.load` + `isinstance(payload, dict)` guard + non-PostToolUse guard → `sys.exit(0)` (tests: invalid JSON, `[]`, `null`, string, number) |
| Editing an unspecced hook script nudges the spec debt | Conformed | `_hook_spec_missing` returns `_HOOK_SPEC_NUDGE` when no candidate shows coverage (test: hook script with no spec/index mention) |
| Editing a specced hook script stays silent | Conformed | own-spec `os.path.isfile` check returns None (test: `docs/spec/<stem>.md` present) |
| Hook covered by an index mention stays silent | Conformed | index-mention check reads `docs/spec/README.md` for the stem (test: chrome-gate pattern) |
| Unverifiable coverage nudges | Conformed | no candidate resolving to `docs/spec/` falls through to the nudge (test: workspace-relative path, no cwd) |
| A non-hook python script is out of scope | Conformed | `_HOOK_SCRIPT_RE` requires `.agents/hooks/*.py` (test: `scripts/install-helper.py` silent) |
| Surface: optional `cwd` candidate root | Conformed | `main` reads `payload.cwd` into `classify(path, cwd)`; `_hook_spec_missing` joins cwd with a relative root (test: cwd candidate resolves a relative workspace root) |
| Hook-spec nudge aggregates with rule classes | Conformed | `_hook_spec_missing` result appended through the same dedup loop (test: uncovered hook + spec file → both texts) |
| Surface: payload (hook_event_name, tool_input shapes, optional tool_response) | Conformed | `payload.get("hook_event_name")`; `tool_input` handled by `_paths_from_tool_input`; `tool_response` by `_edit_succeeded` |
| Surface: output (aggregated additionalContext / nothing) | Conformed | joined deduped rule texts via `hookSpecificOutput`; else exit 0 |

## Coverage proof

- **audited:** Goals 1–5; all 16 scenarios; Proposed Surface (payload inputs incl. optional `tool_response` and `cwd`; aggregated output)
- **unreconciled:** []

## Notes

Reminder-only design (no Stop gate) matches the spec's Non-Goals; the narrowness (no raw-shell-redirect detection) is stated in Non-Goals. Registration matchers (anchored, MCP-qualified) live in user-owned settings — carried by `scripts/install.sh` and the runtime wiring docs, not by the script. The #12 rule is scope-limited to `.agents/hooks/*.py` per Non-Goals (skills' and repo scripts have heterogeneous spec coverage); its live-fire on its own implementation edit confirmed both the nudge and the RPCE workspace-relative-path gap now pinned in Constraints. No drift found.
