#!/usr/bin/env bash
# install.sh — scan this repo's workflows/skills/commands and symlink each into the dirs your tools read.
# Idempotent: detects what's already linked (partial installs) and only fixes what's missing or wrong.
# Adding a new workflow/skill/command? Just drop it in its dir — no edit to this script needed.
# Flags: --dry-run (preview), --uninstall (remove our links), --help.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO/.agents"
RPCE_WF="$HOME/Library/Application Support/RepoPrompt CE/Workflows"
CLAUDE_SKILLS="$HOME/.claude/skills"
AGENTS_SKILLS="$HOME/.agents/skills"
CLAUDE_CMD="$HOME/.claude/commands"

DRY=0; UNINSTALL=0
for a in "$@"; do
  case "$a" in
    --dry-run)   DRY=1 ;;
    --uninstall) UNINSTALL=1 ;;
    -h|--help)   sed -n '2,5p' "$0"; exit 0 ;;
    *) echo "install.sh: unknown flag '$a' (try --help)" >&2; exit 2 ;;
  esac
done

OK=0; FIXED=0; CONFLICT=0; REMOVED=0; SKIPPED=0

# manage <src> <link>  — classify the link, then link/relink/remove/leave per mode.
manage() {
  local src="$1" link="$2" flag cur
  flag="-sfh"; [ -d "$src" ] && flag="-sfn"   # dirs need -n so ln won't follow an existing link

  if [ "$UNINSTALL" = 1 ]; then
    if [ -L "$link" ]; then
      cur="$(readlink "$link" || true)"
      case "$cur" in
        *"$REPO"*) { [ "$DRY" = 1 ] && echo "    rm \"$link\"" || rm -f "$link"; }; echo "  removed  $link"; REMOVED=$((REMOVED+1)) ;;
        *) echo "  skip     $link (points elsewhere)"; SKIPPED=$((SKIPPED+1)) ;;
      esac
    else
      echo "  skip     $link (not a link)"; SKIPPED=$((SKIPPED+1))
    fi
    return
  fi

  if [ -L "$link" ]; then
    cur="$(readlink "$link" || true)"
    if [ "$cur" = "$src" ]; then
      echo "  ok       $link"; OK=$((OK+1)); return
    fi
    # wrong target or broken symlink -> fix it
    if [ "$DRY" = 1 ]; then echo "    ln $flag \"$src\" \"$link\"   (was: $cur)"
    else mkdir -p "$(dirname "$link")"; ln "$flag" "$src" "$link"; fi
    echo "  relinked $link   (was: $cur)"; FIXED=$((FIXED+1))
  elif [ -e "$link" ]; then
    echo "  CONFLICT $link exists and is not a symlink — skipping; resolve manually" >&2; CONFLICT=$((CONFLICT+1))
  else
    if [ "$DRY" = 1 ]; then echo "    mkdir -p \"$(dirname "$link")\"; ln $flag \"$src\" \"$link\""
    else mkdir -p "$(dirname "$link")"; ln "$flag" "$src" "$link"; fi
    echo "  linked   $link"; FIXED=$((FIXED+1))
  fi
}

verb="Installing"; [ "$UNINSTALL" = 1 ] && verb="Uninstalling"
echo "$verb repoprompt-workflows  (repo: $REPO)$([ "$DRY" = 1 ] && echo '  [dry-run — nothing is changed]')"

shopt -s nullglob

echo "• workflows → RepoPrompt CE  (scanning .agents/workflows/*.md)"
for f in "$SRC/workflows"/*.md; do
  b="$(basename "$f")"; [ "$b" = "README.md" ] && continue
  manage "$f" "$RPCE_WF/$b"
done

echo "• skills → ~/.claude/skills + ~/.agents/skills  (scanning .agents/skills/*/)"
for d in "$SRC/skills"/*/; do
  b="$(basename "$d")"
  manage "${d%/}" "$CLAUDE_SKILLS/$b"
  manage "${d%/}" "$AGENTS_SKILLS/$b"
done

echo "• commands → ~/.claude/commands  (scanning .agents/slash/*.md)"
for f in "$SRC/slash"/*.md; do
  b="$(basename "$f")"; [ "$b" = "README.md" ] && continue
  manage "$f" "$CLAUDE_CMD/$b"
done

echo "• hooks → ~/.claude/hooks  (scanning .agents/hooks/*.py; Claude Code)"
for f in "$SRC/hooks"/*.py; do
  b="$(basename "$f")"
  manage "$f" "$HOME/.claude/hooks/$b"
done

shopt -u nullglob

echo
if [ "$UNINSTALL" = 1 ]; then
  echo "Summary: removed=$REMOVED skipped=$SKIPPED. Repo files untouched."
else
  echo "Summary: already-correct=$OK linked-or-fixed=$FIXED conflicts=$CONFLICT."
  [ "$CONFLICT" -gt 0 ] && echo "Note: $CONFLICT conflict(s) need manual resolution (real files where a symlink was expected)." >&2
  echo "Restart RepoPrompt CE to pick up workflow changes."
  echo "Hooks: scripts linked to ~/.claude/hooks/ — activate in Claude Code by adding the block in .agents/hooks/README.md to ~/.claude/settings.json. Codex/opencode activate automatically in this repo (.codex/, .opencode/)."
fi
