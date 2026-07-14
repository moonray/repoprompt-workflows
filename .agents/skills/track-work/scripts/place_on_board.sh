#!/usr/bin/env bash
# Place one canonical GitHub issue URL on a Project single-select field.
set -euo pipefail

command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }
command -v gh >/dev/null || { echo "gh is required" >&2; exit 1; }

usage() { echo "usage: place_on_board.sh <https://github.com/OWNER/REPO/issues/N> <option> --owner O --project P [--field F]" >&2; exit 1; }
[ $# -ge 2 ] || usage
ISSUE=$1; STAGE=$2; shift 2
OWNER="${TW_BOARD_OWNER:-}"; PROJECT="${TW_BOARD_PROJECT:-}"; FIELD="${TW_BOARD_FIELD:-Stage}"
while [ $# -gt 0 ]; do
  case "$1" in
    --owner|--project|--field) [ $# -ge 2 ] || usage;;
    *) usage;;
  esac
  case "$1" in --owner) OWNER=$2;; --project) PROJECT=$2;; --field) FIELD=$2;; esac
  shift 2
done

[[ "$ISSUE" =~ ^https://github\.com/([^/]+)/([^/]+)/issues/([0-9]+)$ ]] || { echo "canonical GitHub issue URL required: $ISSUE" >&2; exit 1; }
ISSUE_OWNER=${BASH_REMATCH[1]}; ISSUE_REPO=${BASH_REMATCH[2]}; NUM=${BASH_REMATCH[3]}
[ -n "$OWNER" ] || OWNER=$ISSUE_OWNER
[ -n "$PROJECT" ] || { echo "--project is required" >&2; exit 1; }

# Verify that the URL still identifies the intended repository before mutation.
CANONICAL=$(gh issue view "$NUM" -R "$ISSUE_OWNER/$ISSUE_REPO" --json url --jq .url)
[ "$CANONICAL" = "$ISSUE" ] || { echo "issue identity mismatch: $CANONICAL" >&2; exit 1; }

projects=$(gh project list --owner "$OWNER" --limit 100 --format json)
if [[ "$PROJECT" =~ ^[0-9]+$ ]]; then
  PROJECT_NUM=$PROJECT
else
  PROJECT_NUM=$(jq -r --arg title "$PROJECT" '.projects[] | select(.title==$title) | .number' <<<"$projects")
fi
[ -n "$PROJECT_NUM" ] && [ "$PROJECT_NUM" != null ] || { echo "project not found for owner $OWNER" >&2; exit 1; }
PROJECT_ID=$(jq -r --argjson number "$PROJECT_NUM" '.projects[] | select(.number==$number) | .id' <<<"$projects")
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != null ] || { echo "project ID not found: $OWNER/$PROJECT_NUM" >&2; exit 1; }

fields=$(gh project field-list "$PROJECT_NUM" --owner "$OWNER" --limit 100 --format json)
FIELD_ID=$(jq -r --arg field "$FIELD" '.fields[] | select(.name==$field) | .id' <<<"$fields")
OPT_ID=$(jq -r --arg field "$FIELD" --arg stage "$STAGE" '.fields[] | select(.name==$field) | .options[]? | select(.name==$stage) | .id' <<<"$fields")
[ -n "$FIELD_ID" ] && [ "$FIELD_ID" != null ] || { echo "field '$FIELD' not found on project $PROJECT_NUM" >&2; exit 1; }
[ -n "$OPT_ID" ] && [ "$OPT_ID" != null ] || { echo "option '$STAGE' not found on field '$FIELD'" >&2; exit 1; }

if ! ITEM_JSON=$(gh project item-add "$PROJECT_NUM" --owner "$OWNER" --url "$ISSUE" --format json 2>&1); then
  # Preserve non-idempotency errors. Only search after item-add reports an existing item.
  case "$ITEM_JSON" in *already*|*exists*) :;; *) printf '%s\n' "$ITEM_JSON" >&2; exit 1;; esac
  items=$(gh project item-list "$PROJECT_NUM" --owner "$OWNER" --limit 1000 --format json)
  ITEM_ID=$(jq -r --arg url "$ISSUE" '.items[] | select(.content.url==$url) | .id' <<<"$items")
else
  ITEM_ID=$(jq -r .id <<<"$ITEM_JSON")
fi
[ -n "$ITEM_ID" ] && [ "$ITEM_ID" != null ] || { echo "could not add or find $ISSUE on project $OWNER/$PROJECT_NUM" >&2; exit 1; }

gh project item-edit --id "$ITEM_ID" --project-id "$PROJECT_ID" --field-id "$FIELD_ID" --single-select-option-id "$OPT_ID" >/dev/null
echo "issue $ISSUE -> $FIELD=$STAGE (project $OWNER/$PROJECT_NUM)"
