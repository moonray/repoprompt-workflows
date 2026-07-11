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

# register_claude_settings — keep our Claude Code hook registrations in ~/.claude/settings.json in sync.
# Safe: parses JSON via python3, backs up before writing, never duplicates an entry, honors --dry-run/--uninstall, non-fatal.
register_claude_settings() {
  local settings="$HOME/.claude/settings.json"
  local regs='[{"event":"PostToolUse","matcher":"Bash","command":"~/.claude/hooks/test-quality-reminder.py"},{"event":"PostToolUse","matcher":"Edit|Write|MultiEdit|apply_edits|file_actions","command":"~/.claude/hooks/spec-quality-reminder.py"},{"event":"PostToolUse","matcher":"Edit|Write|MultiEdit|apply_edits|file_actions","command":"~/.claude/hooks/spec-conformance-gate.py"},{"event":"PostToolUse","matcher":"^Task$|^TaskOutput$|mcp__RepoPromptCE__agent_run","command":"~/.claude/hooks/delegation-reminder.py"},{"event":"Stop","matcher":"*","command":"~/.claude/hooks/test-quality-reminder.py"}]'
  if ! command -v python3 >/dev/null 2>&1; then
    echo "  skip     $settings (python3 not found — register hooks manually; see .agents/hooks/README.md)" >&2
    SKIPPED=$((SKIPPED+1)); return
  fi
  echo "• Claude Code settings.json  (idempotent hook registration)"
  DRY="$DRY" UNINSTALL="$UNINSTALL" SETTINGS="$settings" python3 - "$regs" <<'PY' || { echo "  skip     $settings (registration failed); register hooks manually — see .agents/hooks/README.md" >&2; SKIPPED=$((SKIPPED+1)); }
import json, os, shutil, sys, tempfile
regs = json.loads(sys.argv[1])
path = os.environ["SETTINGS"]; dry = os.environ["DRY"] == "1"; uninst = os.environ["UNINSTALL"] == "1"
os.makedirs(os.path.dirname(path), exist_ok=True)
try:
    with open(path) as f: data = json.load(f)
except FileNotFoundError:
    data = {}
except Exception as e:
    print(f"  skip     {path} (unreadable JSON: {e}); register hooks manually"); sys.exit(0)
if not isinstance(data, dict): data = {}
hooks = data.get("hooks")
if not isinstance(hooks, dict): hooks = {}
data["hooks"] = hooks
ours = {r["command"] for r in regs}
added = removed = 0
for ev in sorted({r["event"] for r in regs}):
    lst = hooks.get(ev, [])
    if not isinstance(lst, list): lst = []
    if uninst:
        kept = []
        for e in lst:
            if not isinstance(e, dict): kept.append(e); continue
            hh = e.get("hooks")
            if not isinstance(hh, list): kept.append(e); continue
            before = len(hh)
            hh = [h for h in hh if not (isinstance(h, dict) and h.get("command") in ours)]
            removed += before - len(hh)
            if hh: e["hooks"] = hh; kept.append(e)
        if kept: hooks[ev] = kept
        else: hooks.pop(ev, None)
    else:
        by_matcher = {}
        for e in lst:
            if isinstance(e, dict) and e.get("matcher") not in by_matcher: by_matcher[e.get("matcher")] = e
        for r in regs:
            if r["event"] != ev: continue
            entry = by_matcher.get(r["matcher"])
            if entry is None:
                entry = {"matcher": r["matcher"], "hooks": []}; lst.append(entry); by_matcher[r["matcher"]] = entry
            hh = entry.setdefault("hooks", [])
            if not isinstance(hh, list): hh = []; entry["hooks"] = hh
            if not any(isinstance(h, dict) and h.get("command") == r["command"] for h in hh):
                hh.append({"type": "command", "command": r["command"]}); added += 1
        hooks[ev] = lst
if dry:
    print(f"    [dry-run] {path}: +{added} -{removed} hook registrations (nothing written)")
elif added or removed or not os.path.exists(path):
    if os.path.exists(path): shutil.copy2(path, path + ".bak")
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path))
    with os.fdopen(fd, "w") as f: json.dump(data, f, indent=2); f.write("\n")
    os.replace(tmp, path)
    bak = f" (backup: {path}.bak)" if os.path.exists(path + ".bak") else ""
    print(f"  settings {path}: +{added} -{removed} hook registrations{bak}")
else:
    print(f"  settings {path}: already registered")
PY
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
register_claude_settings

shopt -u nullglob

echo
if [ "$UNINSTALL" = 1 ]; then
  echo "Summary: removed=$REMOVED skipped=$SKIPPED. Repo files untouched."
else
  echo "Summary: already-correct=$OK linked-or-fixed=$FIXED conflicts=$CONFLICT."
  [ "$CONFLICT" -gt 0 ] && echo "Note: $CONFLICT conflict(s) need manual resolution (real files where a symlink was expected)." >&2
  echo "Restart RepoPrompt CE to pick up workflow changes."
  echo "Hooks: scripts linked to ~/.claude/hooks/ and registered in ~/.claude/settings.json (Claude Code). Codex/opencode activate automatically in this repo (.codex/, .opencode/)."
fi
