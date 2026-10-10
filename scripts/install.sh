#!/usr/bin/env bash
# install.sh — scan this repo's workflows/skills/commands/rules and symlink each into the dirs your tools read.
# Idempotent: detects what's already linked (partial installs) and only fixes what's missing or wrong.
# Adding a new workflow/skill/command? Just drop it in its dir — no edit to this script needed.
# Flags: --dry-run (preview), --uninstall (remove our links), --org-repo=<path> (also link your
#        organization repo's private rules overlay), --help. ORG_REPO env works too.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO/.agents"
RPCE_WF="$HOME/Library/Application Support/RepoPrompt CE/Workflows"
CLAUDE_SKILLS="$HOME/.claude/skills"
AGENTS_SKILLS="$HOME/.agents/skills"
CLAUDE_CMD="$HOME/.claude/commands"
AGENTS_SLASH="$HOME/.agents/slash"
CLAUDE_RULES="$HOME/.claude/rules"
AGENTS_RULES="$HOME/.agents/rules"

DRY=0; UNINSTALL=0; ORG_REPO="${ORG_REPO:-}"; ORG_GIVEN=0
for a in "$@"; do
  case "$a" in
    --dry-run)   DRY=1 ;;
    --uninstall) UNINSTALL=1 ;;
    --org-repo=*) ORG_REPO="${a#--org-repo=}"; ORG_GIVEN=1 ;;
    -h|--help)   sed -n '2,6p' "$0"; exit 0 ;;
    *) echo "install.sh: unknown flag '$a' (try --help)" >&2; exit 2 ;;
  esac
done
# An explicitly empty --org-repo= is almost certainly a typo'd variable (CI:
# --org-repo="$ORG_PATH" with ORG_PATH unset) — refuse it rather than silently
# performing a public-only install the operator believes included the overlay.
if [ "$ORG_GIVEN" = 1 ] && [ -z "$ORG_REPO" ]; then
  echo "install.sh: --org-repo requires a path (empty value given)" >&2; exit 2
fi

# Canonicalize the org repo to an absolute path, failing closed: a relative
# value would become a relative symlink target (resolved against the link's
# directory, not the cwd) and the ok-check would then report the broken link
# as healthy on every later run.
if [ -n "$ORG_REPO" ]; then
  ORG_CANON="$(cd "$ORG_REPO" 2>/dev/null && pwd -P)" ||
    { echo "install.sh: --org-repo path not found: $ORG_REPO" >&2; exit 2; }
  ORG_REPO="$ORG_CANON"
fi

OK=0; FIXED=0; CONFLICT=0; REMOVED=0; SKIPPED=0

# link_is_ours <target> — does this symlink target belong to this repo or the configured org repo?
# Anchored on path boundaries: the target must BE the root or live strictly under it,
# never merely contain it as a substring (a sibling like <repo>-backup must not match).
link_is_ours() {
  case "$1" in
    "$REPO"|"$REPO"/*) return 0 ;;
  esac
  if [ -n "$ORG_REPO" ]; then
    case "$1" in
      "$ORG_REPO"|"$ORG_REPO"/*) return 0 ;;
    esac
  fi
  return 1
}

# manage <src> <link>  — classify the link, then link/relink/remove/leave per mode.
manage() {
  local src="$1" link="$2" flag cur
  flag="-sfh"; [ -d "$src" ] && flag="-sfn"   # dirs need -n so ln won't follow an existing link

  if [ "$UNINSTALL" = 1 ]; then
    if [ -L "$link" ]; then
      cur="$(readlink "$link" || true)"
      if link_is_ours "$cur"; then
        { [ "$DRY" = 1 ] && echo "    rm \"$link\"" || rm -f "$link"; }
        echo "  removed  $link"; REMOVED=$((REMOVED+1))
      else
        echo "  skip     $link (points elsewhere)"; SKIPPED=$((SKIPPED+1))
      fi
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
    if ! link_is_ours "$cur"; then
      # A symlink we cannot prove is ours (this repo or the org repo) is foreign:
      # never silently replace it — report a CONFLICT and let the user decide.
      # (Migrating from another checkout: remove its links or run its --uninstall first.)
      echo "  CONFLICT $link -> $cur (foreign symlink, not owned by this repo or --org-repo) — resolve manually" >&2; CONFLICT=$((CONFLICT+1)); return
    fi
    # wrong/broken target that IS ours -> fix it
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
# The registration table lives inside the python heredoc as native data (no JSON-in-bash
# quoting); matchers are anchored and include MCP-qualified names (bare `apply_edits` never
# matched `mcp__RepoPromptCE__apply_edits`); commands quote $HOME so homes with spaces work.
# Safe: parses JSON via python3, backs up before writing, never duplicates an entry, honors --dry-run/--uninstall, non-fatal.
register_claude_settings() {
  local settings="$HOME/.claude/settings.json"
  if ! command -v python3 >/dev/null 2>&1; then
    echo "  skip     $settings (python3 not found — register hooks manually; see .agents/hooks/README.md)" >&2
    SKIPPED=$((SKIPPED+1)); return
  fi
  echo "• Claude Code settings.json  (idempotent hook registration)"
  DRY="$DRY" UNINSTALL="$UNINSTALL" SETTINGS="$settings" python3 - <<'PY' || { echo "  skip     $settings (registration failed); register hooks manually — see .agents/hooks/README.md" >&2; SKIPPED=$((SKIPPED+1)); }
import json, os, shutil, sys, tempfile
_ANCHORED_EDIT = "^(?:Edit|Write|MultiEdit|apply_edits|file_actions|mcp__RepoPromptCE__(?:apply_edits|file_actions))$"
_TASKS = "^Task$|^TaskOutput$|mcp__RepoPromptCE__agent_run"
regs = [
    {"event": "PostToolUse", "matcher": "Bash|Skill", "command": 'python3 "$HOME/.claude/hooks/test-quality-reminder.py"'},
    {"event": "PostToolUse", "matcher": _ANCHORED_EDIT,   "command": 'python3 "$HOME/.claude/hooks/spec-quality-reminder.py"'},
    {"event": "PostToolUse", "matcher": _ANCHORED_EDIT,   "command": 'python3 "$HOME/.claude/hooks/spec-conformance-gate.py"'},
    {"event": "PostToolUse", "matcher": _TASKS,           "command": 'python3 "$HOME/.claude/hooks/delegation-reminder.py"'},
    {"event": "Stop",        "matcher": "*",             "command": 'python3 "$HOME/.claude/hooks/test-quality-reminder.py"'},
    {"event": "PreToolUse", "matcher": "^mcp__chrome-devtools__", "command": 'python3 "$HOME/.claude/hooks/chrome-gate.py"'},
]
path = os.environ["SETTINGS"]; dry = os.environ["DRY"] == "1"; uninst = os.environ["UNINSTALL"] == "1"
def _hook_cmds(entry):
    hh = entry.get("hooks") if isinstance(entry, dict) else None
    return hh if isinstance(hh, list) else []
try:
    with open(path) as f: data = json.load(f)
except FileNotFoundError:
    data = {}
except Exception:
    sys.exit(1)  # unreadable JSON — let the bash guard count it (SKIPPED) and print the manual-install hint
if not isinstance(data, dict): data = {}
hooks = data.get("hooks")
if not isinstance(hooks, dict): hooks = {}
data["hooks"] = hooks
ours = {r["command"] for r in regs}
# Registrations from older installers used the bare '~/.claude/hooks/<name>.py'
# command form with unanchored matchers. Install migrates them to the current
# entries; uninstall removes both generations, so no dead/duplicate entries
# are ever left behind pointing at (possibly removed) scripts.
legacy = {"~/.claude/hooks/test-quality-reminder.py",
          "~/.claude/hooks/spec-quality-reminder.py",
          "~/.claude/hooks/spec-conformance-gate.py",
          "~/.claude/hooks/delegation-reminder.py",
          "python3 $HOME/.claude/hooks/test-quality-reminder.py",
          "python3 $HOME/.claude/hooks/spec-quality-reminder.py",
          "python3 $HOME/.claude/hooks/spec-conformance-gate.py",
          "python3 $HOME/.claude/hooks/delegation-reminder.py"}
strip_targets = (ours | legacy) if uninst else legacy
added = removed = 0
for ev in sorted({r["event"] for r in regs}):
    lst = hooks.get(ev, [])
    if not isinstance(lst, list): lst = []
    kept = []
    for e in lst:
        if not isinstance(e, dict): kept.append(e); continue
        hh = e.get("hooks")
        if not isinstance(hh, list): kept.append(e); continue
        before = len(hh)
        hh = [h for h in hh if not (isinstance(h, dict) and h.get("command") in strip_targets)]
        removed += before - len(hh)
        if hh: e["hooks"] = hh; kept.append(e)
    lst = kept
    if uninst:
        if kept: hooks[ev] = kept
        else: hooks.pop(ev, None)
    else:
        for r in regs:
            if r["event"] != ev: continue
            matches = [e for e in lst if isinstance(e, dict) and e.get("matcher", "*") == r["matcher"]]
            # already present in ANY same-matcher entry? dedup across duplicates, not just the first
            if any(isinstance(h, dict) and h["command"] == r["command"] for e in matches for h in _hook_cmds(e)):
                continue
            if matches:
                entry = matches[0]
                hh = entry.setdefault("hooks", [])
                if not isinstance(hh, list): hh = []; entry["hooks"] = hh
            else:
                entry = {"matcher": r["matcher"], "hooks": []}; lst.append(entry)
            entry["hooks"].append({"type": "command", "command": r["command"]}); added += 1
        hooks[ev] = lst
write = (removed > 0 or added > 0 or not os.path.exists(path))
if dry:
    print(f"    [dry-run] {path}: +{added} -{removed} hook registrations (nothing written)")
elif write:
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)  # only when actually writing — keeps --dry-run truly read-only
    if os.path.exists(path): shutil.copy2(path, path + ".bak")
    fd, tmp = tempfile.mkstemp(dir=d)
    with os.fdopen(fd, "w") as f: json.dump(data, f, indent=2); f.write("\n")
    os.replace(tmp, path)
    bak = f" (backup: {path}.bak)" if os.path.exists(path + ".bak") else ""
    print(f"  settings {path}: +{added} -{removed} hook registrations{bak}")
else:
    msg = "not registered (nothing to remove)" if uninst else "already registered"
    print(f"  settings {path}: {msg}")
PY
}

# link_sources <src-glob> [skip-basename...] -- <dest-dir>...
# One fan-out for every category: iterate the glob, skip reserved basenames,
# manage() each source into every destination dir.
link_sources() {
  local glob="$1"; shift
  local skips=() skip f src b dest
  while [ $# -gt 0 ] && [ "$1" != "--" ]; do skips+=("$1"); shift; done
  [ "${1:-}" = "--" ] && shift
  for f in $glob; do
    src="${f%/}"
    [ -e "$src" ] || continue
    b="$(basename "$src")"
    for skip in ${skips:+"${skips[@]}"}; do [ "$b" = "$skip" ] && continue 2; done
    for dest in "$@"; do
      manage "$src" "$dest/$b"
    done
  done
}

verb="Installing"; [ "$UNINSTALL" = 1 ] && verb="Uninstalling"
echo "$verb repoprompt-workflows  (repo: $REPO)$([ "$DRY" = 1 ] && echo '  [dry-run — nothing is changed]')"

shopt -s nullglob

echo "• workflows → RepoPrompt CE  (scanning .agents/workflows/*.md)"
link_sources "$SRC/workflows/*.md" README.md -- "$RPCE_WF"

echo "• skills → ~/.claude/skills + ~/.agents/skills  (scanning .agents/skills/*/)"
link_sources "$SRC/skills/*/" -- "$CLAUDE_SKILLS" "$AGENTS_SKILLS"

echo "• commands → ~/.claude/commands + ~/.agents/slash  (scanning .agents/slash/*.md)"
link_sources "$SRC/slash/*.md" README.md -- "$CLAUDE_CMD" "$AGENTS_SLASH"

echo "• rules → ~/.claude/rules + ~/.agents/rules  (scanning .agents/rules/*.md)"
link_sources "$SRC/rules/*.md" README.md -- "$CLAUDE_RULES" "$AGENTS_RULES"
if [ -n "$ORG_REPO" ]; then
  ORG_RULES="$ORG_REPO/.agents/rules"
  if [ -d "$ORG_RULES" ]; then
    echo "• org overlay rules → both rules homes  (from $ORG_RULES; global.md stays the public core)"
    link_sources "$ORG_RULES/*.md" README.md global.md -- "$CLAUDE_RULES" "$AGENTS_RULES"
  else
    echo "  note: $ORG_RULES not found — no org overlay linked" >&2
    SKIPPED=$((SKIPPED+1))
  fi
else
  echo "• org overlay: none — re-run with --org-repo=<path> (or ORG_REPO env) to link your organization repo's private rules overlay; that link is also what makes the org repo discoverable by symlink"
fi

echo "• hooks → ~/.claude/hooks  (scanning .agents/hooks/*.py; Claude Code)"
link_sources "$SRC/hooks/*.py" -- "$HOME/.claude/hooks"
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
