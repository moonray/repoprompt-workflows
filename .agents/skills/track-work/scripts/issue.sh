#!/bin/sh
# File-based issue backend for the track-work skill.
# POSIX sh + awk/sed. Mutations are serialized and atomically replace files.
#
# Usage:
#   issue.sh new     "<title>" [--type bug|feature|enhancement|decision] [--priority p0|p1|p2|p3] [--label a,b]
#   issue.sh list    [--status open|closed|draft|backlog|in-progress|review|blocked]
#   issue.sh show    <ID>
#   issue.sh status  <ID> <draft|backlog|in-progress|review|blocked|closed>
#   issue.sh block   <ID>
#   issue.sh unblock <ID> [draft|backlog|in-progress|review]
#   issue.sh close   <ID>
#   issue.sh reopen  <ID> [draft|backlog|in-progress|review]
#
# Env: TW_ISSUES_DIR (default .agents/issues; repo-relative, no symlinks)
set -eu

DIR="${TW_ISSUES_DIR:-.agents/issues}"
LOCK=""

fail() { printf '%s\n' "$*" >&2; exit 1; }

case "$DIR" in
  ""|/*|*..*) fail "TW_ISSUES_DIR must be a repo-relative path without '..': $DIR" ;;
esac

repo_root=$(git rev-parse --show-toplevel 2>/dev/null) || fail "issue.sh must run inside a git repository"
case "$DIR" in ./*) DIR=${DIR#./};; esac
DIR="$repo_root/$DIR"

validate_id() {
  case "${1:-}" in
    ISSUE-[0-9][0-9][0-9]*) suffix=${1#ISSUE-}; case "$suffix" in *[!0-9]*) fail "invalid issue ID: $1";; esac;;
    *) fail "invalid issue ID: ${1:-}";;
  esac
}
validate_status() { case "${1:-}" in draft|backlog|in-progress|review|blocked|closed) :;; *) fail "invalid status: ${1:-}";; esac; }
validate_reopen_status() { case "${1:-}" in draft|backlog|in-progress|review) :;; *) fail "invalid reopen status: ${1:-}";; esac; }
validate_type() { case "${1:-}" in bug|feature|enhancement|decision) :;; *) fail "invalid type: ${1:-}";; esac; }
validate_priority() { case "${1:-}" in p0|p1|p2|p3) :;; *) fail "invalid priority: ${1:-}";; esac; }
validate_scalar() {
  value=$1; name=$2
  [ -n "$value" ] || fail "$name must not be empty"
  case "$value" in *'
'*|*'
'*|*'"'*) fail "$name contains an unsupported quote or newline";; esac
}
validate_labels() {
  case "$1" in *'
'*|*'
'*|*'['*|*']'*) fail "labels contain unsupported characters";; esac
}

ensure_dir() {
  current="$repo_root"
  old_ifs=$IFS; IFS=/
  set -- ${DIR#"$repo_root"/}
  IFS=$old_ifs
  for part in "$@"; do
    [ -n "$part" ] || continue
    current="$current/$part"
    if [ -L "$current" ]; then fail "issues path must not contain symlinks: $current"; fi
    if [ -e "$current" ] && [ ! -d "$current" ]; then fail "issues path component is not a directory: $current"; fi
    [ -d "$current" ] || mkdir "$current"
  done
  [ ! -L "$DIR/README.md" ] || fail "refusing symlink index: $DIR/README.md"
}

issue_path() {
  validate_id "$1"
  path="$DIR/$1.md"
  [ ! -L "$path" ] || fail "refusing symlink issue: $path"
  printf '%s\n' "$path"
}

getf() {
  awk -v k="$1" 'BEGIN{f=0} /^---$/{c++} c==1 && $0 ~ "^"k":" && !f { sub("^"k": *",""); gsub(/^"|"$/,""); print; f=1 }' "$2"
}

md_escape() { printf '%s' "$1" | sed 's/|/\\|/g'; }

write_index() {
  tmp=$(mktemp "$DIR/.README.XXXXXX") || fail "could not create index temp file"
  {
    printf '%s\n\n' "# Issues"
    printf '%s\n\n' "Shared team backlog - committed. Managed by the \`track-work\` skill (\`issue.sh\`)."
    printf '%s\n' "| ID | Status | Type | Priority | Title |"
    printf '%s\n' "|----|--------|------|----------|-------|"
    for f in "$DIR"/ISSUE-*.md; do
      [ -f "$f" ] && [ ! -L "$f" ] || continue
      id=$(getf id "$f")
      validate_id "$id"
      printf '| [%s](%s) | %s | %s | %s | %s |\n' \
        "$id" "$(basename "$f")" "$(getf status "$f")" "$(getf type "$f")" "$(getf priority "$f")" "$(md_escape "$(getf title "$f")")"
    done
  } > "$tmp" || { rm -f "$tmp"; fail "could not write index"; }
  mv "$tmp" "$DIR/README.md"
}

acquire_lock() {
  ensure_dir
  LOCK="$DIR/.track-work.lock"
  mkdir "$LOCK" 2>/dev/null || fail "another track-work mutation is in progress: $LOCK"
  trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT HUP INT TERM
}

next_id() {
  max=0
  for f in "$DIR"/ISSUE-*.md; do
    [ -f "$f" ] && [ ! -L "$f" ] || continue
    base=$(basename "$f")
    case "$base" in ISSUE-[0-9]*.md) n=${base#ISSUE-}; n=${n%.md};; *) continue;; esac
    n=$(expr "$n" + 0 2>/dev/null || printf '0')
    [ "$n" -gt "$max" ] && max=$n
  done
  printf 'ISSUE-%03d' $((max + 1))
}

cmd_new() {
  [ $# -ge 1 ] || fail "usage: issue.sh new <title> [--type ..] [--priority ..] [--label ..]"
  title=$1; shift; type=bug; priority=p2; labels=""
  validate_scalar "$title" title
  while [ $# -gt 0 ]; do
    case "$1" in
      --type|--priority|--label) [ $# -ge 2 ] || fail "missing value for $1";;
      *) fail "unknown argument: $1";;
    esac
    case "$1" in --type) type=$2;; --priority) priority=$2;; --label) labels=$2;; esac
    shift 2
  done
  validate_type "$type"; validate_priority "$priority"; validate_labels "$labels"
  acquire_lock
  id=$(next_id); f=$(issue_path "$id")
  [ ! -e "$f" ] || fail "issue already exists: $f"
  tmp=$(mktemp "$DIR/.$id.XXXXXX") || fail "could not create issue temp file"
  cat > "$tmp" <<EOF
---
id: $id
title: "$title"
status: draft
previous_status: draft
type: $type
priority: $priority
labels: [$labels]
created: $(date +%Y-%m-%d)
---

## What
$title

## Repro / context
<!-- bugs: steps, expected vs actual -->

## Acceptance criteria
- [ ] 

## Detail / links
<!-- spec / plan / loop / test paths (repo-relative) -->
EOF
  mv "$tmp" "$f"; write_index
  printf '%s  (%s)\n' "$f" "$id"
}

cmd_list() {
  ensure_dir; st=""
  while [ $# -gt 0 ]; do
    case "$1" in --status) [ $# -ge 2 ] || fail "missing value for --status"; st=$2; shift 2;; *) fail "unknown argument: $1";; esac
  done
  [ -z "$st" ] || [ "$st" = open ] || validate_status "$st"
  for f in "$DIR"/ISSUE-*.md; do
    [ -f "$f" ] && [ ! -L "$f" ] || continue
    status=$(getf status "$f")
    if [ "$st" = open ]; then [ "$status" != closed ] || continue
    elif [ -n "$st" ] && [ "$status" != "$st" ]; then continue; fi
    printf '%s\t%s\t%s\n' "$(getf id "$f")" "$status" "$(getf title "$f")"
  done
}

cmd_show() {
  [ $# -eq 1 ] || fail "usage: issue.sh show <ID>"
  f=$(issue_path "$1"); [ -f "$f" ] || fail "not found: $f"; cat "$f"
}

set_field() {
  f=$(issue_path "$1"); key=$2; value=$3
  [ -f "$f" ] || fail "not found: $f"
  tmp=$(mktemp "$DIR/.$1.XXXXXX") || fail "could not create issue temp file"
  awk -v k="$key" -v v="$value" 'BEGIN{done=0} /^---$/{c++} c==1 && $0 ~ "^"k":" && !done {print k": "v; done=1; next} {print} END{if(!done) exit 42}' "$f" > "$tmp" || { rm -f "$tmp"; fail "missing frontmatter field '$key' in $1"; }
  mv "$tmp" "$f"
}

cmd_status() {
  [ $# -eq 2 ] || fail "usage: issue.sh status <ID> <state>"
  validate_status "$2"; acquire_lock
  current=$(getf status "$(issue_path "$1")")
  [ "$2" = blocked ] || set_field "$1" previous_status "$2"
  [ "$2" != blocked ] || [ "$current" = blocked ] || set_field "$1" previous_status "$current"
  set_field "$1" status "$2"; write_index; printf '%s -> %s\n' "$1" "$2"
}
cmd_block() { [ $# -eq 1 ] || fail "usage: issue.sh block <ID>"; cmd_status "$1" blocked; }
cmd_unblock() {
  [ $# -ge 1 ] && [ $# -le 2 ] || fail "usage: issue.sh unblock <ID> [state]"
  f=$(issue_path "$1"); target=${2:-$(getf previous_status "$f")}; validate_reopen_status "$target"; cmd_status "$1" "$target"
}
cmd_close() { [ $# -eq 1 ] || fail "usage: issue.sh close <ID>"; cmd_status "$1" closed; }
cmd_reopen() {
  [ $# -ge 1 ] && [ $# -le 2 ] || fail "usage: issue.sh reopen <ID> [state]"
  target=${2:-backlog}; validate_reopen_status "$target"; cmd_status "$1" "$target"
}

case "${1:-}" in
  new|list|show|status|block|unblock|close|reopen) cmd=$1; shift; "cmd_$cmd" "$@";;
  *) fail "usage: issue.sh {new|list|show|status|block|unblock|close|reopen} ...";;
esac
