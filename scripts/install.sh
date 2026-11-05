#!/usr/bin/env bash
# install.sh — scan this repo's workflows/skills/commands/rules and symlink each into the dirs your tools read.
# Idempotent: detects what's already linked (partial installs) and only fixes what's missing or wrong.
# Adding a new workflow/skill/command? Just drop it in its dir — no edit to this script needed.
# Flags: --dry-run (preview), --uninstall (remove our links), --org-repo=<path> (also link your
#        organization repo's private rules overlay), --style-guide=<path> (link your custom style
#        guide to the generic ~/.agents/style-guide.md pointer), --help. ORG_REPO/STYLE_GUIDE env work too.
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
AGENTS_STYLE="$HOME/.agents/style-guide.md"

DRY=0; UNINSTALL=0; ORG_REPO="${ORG_REPO:-}"; ORG_GIVEN=0; STYLE_GUIDE="${STYLE_GUIDE:-}"; STYLE_GIVEN=0
for a in "$@"; do
  case "$a" in
    --dry-run)   DRY=1 ;;
    --uninstall) UNINSTALL=1 ;;
    --org-repo=*) ORG_REPO="${a#--org-repo=}"; ORG_GIVEN=1 ;;
    --style-guide=*) STYLE_GUIDE="${a#--style-guide=}"; STYLE_GIVEN=1 ;;
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
if [ "$STYLE_GIVEN" = 1 ] && [ -z "$STYLE_GUIDE" ]; then
  echo "install.sh: --style-guide requires a path (empty value given)" >&2; exit 2
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

# Canonicalize the style guide to an absolute existing file: a relative value would become a
# relative symlink target, and a missing one a permanently broken pointer every later run
# would then report as healthy.
if [ -n "$STYLE_GUIDE" ]; then
  [ -f "$STYLE_GUIDE" ] || { echo "install.sh: --style-guide file not found: $STYLE_GUIDE" >&2; exit 2; }
  STYLE_GUIDE="$(cd "$(dirname "$STYLE_GUIDE")" && pwd -P)/$(basename "$STYLE_GUIDE")"
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
  if [ -n "$STYLE_GUIDE" ]; then
    case "$1" in
      "$STYLE_GUIDE") return 0 ;;
    esac
  fi
  return 1
}

# manage <src> <link>  — classify the link, then link/relink/remove/leave per mode.
# Classify first (early-return ok/CONFLICT); one shared apply step below then covers
# both wrong-target (relink) and missing-target (link) — the mkdir+ln mutation is
# written exactly once instead of once per branch.
manage() {
  local src="$1" link="$2" flag cur was
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

  was=""
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
    was="$cur"   # wrong/broken target that IS ours -> fix it below
  elif [ -e "$link" ]; then
    echo "  CONFLICT $link exists and is not a symlink — skipping; resolve manually" >&2; CONFLICT=$((CONFLICT+1)); return
  fi

  # apply — dry-run mirrors the mutation; the mkdir prefix appears only for a fresh
  # link (an existing link's parent dir already exists).
  if [ "$DRY" = 1 ]; then
    if [ -n "$was" ]; then
      echo "    ln $flag \"$src\" \"$link\"   (was: $was)"
    else
      echo "    mkdir -p \"$(dirname "$link")\"; ln $flag \"$src\" \"$link\""
    fi
  else
    mkdir -p "$(dirname "$link")"; ln "$flag" "$src" "$link"
  fi
  if [ -n "$was" ]; then echo "  relinked $link   (was: $was)"
  else echo "  linked   $link"; fi
  FIXED=$((FIXED+1))
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
_ROSTER = "^mcp__RepoPromptCE__(?:app_settings|agent_manage|ask_oracle)$"
regs = [
    {"event": "PostToolUse", "matcher": "Bash|Skill", "command": 'python3 "$HOME/.claude/hooks/test-quality-reminder.py"'},
    {"event": "PostToolUse", "matcher": "Bash",          "command": 'python3 "$HOME/.claude/hooks/doc-freshness-reminder.py"'},
    {"event": "PostToolUse", "matcher": _ANCHORED_EDIT,   "command": 'python3 "$HOME/.claude/hooks/spec-quality-reminder.py"'},
    {"event": "PostToolUse", "matcher": _ANCHORED_EDIT,   "command": 'python3 "$HOME/.claude/hooks/spec-accuracy-reminder.py"'},
    {"event": "PostToolUse", "matcher": _ANCHORED_EDIT,   "command": 'python3 "$HOME/.claude/hooks/doc-freshness-reminder.py"'},
    {"event": "PostToolUse", "matcher": _ANCHORED_EDIT,   "command": 'python3 "$HOME/.claude/hooks/spec-conformance-gate.py"'},
    {"event": "PostToolUse", "matcher": _TASKS,           "command": 'python3 "$HOME/.claude/hooks/delegation-reminder.py"'},
    {"event": "PostToolUse", "matcher": _ROSTER,           "command": 'python3 "$HOME/.claude/hooks/model-roster-reminder.py"'},
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

# register_codex_global — keep the GLOBAL Codex hook layer (~/.codex/hooks.json) in sync.
# Codex discovers hooks from every active config layer: the user-level file loads for EVERY
# project (even untrusted ones; project layers merge on top), so this is the all-repos-
# including-future-ones mechanism. Scripts resolve via $HOME/.claude/hooks (the symlinks
# this installer maintains). One-time /hooks trust after the first write. Idempotent:
# merges our registrations into an existing file without touching foreign entries;
# --uninstall removes only entries that are exactly ours.
register_codex_global() {
  if ! command -v python3 >/dev/null 2>&1; then
    echo "  skip     ~/.codex/hooks.json (python3 not found — register manually)" >&2
    SKIPPED=$((SKIPPED+1)); return
  fi
  echo "• Codex global hooks  (~/.codex/hooks.json — every repo; trust once via /hooks)"
  DRY="$DRY" UNINSTALL="$UNINSTALL" CODEX_HOOKS="$HOME/.codex/hooks.json" python3 - <<'PY' || { echo "  skip     ~/.codex/hooks.json (registration failed)" >&2; SKIPPED=$((SKIPPED+1)); }
import json, os, shutil, sys, tempfile
path = os.environ["CODEX_HOOKS"]; dry = os.environ["DRY"] == "1"; uninst = os.environ["UNINSTALL"] == "1"
def hook(name, msg=None, env="", extra=None):
    h = {"type": "command", "command": f'{env}python3 "$HOME/.claude/hooks/{name}"'.strip()}
    if msg: h["statusMessage"] = msg
    if extra: h.update(extra)
    return h
expected = {
  "PreToolUse": [{"matcher": "^mcp__chrome[-_]devtools__", "hooks": [hook("chrome-gate.py", "chrome skill gate")]}],
  "PostToolUse": [
    {"matcher": "Bash", "hooks": [hook("test-quality-reminder.py", "Checking test run + vetting", env="TQ_HOOK_RUNTIME=codex "),
                                    hook("doc-freshness-reminder.py", "Doc-freshness close reminder")]},
    {"matcher": "apply_patch|Edit|Write", "hooks": [hook("spec-quality-reminder.py", "Spec-quality reminder"),
                                                     hook("spec-accuracy-reminder.py", "Spec-accuracy drift reminder"),
                                                     hook("spec-conformance-gate.py", "Spec-conformance gate"),
                                                     hook("doc-freshness-reminder.py", "Doc-freshness close reminder")]},
    {"matcher": "^mcp__RepoPromptCE__(app_settings|agent_manage|ask_oracle)$", "hooks": [hook("model-roster-reminder.py", "Model-roster drift check")]},
  ],
  "Stop": [{"hooks": [hook("test-quality-reminder.py", env="TQ_HOOK_RUNTIME=codex ", extra={"timeout": 30})]}],
}
try:
    with open(path) as f: data = json.load(f)
except FileNotFoundError:
    data = {}
except Exception:
    sys.exit(1)  # unreadable JSON — let the bash guard count it (SKIPPED) and print the hint
if not isinstance(data, dict): sys.exit(1)
hooks = data.get("hooks")
if not isinstance(hooks, dict): hooks = {}
data["hooks"] = hooks
ours = {h["command"] for ev in expected.values() for e in ev for h in e["hooks"]}
if uninst:
    removed = 0
    for ev, entries in expected.items():
        lst = hooks.get(ev, [])
        if not isinstance(lst, list): continue
        for e in lst:
            if not isinstance(e, dict): continue
            hh = e.get("hooks")
            if isinstance(hh, list):
                before = len(hh)
                e["hooks"] = [h for h in hh if not (isinstance(h, dict) and h.get("command") in ours)]
                removed += before - len(e["hooks"])
        hooks[ev] = [e for e in lst if isinstance(e, dict) and e.get("hooks")]
        if not hooks[ev]: hooks.pop(ev, None)
    write = removed > 0 and all(not v for v in hooks.values())
    if write:
        os.remove(path); print(f"  removed  {path} ({removed} hook registrations)")
    else:
        print(f"  settings {path}: removed {removed} registrations" if removed else f"  settings {path}: nothing to remove")
    sys.exit(0)
added = 0
for ev, entries in expected.items():
    lst = hooks.get(ev, [])
    if not isinstance(lst, list): lst = []
    for want in entries:
        matches = [e for e in lst if isinstance(e, dict) and e.get("matcher", "*") == want.get("matcher", "*")]
        entry = matches[0] if matches else None
        if entry is None:
            entry = {"matcher": want["matcher"], "hooks": []}; lst.append(entry)
        hh = entry.setdefault("hooks", [])
        if not isinstance(hh, list): hh = []; entry["hooks"] = hh
        for h in want["hooks"]:
            if not any(isinstance(x, dict) and x.get("command") == h["command"] for x in hh):
                hh.append(h); added += 1
    hooks[ev] = lst
write = added > 0 or not os.path.exists(path)
if dry:
    print(f"    [dry-run] {path}: +{added} hook registrations (nothing written)")
elif write:
    d = os.path.dirname(path); os.makedirs(d, exist_ok=True)
    if os.path.exists(path): shutil.copy2(path, path + ".bak")
    fd, tmp = tempfile.mkstemp(dir=d)
    with os.fdopen(fd, "w") as f: json.dump(data, f, indent=2); f.write("\n")
    os.replace(tmp, path)
    bak = f" (backup: {path}.bak)" if os.path.exists(path + ".bak") else ""
    print(f"  settings {path}: +{added} hook registrations{bak} — review/trust once via /hooks")
else:
    print(f"  settings {path}: already registered")
PY
}

# register_opencode_global — keep the global opencode plugin entry (~/.config/opencode/opencode.jsonc)
# pointing at this repo's plugin package. opencode 2.x loads plugin PACKAGES (directories) from
# the config "plugin" array — verified live 2026-11-03: bare .mjs entries are rejected
# ("configured plugin path must be a directory") and the plugins dir is not auto-scanned.
# Idempotent: appends the entry only when missing; --uninstall removes exactly our path;
# a config that is not plain JSON (jsonc with comments) is skipped with a hint, never mangled.
register_opencode_global() {
  if ! command -v python3 >/dev/null 2>&1; then
    echo "  skip     opencode.jsonc (python3 not found)" >&2; SKIPPED=$((SKIPPED+1)); return
  fi
  CONFIG_OC="$HOME/.config/opencode/opencode.jsonc" PLUGIN_OC="$REPO/.opencode/plugins/repoprompt-hooks" \
  DRY="$DRY" UNINSTALL="$UNINSTALL" python3 - <<'PY' || { echo "  skip     opencode.jsonc (registration failed)" >&2; SKIPPED=$((SKIPPED+1)); }
import json, os, shutil, sys, tempfile
path = os.environ["CONFIG_OC"]; entry = os.environ["PLUGIN_OC"]
dry = os.environ["DRY"] == "1"; uninst = os.environ["UNINSTALL"] == "1"
try:
    with open(path) as f: data = json.load(f)
except FileNotFoundError:
    data = {}
except Exception:
    print("  skip     opencode.jsonc (not plain JSON — add \"plugin\": [\"%s\"] manually)" % entry)
    sys.exit(0)
if not isinstance(data, dict): data = {}
plugins = data.get("plugin")
if uninst:
    if isinstance(plugins, list) and entry in plugins:
        plugins.remove(entry)
        if plugins: data["plugin"] = plugins
        else: data.pop("plugin", None)
        # fall through to write
    else:
        print("  settings %s: nothing to remove" % path); sys.exit(0)
else:
    if plugins is None:
        plugins = []
    elif not isinstance(plugins, list):
        print("  skip     opencode.jsonc (\"plugin\" key is not a list — merge manually)"); sys.exit(0)
    if entry in plugins:
        print("  settings %s: already registered" % path); sys.exit(0)
    plugins.append(entry); data["plugin"] = plugins
write = True
if dry:
    print("    [dry-run] %s: plugin entry %s (nothing written)" % (path, entry)); sys.exit(0)
d = os.path.dirname(path); os.makedirs(d, exist_ok=True)
if os.path.exists(path): shutil.copy2(path, path + ".bak")
fd, tmp = tempfile.mkstemp(dir=d)
with os.fdopen(fd, "w") as f: json.dump(data, f, indent=2); f.write("\n")
os.replace(tmp, path)
bak = f" (backup: {path}.bak)" if os.path.exists(path + ".bak") else ""
print("  settings %s: plugin entry added%s" % (path, bak))
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

echo "• custom style guide → ~/.agents/style-guide.md  (generic pointer; skills follow it for outbound/published prose when present)"
if [ -n "$STYLE_GUIDE" ]; then
  manage "$STYLE_GUIDE" "$AGENTS_STYLE"
elif [ -e "$AGENTS_STYLE" ]; then
  echo "  present  $AGENTS_STYLE (left as-is this run — pass --style-guide=<path> to manage it)"
else
  echo "  none     — to opt in, re-run with --style-guide=<path> (or STYLE_GUIDE env); no guide is ever created for you, and consumers without one simply skip the house-style step"
fi

echo "• hooks → ~/.claude/hooks  (scanning .agents/hooks/*.py; Claude Code)"
link_sources "$SRC/hooks/*.py" -- "$HOME/.claude/hooks"
register_claude_settings

echo "• opencode global plugin → ~/.config/opencode  (config entry → this repo's plugin package)"
register_opencode_global

shopt -u nullglob

echo
if [ "$UNINSTALL" = 1 ]; then
  echo "Summary: removed=$REMOVED skipped=$SKIPPED. Repo files untouched."
else
  echo "Summary: already-correct=$OK linked-or-fixed=$FIXED conflicts=$CONFLICT."
  [ "$CONFLICT" -gt 0 ] && echo "Note: $CONFLICT conflict(s) need manual resolution (real files where a symlink was expected)." >&2
  echo "Restart RepoPrompt CE to pick up workflow changes."
  echo "Hooks: scripts linked to ~/.claude/hooks/ and registered in ~/.claude/settings.json (Claude Code, global). Codex: global layer ~/.codex/hooks.json (every repo — review/trust once via /hooks); the committed repo .codex/hooks.json remains for consumers without the global layer. opencode: plugin package entry in ~/.config/opencode/opencode.jsonc (global, hot-reloaded) + the project declaration in this repo."
fi
