#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
ISSUE="$SCRIPT_DIR/issue.sh"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/track-work-test.XXXXXX")
trap 'rm -rf "$TMP"' EXIT HUP INT TERM

git init -q "$TMP"
cd "$TMP"

"$ISSUE" new "First issue" --type feature --priority p1 >/dev/null
"$ISSUE" status ISSUE-001 backlog >/dev/null
"$ISSUE" block ISSUE-001 >/dev/null
"$ISSUE" unblock ISSUE-001 >/dev/null
[ "$("$ISSUE" list --status open | cut -f2)" = backlog ]

if "$ISSUE" show ../../README >/dev/null 2>&1; then
  echo "path traversal accepted" >&2; exit 1
fi
if TW_ISSUES_DIR=../escape "$ISSUE" list >/dev/null 2>&1; then
  echo "escaping issues dir accepted" >&2; exit 1
fi
if "$ISSUE" new 'bad " title' >/dev/null 2>&1; then
  echo "unsafe title accepted" >&2; exit 1
fi

create_with_retry() {
  title=$1; attempts=0
  until "$ISSUE" new "$title" --type bug --priority p2 >/dev/null 2>&1; do
    attempts=$((attempts + 1))
    [ "$attempts" -lt 20 ] || { echo "lock did not clear" >&2; return 1; }
    sleep 0.05
  done
}
create_with_retry "Parallel A" & p1=$!
create_with_retry "Parallel B" & p2=$!
wait "$p1"
wait "$p2"

printf 'custom body content\n' > "$TMP/body.md"
"$ISSUE" new "With body" --type feature --priority p3 --body-file "$TMP/body.md" >/dev/null
grep -q "custom body content" .agents/issues/ISSUE-004.md
ln -s "$TMP/body.md" "$TMP/body-link.md"
if "$ISSUE" new "Bad body" --body-file "$TMP/body-link.md" >/dev/null 2>&1; then
  echo "symlink body accepted" >&2; exit 1
fi
if "$ISSUE" new "Bad body" --body-file "$TMP/nope.md" >/dev/null 2>&1; then
  echo "missing body accepted" >&2; exit 1
fi

[ "$("$ISSUE" list | wc -l | tr -d ' ')" = 4 ]
[ "$(grep -c '^| \[ISSUE-' .agents/issues/README.md)" = 4 ]

sh -n "$ISSUE"
echo "issue.sh tests passed"
