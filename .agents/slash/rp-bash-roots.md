---
description: Use when a shell/Bash task needs to cd into or reference a RepoPrompt workspace root's real filesystem path — roots are arbitrary loaded paths, never assume they are children of the cwd; resolve from tool output or workspace.json repoPaths before cd
---

# Workspace-root paths in Bash

RepoPrompt workspace roots are arbitrary loaded paths — not necessarily children of the current directory. Resolve a root's real filesystem path from tool output (echoed absolute paths, directory listings, `workspace.json` `repoPaths`) before `cd`; never construct `<cwd>/<root-name>`.

> Source of truth: `.agents/slash/rp-bash-roots.md` in this repo, symlinked into `~/.claude/commands/` by `scripts/install.sh`. Not app-managed: never edit RepoPrompt CE's managed `rp-*` command files in place (see `../rules/global.md` — Externally Managed Files).
