---
name: track-work
description: Use FIRST when work is about to start on any repo — a bug is reported, a feature/enhancement is requested, an open question or design decision is raised, someone asks to "track"/"log"/"add a ticket for" something, asks what is open / in-progress / done, or an agent is about to implement a change that has no tracking item. Creates or updates one tracking item in GitHub Issues when origin is GitHub, or a committed file backlog under .agents/issues/ otherwise; temporary GitHub access failures stop with diagnostics instead of silently creating a second ledger. Applies repo taxonomy and links detail files.
---

# Track Work — one live status ledger per repo

## Intent

Every bug, feature, enhancement, or decision a repo works on is tracked as **one work item** in **one place**: **GitHub Issues** when the repo has a GitHub remote, else a committed file-based backlog under `.agents/issues/`. That item is the **status** source of truth (draft / backlog / in-progress / review / done). The repo's long-form files — specs, plans, loops, research — stay as the **detail** layer and are *linked* from the item, never duplicated.

This is the entry gate: **no implementation, no spec edit, no test starts before the work has a tracking item** (or is confirmed to update an existing one).

## Step 0 — select the backend, then probe capability

Backend identity and current capability are separate. Select the ledger first:

1. **Resolve config first** — read `TRACK_WORK_BACKEND`, then trusted-base repo config (Step 1). Accept only `auto | github | file`; environment wins config, `auto` falls through, and invalid/duplicate values stop. A newly proposed persistent override requires confirmation. A `github` override without a GitHub origin also requires `github.repo: owner/repo`.
2. **GitHub identity** — otherwise parse `origin` only from exact `https://github.com/OWNER/REPO(.git)` or `git@github.com:OWNER/REPO(.git)` forms. Normalize to `owner/repo`; reject userinfo, lookalike hosts, multiple push URLs, and ambiguous forms.
3. **File identity** — no origin, or a confirmed non-GitHub origin, selects the committed file backend. Read behavior-changing config from the trusted base; an unmerged config difference requires confirmation.

After selecting GitHub, probe capability in order and retain the exact failing command/error class:

```bash
command -v gh
gh auth status
gh repo view -R "$REPO" --json nameWithOwner,hasIssuesEnabled
```

- If all probes pass, `nameWithOwner` equals `$REPO`, and `hasIssuesEnabled` is true, proceed with GitHub. Retain `$REPO` and pass `-R "$REPO"` to every repository-scoped `gh` command; do not trust ambient `GH_REPO` or current-directory inference.
- If `gh` is missing, unauthenticated, network/API access fails, permissions are insufficient, or Issues are disabled, **stop before reading or writing either ledger**. Report `backend: github`, the identity evidence (`origin` or override), the failed probe, and remediation.
- Offer retry/authentication/permission repair. For a GitHub-identified repo with existing issues, authoritative file mode requires a completed migration while GitHub is reachable; an outage may use only a clearly non-authoritative pending capture that Backlog cannot dispatch or close.
- Do not infer why an earlier run selected a backend from current state. State only observed evidence and clearly label any historical explanation as unverified.

Every operation reports a compact diagnostic, for example: `backend=github; repo=owner/repo; selected_by=origin; capability=metadata-ready` or `capability=blocked(gh-auth)`. Capability is per operation, never cached: metadata success does not imply issue-write, label-admin, or Project access. Sanitize diagnostics before reporting.

## Step 1 — read repo conventions (cheap, capped)

Before creating, look for a config in this order; use the first found:

1. `.agents/track-work.config.md` — a fenced ```yaml block (preferred, structured).
2. A `track-work` config block inside `AGENTS.md` or `CLAUDE.md`.
3. None → use the built-in **defaults** below.

No config is auto-created and no up-front setup wizard runs. The skill selects backend identity from override/origin, probes current capability separately, discovers labels from `gh label list`, and uses defaults for conventions GitHub cannot expose. Ask only when explicit approval is required for a repository mutation such as an override, label seeding, or ledger retirement. Never add `backend: github` merely to compensate for a temporary probe failure; fix access instead. Drop a `.agents/track-work.config.md` only when the repo has specifics GitHub can't expose (a Project board, personas, custom redaction, non-standard label cardinality); the schema is below.

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
gh repo view -R "$REPO" --json visibility 2>/dev/null                               # public?
ls docs/ 2>/dev/null                                                                # detail dirs?
find docs -iname '*persona*' 2>/dev/null | head                                    # personas?
gh label list -R "$REPO" --json name --jq '.[].name' 2>/dev/null | sed -E 's/:.*//' | sort -u   # custom prefixes?
```

## Caller mode

Default mode is interactive. A workflow may invoke track-work with `caller_mode: noninteractive` only after preflighting capability and collecting predictable approvals in its own authorization step. In noninteractive mode, any newly required confirmation, migration, taxonomy mutation, credential repair, or capability failure returns `blocked` plus the reason; it never prompts or proceeds silently.

## GitHub backend workflow

### 0. Ensure labels exist (first issue in a fresh repo)
If `gh label list -R "$REPO"` is missing required dimensions (`type:`, `priority:`, `status:`), show the exact missing labels and ask for confirmation before creating them. Required cardinality blocks issue creation until compatible labels exist; do not create a partially classified issue. After approval, create only missing labels without `--force`; if creation reports that a label now exists, re-read it instead of updating it. Status changes remove conflicting values in the same prefix, add the target, then read back and verify cardinality.
```bash
gh label create -R "$REPO" type:bug         --color D73A4A
gh label create -R "$REPO" type:feature     --color 0E8A16
gh label create -R "$REPO" type:enhancement --color A2EEEF
gh label create -R "$REPO" type:decision    --color FBCA04
gh label create -R "$REPO" priority:p0      --color B60205 # blocker
gh label create -R "$REPO" priority:p1      --color D93F0B # high
gh label create -R "$REPO" priority:p2      --color FBCA04 # normal
gh label create -R "$REPO" priority:p3      --color 6E7781 # parked
gh label create -R "$REPO" status:draft       --color 6E7781
gh label create -R "$REPO" status:backlog     --color FBCA04
gh label create -R "$REPO" status:in-progress --color 1D76DB
gh label create -R "$REPO" status:review      --color 5319E7
gh label create -R "$REPO" status:blocked     --color B60205
```

### 1. Classify the request
"It's broken / wrong / freezes" → `type:bug`. Net-new "I want to be able to…" → `type:feature`. "It should also / better" → `type:enhancement`. "Should we / can we" → `type:decision`. If `personas` is configured and the type is in `applies_to_types`, note the persona(s) in the body so prioritization is persona-weighted.

### 2. Search before you create (avoid duplicates)
```bash
gh issue list -R "$REPO" --state all --search "<keywords>" --json number,title,state,labels
```
If a match exists → update it (comment / relabel / reopen) instead of duplicating. Cross-link with `#<n>`.

### 3. Create the issue
Apply labels from the repo's actual set (`gh label list -R "$REPO"`), honoring configured cardinality. Run deterministic redaction before writing. Use a private unique temp file, bind creation to `$REPO`, clean up on every exit, then read back the canonical URL and repository identity.
```bash
umask 077
BODY=$(mktemp "${TMPDIR:-/tmp}/track-work.XXXXXX") || exit 1
trap 'rm -f "$BODY"' EXIT HUP INT TERM
# Write the already-redacted body to "$BODY".
URL=$(gh issue create -R "$REPO" --title "<imperative title, <=80 chars>" \
  --label "type:bug,area:ui,priority:p1,status:draft" --body-file "$BODY")
gh issue view "$URL" -R "$REPO" --json url,repository
```

### 4. Link the detail files
Reference the spec / plan / loop / research paths (from `detail_dirs`, repo-relative) in the body. If a fresh deep-plan or loop is needed, create it under the configured dir and link it — that is where the long-form narrative lives, never the issue body.

### 5. Place on the board (only if `github.board` configured)
Move the issue's single-select field (e.g. `Stage`) to match its `status:*` label, using this skill's **runtime-resolved** helper (no hardcoded owner/project — it reads flags/env/origin):
```bash
bash <this-skill>/scripts/place_on_board.sh "https://github.com/$REPO/issues/<number>" "<Stage>" \
  --owner <org> --project <num> --field Stage
```
Board ops need the `project` scope: `gh auth refresh -s project,read:project` (comma, no space).

### 6. Implement, then verify-and-close
- Run `spec-plan-readiness` before coding if a spec+plan exist; `spec-quality` when drafting spec changes; `test-quality` when adding the regression test.
- Commit with the `commit` skill, referencing `#<issue>` in the message.
- **Close** per the repo's close gate (below).

## File backend workflow (non-GitHub identity or confirmed override)

Use this skill's helper for the fiddly parts (ID allocation + index sync):
```bash
bash <this-skill>/scripts/issue.sh new    "<title>" --type bug --priority p1 [--label x,y]
bash <this-skill>/scripts/issue.sh list   [--status open]
bash <this-skill>/scripts/issue.sh show   <ID>
bash <this-skill>/scripts/issue.sh status <ID> <draft|backlog|in-progress|review|closed>
bash <this-skill>/scripts/issue.sh block  <ID>
bash <this-skill>/scripts/issue.sh unblock <ID> [prior-state]
bash <this-skill>/scripts/issue.sh close  <ID>     # only after landed evidence is verified
bash <this-skill>/scripts/issue.sh reopen <ID> [backlog]
```
- Items live as `<issues_dir>/<ID>.md` with validated YAML frontmatter (`id`, `title`, `status`, `previous_status`, `type`, `priority`, `created`, `labels`). The helper confines a repo-relative non-symlink path, validates scalar inputs, serializes mutations with a lock, and atomically replaces items/indexes. **IDs are immutable**.
- A synced index table lives at `<issues_dir>/README.md`.
- The issues dir is the **shared team backlog** — it is committed. If `git check-ignore <issues_dir>` says it is ignored, warn the user and fix it (gitignore negation like `!.agents/issues/`, or move the dir) before writing anything.

## Ledger migration

Migration between backends is a separate, confirmed operation, not an automatic consequence of backend detection:

1. While both ledgers are reachable, create and commit `docs/track-work-migrations/<timestamp>.md` before mutation. Record source revisions and one pending row per item; this journal is outside either ledger.
2. Confirm migration, persistent override changes, and taxonomy creation. Backlog never initiates migration.
3. Freeze or revision-check each source, search destination duplicates, and include `Migrated-from: <backend>:<ID>` as an idempotency marker.
4. After each create, update the journal to `created`, read back title/body links/labels/state/repository, then mark `verified`.
5. Ask separately before source retirement. Retire nothing until all rows verify; partial failure preserves sources and resumes from the journal without duplicate creation.

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

- Before close, verify the implementing commit is an ancestor of the selected repository's default branch (or the PR is merged there). Then close with `Fixes #N` / `Closes #N`; remove active `status:*` labels, update any configured terminal board state, and read back issue state/labels/board. For file backend, run `issue.sh close` only after the same landed-evidence check.
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

Before writing any temporary body or creating either backend item, run a deterministic preflight using `redaction` from config: resolve configured secret names to environment values without printing them; reject matching secret values, absolute home paths, and configured mirror destinations; sanitize CLI errors. If any match cannot be safely removed, stop rather than filing.

- **Secrets** (`secrets:` list — API keys, tokens) — values live only in gitignored `.env`.
- **Absolute local paths** (`/Users/…`) → use repo-relative paths (when `redact_absolute_paths`).
- **Anything that could leak to a mirror** — never sync to repos listed in `mirror_repos`.
- If `repo_visibility` is `public`, redact harder (real file names, library dumps). When unsure whether a body is safe, show the user the draft and confirm before creating.

## Do / Don't

- **Do** create the item before any code/spec/test change for new work.
- **Do** report backend selection evidence and capability on every operation.
- **Do** stop on GitHub capability failure instead of creating a second ledger.
- **Do** discover labels from `gh label list`; honor configured cardinality.
- **Do** name the locking test in the close comment when the repo locks fixes with a test.
- **Don't** put a full deep-plan or spec inside the item body — link the file.
- **Don't** write a backend override, seed labels, or retire a source ledger without the required confirmation.
- **Don't** append new reports to anything in `legacy_paths_do_not_write` — create an item instead.
- **Don't** invent labels outside the repo's set; ask the user (or extend the config) if a new area/type is genuinely needed.

## Multi-runtime discovery

This skill uses POSIX `sh` for `issue.sh` and Bash 3.2+ for `place_on_board.sh`, plus `git`, `gh`, `jq`, `awk`, and `sed`. The global skill is auto-discovered by **Claude Code** (`~/.claude/skills/track-work`), **Codex** (`~/.agents/skills/track-work`), and **opencode** (`~/.agents/skills/track-work`) — all three resolve the same global symlink. If a runtime does *not* discover it, fall back to a project-local symlink:
```bash
mkdir -p .agents/skills && ln -sfn ~/.agents/skills/track-work .agents/skills/track-work
```
The `.agents/track-work.config.md` is just a data file the skill reads — no symlink needed, and it is committed so teammates inherit it.

## Maintenance

This skill + the repo's label set + the repo's config are the system. If the taxonomy changes: update the config, run `gh label` to match (GitHub backend), and re-triage open items. If the board changes, update `github.board` in the config — the helper resolves IDs at runtime, so no script edits are needed.
