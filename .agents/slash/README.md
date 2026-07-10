# Slash Commands

Manual slash commands. Each command is a markdown file with YAML frontmatter (`description` required; `model`, `allowed-tools`, `argument-hint`, and `disable-model-invocation` optional). Commands are invoked as `/name` in Claude Code and other runtimes that read from a commands directory.

## Commands

| Command | Location | Use when |
|---|---|---|
| `document` | [`document.md`](document.md) | Manual shortcut for the `document` skill; syncs or audits docs against code, dry-run by default unless `apply` is explicit. |

## Discovery and install

Claude Code discovers commands from `~/.claude/commands/` (user) and `.claude/commands/` (project). The repo installer (`scripts/install.sh`) links every command here at once; or symlink manually:

```bash
REPO="$(pwd)"   # run from the repo root
ln -sfn "$REPO/.agents/slash/document.md" "$HOME/.claude/commands/document.md"
```

> This extraction ships only `/document` (a shortcut to the `document` skill); other commands from the source repo were business-specific and excluded.

## Adding or updating commands

- One markdown file per command, named `<command>.md`.
- Frontmatter: `description` (required), plus `model` / `allowed-tools` / `argument-hint` / `disable-model-invocation` as needed.
- Keep command bodies concise; put cross-command notes here rather than inside individual files.
- For behavior that should be model-invokable during normal work, keep the full guidance in a skill and make the slash command a shortcut to that skill.
