# Spec Conformance — Spec-Accuracy Reminder Hook

- **Spec:** `docs/spec/spec-accuracy-reminder.md` (Spec-Accuracy Reminder Hook)
- **Implementation:** `.agents/hooks/spec-accuracy-reminder.py`; contract tests `.agents/hooks/spec-accuracy-reminder.test.mjs`
- **Audited:** 2026-11-03
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the script; evidence = regex / function / code branch, with the pinning test where one exists.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 detect an operational-doc edit at change time | Conformed | `_OPDOC_RES` (`.agents/slash/*.md`, `docs/procedures/*.md`); `_is_opdoc()` with README exclusion |
| G2 nudge the same-session spec-accuracy check | Conformed | `NUDGE` carries: same-session check while context is fresh, OLD-behavior drift, specs + conformance matrices, fix-or-flag, quick-no-op allowance |
| G3 silence where there is nothing to check | Conformed | `_spec_dir_state()` positive-absence gate; `_is_opdoc()` path filter; `_edit_succeeded()` suppression |
| G4 fail open on malformed input | Conformed | `try/except json.load` → exit 0; non-dict payload → exit 0 |
| S-001 runbook edit in a specs repo fires | Conformed | `_OPDOC_RES[0]` + `_spec_dir_state() is not False`; test "runbook edit … fires the nudge" |
| S-002 procedure edit in a specs repo fires | Conformed | `_OPDOC_RES[1]`; test "procedure edit … fires the nudge" |
| S-003 positively spec-less repo stays silent | Conformed | `_spec_dir_state()` returns False when a resolvable base lacks `docs/spec/`; test "repo without docs/spec/ stays silent" |
| S-004 unresolvable root nudges | Conformed | `_spec_dir_state()` returns None when no base resolves → `is not False` → nudge; test "unresolvable root nudges" |
| S-005 relative paths resolve against payload cwd, exclusively | Conformed | `_repo_root("")` + explicit-cwd-only `bases` (process cwd consulted only when payload cwd absent — the poisoning defect the test caught pre-fix); test "relative path resolves against payload cwd" |
| S-006 README basenames silent | Conformed | `_EXCLUDE_BASENAMES`; test "README.md under a watched dir stays silent" |
| S-007 non-operational paths silent | Conformed | no `_OPDOC_RES` match for specs/plans/source/operations; test "non-watched paths stay silent" |
| S-008 failed edits suppressed; unknown response shapes nudge | Conformed | `_edit_succeeded()` recognizes `is_error`/`isError`, truthy `error`, `status:error`, `ok`/`success` false; defaults True; test "failed edit is suppressed; unknown response shape still nudges" |
| S-009 batch/move/apply-patch path forms covered | Conformed | `_paths_from_tool_input()` scalar keys + `files`/`edits`/`paths` arrays (dict items incl. `new_path`/`old_path`) + `_paths_from_patch()` Add/Update/Delete/Move headers; tests "batch inputs surface watched paths from arrays and moves", "apply_patch command forms are parsed for paths" |
| S-010 exactly one nudge per event | Conformed | single `print` in `main()` gated by `any()`; test "exactly one nudge per event with multiple watched paths" |
| S-011 foreign events ignored | Conformed | `hook_event_name != "PostToolUse"` → exit 0; test "foreign events are ignored" |
| S-012 malformed input exits cleanly | Conformed | `json.load` except → exit 0; non-dict guard → exit 0; test "malformed input exits cleanly with no output" |
| S-013 nudge content contract | Conformed | `NUDGE` text asserts: same-session/NOW, OLD behavior, conformance matrix, no-op; test "nudge content names the same-session check, old behavior, matrices, and the no-op" |
| Surface: payload inputs | Conformed | `hook_event_name`, `tool_input` (all path forms above), `cwd` (string or absent), `tool_response` (failure indicators) |
| Surface: spec-dir gate | Conformed | `_repo_root()` (absolute prefix, cwd-relative empty root, None) + `_spec_dir_state()` three-valued True/False/None |
| Surface: output | Conformed | `hookSpecificOutput.additionalContext` carrying `NUDGE` on signal; else no output, exit 0 |

## Coverage proof

- **audited:** Goals 1–4; all 13 scenarios (S-001–S-013); Proposed Surface (payload inputs; spec-dir gate; output)
- **unreconciled:** []

## Notes

The suite earned its keep before landing: the S-005 test failed against the first implementation (the hook process's own cwd was consulted alongside the payload cwd, letting an unrelated repo's `docs/spec/` invent specs the edited repo lacked) — the fix made the explicit payload cwd the sole resolution, and that defect is now pinned.
