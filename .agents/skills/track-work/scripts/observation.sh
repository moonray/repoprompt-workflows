#!/bin/sh
# observation.sh — backend-agnostic READ-ONLY *rich* observation of a track-work item.
#
# Additive companion to status.sh (which is unchanged and still returns one open/closed
# line). Returns the fields the archive obligation layer needs to compute a state-episode
# version for source-backed closure (docs/spec/obligation-terminal-closure.md): the
# item's authoritative close reason and its close/reopen event history. Never mutates
# the item; never infers "completed" from "closed".
#
# Usage: observation.sh <ref>
#   ref: GitHub issue URL | <owner>/<repo>#<N> | file item ID (ISSUE-<NNN> | <NNN>)
#
# Emits one JSON line:
#   {"state","state_reason","events":[{"event","id"}],"backend","url","fetched_at"}
#
# state_reason is null when the backend cannot supply it authoritatively (the file
# backend, or any value GitHub does not return). events is the close/reopen history
# with stable provider ids (GitHub databaseId), oldest-first; empty for the file
# backend. exits 0 for a known state, non-zero for unknown. Callers MUST treat
# unknown/non-zero as non-fatal.

set -u

ref=${1:-}
[ -n "$ref" ] || { echo '{"state":"unknown","reason":"missing reference"}'; exit 2; }

now=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || printf '')

# --- GitHub-shaped ref -> gh (repo is in the ref; cwd-independent) ---
repo=""; num=""
case "$ref" in
  https://github.com/*/issues/[0-9]*|https://github.com/*/pull/[0-9]*)
    repo=$(printf '%s\n' "$ref" | sed -E 's#https://github\.com/([^/]+)/([^/]+)/.*#\1/\2#')
    num=$(printf '%s\n' "$ref" | sed -E 's#.*/([0-9]+)$#\1#')
    ;;
  */*#[0-9]*)
    repo=${ref%#*}; num=${ref#*#}
    ;;
esac

if [ -n "$repo" ] && [ -n "$num" ]; then
  command -v gh >/dev/null 2>&1 || { echo '{"state":"unknown","reason":"gh not installed"}'; exit 3; }
  command -v jq >/dev/null 2>&1 || { echo '{"state":"unknown","reason":"jq not installed"}'; exit 3; }
  meta=$(gh issue view "$num" -R "$repo" --json state,stateReason,url 2>/dev/null) \
    || { echo '{"state":"unknown","reason":"gh issue view failed"}'; exit 4; }
  events=$(gh api "repos/$repo/issues/$num/events?per_page=100" \
    --jq '[.[] | select(.event=="closed" or .event=="reopened") | {"event":.event,"id":(.id|tostring)}]' 2>/dev/null) \
    || events='[]'
  jq -nc --argjson m "$meta" --argjson e "$events" --arg now "$now" \
    '{state:($m.state | if .=="OPEN" then "open" elif .=="CLOSED" then "closed" else "unknown" end),
      state_reason:($m.stateReason),
      events:$e, backend:"github", url:($m.url // null), fetched_at:$now}'
  exit 0
fi

# --- Bare ID -> file backend (current repo) ---
here=$(cd "$(dirname "$0")" && pwd); issue_sh="$here/issue.sh"
case "$ref" in
  ISSUE-[0-9]*|[0-9]*) : ;;
  *) echo '{"state":"unknown","reason":"unrecognized reference"}'; exit 6 ;;
esac
[ -r "$issue_sh" ] || { echo '{"state":"unknown","reason":"issue.sh not found"}'; exit 7; }
out=$(sh "$issue_sh" show "$ref" 2>/dev/null) || { echo '{"state":"unknown","reason":"issue.sh show failed"}'; exit 8; }
status=$(printf '%s\n' "$out" | sed -n 's/^status:[[:space:]]*//p' | head -1)
state="open"
case "$status" in
  closed) state="closed" ;;
  "") echo '{"state":"unknown","reason":"status not found"}'; exit 9 ;;
esac
# File backend has NO authoritative state_reason or event history, so it cannot
# satisfy a work_item_state(closed, completed) criterion (never infer completed).
printf '{"state":"%s","state_reason":null,"events":[],"backend":"file","url":null,"fetched_at":"%s"}\n' "$state" "$now"
exit 0
