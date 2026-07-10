---
name: track-work
description: Use FIRST when work is about to start on any repo — a bug is reported, a feature/enhancement is requested, an open question or design decision is raised, someone asks to "track"/"log"/"add a ticket for" something, asks what is open / in-progress / done, or an agent is about to implement a change that has no tracking item. Creates or updates one tracking item in GitHub Issues (when the repo has GitHub) or a committed file-based backlog under .agents/issues/ (when it doesn't), applies the repo's own label/taxonomy conventions, and links the spec/plan/loop/research files as the detail layer. Replaces ad-hoc issues_N.md reports and hand-maintained status lists.
---

# Track Work — one live status ledger per repo

## Intent

Every bug, feature, enhancement, or decision a repo works on is tracked as **one work item** in **one place**: **GitHub Issues** when the repo has a GitHub remote, else a committed file-based backlog under `.agents/issues/`. That item is the **status** source of truth (draft / backlog / in-progress / review / done). The repo's long-form files — specs, plans, loops, research — stay as the **detail** layer and are *linked* from the item, never duplicated.

This is the entry gate: **no implementation, no spec edit, no test starts before the work has a tracking item** (or is confirmed to update an existing one).

## Step 0 — detect the backend

Run in order; pick the first that holds:

1. **Override** — a `backend:` value in the repo config (Step 1) or env `TRACK_WORK_BACKEND` (`github` | `file`) wins always. Covers "GitHub exists but I want to draft locally first."
2. **GitHub** — `gh auth status` succeeds **and** `git remote get-url origin` is a GitHub URL **and** `gh repo view --json owner,name` succeeds → **GitHub Issues**.
3. **File** — anything else (no remote, `gh` missing/not authed, issues disabled, non-GitHub host) → **file backend**.

If GitHub is reachable but `gh issue list` reports issues are disabled, fall back to **file** and tell the user.

## Step 1 — read repo conventions (cheap, capped)

Before creating, look for a config in this order; use the first found:

1. `.agents/track-work.config.md` — a fenced ```yaml block (preferred, structured).
2. A `track-work` config block inside `AGENTS.md` or `CLAUDE.md`.
3. None → use the built-in **defaults** below.

No config is auto-created and no wizard runs. The skill detects what it can — backend from the git remote + `gh`, labels from `gh label list` — and falls back to defaults for the rest. Drop a `.agents/track-work.config.md` only when the repo has specifics GitHub can't expose (a Project board, personas, custom redaction, non-standard label cardinality); the schema is below.

For the **GitHub** backend also run `gh label list` and group by prefix (`type:`, `area:`, `priority:`, `status:`, …). These are the repo's *actual* labels and always beat any list written in a config. For the **file** backend the config's label dimensions are the source (there is no GitHub to ask).

**Default (no config):** generic labels `type:bug|feature|enhancement|decision`, `priority:p0|p1|p2|p3`, `status:draft|backlog|in-progress|review|blocked`; no board; close = set status closed (+ commit `Fixes #N` if git); redact obvious secrets/absolute paths; detail files discovered loosely under `docs/`.

### Config schema (what a repo can express)

Only fill in what differs from the defaults. Labels are discovered from `gh label list` — do **not** re-list them here; this only carries what GitHub *can't* tell the skill (cardinality, board, close-gate, personas, redaction, detail dirs, legacy).

```yaml
backend: auto              # auto | github | file
issues_dir: .agents/issues # file backend; committed (shared backlog)
labels:
  dimensions:              # per-prefix cardinality the skill enforces
    - { prefix: type,     count: exactly1 }
    - { prefix: area,     count: at_least1 }
    - { prefix: priority, count: exactly1 }
    - { prefix: status,   count: exactly1 }
    # a dimension may use `prefixes: [a, b]` to enforce cardinality across a group
    # (e.g. exactly-one trace across `pass:*` and `from:*`):
    # - { prefixes: [pass, from], count: at_most1 }
github:
  board:                   # optional GitHub Project board
    owner: <org>           # resolved from origin if omitted
    project: <number-or-name>
    field: Stage
    map: { draft: Draft, backlog: Backlog, in-progress: "In Progress", review: Review, blocked: Blocked }
close_gate:
  enforcement: .github/workflows/issue-close-check.yml   # absent = not enforced
  require_pushed: true   # done requires the change landed on the default branch (PR merged / trunk push), not just local
  locking_test_dir: tests
  exempt_labels: [wontfix, duplicate, invalid, type:decision, type:question]
redaction:
  repo_visibility: private   # private | public — tightens redaction when public
  secrets: [EXAMPLE_API_KEY]
  redact_absolute_paths: true
  mirror_repos: [owner/repo-to-never-sync]
personas:
  file: docs/product/personas.md
  applies_to_types: [feature, enhancement, decision]
detail_dirs:
  spec: docs/spec
  plan: docs/plans
  progress: docs/progress
  research: docs/research
legacy_paths_do_not_write: [docs/issues_*.md]
```

## When to add a config (and why)

Defaults cover most repos — **no config is written unless a signal below is present.** When one is, the skill drafts `.agents/track-work.config.md` with the detected values filled in (you confirm before it's written; commit it so teammates inherit it). Each field exists for a concrete reason:

| Signal (detectable on first run) | Why a config helps | Field |
|---|---|---|
| `gh project list` returns a project | keep the board column in sync with `status:*` automatically, not by hand | `github.board` |
| `.github/workflows/*issue-close*` exists | honor close enforcement — don't `gh issue close` a fix the workflow will reopen | `close_gate.enforcement` |
| `.env.example` names `*_KEY`/`*_TOKEN`/`*_SECRET` | redact those before filing so bodies never leak them | `redaction.secrets` |
| repo is public, or has a public mirror | tighten redaction (real file/library names, absolute paths) | `redaction.repo_visibility`, `mirror_repos` |
| `docs/{spec,plans,progress,…}` exist | link the right detail dirs from each issue body | `detail_dirs` |
| a personas/roles doc exists (e.g. `docs/product/*personas*`) | persona-weighted prioritization + the body's Personas line | `personas` |
| labels use a custom prefix beyond type/priority/status/area | enforce custom cardinality (e.g. exactly-one trace across two prefixes) | `labels.dimensions` |

First-run detection (run when no config exists):
```bash
OWNER=$(git remote get-url origin | sed -E 's#.*(github.com[:/])([^/]+)/.*#\2#')
gh project list --owner "$OWNER" --limit 100 2>/dev/null                              # board?
ls .github/workflows/ 2>/dev/null | grep -i 'close'                                 # close-gate?
grep -oE '[A-Z0-9_]*(KEY|TOKEN|SECRET)[A-Z0-9_]*' .env.example 2>/dev/null | sort -u   # secrets?
gh repo view --json visibility 2>/dev/null                                          # public?
ls docs/ 2>/dev/null                                                                # detail dirs?
find docs -iname '*persona*' 2>/dev/null | head                                    # personas?
gh label list --json name --jq '.[].name' 2>/dev/null | sed -E 's/:.*//' | sort -u   # custom prefixes?
```

## GitHub backend workflow

### 0. Ensure labels exist (first issue in a fresh repo)
If `gh label list` is missing the core dimensions (`type:`, `priority:`, `status:`), seed a minimal organized set once so issues don't pile up unlabelled. Idempotent (`--force` updates in place); run only the labels that are missing; never delete labels the repo already has. Announce what you seeded. Reversible with `gh label delete <name>`.
```bash
gh label create type:bug         --color D73A4A --force
gh label create type:feature     --color 0E8A16 --force
gh label create type:enhancement --color A2EEEF --force
gh label create type:decision    --color FBCA04 --force
gh label create priority:p0      --color B60205 --force   # blocker
gh label create priority:p1      --color D93F0B --force   # high
gh label create priority:p2      --color FBCA04 --force   # normal
gh label create priority:p3      --color 6E7781 --force   # parked
gh label create status:draft       --color 6E7781 --force
gh label create status:backlog    --color FBCA04 --force
gh label create status:in-progress --color 1D76DB --force
gh label create status:review     --color 5319E7 --force
gh label create status:blocked    --color B60205 --force
```

### 1. Classify the request
"It's broken / wrong / freezes" → `type:bug`. Net-new "I want to be able to…" → `type:feature`. "It should also / better" → `type:enhancement`. "Should we / can we" → `type:decision`. If `personas` is configured and the type is in `applies_to_types`, note the persona(s) in the body so prioritization is persona-weighted.

### 2. Search before you create (avoid duplicates)
```bash
gh issue list --state all --search "<keywords>" --json number,title,state,labels
```
If a match exists → update it (comment / relabel / reopen) instead of duplicating. Cross-link with `#<n>`.

### 3. Create the issue
Apply labels from the repo's actual set (`gh label list`), honoring the configured **cardinality** (e.g. exactly one `type:`, one `priority:`, one `status:`; ≥1 `area:`). Write the body to a temp file first (handles multi-line + backticks).
```bash
gh issue create --title "<imperative title, <=80 chars>" \
  --label "type:bug,area:ui,priority:p1,status:draft" --body-file /tmp/issue-body.md
```

### 4. Link the detail files
Reference the spec / plan / loop / research paths (from `detail_dirs`, repo-relative) in the body. If a fresh deep-plan or loop is needed, create it under the configured dir and link it — that is where the long-form narrative lives, never the issue body.

### 5. Place on the board (only if `github.board` configured)
Move the issue's single-select field (e.g. `Stage`) to match its `status:*` label, using this skill's **runtime-resolved** helper (no hardcoded owner/project — it reads flags/env/origin):
```bash
bash <this-skill>/scripts/place_on_board.sh <issue-number-or-url> "<Stage>" \
  --owner <org> --project <num> --field Stage
```
Board ops need the `project` scope: `gh auth refresh -s project,read:project` (comma, no space).

### 6. Implement, then verify-and-close
- Run `spec-plan-readiness` before coding if a spec+plan exist; `spec-quality` when drafting spec changes; `test-quality` when adding the regression test.
- Commit with the `commit` skill, referencing `#<issue>` in the message.
- **Close** per the repo's close gate (below).

## File backend workflow (no GitHub)

Use this skill's helper for the fiddly parts (ID allocation + index sync):
```bash
bash <this-skill>/scripts/issue.sh new    "<title>" --type bug --priority p1 [--label x,y]
bash <this-skill>/scripts/issue.sh list   [--status open]
bash <this-skill>/scripts/issue.sh show   <ID>
bash <this-skill>/scripts/issue.sh close  <ID>     # sets status: closed, updates index
bash <this-skill>/scripts/issue.sh reopen <ID>
```
- Items live as `<issues_dir>/<ID>.md` (default `.agents/issues/ISSUE-NNN.md`) with YAML frontmatter (`id`, `title`, `status`, `type`, `priority`, `created`, `labels`). **IDs are immutable** — never renumber or rename them; they are referenced from commits, specs, and other items.
- A synced index table lives at `<issues_dir>/README.md`.
- The issues dir is the **shared team backlog** — it is committed. If `git check-ignore <issues_dir>` says it is ignored, warn the user and fix it (gitignore negation like `!.agents/issues/`, or move the dir) before writing anything.

## Status lifecycle

```
draft → backlog → in-progress → review → CLOSE (done)
                  (any step ⇄ blocked; unblock returns to the prior step)
```
- `draft`: captured, not ready (needs repro / a decision).
- `backlog`: triaged, acceptance criteria clear, waiting to start.
- `in-progress`: actively being worked.
- `review`: code complete and **posted for verification** — a PR opened / branch pushed (PR-based flow), or committed + pushed to the default branch (trunk-based flow). Verification (tests, locking test, spec ratification, human review) happens here. `review` ≠ `done` — see Closing.
- **done = close the item.** Never use a `status:done`/`status:closed` label as a substitute for closing.

## Closing — done means the fix is on the default branch

An item is "done" **only when the change is verified and landed on the default branch** — a PR merged, or a trunk-based commit pushed to default and kept — never when code is merely local or sitting on an unmerged branch. (`review` is the step before: code posted for verification but not yet landed; don't conflate the two.)

- Close a code fix with a commit/PR whose message/body contains `Fixes #N` / `Closes #N` (GitHub auto-closes + links); for the file backend, set `status: closed` after the commit lands.
- If `close_gate.enforcement` names a workflow (e.g. `issue-close-check.yml`), **do not** use `gh issue close` for a code fix — that workflow will reopen it. Close only via the referencing commit/PR.
- Don't set `review` until the change is **posted for verification** (PR opened / branch pushed, or committed + pushed to default in a trunk flow) — not while it's only local. `done` (close) is the further gate: the change must have **landed on the default branch** (PR merged, or trunk commit verified + kept).
- Name the locking test (under `close_gate.locking_test_dir`) in the close comment when one exists.
- **Exempt** (may close without code): anything in `close_gate.exempt_labels` (typically `wontfix`, `duplicate`, `invalid`, `type:decision`, `type:question`).

## Issue body template

```markdown
## What
<1–2 sentences: the problem or desired capability, in the user's framing. For a migrated item, keep the original wording.>

## Repro / context  (bugs only)
1. <step>
2. <observed>
**Expected:** <behavior>   **Actual:** <behavior>

## Acceptance criteria
- [ ] <observable, testable outcome>
- [ ] <regression test added>

## Detail / links
- Spec: docs/spec/<file>.md (§…)
- Plan: docs/plans/<file>.md
- Loop/audit: docs/progress/<file>.md
- Tests: <file>
- Personas: <only if configured>

## Source
<origin — migrated from X, or "reported by user YYYY-MM-DD">
```

## Privacy / redaction before filing

Before creating an item, scrub the body of anything that must not be public, using `redaction` from the config:

- **Secrets** (`secrets:` list — API keys, tokens) — values live only in gitignored `.env`.
- **Absolute local paths** (`/Users/…`) → use repo-relative paths (when `redact_absolute_paths`).
- **Anything that could leak to a mirror** — never sync to repos listed in `mirror_repos`.
- If `repo_visibility` is `public`, redact harder (real file names, library dumps). When unsure whether a body is safe, show the user the draft and confirm before creating.

## Do / Don't

- **Do** create the item before any code/spec/test change for new work.
- **Do** discover labels from `gh label list`; honor configured cardinality.
- **Do** name the locking test in the close comment when the repo locks fixes with a test.
- **Don't** put a full deep-plan or spec inside the item body — link the file.
- **Don't** append new reports to anything in `legacy_paths_do_not_write` — create an item instead.
- **Don't** invent labels outside the repo's set; ask the user (or extend the config) if a new area/type is genuinely needed.

## Multi-runtime discovery

This skill is plain Markdown + POSIX shell (`sh`, `gh`, `jq`), so the procedure and scripts run under any backend. The global skill is auto-discovered by **Claude Code** (`~/.claude/skills/track-work`), **Codex** (`~/.agents/skills/track-work`), and **opencode** (`~/.agents/skills/track-work`) — all three resolve the same global symlink. If a runtime does *not* discover it, fall back to a project-local symlink:
```bash
mkdir -p .agents/skills && ln -sfn ~/.agents/skills/track-work .agents/skills/track-work
```
The `.agents/track-work.config.md` is just a data file the skill reads — no symlink needed, and it is committed so teammates inherit it.

## Maintenance

This skill + the repo's label set + the repo's config are the system. If the taxonomy changes: update the config, run `gh label` to match (GitHub backend), and re-triage open items. If the board changes, update `github.board` in the config — the helper resolves IDs at runtime, so no script edits are needed.
