#!/usr/bin/env bash
# Place a GitHub issue onto a Project board with a given single-select field value.
# Generic: owner/project/field are resolved at runtime from flags, env, or the
# git origin remote. No hardcoded org/project.
#
# Usage:
#   place_on_board.sh <issue-url-or-number> "<option>" [--owner O] [--project P] [--field F]
#   option ∈ the field's single-select values (e.g. Draft, Backlog, "In Progress", Review, Blocked)
#
# Examples:
#   place_on_board.sh 4 Backlog --owner <github-owner> --project 1 --field Stage
#   place_on_board.sh "$(gh issue view 4 --json url --jq .url)" "In Progress"
#
# Env overrides: TW_BOARD_OWNER, TW_BOARD_PROJECT, TW_BOARD_FIELD
set -euo pipefail

command -v jq >/dev/null || { echo "jq is required"; exit 1; }
command -v gh  >/dev/null || { echo "gh is required"; exit 1; }

[ $# -ge 2 ] || { echo "usage: place_on_board.sh <issue-url|number> <option> [--owner O] [--project P] [--field F]"; exit 1; }
ISSUE="$1"; STAGE="$2"; shift 2

OWNER="${TW_BOARD_OWNER:-}"; PROJECT="${TW_BOARD_PROJECT:-}"; FIELD="${TW_BOARD_FIELD:-Stage}"
while [ $# -gt 0 ]; do
  case "$1" in
    --owner)   OWNER="$2"; shift 2;;
    --project) PROJECT="$2"; shift 2;;
    --field)   FIELD="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 1;;
  esac
done

# Resolve a bare issue number to its URL (gh already has repo context).
if [[ "$ISSUE" =~ ^[0-9]+$ ]]; then
  ISSUE=$(gh issue view "$ISSUE" --json url --jq '.url')
fi
NUM="${ISSUE##*/}"

# Default owner from the origin remote (git@github.com:OWNER/NAME.git or https://github.com/OWNER/NAME).
if [ -z "$OWNER" ]; then
  REMOTE=$(git remote get-url origin 2>/dev/null || true)
  OWNER=$(printf '%s\n' "$REMOTE" | sed -E 's#.*(github.com[:/])([^/]+)/.*#\2#')
fi
[ -n "$OWNER" ]   || { echo "couldn't infer --owner (no origin remote?); pass --owner"; exit 1; }
[ -n "$PROJECT" ] || { echo "--project (number or name) is required"; exit 1; }

# If a project name was given, resolve it to a number.
if ! [[ "$PROJECT" =~ ^[0-9]+$ ]]; then
  PROJECT=$(gh project list --owner "$OWNER" --format json \
    --jq '.projects[] | select(.title=="'"$PROJECT"'") | .number')
  [ -n "$PROJECT" ] || { echo "project not found for owner $OWNER"; exit 1; }
fi

PROJECT_ID=$(gh project list --owner "$OWNER" --format json \
  --jq '.projects[] | select(.number=='"$PROJECT"') | .id')
FIELD_ID=$(gh project field-list "$PROJECT" --owner "$OWNER" --format json \
  --jq '.fields[] | select(.name=="'"$FIELD"'") | .id')
OPT_ID=$(gh project field-list "$PROJECT" --owner "$OWNER" --format json \
  --jq '.fields[] | select(.name=="'"$FIELD"'") | .options[] | select(.name=="'"$STAGE"'") | .id')

[ -n "$FIELD_ID" ] || { echo "field '$FIELD' not found on project $PROJECT — create it (see SKILL.md)."; exit 1; }
[ -n "$OPT_ID" ]   || { echo "option '$STAGE' not found on field '$FIELD'."; exit 1; }

# Add to the board (idempotent: if already added, look up the existing item).
ITEM_ID=$(gh project item-add "$PROJECT" --owner "$OWNER" --url "$ISSUE" --format json --jq '.id' 2>/dev/null) || \
  ITEM_ID=$(gh project item-list "$PROJECT" --owner "$OWNER" --format json \
    --jq '.items[] | select((.content.number // 0)=='"$NUM"') | .id')
[ -n "$ITEM_ID" ] || { echo "could not add or find issue #$NUM on project $PROJECT."; exit 1; }

gh project item-edit --id "$ITEM_ID" --project-id "$PROJECT_ID" \
  --field-id "$FIELD_ID" --single-select-option-id "$OPT_ID" >/dev/null

echo "✓ issue #$NUM → $FIELD=$STAGE (project $OWNER/$PROJECT)"
