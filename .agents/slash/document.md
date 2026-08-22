---
description: Run the document skill in code mode (reconcile docs to code changes or scan for drift) or intent mode (review work against the repo's intent anchor)
---

Use the `document` skill for this request. Treat this slash command as a manual shortcut only — it routes, the skill defines behavior.

- Bare invocation: `code` mode, change-driven over the working-tree diff — never an error, never a required flag.
- Code-mode flags pass through: `--change <staged diff or commit range>`, `--full` (corpus drift scan; composes with `--change` in one run), `--scope <path, doc type, or doc set>`.
- `intent` subcommand: run `intent` mode, passing through window flags `--all`, `--since <ref>`, `--last N`; with none, the skill's baseline-aware default window applies.
- `apply` passes through in both modes; without it the run is dry-run only — the default is unchanged.
- When mode is not stated, infer mode per the skill's precedence: a mission/alignment question → `intent`; a change-shaped request → `code` change-driven; a drift question → `code --full`.
