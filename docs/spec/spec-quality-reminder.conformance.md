# Spec Conformance — Spec Quality Reminder Hook

- **Spec:** `docs/spec/spec-quality-reminder.md` (Spec Quality Reminder Hook)
- **Implementation:** `.agents/hooks/spec-quality-reminder.py`
- **Audited:** 2026-07-10
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the script; evidence = function / code branch.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 detect an edit touching a spec file (docs/spec/*.md excluding the index) | Conformed | `is_spec_file` + `_SPEC_DIR_RE` + README exclusion |
| G2 nudge the spec-quality skill on such edits | Conformed | `REMINDER` emitted when `any(is_spec_file(...))` |
| G3 recognize edited paths across runtimes (path field or apply_patch) | Conformed | `_paths_from_payload` (file_path/path/filePath/notebook_path) + `_paths_from_patch` |
| Editing a spec file nudges spec-quality | Conformed | `is_spec_file` True → print `hookSpecificOutput.additionalContext` |
| Editing the spec index is ignored | Conformed | `basename == readme.md` → `is_spec_file` False |
| Non-spec file is ignored | Conformed | `_SPEC_DIR_RE` miss → no reminder |
| apply_patch edits are recognized | Conformed | `_PATCH_FILE_RE` in `_paths_from_patch` |
| Malformed payload exits cleanly | Conformed | `try/except` + non-PostToolUse guard → `sys.exit(0)` |
| Surface: payload (hook_event_name, tool_input path/command) | Conformed | `payload.get("hook_event_name")`, `tool_input` keys + `command` |
| Surface: output (additionalContext / nothing) | Conformed | reminder via `hookSpecificOutput`; else exit 0 |

## Coverage proof

- **audited:** Goals 1–3; all 5 scenarios; Proposed Surface (payload inputs; output)
- **unreconciled:** []

## Notes

Reminder-only design (no Stop gate) matches the spec's Non-Goals; path detection covers both Claude path fields and Codex/opencode apply_patch. No drift found.
