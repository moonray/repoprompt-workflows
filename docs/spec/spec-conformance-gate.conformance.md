# Spec Conformance — Spec Conformance Gate Hook

- **Spec:** `docs/spec/spec-conformance-gate.md` (Spec Conformance Gate Hook)
- **Implementation:** `.agents/hooks/spec-conformance-gate.py`
- **Audited:** 2026-07-10
- **Method:** each Goal + scenario + Proposed Surface element mapped to its realization in the script; evidence = function / code branch.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 detect spec files broadly (path / *.spec.md / frontmatter type) | Conformed | `_is_spec_path` + `_SPEC_TYPES` in `_evaluate` |
| G2 block a terminal-status edit with no matrix | Conformed | `_TERMINAL` check + `_evaluate` returns block |
| G3 matrix satisfied by sibling file OR frontmatter key | Conformed | `_matrix_present` (frontmatter keys + sibling `<stem>.conformance.*`) |
| G4 evaluate each file in a multi-file apply_patch independently | Conformed | `main()` loops `_paths_from_payload` and calls `_evaluate` per path |
| Closing a spec without a matrix is blocked | Conformed | `_evaluate`: spec + terminal status + no matrix → block dict |
| A sibling conformance matrix allows the close | Conformed | `_matrix_present` finds sibling prefix → no block |
| A frontmatter conformance reference allows the close | Conformed | `_matrix_present` checks conformance/conformed/audited keys |
| Non-terminal status is not gated | Conformed | `fm.get("status") not in _TERMINAL` → None |
| Non-spec file is not gated | Conformed | `_is_spec_path` False and type not in `_SPEC_TYPES` → None |
| One tripping file in a multi-file edit blocks | Conformed | `main()` loops paths, `break` on first block |
| Missing/unreadable file no-ops | Conformed | `os.path.isfile(path)` False → None |
| Malformed payload exits cleanly | Conformed | `try/except` + PostToolUse guard → exit 0 |
| Surface: payload (hook_event_name, tool_input path/command) | Conformed | `_paths_from_payload` (path fields + apply_patch) |
| Surface: output (decision:block / nothing) | Conformed | `_evaluate` block dict printed; else exit 0 |

## Coverage proof

- **audited:** Goals 1–4; all 8 scenarios; Proposed Surface (payload inputs; output)
- **unreconciled:** []

## Notes

Gate logic, the two matrix-satisfaction paths, and per-file evaluation in apply_patch all match the spec. No drift found.
