# Spec Conformance — Test Quality Reminder Hook

- **Spec:** `docs/spec/test-quality-reminder.md` (Test Quality Reminder Hook)
- **Implementation:** `.agents/hooks/test-quality-reminder.py`
- **Audited:** 2026-07-10
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the script; evidence = function / code branch.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 detect genuine runs, ignore runner words in comments/heredocs/strings/non-run subcommands | Conformed | `is_test_run_command` + `_segment_tokens` + `_strip_heredocs` + `_subcommand_is_test` |
| G2 per-repo last-run marker keyed by repo root | Conformed | `lastrun_path` + `repo_root` + `CACHE_DIR` |
| G3 block Stop while an uncommitted test file outruns the last run | Conformed | `main()` Stop branch + `dirty_test_files` + mtime comparison |
| G4 nudge test-quality each time a suite runs | Conformed | `VET_REMINDER` emitted in PostToolUse branch |
| G5 documentation files are not tests | Conformed | `DOC_FILE_RE` exclusion in `dirty_test_files` |
| Running a suite records a run and nudges vetting | Conformed | PostToolUse: `is_test_run_command` → touch `lastrun_path` + print `VET_REMINDER` |
| Non-run command does nothing | Conformed | `is_test_run_command` returns False → no marker, no output |
| Help/version and install invocations are not runs | Conformed | `_HELP_FLAGS` skip + `_PM_NO_RUN` subcommand guard |
| Stop blocked when a test file is dirty since the last run | Conformed | Stop branch: `newest_edit > lastrun_ts` → `{"decision":"block","reason":STOP_REASON}` |
| edit→run→stop is allowed | Conformed | `newest_edit <= lastrun_ts` → no block |
| Committing/cleaning test changes clears the gate | Conformed | `dirty_test_files` empty → `sys.exit(0)` |
| Documentation files are not counted as tests | Conformed | `DOC_FILE_RE.search(path)` → `continue` in `dirty_test_files` |
| Malformed payload exits cleanly | Conformed | `try/except` around `json.load` → `sys.exit(0)` |
| Surface: payload (hook_event_name, cwd, tool_input.command) | Conformed | `payload.get("hook_event_name")`, `cwd`, `tool_input.command` in `main()` |
| Surface: output (additionalContext / decision:block / nothing) | Conformed | PostToolUse prints `hookSpecificOutput`; Stop prints `decision:block`; else exit 0 |

## Coverage proof

- **audited:** Goals 1–5; all 8 scenarios; Proposed Surface (payload inputs; output fields)
- **unreconciled:** []

## Notes

Every Goal, scenario, and surface element is realized in the script with matching evidence, including the edit→run→stop mtime logic and the documentation-file exclusion. No drift found.
