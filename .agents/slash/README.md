# Slash Commands

Manual slash commands. Each command is a markdown file with YAML frontmatter (`description` required; `model`, `allowed-tools`, `argument-hint`, and `disable-model-invocation` optional). Commands are invoked as `/name` in Claude Code and other runtimes that read from a commands directory.

## Commands

| Command | Location | Use when |
|---|---|---|
| `document` | [`document.md`](document.md) | Manual shortcut for the `document` skill; syncs or audits docs against code, dry-run by default unless `apply` is explicit. |
| `rp-bash-roots` | [`rp-bash-roots.md`](rp-bash-roots.md) | A shell task needs to `cd` into or reference a RepoPrompt workspace root's real filesystem path — resolve it from tool output or `workspace.json` `repoPaths` before `cd`; never construct `<cwd>/<root-name>`. (Community command in the `rp-*` namespace — distinct from RPCE's app-managed `rp-*` commands.) |
| `commit` | [`commit.md`](commit.md) | Committing staged changes in logical groups — verify the staged set matches the intended group first (`git diff --cached --stat`); file-tool edits land in the working tree, not the index. |
| `pre-mortem` | [`pre-mortem.md`](pre-mortem.md) | Imagining future bug post-mortems for a file, directory, or code area to expose fragile assumptions before they break. |

## Discovery and install

Claude Code discovers commands from `~/.claude/commands/` (user) and `.claude/commands/` (project). The repo installer (`scripts/install.sh`) links every command here at once; or symlink manually:

```bash
REPO="$(pwd)"   # run from the repo root
ln -sfn "$REPO/.agents/slash/document.md" "$HOME/.claude/commands/document.md"
```

> This repo ships four commands: `/document`, `/rp-bash-roots`, `/commit`, and `/pre-mortem`. Commands that were business-specific in the source workspace were excluded from the extraction and live in that workspace's own repo.

## Adding or updating commands

- One markdown file per command, named `<command>.md`.
- Frontmatter: `description` (required), plus `model` / `allowed-tools` / `argument-hint` / `disable-model-invocation` as needed.
- Keep command bodies concise; put cross-command notes here rather than inside individual files.
- For behavior that should be model-invokable during normal work, keep the full guidance in a skill and make the slash command a shortcut to that skill.
