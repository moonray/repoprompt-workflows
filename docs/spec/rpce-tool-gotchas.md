---
title: RPCE Tool Gotchas Skill
issue: none
status: implemented
---

# RPCE Tool Gotchas Skill

## Problem

RepoPrompt CE's workspace file tools (`apply_edits`, `file_actions`, MCP read/write) are scoped to the loaded workspace roots, and multi-edit batches can land partially or contradict the editor's expectation. Both facts are invisible until they bite: an out-of-root path fails with an error that reads as "file does not exist", and a "successful" edit batch can leave a duplicate definition or partial write that the next edit compounds. Agents re-learn both by failure — the `rpce-tool-gotchas` skill is the contract that encodes them so the failure does not have to happen again.

## Goals

1. Fire on the right triggers — a plan involving files outside loaded roots, an RPCE file-tool failure on such a path, or follow-up work stacking on freshly batch-edited files — proactively, not only after an error. (S-001, S-003)
2. Route out-of-root file operations through Bash from the start — heredoc or anchored python, verified by read-back — never discovering the boundary by failure. (S-001)
3. Interpret an out-of-root tool error as a boundary fact, not a missing file — nothing recreated that was never lost, nothing assumed written that never was. (S-002)
4. Make the read-back, not the edit tool's success message, the state of record after a batch edit: re-read changed regions, run the cheapest syntax check, then build. (S-003)
5. Repair from observed file state when partial or contradictory outcomes surface, with the change's full verification re-run following — self-caused defects do not ship. (S-004)

## Non-Goals

- Editing app-managed files (`repoprompt_managed: true` or harness-injected skill entries) — the Externally Managed Files global rule governs; this skill re-homes lessons into user-owned files, never patches managed ones.
- General file-safety or git-safety guidance — those live in the global rules.
- RPCE tool documentation or discovery — the app owns its own tool docs.

## Constraints

- Runtime-generic (MCP and CLI variants alike) and provenance-free: no workspace names, session IDs, or incident specifics in the skill text — generalized facts only.
- Two facts only; a new tool gotcha joins by the same standard that admitted these: verified across more than one incident before encoding.

## Scenarios

- **S-001 — out-of-root plan routes through Bash.** Given a task needing files outside the loaded workspace roots (a `/tmp` one-off script, a sibling repo, a home-dir config), when the agent plans its file operations, then writes and reads for those paths go through Bash (heredoc / anchored python) from the start, verified by read-back — and no workspace-tool attempt precedes them.
- **S-002 — boundary error is not data loss.** Given an RPCE file-tool error naming a path outside the workspace roots, when the agent interprets it, then it treats the error as the root-scoping boundary (by design), not as a missing file — nothing is recreated that was never lost, and nothing is assumed written that never was.
- **S-003 — read-back is the state of record.** Given a completed multi-edit batch on a file, when further edits or conclusions build on it, then the agent first re-reads the changed regions (the whole file when small) and runs the cheapest syntax check (`node --check`, `py_compile`, …) — the read-back, not the success message, is authoritative.
- **S-004 — partial outcomes repaired from observed state.** Given a read-back that contradicts the edit result (duplicate definition, partial write, premature reference), when repairing, then repairs target the observed file state and the change's full verification suite re-runs afterward.

## Proposed Surface

- Skill description triggers (out-of-root tool failure or plan; chained edits over freshly edited files).
- Two operational rules in `SKILL.md`: §1 root-scoped file tools → Bash; §2 read-back + syntax check before building on a batch edit.
