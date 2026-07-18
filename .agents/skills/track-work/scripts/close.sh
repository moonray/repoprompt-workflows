#!/bin/sh
# close.sh — backend-agnostic close of a track-work item with a reason. (#8)
#
# Pure ADDITION: does not modify issue.sh, place_on_board.sh, status.sh, or any
# existing command. Companion to status.sh for the obligation close-on-terminal
# projection (docs/spec/client-activity.obligation-work-link.md OWL-004).
#
# Usage:
#   close.sh <ref> [<reason>]
#     <ref> as in status.sh (GitHub issue URL / owner/repo#N / file ISSUE-<NNN>)
#
# Prints "closed" on success or "failed: <reason>" on failure (non-zero exit).
# GitHub: adds <reason> as a comment, then closes the issue. File: closes the
# item (the reason lives on the archive side; the file backend records status).
# This accessor MUTATES the item — callers MUST gate it behind confirmation.

set -u

ref=${1:-}
reason=${2:-}
[ -n "$ref" ] || { echo "failed: missing reference"; exit 2; }

here=$(cd "$(dirname "$0")" && pwd)
issue_sh="$here/issue.sh"

# --- GitHub-shaped ref -> gh ---
repo=""
num=""
case "$ref" in
  https://github.com/*/issues/[0-9]*)
    repo=$(printf '%s\n' "$ref" | sed -E 's#https://github\.com/([^/]+)/([^/]+)/.*#\1/\2#')
    num=$(printf '%s\n' "$ref" | sed -E 's#.*/([0-9]+)$#\1#')
    ;;
  */*#[0-9]*)
    repo=${ref%#*}
    num=${ref#*#}
    ;;
esac

if [ -n "$repo" ] && [ -n "$num" ]; then
  command -v gh >/dev/null 2>&1 || { echo "failed: gh not installed"; exit 3; }
  if [ -n "$reason" ]; then
    printf '%s\n' "$reason" | gh issue comment "$num" -R "$repo" --body-file - 2>/dev/null \
      || { echo "failed: gh issue comment failed for $repo#$num"; exit 4; }
  fi
  gh issue close "$num" -R "$repo" 2>/dev/null \
    || { echo "failed: gh issue close failed for $repo#$num"; exit 5; }
  echo "closed"
  exit 0
fi

# --- Bare ID -> file backend (current repo) ---
case "$ref" in
  ISSUE-[0-9]*|[0-9]*) : ;;
  *) echo "failed: unrecognized reference '$ref'"; exit 6 ;;
esac
[ -r "$issue_sh" ] || { echo "failed: issue.sh not found at $issue_sh"; exit 7; }
sh "$issue_sh" close "$ref" >/dev/null 2>&1 || { echo "failed: issue.sh close failed for $id"; exit 8; }
echo "closed"
exit 0
