# Spec Conformance — Oracle-Review Reminder Hook

- **Spec:** `docs/spec/oracle-review-reminder.md` (Oracle-Review Reminder Hook)
- **Implementation:** `.agents/hooks/oracle-review-reminder.py`; contract tests `.agents/hooks/oracle-review-reminder.test.mjs`
- **Audited:** 2026-11-05 (re-audited post-review same day)
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the script; evidence = regex / function / code branch, with the pinning test where one exists. Rows S-007/S-008/S-013/S-014 and the state/payload surface rows reflect fixes from a 3-lane `ask_oracle` review of `e924941` (state keying + atomicity, steering-markdown classification, commit-regex gaps, dry-run suppression) — each fix carries a pinning test.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 detect the wrap-up moment (successful `git commit`) | Conformed | `_COMMIT_RE` adjacency (`git commit`, `git -C`, `&&`-chained) checked in `main()` step 3 under `_succeeded(payload)` |
| G2 one-shot nudge on substantial + unconsulted change sets | Conformed | `len(non_doc) >= 3 or state["spec"]` and `consulted`/`nudged` guards; single `print`; `nudged` persisted before emit |
| G3 bounded directive in the nudge | Conformed | `NUDGE` names `ask_oracle` review mode, `model-routing` routing, fold-or-reason-skip, one-shot |
| G4 silence on small/mechanical/doc-only/consulted/post-nudge work | Conformed | threshold guard + `_DOC_EXT_RE` exclusion + `consulted`/`nudged` flags; tests: below-threshold, doc-only, consulted, one-shot |
| G5 fail open | Conformed | `try/except json.load` → exit 0; non-dict → exit 0; `_save` swallows all exceptions |
| S-001 ≥3-file commit nudges | Conformed | threshold branch; test "threshold (3 non-doc files) with no consultation nudges once" (branch dispatch proven live: the mis-wired-argument interim test fired the nudge, the fixed one stays silent — discriminating probe) |
| S-002 spec/plan write crosses alone | Conformed | `_SPEC_PLAN_RE` sets `state["spec"]` on any edit under `docs/spec|specs|plans/`; test "spec/plan write alone crosses the threshold" |
| S-003 consulted session silent | Conformed | `_ORACLE_TOOL_RE` stamps `consulted` (any outcome — no `_succeeded` check on this path); test "consulted session stays silent at commit" |
| S-004 below threshold silent | Conformed | `len(non_doc) >= 3` guard; test "below threshold (2 files) stays silent" |
| S-005 one-shot | Conformed | `nudged` persisted in the same `_save` as the emit; test asserts second commit silent |
| S-006 failed edits not counted | Conformed | `_paths_from_payload` branch gated on `_succeeded(payload)`; test "failed edits do not count toward the threshold" |
| S-007 doc-only silent | Conformed | `_DOC_EXT_RE` excludes `.md/.markdown/.mdx/.txt/.rst/.adoc` from `non_doc`, except steering paths (`_STEERING_RE`: `.agents/(skills|workflows|rules|slash)/`, `SKILL.md`); tests "doc-only change sets stay silent" + "steering markdown counts as non-doc" |
| S-008 non-commit commands never nudge | Conformed | `_COMMIT_RE` requires the `git … commit` adjacency on shell-tool events, `commit(?![\w-])` excludes commit-tree/commit-graph, `--dry-run` suppressed in `main()`; tests assert `git status`/`git add`/`git push`/`gh pr close`/commit-tree/commit-graph/dry-run silent + one-shot preserved |
| S-009 failed commit silent, one-shot not consumed | Conformed | `nudged` set only inside the emit path, after `_succeeded`; test "a failed commit stays silent and does not consume the one-shot" |
| S-010 chained/flagged commit forms detected | Conformed | regex flag-value group + segment adjacency; test covers `git add -A && git commit` and `git -C /path commit` |
| S-011 foreign events / pathless edits ignored | Conformed | `hook_event_name != "PostToolUse"` → exit 0; empty `_paths_from_payload` + non-command input falls through; test "foreign events are ignored" |
| S-012 malformed input exits cleanly | Conformed | `json.load` except → exit 0; non-dict guard → exit 0; test "malformed input exits cleanly" |
| S-013 steering markdown counts as non-doc | Conformed | `_STEERING_RE` override in `_is_doc()`; test "steering markdown (.agents skills/workflows/rules) counts as non-doc" |
| S-014 look-alikes/dry-runs don't consume the one-shot | Conformed | `commit(?![\w-])` + `--dry-run` check before the trigger; `nudged` set only on emit; test "commit look-alikes and dry-runs do not trigger" |
| Surface: session state | Conformed | `_state_path()` keys on `session_id` (fallback `cwd` — tested) sha1; `_load`/`_save` atomic-replace under `_locked()` flock around load-modify-save; TTL reset on load + 7-day `sess-*` prune on write; `ORACLE_REVIEW_STATE_DIR` override honored (used by every test) |
| Surface: payload inputs | Conformed | `_ORACLE_TOOL_RE` (`(?:^|__)ask_oracle$`), `_paths_from_payload()` scalar keys + lexical `_norm`, `_paths_from_patch()` Add/Update/Delete headers, `tool_response` failure indicators in `_succeeded()`, shell `tool_name` guard + `--dry-run` suppression |
| Surface: output | Conformed | `hookSpecificOutput.additionalContext` on qualifying commit; else no output, exit 0 |

## Coverage proof

`{ audited: [G1–G5, S-001–S-012, payload inputs, session state, output], unreconciled: [] }`

Runtime-level wiring (settings/Codex/opencode registrations delivering events to the script) is outside this matrix's unit evidence; it is exercised by installer dry-run review plus the live-fire probe recorded in the repo work log.
