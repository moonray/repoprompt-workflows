# Spec Conformance — Delegation Reminder Hook

- **Spec:** `docs/spec/delegation-reminder.md` (Delegation Reminder Hook)
- **Implementation:** `.agents/hooks/delegation-reminder.py`
- **Audited:** 2026-07-10
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the script; evidence = function / code branch.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 detect a delegation tool return (Task/TaskOutput/agent_run) | Conformed | `_DELEGATION_TOOLS` set + `tool_name` check in `main()` |
| G2 remind the delegating agent to verify before accepting | Conformed | `REMINDER` emitted via `hookSpecificOutput.additionalContext` |
| G3 avoid false emits on similarly named non-delegation tools | Conformed | precise `_DELEGATION_TOOLS` set (excludes TaskCreate/TaskUpdate/…) |
| Delegation tool return triggers the reminder | Conformed | `tool_name in _DELEGATION_TOOLS` → print reminder |
| Non-delegation tools are ignored | Conformed | `tool_name not in _DELEGATION_TOOLS` → exit 0 |
| Non-PostToolUse events are ignored | Conformed | `hook_event_name != "PostToolUse"` → exit 0 |
| Malformed payload exits cleanly | Conformed | `try/except` around `json.load` → exit 0 |
| Surface: payload (hook_event_name, tool_name) | Conformed | `payload.get("hook_event_name")`, `payload.get("tool_name")` |
| Surface: output (additionalContext / nothing) | Conformed | reminder via `hookSpecificOutput`; else exit 0 |

## Coverage proof

- **audited:** Goals 1–3; all 4 scenarios; Proposed Surface (payload inputs; output)
- **unreconciled:** []

## Notes

Reminder-only design and the precise tool set (so a broad matcher cannot cause a false emit) match the spec. No drift found.
