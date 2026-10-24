---
name: track-work
description: Use FIRST when work is about to start on any repo — a bug is reported, a feature/enhancement is requested, an open question or design decision is raised, someone asks to "track"/"log"/"add a ticket for" something, asks what is open / in-progress / done, or an agent is about to implement a change that has no tracking item. Creates or updates one tracking item in GitHub Issues when origin is GitHub, or a committed file backlog under .agents/issues/ otherwise; temporary GitHub access failures stop with diagnostics instead of silently creating a second ledger. In a multi-repo workspace, a workspace-level question ("what's open", priorities) spans every repo's ledger, never just the primary. Applies repo taxonomy and links detail files.
---

# Track Work — one live status ledger per repo

## Intent

Every bug, feature, enhancement, or decision a repo works on is tracked as **one work item** in **one place**: **GitHub Issues** when the repo has a GitHub remote, else a committed file-based backlog under `.agents/issues/`. That item is the **status** source of truth (draft / backlog / in-progress / review / done). The repo's long-form files — specs, plans, loops, research — stay as the **detail** layer and are *linked* from the item, never duplicated.

This is the entry gate: **no implementation, no spec edit, no test starts before the work has a tracking item** (or is confirmed to update an existing one).

## The CLI is the mechanical executor

Every mechanical operation runs through this skill's CLI; the prompt keeps the judgment (classification, signature dedup, triage, confirmations, what belongs in a body at all):

```bash
TW=<this-skill>/scripts/tw.py
python3 "$TW" resolve                                            # envelope: backend, selected_by, repo|issues_dir, capability
python3 "$TW" list [--status open|draft|..] [--label ..]         # items[] with id/title/status/labels/repo
python3 "$TW" create --title .. --type bug --priority p1 [--label ..] [--body-file ..]
python3 "$TW" status <ref> <draft|backlog|in-progress|review|blocked>
python3 "$TW" close <ref> [--reason ..]
python3 "$TW" migrate --to github|file [--status] [--retire-source]
```

- One JSON envelope per invocation (`ok`, `command`, `backend`, plus the result or a typed `error: {code, message}`); exit 0 success / 2 usage / 1 other failures. Consume the envelope — never screen-scrape.
- `<ref>` is `owner/repo#N` or an issue URL on GitHub; `ISSUE-NNN` on the file backend.
- The CLI owns the mechanics: identity resolution, `-R` binding on every repo-scoped call with wrong-repository read-back checks, deterministic redaction before staging, private (0600) body staging with guaranteed cleanup, label validation + one-operation cardinality transitions, landed-evidence checks on close, and journaled migrations.
- Noninteractive callers (Backlog, workflows) pass `--noninteractive` (or `TW_NONINTERACTIVE=1`): confirmations and capability failures return `blocked` instead of prompting, with no mutation.
- The file backend wraps `scripts/issue.sh` — ID allocation, locking, and atomic writes stay in the engine, which also remains directly usable.

## Workspace scope — multi-repo fan-out

The ledger is per-repo, but questions often aren't. A workspace-level question — "what's open?", "list open issues by priority", "what should I work on next?" — spans **every repo in the workspace**: in RPCE, every loaded root that is a git repo (plus any repo the question names); elsewhere, every checkout the workspace covers. Answering it from the primary repo alone presents a partial list as complete, which is the one failure this section exists to prevent.

- **Enumerate the repo set before querying any ledger.** The primary root or cwd is a routing default for repo-scoped commands, never the scope of a workspace-level question; only an explicit user narrowing ("just the website repo") reduces the set.
- **Run backend selection (Step 0) and config discovery (Step 1) per repo** — one workspace can mix GitHub and file backends, each with its own labels and config.
- **Bind every query to its repo** — run `tw list` inside each repo's tree (the CLI binds every GitHub call `-R owner/repo`; ambient `GH_REPO` cannot redirect) and aggregate into a single answer with each item labeled by repo (`owner/repo#123`, `<repo> #ID` for file backends) so a merged priority order stays unambiguous.
- **Report unreachable ledgers as gaps**, never silently omit them — a repo whose `gh` probes fail still appears in the answer as "unqueried (reason)".

## Step 0 — select the backend, then probe capability

Backend identity and current capability are separate. Select the ledger first:

1. **Resolve config first** — read `TRACK_WORK_BACKEND`, then trusted-base repo config (Step 1). Accept only `auto | github | file`; environment wins config, `auto` falls through, and invalid/duplicate values stop. A newly proposed persistent override requires confirmation. A `github` override without a GitHub origin also requires `github.repo: owner/repo`.
2. **GitHub identity** — otherwise parse `origin` only from exact `https://github.com/OWNER/REPO(.git)` or `git@github.com:OWNER/REPO(.git)` forms. Normalize to `owner/repo`; reject userinfo, lookalike hosts, multiple push URLs, and ambiguous forms.
3. **File identity** — no origin, or a confirmed non-GitHub origin, selects the committed file backend. Read behavior-changing config from the trusted base; an unmerged config difference requires confirmation.
4. **Rejected ≠ non-GitHub** — a GitHub-shaped origin that fails strict parsing (userinfo, lookalike host, ambiguity) is neither absent nor confirmed non-GitHub: stop before selecting a backend, report `origin-rejected(<reason>)` with the remediation (strip the userinfo from the remote URL, or pin `backend: github` + `github.repo` in config), and confirm the intended ledger before any write. Silently falling back to the file backend here is how a repo ends up with two live ledgers.

After identity, capability is probed separately (gh presence, auth, repo view, Issues enabled) and reported in the envelope — it never changes the selected identity:

```bash
python3 "$TW" resolve
```

- If the envelope reports `capability.ok`, proceed with GitHub — the CLI retains `$REPO` and binds `-R "$REPO"` to every repository-scoped call itself; ambient `GH_REPO` and working directory cannot redirect it.
- If `gh` is missing, unauthenticated, network/API access fails, permissions are insufficient, or Issues are disabled, **stop before reading or writing either ledger**. Report `backend: github`, the identity evidence (`origin` or override), the failed probe, and remediation.
- Offer retry/authentication/permission repair. For a GitHub-identified repo with existing issues, authoritative file mode requires a completed migration while GitHub is reachable; an outage may use only a clearly non-authoritative pending capture that Backlog cannot dispatch or close. That capture still goes through the CLI's file backend (`TRACK_WORK_BACKEND=file` + `tw create`; the engine's frontmatter validation is the guard), carries a pending-mirror note, and the first successful GitHub operation mirrors it and cross-links; a fallback that outlives its outage is a second ledger.
- Do not infer why an earlier run selected a backend from current state. State only observed evidence and clearly label any historical explanation as unverified.

Every operation's envelope carries `backend`, `selected_by`, the normalized target, and `capability` (or the typed error) — report compactly from it, e.g. `backend=github; repo=owner/repo; selected_by=origin; capability=ok` or `capability=failed(gh-auth)`. Capability is per operation, never cached: metadata success does not imply issue-write, label-admin, or Project access. Sanitize what you add around the envelope before reporting.

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
triage:                      # optional — per-repo overrides of creation-time defaults; absent = built-in defaults
  priority_defaults: { live_failure_bug: p1, blocking_gap: p2, cosmetic_gap: p3, parked_idea: p3 }  # keys = the defaults-table rows
  entry_state: backlog       # birth state when acceptance is clear (draft when it isn't) — draft|backlog only
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
| repo's creation-time triage defaults differ (priorities, birth state) | items born with the right priority/state without editing the skill | `triage` |

First-run detection (run when no config exists):
```bash
OWNER=$(git remote get-url origin | sed -E 's#.*(github.com[:/])([^/]+)/.*#\2#')
gh project list --owner "$OWNER" --limit 100 2>/dev/null                              # board?
ls .github/workflows/ 2>/dev/null | grep -i 'close'                                 # close-gate?
grep -oE '[A-Z0-9_]*(KEY|TOKEN|SECRET)[A-Z0-9_]*' .env.example 2>/dev/null | sort -u   # secrets?
gh repo view "$REPO" --json visibility 2>/dev/null                               # public?
ls docs/ 2>/dev/null                                                                # detail dirs?
find docs -iname '*persona*' 2>/dev/null | head                                    # personas?
gh label list -R "$REPO" --json name --jq '.[].name' 2>/dev/null | sed -E 's/:.*//' | sort -u   # custom prefixes?
```

## Triage (creation-time rules)

These rules govern the moment an item is **born** — entry state, default priority, and routing. They are creation-time only: consumption-time triage (re-ranking, flight-sets, sequencing) stays with Backlog's Phase 1 and the `triage-work` skill. The shared atoms — **Stable Identifiers**, **Review Quality** signatures, **Verifying Delegated Work**, **Git Safety** — are named, not restated; they live in `.agents/rules/global.md`.

- **Decisions route to humans.** A `type:decision` finding is created for human triage, never auto-queued or auto-resolved at creation (Backlog's rollup consumes it later).
- **Birth states: `status:draft` or `status:backlog` only.** `draft` = needs repro/decision; `backlog` = triaged, acceptance clear. Nothing is born `in-progress`, `review`, or `blocked`; `in-progress` is claimed only by the actor that starts work.
- **Batch/summary items carry a parent link.** An item filed from a batch or summary artifact enters with its Source/Detail section linking the originating batch item or run — never a free-floating duplicate.
- **Priority defaults** (creation-time; consumption triage may re-rank; per-repo override via the `triage:` config block):

  | finding kind / work state | default priority |
  |---|---|
  | live-failure bug | `priority:p1` |
  | process or doc gap blocking active work | `priority:p2` |
  | process or doc gap, cosmetic | `priority:p3` |
  | parked idea or future enhancement | `priority:p3` |

- **Dedup by signature before create.** Before creating, search the ledger for the item's **review signature** (the Review Quality atom); on a match, update the existing item (comment/relabel) instead of creating — the signature, not loose keywords, is the dedup key (GitHub step 2 below runs on it).

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
python3 "$TW" list --status open     # then judge matches against the item's review signature
```
Search by the item's **review signature** (see *Triage — creation-time rules*), not loose keywords; if a match exists → update it (comment / relabel / reopen) instead of duplicating. Cross-link with `#<n>`.

### 3. Create the issue
Compose the body from the template below, write it to a file, and hand it to the CLI — redaction (per config `redaction:`), private staging, `-R` binding, label validation against the repo's actual set, and the post-create read-back are the CLI's mechanics (the envelope reports the applied redaction classes; a wrong-repository read-back fails `wrong-repository`):
```bash
BODY=$(mktemp "${TMPDIR:-/tmp}/track-work.XXXXXX")   # compose the body here
python3 "$TW" create --title "<imperative title, <=80 chars>" \
  --type bug --priority p1 [--label area:ui,..] --body-file "$BODY"
rm -f "$BODY"
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
- Commit with the `commit` skill, referencing `#<issue>` in the message — that reference is the CLI's landed-evidence anchor.
- **Close** with `python3 "$TW" close owner/repo#N [--reason ..]` per the repo's close gate (below); the CLI verifies the evidence before mutating.

## File backend workflow (non-GitHub identity or confirmed override)

Mechanics go through the CLI (which wraps `scripts/issue.sh`); the engine stays directly usable for raw operations:
```bash
python3 "$TW" create --title "<title>" --type bug --priority p1 [--label x,y] [--body-file ..]
python3 "$TW" list [--status open]
python3 "$TW" status ISSUE-001 <draft|backlog|in-progress|review|blocked>   # close is a separate command
python3 "$TW" close ISSUE-001 [--reason ..]                                 # verifies landed evidence first
# engine-level (raw): issue.sh show/block/unblock/reopen — same validations, no envelope
```
- Items live as `<issues_dir>/<ID>.md` with validated YAML frontmatter (`id`, `title`, `status`, `previous_status`, `type`, `priority`, `created`, `labels`). The engine confines a repo-relative non-symlink path, validates scalar inputs, serializes mutations with a lock, and atomically replaces items/indexes. **IDs are immutable**.
- A synced index table lives at `<issues_dir>/README.md`.
- The issues dir is the **shared team backlog** — it is committed. If `git check-ignore <issues_dir>` says it is ignored, warn the user and fix it (gitignore negation like `!.agents/issues/`, or move the dir) before writing anything.
- A status or item change commits the item **and** its synced index together — both or neither. Committing the item alone leaves a dirty index for the next session, and item and index drift.

## Ledger migration

Migration between backends is a separate, confirmed operation, not an automatic consequence of backend detection:

1. Confirm migration, persistent override changes, and taxonomy creation first — Backlog never initiates migration, and an interactive `tw migrate` refuses without even creating a journal.
2. Run the migration noninteractively once confirmed: `python3 "$TW" migrate --to github|file --noninteractive`. The CLI writes and commits `docs/track-work-migrations/<timestamp>.md` **before** any mutation, moves open items with `Migrated-from: <backend>:<ID>` idempotency markers (searching the destination before every create), advances rows `pending → created → verified` only on destination read-back, and leaves closed items in the source.
3. Resume after partial failure by re-running the same command — verified rows are skipped, created rows re-checked via their marker, never re-created. `migrate --status` reports row states read-only.
4. When rewriting in-body source-ID cross-references to destination `#<n>`s (your judgment, not the CLI's), scope the substitution to cross-reference lines — a global replace also rewrites the `Migrated-from:` marker itself, corrupting the idempotency trail.
5. Ask separately before source retirement, then `python3 "$TW" migrate --to .. --retire-source --noninteractive` — it refuses unless every row is verified.

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

- Close via `python3 "$TW" close <ref> [--reason ..]`: the CLI verifies the landed evidence (a digit-bounded `Fixes #N`/`Closes #N` referencing commit on the default branch, or a merged PR; `ISSUE-NNN`/`ISSUE-N` references on the file backend) or an exempt label before mutating, and reads closed state back. You still verify the change itself (tests, review) and update any configured terminal board state; the close comment names the locking test when one exists.
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

`tw create` runs the deterministic preflight itself using `redaction` from config — configured secret values (resolved from the environment, never printed) and absolute local paths are replaced before the item exists on any backend, the envelope reports which redaction classes applied, and no unredacted staged copy survives the command. Your duties are the judgment around it: what belongs in a body at all, sanitizing anything you write *around* the envelope, and stopping rather than filing when content cannot be made safe.

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
- **Do** verify explicit ownership before claiming work is tracked: an item tracks the work only through its primary scope or a concrete acceptance criterion with an actionable completion condition — narrative mention in another item's body, a report, a caution banner, or a spec doc is **not** tracking. Consequential work (especially P0/P1) gets a dedicated item unless an existing item explicitly owns the same work; never create a duplicate when an authoritative equivalent exists. Any "tracked in #N" claim must first verify #N actually carries that obligation.
- **Don't** put a full deep-plan or spec inside the item body — link the file.
- **Don't** write a backend override, seed labels, or retire a source ledger without the required confirmation.
- **Don't** append new reports to anything in `legacy_paths_do_not_write` — create an item instead.
- **Don't** invent labels outside the repo's set; ask the user (or extend the config) if a new area/type is genuinely needed.
- **Don't** cache ledger state across commitments — the ledger is shared and mutable by other actors (humans, other agents) while you work. Re-read authoritative item state at commitment boundaries: before assigning or dispatching, before changing open/blocked/done state, before closing/replacing/claiming completion, and after any indication of external change.
- **Do** track the root defect, not only the mitigations: an incident is fixed only when its causal defect is removed or explicitly accepted. Keep the existing incident item open as owner of the unresolved cause; create a separate root item only when ownership or lifecycle genuinely differs (a defect that is upstream marks blocked/external-owner, with "report upstream" recorded as the next action only where a channel exists and disclosure is authorized). Mitigation completion is acceptance evidence on the root item, never grounds to close it.
- **Don't** auto-file findings that are personal-only AND untracked AND not shared/synced into team or client systems AND show no active compromise AND violate no repository/organization policy (e.g., a token in a local single-user shell profile): interactive callers confirm with the user first; noninteractive callers return blocked/pending-confirmation without creating an item. Shared credentials, repository exposure, client systems, or policy-governed secrets remain eligible for normal tracking. If the user declines an already-created item, close it wontfix with the decision recorded — never delete the entry.

## Multi-runtime discovery

This skill uses `python3` for `tw.py` (the CLI), POSIX `sh` for `issue.sh` (the file engine it wraps) and `test_issue.sh`, Bash 3.2+ for `place_on_board.sh`, plus `git`, `gh`, `jq`, `awk`, and `sed`. The CLI's own suite is `test_tw.py` (`python3 -m unittest discover -s <this-skill>/scripts -p 'test_tw.py'`). The global skill is auto-discovered by **Claude Code** (`~/.claude/skills/track-work`), **Codex** (`~/.agents/skills/track-work`), and **opencode** (`~/.agents/skills/track-work`) — all three resolve the same global symlink. If a runtime does *not* discover it, fall back to a project-local symlink:
```bash
mkdir -p .agents/skills && ln -sfn ~/.agents/skills/track-work .agents/skills/track-work
```
The `.agents/track-work.config.md` is just a data file the skill reads — no symlink needed, and it is committed so teammates inherit it.

## Maintenance

This skill + the repo's label set + the repo's config are the system. If the taxonomy changes: update the config, run `gh label` to match (GitHub backend), and re-triage open items. If the board changes, update `github.board` in the config — the helper resolves IDs at runtime, so no script edits are needed.
