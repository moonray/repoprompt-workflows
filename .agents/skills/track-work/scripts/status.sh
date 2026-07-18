#!/bin/sh
# status.sh — backend-agnostic READ-ONLY status of a track-work item. (#8)
#
# Pure ADDITION: does not modify issue.sh, place_on_board.sh, or any existing
# command or expectation. Companion to the obligation <-> track-work link
# (docs/spec/client-activity.obligation-work-link.md), which needs an
# open/closed answer that works regardless of track-work's backend.
#
# Usage:
#   status.sh <ref>
#     <ref> is one of:
#       https://github.com/<owner>/<repo>/issues/<N>   (GitHub issue URL)
#       <owner>/<repo>#<N>                             (GitHub shorthand)
#       ISSUE-<NNN> | <NNN>                            (file-backend item ID,
#                                                        resolved against the
#                                                        current repo's file backend)
#
# Prints exactly one line — "open", "closed", or "unknown[: <reason>]" — and
# exits 0 for a known state, non-zero for unknown. Callers (e.g. the archive
# obligation read-side) MUST treat "unknown" as non-fatal. This accessor never
# mutates the item.
#
# Backend selection follows the reference itself: a GitHub-shaped ref is queried
# via `gh` (the repo is encoded in the ref, so cwd is irrelevant); a bare ID is
# read from the current repo's file backend via issue.sh (so the caller runs it
# in that repo for file refs).

set -u

ref=${1:-}
[ -n "$ref" ] || { echo "unknown: missing reference"; exit 2; }

here=$(cd "$(dirname "$0")" && pwd)
issue_sh="$here/issue.sh"

# --- GitHub-shaped ref -> gh (repo is in the ref; cwd-independent) ---
repo=""
num=""
case "$ref" in
  https://github.com/*/issues/[0-9]*|https://github.com/*/pull/[0-9]*)
    repo=$(printf '%s\n' "$ref" | sed -E 's#https://github\.com/([^/]+)/([^/]+)/.*#\1/\2#')
    num=$(printf '%s\n' "$ref" | sed -E 's#.*/([0-9]+)$#\1#')
    ;;
  */*#[0-9]*)
    repo=${ref%#*}
    num=${ref#*#}
    ;;
esac

if [ -n "$repo" ] && [ -n "$num" ]; then
  command -v gh >/dev/null 2>&1 || { echo "unknown: gh not installed"; exit 3; }
  state=$(gh issue view "$num" -R "$repo" --json state --jq '.state' 2>/dev/null) \
    || { echo "unknown: gh issue view failed for $repo#$num"; exit 4; }
  case "$state" in
    OPEN|open) echo "open"; exit 0 ;;
    CLOSED|closed) echo "closed"; exit 0 ;;
    *) echo "unknown: unexpected state '$state'"; exit 5 ;;
  esac
fi

# --- Bare ID -> file backend (current repo) ---
case "$ref" in
  ISSUE-[0-9]*|[0-9]*) : ;;
  *) echo "unknown: unrecognized reference '$ref'"; exit 6 ;;
esac
[ -r "$issue_sh" ] || { echo "unknown: issue.sh not found at $issue_sh"; exit 7; }
# Resolve ISSUE-<NNN> aliases the same way issue.sh does.
id=$ref
out=$(sh "$issue_sh" show "$id" 2>/dev/null) || { echo "unknown: issue.sh show failed for $id"; exit 8; }
status=$(printf '%s\n' "$out" | sed -n 's/^status:[[:space:]]*//p' | head -1)
case "$status" in
  closed) echo "closed"; exit 0 ;;
  "") echo "unknown: status not found for $id"; exit 9 ;;
  *) echo "open"; exit 0 ;;   # any non-closed file status is "open"
esac
