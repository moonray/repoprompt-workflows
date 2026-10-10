# RepoPrompt CE Workflows

Canonical [RepoPrompt CE](https://repoprompt.com) workflows live here. These are agent workflow prompts that RepoPrompt CE loads from its application support directory; this folder is the **source of truth**, and RepoPrompt CE reads each one through a symlink (see [Install](#install)).

## Workflows

| Workflow | File | Purpose |
|---|---|---|
| `Spec` | [`Spec.md`](Spec.md) | Elicit intent, draft scenarios and constraints, check for redundancy/gaps/ambiguity, and write a rigorous minimal spec to `docs/spec/`. |
| `Test` | [`Test.md`](Test.md) | Read a spec's Given/When/Then scenarios, discover the repo's test framework and conventions, map scenarios to native tests, and write them. |
| `Loop` | [`Loop.md`](Loop.md) | Initialize durable progress, consume an immutable Spec/Deep Plan tuple, gate readiness/delegation, and coordinate red/green/review/refactor. Standalone missing-contract work hands off externally; orchestrated work stops at `merge_ready`. |
| `Deep Review` | [`Deep-Review.md`](Deep-Review.md) | Map a change set, run parallel context-grounded review shots across lenses (correctness, thermo-nuclear maintainability, security, tests, docs), aggregate and govern findings (stable signatures, dedup, revalidation), and reconcile with the author. Named Deep Review to avoid collision with RPCE's built-in Review. |
| `Backlog` | [`Backlog.md`](Backlog.md) | Discover/triage via `track-work`, own external contract preparation and deterministic re-gating, dispatch isolated Loop epochs, independently verify `merge_ready`, then own publication, landing, status/close, replacement, and cleanup. |

`Spec` → `Test` form a pair: spec the work first, then generate tests against that spec. `Loop` initializes its durable epoch before readiness, applies `spec-plan-readiness` to an immutable Spec + Deep Plan tuple, preserves inline fallback checks, and orchestrates implementation loops without assuming landing responsibility. `Deep Review` consumes a change set and produces governed, revalidatable findings; it pairs with `Loop`, where accepted findings become follow-up tasks. `Backlog` sits above `Loop`: it owns external `Spec`/RPCE core `Deep Plan` preparation, immutable contract identity, deterministic readiness, dispatch/replacement, independent closeout verification, publication/landing, issue status/close, and cleanup — max 3 concurrent, one unique worktree+branch per issue. Reusable discipline a workflow needs lives in a [skill](../skills/README.md) (see "Extracting reusable parts from workflows into skills"); each workflow inlines a copy and names the skill canonical. Keep them in sync: change an inlined discipline in a workflow and you must update its source skill; change a skill’s discipline and you must update every workflow that inlines it.

## Install

RepoPrompt CE loads `*.md` workflows from `~/Library/Application Support/RepoPrompt CE/Workflows/`; this folder is the source of truth, read through symlinks.

The repo installer ([`../../scripts/install.sh`](../../scripts/install.sh)) links every workflow here and re-links on re-run. New workflows are picked up **automatically** — just drop a `.md` in this directory; the installer scans it, so there's no manual `ln` line to maintain.

Manual fallback (run from the repo root):

```bash
WF="$HOME/Library/Application Support/RepoPrompt CE/Workflows"
mkdir -p "$WF"
for w in Spec Test Loop Deep-Review Backlog; do
  ln -sfh "$(pwd)/.agents/workflows/$w.md" "$WF/$w.md"
done
```

Restart RepoPrompt CE and all workflows appear in the picker. Edit them here — RPCE follows the symlinks.

> The RPCE Workflows directory also holds an app-managed `.DS_Store`; leave it alone.
