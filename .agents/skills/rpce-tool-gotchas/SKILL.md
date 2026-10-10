---
name: rpce-tool-gotchas
description: RepoPrompt CE workspace-tool boundaries that agents keep re-learning by failure. Use when an RPCE file/edit tool (apply_edits, file_actions, read_file, MCP file writes) fails or cannot see a path outside the loaded workspace roots — /tmp one-off scripts, a sibling repo, ~/ dotfiles: those tools are root-scoped by design, so route out-of-root reads/writes through Bash (heredoc/python) from the start. Also use when stacking more edits onto files just changed by a batch of edits, especially multi-file refactors: re-read the edited file and syntax-check it (node --check, py_compile, …) before building on the result — batch edits can land partially or contradict the editor's expectation (duplicates surviving a "successful" edit, partial writes under file locks), and the next edit compounds the defect. Trigger proactively for out-of-root file plans and chained edits over fresh files, not only after errors.
---

# RPCE tool gotchas

Two verified facts about RepoPrompt CE's workspace tools. Both cost real rework before they were encoded here (provenance: cross-workspace session mining, 2026-10 — general facts, no single repo).

## 1. Workspace file tools are root-scoped

`apply_edits`, `file_actions`, and the MCP read/write tools operate ONLY on paths inside the loaded workspace root(s). A path outside them — `/tmp` throwaway scripts, a sibling repository, `~/.config` — either fails outright ("file does not exist") or, worse, strands work when a create is assumed to have happened but silently didn't.

**Do:** when a task needs files outside loaded roots (one-off evaluator scripts, cross-repo ledger edits, scratch dumps), write them via Bash from the start — heredoc into a file, or `python3 - <<'EOF'` for anchored edits — and verify by reading back. Don't first try the workspace tool and discover the boundary by failure: the failure reads as "file does not exist" and invites recreating content that was never lost, or losing content that was never written.

## 2. Batch edits can land partially — verify before building on them

A multi-edit batch (especially across several files in a refactor) can report success while the file state contradicts the editor's expectation: a duplicate definition survives, a reference precedes its definition, a partial write lands under a file lock. Stacking the next edit onto that assumed state compounds one defect into several, each needing separate repair.

**Do:** after each file's edit batch — before editing the next file or reasoning about the result — re-read the changed regions (the whole file when small) and run the cheapest syntax check (`node --check`, `python -m py_compile`, `ruby -c`, …). Treat the read-back, not the edit tool's success message, as the state of record. One read per file costs seconds; repairing three stacked defects costs a full verification re-run.
