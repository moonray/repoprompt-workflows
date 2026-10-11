---
title: Model Roster Reminder Hook — Conformance
issue: 10
spec: model-roster-reminder.md
audited: 2026-10-11
---

# Model Roster Reminder Hook — Conformance Matrix

Implementation audited: `.agents/hooks/model-roster-reminder.py` (+ `.test.mjs`) and the three backend registrations. Evidence = code lines, test names, registration sites.

## Matrix

| Section | Item | Status | Evidence | Note |
|---|---|---|---|---|
| Constraints | Local-file sources only; env overrides for tests | Conformed | `model-roster-reminder.py` `_load_skill`/`_load_cache` (env first, then defaults) | no network, no watcher |
| Constraints | Two naming shapes normalized; unparsable skipped | Conformed | `GPT_NAME_RE`/`CLAUDE_NAME_RE` in `_parse_picks` | template rows like `<model>` cannot match and are skipped |
| Constraints | Nudge names the skill, forbids silent re-routing | Conformed | `additionalContext` string in `main()` | verbatim per spec |
| Scenarios | S-001 Trigger scope | Conformed | `TOOL_RE` gate in `main()`; test "non-matching tool is silent" | `mcp__RepoPromptCE__file_actions` produces no output |
| Scenarios | S-002 Silence when current | Conformed | test "current picks are silent (the zero-token common case)"; live smoke 2026-10-11 against real skill + real caches emitted nothing | |
| Scenarios | S-003 Newer generation flagged | Conformed | `detect()` version-tuple comparison; test "newer generation flags with a suggestion" (gpt-6.6-sol fixture) | asserts drift text, the specific slug, and the suggestion |
| Scenarios | S-004 Missing pick flagged | Conformed | test "missing pick flags roster drift" (claude-opus-5-5 absent from cc fixture) | provider-aware cache lookup |
| Scenarios | S-005 Fail open | Conformed | blanket `except Exception: return 0`; test "fails open when the skill is absent" | hook never blocks and never errors the tool call |
| Scenarios | S-006 Cross-backend registration | Conformed | `scripts/install.sh` regs (`_ROSTER` matcher), `.codex/hooks.json` PostToolUse entry, `.opencode/plugins/repoprompt-hooks.mjs` roster branch | opencode surfaces as warn log (no model-visible injection, re-verified 2026-10-11, #9) |
| Proposed Surface | Input: PostToolUse payload + skill + caches | Conformed | `main()` reads `tool_name`/`cwd`; `_load_skill` resolves symlink → user-scope → cwd-relative | |
| Proposed Surface | Output: silent, or one drift reminder | Conformed | single `print` of the `hookSpecificOutput` shape | matches the house reminder schema |

## Coverage proof

```yaml
audited:
  - Constraints: local-file sources + env overrides
  - Constraints: pick normalization shapes
  - Constraints: nudge wording
  - S-001 .. S-006 (all scenarios)
  - Surface: inputs
  - Surface: output
unreconciled: []
```

Every scenario, Proposed Surface element, and stated constraint was checked; none Diverged or Not-built. Verification: `python3 -m py_compile` clean; `node --test` 5/5 pass; live smoke (real skill + real caches, current picks) silent.
