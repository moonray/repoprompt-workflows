# Spec Conformance — Doc-Freshness Reminder Hook

- **Spec:** `docs/spec/doc-freshness-reminder.md` (Doc-Freshness Reminder Hook)
- **Implementation:** `.agents/hooks/doc-freshness-reminder.py`; contract tests `.agents/hooks/doc-freshness-reminder.test.mjs`
- **Audited:** 2026-10-26
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the script; evidence = regex / function / code branch, with the pinning test where one exists.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 detect a work-item close (shell command or closed ledger item) | Conformed | `_CLOSE_CMD_RES` adjacency forms + `_file_closed()` state check in `main()` |
| G2 nudge the change-driven drift audit | Conformed | `NUDGE` directs `document` skill, code mode, change-driven, dry-run first, apply-gated, findings-with-close, skip condition |
| G3 silence on non-close activity | Conformed | adjacency + ref-shaped `close.sh` regexes; no PR-close rule; `_edit_succeeded()` suppression; status≠closed → no nudge |
| G4 fail open on malformed input | Conformed | `try/except json.load` → exit 0; non-dict payload → exit 0 |
| S-001 canonical `$TW` variable close | Conformed | regex `\$\{?TW\}?['\"]?\s+close\b`; test "canonical $TW variable invocation" |
| S-002 other recognized close shapes | Conformed | remaining `_CLOSE_CMD_RES` forms; tests: tw.py-adjacent, `tw close`, `issue.sh close`, `close.sh ISSUE-007`, `gh issue close` |
| S-003 ledger edit with status closed (incl. already-closed) | Conformed | `_file_closed()` is state-based; test "file-backend frontmatter flip to closed fires" |
| S-004 one nudge, full directive contract | Conformed | single `print` in `main()` (one nudge per event); `NUDGE` carries all S-004 directives |
| S-005 non-adjacent prose / `close.sh` without ref stays silent | Conformed | adjacency requirement + ref-shape group; tests "word 'close' alone", "prose … does not fire", "close.sh without a ref-shaped argument" |
| S-006 exact close subcommand in prose fires (accepted residual) | Conformed | `\bgh\s+issue\s+close\b` matches prose sequences; test "exact close-subcommand sequence embedded in prose fires" |
| S-007 `gh pr close` silent | Conformed | no rule matches `pr close`; dedicated test |
| S-008 explicit failure indicators suppress; absent/unknown nudge | Conformed | `_edit_succeeded()` recognizes `is_error`/`isError`, truthy `error`, `status:error`, `ok`/`success` false; defaults True; test "failed close command is suppressed" |
| S-009 non-closing edits silent | Conformed | `_file_closed()` False on open status, absent frontmatter, unreadable/missing file, non-ledger path; tests "still open", "README index", "non-issue doc edit" |
| S-010 foreign events ignored | Conformed | `hook_event_name != "PostToolUse"` → exit 0 |
| S-011 malformed input exits cleanly | Conformed | `json.load` except → exit 0; non-dict guard → exit 0 |
| Surface: payload inputs | Conformed | `_paths_from_payload()` scalar path keys + `_paths_from_patch()` Add/Update/Delete headers; arrays/move destinations deliberately unparsed (documented uncovered → silent) |
| Surface: ledger file check | Conformed | `_ISSUE_FILE_RE` (immediate-child `.md` of `.agents/issues/`) + `_FRONTMATTER_RE` + case-insensitive `status: closed` |
| Surface: output | Conformed | `hookSpecificOutput.additionalContext` on signal; else no output, exit 0 |

## Coverage proof

- **audited:** Goals 1–4; all 11 scenarios (S-001–S-011); Proposed Surface (payload inputs; ledger file check; output)
- **unreconciled:** []

## Notes

Oracle cross-check (2026-10-26) findings folded before implementation was frozen: `close.sh` ref-shape tightening (S-002/S-005), state-based ledger semantics named (Constraints/S-003), failure-indicator contract enumerated (Constraints/S-008), path-input boundary enumerated (Surface), S-004 made self-contained with the full directive set, malformed-input cases split (S-010/S-011).
