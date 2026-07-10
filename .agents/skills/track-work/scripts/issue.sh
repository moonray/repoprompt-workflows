#!/bin/sh
# File-based issue backend for the track-work skill.
# POSIX sh + awk/sed — no Python/Node dependency. Operates on a committed backlog.
#
# Usage:
#   issue.sh new    "<title>" [--type bug|feature|enhancement|decision] [--priority p0|p1|p2|p3] [--label a,b]
#   issue.sh list   [--status open|closed|draft|backlog|in-progress|review|blocked]
#   issue.sh show   <ID>
#   issue.sh close  <ID>
#   issue.sh reopen <ID>
#
# Env: TW_ISSUES_DIR  (default .agents/issues)
# IDs are ISSUE-NNN (zero-padded, immutable — never renumber).
set -eu

DIR="${TW_ISSUES_DIR:-.agents/issues}"

# getf <key> <file>  — first value of `key:` within the frontmatter block.
getf() {
  awk -v k="$1" 'BEGIN{f=0} /^---$/{c++} c==1 && $0 ~ "^"k":" && !f { sub("^"k": *",""); gsub(/^"|"$/,""); print; f=1 }' "$2"
}

write_index() {
  {
    echo "# Issues"
    echo ""
    echo "Shared team backlog — committed. Managed by the \`track-work\` skill (\`issue.sh\`)."
    echo ""
    echo "| ID | Status | Type | Priority | Title |"
    echo "|----|--------|------|----------|-------|"
    for f in "$DIR"/ISSUE-*.md; do
      [ -e "$f" ] || continue
      id=$(getf id "$f")
      printf '| [%s](%s) | %s | %s | %s | %s |\n' \
        "$id" "$(basename "$f")" "$(getf status "$f")" "$(getf type "$f")" "$(getf priority "$f")" "$(getf title "$f")"
    done
  } > "$DIR/README.md"
}

next_id() {
  max=0
  for f in "$DIR"/ISSUE-*.md; do
    [ -e "$f" ] || continue
    n=$(basename "$f" | sed -E 's/ISSUE-0*([0-9]+)\.md/\1/')
    n=$(expr "$n" + 0 2>/dev/null || echo 0)
    [ "$n" -gt "$max" ] && max=$n
  done
  printf 'ISSUE-%03d' $((max + 1))
}

cmd_new() {
  [ $# -ge 1 ] || { echo "usage: issue.sh new <title> [--type ..] [--priority ..] [--label ..]"; exit 1; }
  title=$1; shift
  type=bug; priority=p2; labels=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --type)     type=$2; shift 2;;
      --priority) priority=$2; shift 2;;
      --label)    labels=$2; shift 2;;
      *) shift;;
    esac
  done
  mkdir -p "$DIR"
  id=$(next_id)
  f="$DIR/$id.md"
  cat > "$f" <<EOF
---
id: $id
title: "$title"
status: open
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
  write_index
  echo "$f  ($id)"
}

cmd_list() {
  st=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --status) st="$2"; shift 2;;
      -*) shift;;
      *) st="$1"; shift;;
    esac
  done
  for f in "$DIR"/ISSUE-*.md; do
    [ -e "$f" ] || continue
    status=$(getf status "$f")
    [ -n "$st" ] && [ "$status" != "$st" ] && continue
    printf '%s\t%s\t%s\n' "$(getf id "$f")" "$status" "$(getf title "$f")"
  done
}

cmd_show() {
  [ -n "${1:-}" ] || { echo "usage: issue.sh show <ID>"; exit 1; }
  f="$DIR/$1.md"
  [ -e "$f" ] || { echo "not found: $f"; exit 1; }
  cat "$f"
}

# set_field <ID> <field> <value>  — replace one frontmatter key's value.
set_field() {
  f="$DIR/$1.md"
  [ -e "$f" ] || { echo "not found: $f"; exit 1; }
  tmp=$(mktemp)
  awk -v k="$2" -v v="$3" 'BEGIN{done=0} /^---$/{c++} c==1 && $0 ~ "^"k":" && !done {print k": "v; done=1; next} {print}' "$f" > "$tmp" && mv "$tmp" "$f"
}

cmd_close()  { set_field "$1" status closed; write_index; echo "closed $1"; }
cmd_reopen() { set_field "$1" status open;   write_index; echo "reopened $1"; }

case "${1:-}" in
  new)    shift; cmd_new "$@";;
  list)   shift; cmd_list "$@";;
  show)   shift; cmd_show "$@";;
  close)  shift; cmd_close "$@";;
  reopen) shift; cmd_reopen "$@";;
  *) echo "usage: issue.sh {new|list|show|close|reopen} ..."; exit 1;;
esac
