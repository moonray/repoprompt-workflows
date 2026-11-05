# RepoPrompt Workflows

A shareable agent workflow system for [RepoPrompt CE](https://repoprompt.com) (RPCE) and the model CLIs it drives — Claude Code, Codex, opencode, pi, and Antigravity (`agy`). Five orchestrated **workflows**, the reusable **skills** they invoke, supporting slash **commands**, the cross-cutting **rules** and **hooks** that enforce them, and the dogfooded **specs** that document each piece.

The workflows inline the discipline from the skills they depend on wherever an inline copy suffices — `Backlog` additionally requires the `track-work` and `spec-plan-readiness` skills (discovery, gating, and close go through them, with no inline fallback). The skills are the canonical standalone versions.

## For users — install and run

**Requirements:**

- **[RepoPrompt CE](https://github.com/repoprompt/repoprompt-ce)** (macOS today) to run the workflows — RPCE drives a backend CLI (Claude Code, Codex, opencode, or pi). RP Classic may work but is **untested**.
- **bash** for the installer; **python3** for the hooks and the track-work CLI (`track-work/scripts/tw.py`); **node** for the optional `sync-maintainability-review.mjs` sync script.
- The **Deep Plan** that `Loop`/`Backlog` consume ships with **RPCE core** — it is *not* in this repo.

Workflows are macOS-only because RPCE is macOS-only today. Skills, slash commands, rules, and hooks are cross-platform (anywhere those CLIs and symlinks are supported).

> **No RepoPrompt CE (or not on macOS)?** Skills and rules work directly with Claude Code, Codex, opencode, pi, and Antigravity (`agy` — skills); command and hook support varies by runtime — see the compatibility table under [Reference](#reference).

**The five workflows:**

| Workflow | Purpose |
|---|---|
| `Spec` | Elicit intent and write a minimal, scenario-based spec to `docs/spec/`. |
| `Test` | Read a spec's scenarios and write native tests for the repo's test framework. |
| `Loop` | Verify readiness, then run red/green/review/refactor loops against a Spec + Deep Plan, with durable, resumable progress. |
| `Deep Review` | Multi-lens review of a change set, producing governed, revalidatable findings. |
| `Backlog` | Triage tracked issues, ensure a current Spec + Deep Plan per issue (generating or reconciling when missing/stale), then dispatch `Loop` in isolated worktrees and own landing/close. |

`Spec` → `Test` form a pair; `Loop` builds on both; `Deep Review` pairs with `Loop`; `Backlog` sits above `Loop`.

### Install

This repo is a **library, not an app** — you symlink its workflows/skills/commands into the directories your tools already read. **Symlinks, not copies**: this repo stays the single source of truth, so an edit here is seen by every tool.

There's an idempotent installer — [`scripts/install.sh`](scripts/install.sh) — that links everything and fixes partial or broken installs on re-run. Use it one of two ways:

#### Option A — let an agent do it (easiest)

Paste into Claude Code (or any agent with shell access):

```text
Install the repoprompt-workflows repo into my environment. If ~/Sites/repoprompt-workflows doesn't already exist, clone https://github.com/moonray/repoprompt-workflows there. Then run `bash scripts/install.sh`, paste me its full output, and tell me to restart RepoPrompt CE.
```

> Have an [organization repo](#your-organization-repo-optional)? Append to the prompt: *“Run the installer with `--org-repo=$HOME/Sites/<myorg>`.”* A style guide at `<myorg>/docs/style-guide.md` is linked automatically by that same flag; anyone else can add `--style-guide=<path>` (see [Custom style guide](#custom-style-guide-optional)). **No org repo yet?** Have the agent create one first, then install: *“Create `$HOME/Sites/<myorg>` as an org repo (git init; an empty private rules overlay at `.agents/rules/<myorg>-private.md`; a starter style guide at `docs/style-guide.md`, asking me a few style questions first), then run the installer with `--org-repo=$HOME/Sites/<myorg>`.”*

#### Option B — run the installer yourself

```bash
git clone --recurse-submodules https://github.com/moonray/repoprompt-workflows ~/Sites/repoprompt-workflows
# (already cloned without submodules? git submodule update --init -- .agents/skills/.anthropic-skills-skill-creator)
cd ~/Sites/repoprompt-workflows
bash scripts/install.sh              # link workflows + skills + commands + rules + hooks (safe to re-run)
bash scripts/install.sh --dry-run    # preview: print every link without creating it
bash scripts/install.sh --uninstall  # remove the symlinks (repo files are untouched)
```

What it links (it scans these dirs — drop in a new file/dir and the next run links it automatically):

- every `*.md` in `.agents/workflows/` (excl. README) → the RPCE Workflows directory
- every directory in `.agents/skills/` → `~/.claude/skills/` and `~/.agents/skills/` (available in every repo, not just this one)
- every `*.md` in `.agents/slash/` (excl. README) → `~/.claude/commands/` **and** `~/.agents/slash/` (RepoPrompt CE's cross-backend command source)
- every `.py` in `.agents/hooks/` → `~/.claude/hooks/`, registered in `~/.claude/settings.json` (Claude Code)
- every `*.md` in `.agents/rules/` (excl. README) → `~/.claude/rules/` and `~/.agents/rules/` (the generic rule core)
- optionally, your **custom style guide** (`--style-guide=<path>`) → `~/.agents/style-guide.md` — a single generic pointer; skills that draft prose you will publish or send follow it when it is present ([details](#custom-style-guide-optional))

**Your organization repo (optional):** if you keep org-specific (non-public) content in an org repo, pass it at install time — definition, when you need one, and every way to configure it in [**Your organization repo**](#your-organization-repo-optional), after the worked example below.

For each link it prints `linked` (was missing), `ok` (already points here), `relinked` (an owned link with a wrong or broken target — repaired), or `CONFLICT` (a real file — or a symlink the installer cannot prove belongs to this repo or the `--org-repo` checkout — is in the way; it is never silently clobbered). Re-run any time to repair a partial install. Migrating from another checkout of this system? Remove that checkout's links (or run its `--uninstall`) first — the installer only re-points links it owns.

Then restart RepoPrompt CE and open the workflows picker — Spec, Test, Loop, Deep Review, Backlog should all appear.

Hooks are active after install + restart (Claude Code); Codex/opencode activate automatically when working in this repo. Manual wiring and undo: [`hooks/README.md`](.agents/hooks/README.md).

### Run — a worked example

The core loop is **Spec → (Deep Plan) → Test → Loop**.

1. **`Spec`** — point it at a feature description. It elicits intent and writes a minimal behavioral contract (Given/When/Then scenarios, no implementation) to `docs/spec/<feature>.md`.
   *Run `Spec` with:* «add a `--dry-run` flag that prints actions without performing them»
2. **Deep Plan** — derive the *how* from the spec. The **Deep Plan** workflow ships with **RepoPrompt CE core** (not this repo); run it against the spec to get an ordered, work-item plan with risk/rollback notes.
3. **`Test`** — point it at the spec; it discovers the repo's test framework and writes native tests for each scenario (they fail — red).
4. **`Loop`** — point it at **both** the spec and the deep plan. It verifies readiness, then runs red/green/review/refactor until green, committing one revertible commit per work item.

`Deep Review` runs against any change set to produce governed, revalidatable findings; `Backlog` triages tracked issues, ensures a current Spec + Deep Plan per issue (generating when missing/stale), and runs `Loop` per issue in isolated worktrees (max 3 concurrent).

### Your organization repo (optional)

**Definition.** An *organization repo* is a repo you own that holds your org-specific — deliberately non-public — agent content: private skills (anything touching internal systems, client data, business workflows, or personal-machine scope), org documentation, and a **private rules overlay**: a small `.agents/rules/<org>-private.md` that extends this repo's generic `global.md` with your exceptions. This repo ships only generic, public-appropriate machinery by design; nothing non-public belongs in it, so that content needs its own home.

**Do you need one?** Only if you have non-public content you want available across your repos. A plain install with no org repo is fully functional — every workflow, skill, command, hook, and the generic rules work as-is. Expect to add one when your first org-specific rule or skill shows up; wiring it later is a single re-run of the installer, so deciding later costs nothing.

**Create one from scratch** (once; by hand, or by the agent prompt above):

```bash
mkdir -p "$HOME/Sites/myorg/.agents/rules" "$HOME/Sites/myorg/docs"
cd "$HOME/Sites/myorg" && git init
$EDITOR .agents/rules/myorg-private.md   # your private exceptions to global.md; a heading + one rule is a fine start
$EDITOR docs/style-guide.md              # your house style — starter template in Custom style guide below
```

**What the installer does with it.** `--org-repo` links `<org>/.agents/rules/*.md` (except `README.md` and `global.md` — that name stays the public core) into `~/.claude/rules/` and `~/.agents/rules/`, alongside this repo's `global.md`, and — if `<org>/docs/style-guide.md` exists — links it as your [custom style guide](#custom-style-guide-optional) too. Nothing else in the org repo is touched; org-private skills and commands follow your org repo's own install docs.

**Configure it** (flag and env forms; both idempotent):

```bash
bash scripts/install.sh --org-repo="$HOME/Sites/myorg"   # flag form
ORG_REPO="$HOME/Sites/myorg" bash scripts/install.sh     # env form
```

- **At install time** — pass the flag with Option B, or name the path in your Option A prompt.
- **After install** — re-run the same command; adding or changing the org repo later is just another idempotent run.
- **Fully manual** (what the flag automates):

```bash
for t in "$HOME/.claude/rules" "$HOME/.agents/rules"; do
  ln -sfh "$HOME/Sites/myorg/.agents/rules/myorg-private.md" "$t/myorg-private.md"
done
```

**Why the overlay link matters.** It is the runtime discovery contract: an agent resolves your two shared homes by following symlink targets — `readlink ~/.claude/rules/global.md` points at this public machinery repo, and the overlay link beside it points at your org repo. Wherever the links point *is* the active source, so re-pointing them (a fork, a moved checkout, a second machine) re-configures discovery with no static config to keep up to date.

### Custom style guide (optional)

**Definition.** A *custom style guide* is a markdown file you own — house rules for prose an agent drafts on your behalf that a human will later publish or send: client emails and chat messages, reports and proposals, posts and titles. This repo ships no guide content and stays consumer-agnostic; it defines only the **pointer**: when configured, your guide is linked at `~/.agents/style-guide.md`, and skills reference that generic path — never your repo or organization — so the same machinery works for any consumer.

**Configure it** (all idempotent):

```bash
bash scripts/install.sh --org-repo="$HOME/Sites/myorg"                          # org repo; also links its docs/style-guide.md if present
bash scripts/install.sh --style-guide="$HOME/Sites/myorg/docs/style-guide.md"   # explicit flag form
STYLE_GUIDE="$HOME/Sites/myorg/docs/style-guide.md" bash scripts/install.sh     # env form
```

The conventional home is `<org>/docs/style-guide.md`: with `--org-repo` given and no explicit `--style-guide`, a guide found there is linked automatically (the org repo's content at a conventional path is the opt-in, same as the rules overlay); an explicit `--style-guide` always overrides. Nothing is ever created or seeded for you — absence is a valid state, and the installer says so on every run. Fully manual (what the flag automates):

```bash
ln -sfh "$HOME/Sites/myorg/docs/style-guide.md" "$HOME/.agents/style-guide.md"
```

**Starting one from scratch.** The file is created when you instantiate your org repo ([Create one from scratch](#your-organization-repo-optional) above) — by hand, or by letting the agent that sets up your org repo ask you a few style questions first. The installer links it but never writes it. Minimal generic starter, edit freely:

```markdown
# <My Org> Style Guide

House rules for prose an agent drafts that a person will publish or send.
Delete what you don't care about; presence at the conventional path is what activates the pointer.

1. **Voice:** "I" for work the writer personally did; name the specific system touched, not "our side".
2. **Punctuation:** e.g. no em-dashes: use a colon or commas instead.
3. **Greetings/endings per medium:** e.g. email opens `Hi Name,` and ends after the last content line; chat opens with an @-mention.
4. **One message, one topic;** end with the reader's next step, not with the sender's availability.
```

**The skill-side convention.** A skill that authors publishable or sendable prose carries a line like: *“If a custom style guide is linked at `~/.agents/style-guide.md`, follow it for this output; if absent, proceed without one.”* Uninstalling? Pass the same `--style-guide` flag (or `--org-repo`, which finds the conventional path) so `--uninstall` recognizes and removes the link.

**If the pointer goes away.** A deleted or never-set link degrades silently — skills just proceed without a house style; nothing errors. Every installer run is the health check: the pointer is reported as `ok` (already correct), `present` (exists, not configured this run), `broken` (dangling target, printed with the repair command), or `none` (how to opt in), and anything the installer can prove it owns is repaired in place. Re-running your original install command is always the repair — which is why the org-repo conventional path matters: `--org-repo` alone fully rewires a new machine.

---

## For developers — extend and contribute

**Repo layout**

| Path | What |
|---|---|
| `.agents/workflows/` | Five RPCE workflows. See [`workflows/README.md`](.agents/workflows/README.md). |
| `.agents/skills/` | Seventeen reusable skills the workflows invoke (`skill-creator` is a tracked symlink into a sparse upstream submodule). See [`skills/README.md`](.agents/skills/README.md). |
| `.agents/slash/` | Slash commands — `/document`, `/rp-bash-roots`, `/commit`, `/pre-mortem`. See [`slash/README.md`](.agents/slash/README.md). |
| `.agents/rules/global.md` | Cross-cutting hard rules (git safety, stable IDs, minimalism, reconciliation gates). |
| `.agents/hooks/` | Canonical Python hooks enforcing those rules. See [`hooks/README.md`](.agents/hooks/README.md). |
| `docs/spec/` | Dogfooded specs + conformance matrices. Every workflow/skill/hook should have one (see [`docs/spec/README.md`](docs/spec/README.md) for current coverage). |
| `scripts/install.sh` | Idempotent installer — symlinks workflows/skills/commands/rules, registers Claude Code hooks, links an org repo's private rules overlay via `--org-repo`, and an optional custom style guide via `--style-guide` (auto-linked from `<org>/docs/style-guide.md` when `--org-repo` is given) (`--dry-run`, `--uninstall`). |
| `scripts/sync-maintainability-review.mjs` | Re-syncs the vendored `maintainability-review` lens from upstream. |
| `AGENTS.md` | Agent guide for working in this repo (`CLAUDE.md` is a symlink to it). |

**Keep workflows and skills in sync — both directions.** Each workflow inlines the discipline of the skills it depends on (so it runs without the skill installed) and names the skill as canonical. That binds them: **change a skill → update every workflow that inlines it; change an inlined discipline inside a workflow → update the source skill.** Drift between the inline copy and the skill is the main way this repo goes wrong.

**How the pieces fit**

- **Workflows** (RPCE) orchestrate. They inline the discipline from the skills they depend on; most run without the skill installed, but `Backlog` requires the `track-work` and `spec-plan-readiness` skills outright (no inline fallback).
- **Skills** are discovered by each runtime: Claude Code reads `.claude/skills` (project) + `~/.claude/skills` (personal) — not `.agents/skills`; Codex, opencode, pi, and Antigravity (`agy`) read `.agents/skills` (plus `~/.agents/skills` user scope); RepoPrompt CE's catalog scans both families for every backend it drives.
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

**Provenance** — extracted from a private mono-repo and de-branded for sharing. The workflows and skills are carried over from that source with install paths and READMEs adapted for this standalone repo.

**Runtime compatibility**

| Artifact | Claude Code | Codex | opencode | pi | agy | RPCE |
|---|---|---|---|---|---|---|
| Workflows | — | — | — | — | — | loads from app-support dir |
| Skills | `.claude/skills` + `~/.claude/skills` | `.agents/skills` + `~/.agents/skills` | `.agents/skills` | `.agents/skills` | `.agents/skills` + `~/.agents/skills` | scans all skill sources per backend |
| Commands | `~/.claude/commands` | `~/.codex/prompts` (deprecated → skills) | `.opencode/commands/` (not wired by the installer) | — | — (skills become slash commands in its TUI) | `~/.agents/slash` + workspace `.agents/slash` |
| Rules | portable | portable | portable | portable | — | — |
| Hooks | `~/.claude/settings.json` | `.codex/hooks.json` | `.opencode/plugins/*.mjs` | not yet supported | — | — |

**Standards** — skills follow the [Agent Skills](https://agentskills.io) open standard (`<skill>/SKILL.md` with `name`/`description` frontmatter), which Claude Code, Codex, opencode, pi, and Antigravity all read. The newer `.agents` directory-protocol draft ([dotagentsprotocol.com](https://dotagentsprotocol.com)) specifies a different skill format (lowercase `skill.md`, `id`/`enabled` frontmatter) and defines no `rules/`, `slash/`, `hooks/`, or `workflows/` — deliberately not adopted here; those directories are community extensions consumed by this repo's installer and RepoPrompt CE.

**License** — MIT; see [`LICENSE`](LICENSE). Third-party vendored content (`maintainability-review`, from [cursor/plugins](https://github.com/cursor/plugins/tree/main/cursor-team-kit/skills/thermo-nuclear-code-quality-review), MIT) is attributed in [`NOTICE`](NOTICE).
