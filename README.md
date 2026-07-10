# RepoPrompt Workflows

A shareable agent workflow system for [RepoPrompt CE](https://repoprompt.com) (RPCE) and the model CLIs it drives — Claude Code, Codex, opencode, and pi. Five orchestrated **workflows**, the reusable **skills** they invoke, supporting slash **commands**, the cross-cutting **rules** and **hooks** that enforce them, and the dogfooded **specs** that document each piece.

The workflows inline the discipline from the skills they depend on, so each runs deterministically whether or not a skill is installed; the skills are the canonical standalone versions.

---

## For users — install and run

**Requirements:** [RepoPrompt CE](https://repoprompt.com) to run the workflows, plus any backend it drives. Skills, rules, and hooks are portable across backends.

**The five workflows:**

| Workflow | Purpose |
|---|---|
| `Spec` | Elicit intent, draft scenarios/constraints, check for redundancy/gaps/ambiguity, write a minimal spec to `docs/spec/`. |
| `Test` | Read a spec's Given/When/Then, discover the repo's test framework, map scenarios to native tests, write them. |
| `Loop` | Consume a Spec + Deep Plan, verify readiness, then run red/green/review/refactor loops with resumable progress. |
| `Deep Review` | Map a change set, run parallel context-grounded review shots across lenses, govern/revalidate findings, reconcile with the author. |
| `Backlog` | Triage tracked issues via `track-work`; for each run Spec/plan-if-missing, then a worktree-isolated `Loop` subagent, verify closeout, close. |

`Spec` → `Test` form a pair; `Loop` builds on both; `Deep Review` pairs with `Loop`; `Backlog` sits above `Loop`.

### Install

This repo is a **library, not an app** — you symlink its workflows/skills/commands into the directories your tools already read. **Symlinks, not copies**: this repo stays the single source of truth, so an edit here is seen by every tool.

> The RepoPrompt CE path is macOS (`~/Library/Application Support/...`); the skills/commands paths (`~/.claude/...`, `~/.agents/...`) are the same on every OS.

There's an idempotent installer — [`scripts/install.sh`](scripts/install.sh) — that links everything and fixes partial or broken installs on re-run. Use it one of two ways:

#### Option A — let an agent do it (easiest)

Paste into Claude Code (or any agent with shell access):

```text
Install the repoprompt-workflows repo into my environment. If ~/Sites/repoprompt-workflows doesn't already exist, clone it there — ASK ME for the git remote first, don't guess. Then run `bash scripts/install.sh`, paste me its full output, and tell me to restart RepoPrompt CE.
```

#### Option B — run the installer yourself

```bash
git clone <remote> ~/Sites/repoprompt-workflows
cd ~/Sites/repoprompt-workflows
bash scripts/install.sh              # link workflows + skills + commands (safe to re-run)
bash scripts/install.sh --dry-run    # preview: print every link without creating it
bash scripts/install.sh --uninstall  # remove the symlinks (repo files are untouched)
```

What it links (it scans these dirs — drop in a new file/dir and the next run links it automatically):

- every `*.md` in `.agents/workflows/` (excl. README) → `~/Library/Application Support/RepoPrompt CE/Workflows/`
- every directory in `.agents/skills/` → `~/.claude/skills/` and `~/.agents/skills/` (available in other repos too)
- every `*.md` in `.agents/slash/` (excl. README) → `~/.claude/commands/`

For each link it prints `ok` (already points here), `relinked` (was missing/broken/pointing elsewhere), or `CONFLICT` (a real file is in the way — it won't clobber that). Re-run any time to repair a partial install.

Then restart RepoPrompt CE and open the workflows picker — Spec, Test, Loop, Deep Review, Backlog should all appear.

> **Re-linking:** if you previously symlinked any of these from another checkout (e.g. an older monorepo), the installer re-points them here — that's the partial-install case it's built for.

Hooks are **not** linked by the installer — they need per-backend registration in `settings.json`; see [`hooks/README.md`](.agents/hooks/README.md).

### Run

In RepoPrompt CE, pick a workflow and point it at a target — e.g. run `Spec` on a feature description, then `Test` on the resulting spec, then `Loop` on the spec plus a deep plan.

---

## For developers — extend and contribute

**Repo layout**

| Path | What |
|---|---|
| `.agents/workflows/` | Five RPCE workflows. See [`workflows/README.md`](.agents/workflows/README.md). |
| `.agents/skills/` | Ten reusable skills the workflows invoke. See [`skills/README.md`](.agents/skills/README.md). |
| `.agents/slash/` | Slash commands — currently `/document`. See [`slash/README.md`](.agents/slash/README.md). |
| `.agents/rules/global.md` | Cross-cutting hard rules (git safety, stable IDs, minimalism, reconciliation gates). |
| `.agents/hooks/` | Canonical Python hooks enforcing those rules. See [`hooks/README.md`](.agents/hooks/README.md). |
| `docs/spec/` | Dogfooded specs + conformance matrices for each workflow/skill. |
| `scripts/install.sh` | Idempotent installer — symlinks workflows/skills/commands (`--dry-run`, `--uninstall`). |
| `scripts/sync-maintainability-review.mjs` | Re-syncs the vendored `maintainability-review` lens from upstream. |
| `AGENTS.md` | Agent guide for working in this repo (`CLAUDE.md` is a symlink to it). |

**Keep workflows and skills in sync — both directions.** Each workflow inlines the discipline of the skills it depends on (so it runs without the skill installed) and names the skill as canonical. That binds them: **change a skill → update every workflow that inlines it; change an inlined discipline inside a workflow → update the source skill.** Drift between the inline copy and the skill is the main way this repo goes wrong.

**How the pieces fit**

- **Workflows** (RPCE) orchestrate. They inline the discipline from the skills they depend on, so they run even when a skill isn't installed.
- **Skills** are discovered by the backend CLI, **not** RPCE: Claude Code reads `.agents/skills` + `~/.claude/skills`; Codex scans `.agents/skills` + `~/.agents/skills`; opencode and pi read `.agents/skills`.
- **Rules** (`global.md`) are the cross-cutting hard rules the workflows and hooks reference.
- **Hooks** enforce those rules at the tool-call lifecycle; logic lives once in `.agents/hooks/*.py` (runtime-agnostic Python on stdin), registered per backend.
- **Specs** under `docs/spec/` are the dogfooded contracts for these very workflows/skills, each with a conformance matrix.

**Editing**

- Workflows: edit the `.md` in `.agents/workflows/`; RPCE follows the symlinks. See [`workflows/README.md`](.agents/workflows/README.md).
- Skills: add a `<name>/SKILL.md`, symlink for global use, and run the distinctness check in [`skills/README.md`](.agents/skills/README.md).
- Vendored lens: `maintainability-review` is synced from upstream — check or re-sync with the script below; don't hand-edit between the markers.

```bash
node scripts/sync-maintainability-review.mjs            # check for drift
node scripts/sync-maintainability-review.mjs --update   # re-sync skill + Deep Review inline block
```

---

## Reference

**Provenance** — extracted from a larger mono-repo and de-branded for sharing. The five workflows and ten skills are byte-identical to their source; only install paths and READMEs were generalized.

**Runtime compatibility**

| Artifact | Claude Code | Codex | opencode | pi | RPCE |
|---|---|---|---|---|---|
| Workflows | — | — | — | — | loads from app-support dir |
| Skills | `.agents/skills` + `~/.claude/skills` | `.agents/skills` + `~/.agents/skills` | `.agents/skills` | `.agents/skills` | — |
| Rules | portable | portable | portable | portable | — |
| Hooks | `~/.claude/settings.json` | `.codex/hooks.json` | `.opencode/plugins/*.mjs` | `~/.pi/agent/extensions/*.ts` | — |

**License** — MIT; see [`LICENSE`](LICENSE). Third-party vendored content (`maintainability-review`, from [cursor/plugins](https://github.com/cursor/plugins/tree/main/cursor-team-kit/skills/thermo-nuclear-code-quality-review), MIT) is attributed in [`NOTICE`](NOTICE).
