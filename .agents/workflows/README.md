# RepoPrompt CE Workflows

Canonical [RepoPrompt CE](https://repoprompt.com) workflows live here. These are agent workflow prompts that RepoPrompt CE loads from its application support directory; this folder is the **source of truth**, and RepoPrompt CE reads each one through a symlink (see [Install](#install)).

## Workflows

| Workflow | File | Purpose |
|---|---|---|
| `Spec` | [`Spec.md`](Spec.md) | Elicit intent, draft scenarios and constraints, check for redundancy/gaps/ambiguity, and write a rigorous minimal spec to `docs/spec/`. |
| `Test` | [`Test.md`](Test.md) | Read a spec's Given/When/Then scenarios, discover the repo's test framework and conventions, map scenarios to native tests, and write them. |
| `Loop` | [`Loop.md`](Loop.md) | Consume a Spec doc and Deep Plan doc, verify readiness, then coordinate red/green/review/refactor loops with resumable progress. |
| `Deep Review` | [`Deep-Review.md`](Deep-Review.md) | Map a change set, run parallel context-grounded review shots across lenses (correctness, thermo-nuclear maintainability, security, tests, docs), aggregate and govern findings (stable signatures, dedup, revalidation), and reconcile with the author. Named Deep Review to avoid collision with RPCE's built-in Review. |
| `Backlog` | [`Backlog.md`](Backlog.md) | Discover and triage tracked issues via the `track-work` skill (bugs → priority → ease); for each, run Spec/Deep-Plan-if-missing then a worktree-isolated `Loop` subagent, verify closeout, and close via track-work. Max 3 concurrent; one unique worktree+branch per issue. |

`Spec` → `Test` form a pair: spec the work first, then generate tests against that spec. `Loop` builds on both by applying `spec-plan-readiness` to a Spec + Deep Plan, preserving inline fallback checks, and orchestrating implementation loops. `Deep Review` consumes a change set and produces governed, revalidatable findings; it pairs with `Loop`, where accepted findings become follow-up tasks. `Backlog` sits above `Loop`: it discovers and triages tracked issues (via the `track-work` skill), and for each runs `Spec`/Deep-Plan-if-missing then a worktree-isolated `Loop`, verifying closeout and closing the item — max 3 concurrent, one worktree+branch per issue. Reusable discipline a workflow needs lives in a [skill](../skills/README.md) (see "Extracting reusable parts from workflows into skills"); each workflow inlines a copy and names the skill canonical. Keep them in sync: change an inlined discipline in a workflow and you must update its source skill; change a skill’s discipline and you must update every workflow that inlines it.

## Install

RepoPrompt CE looks for `*.md` workflows in:

```text
~/Library/Application Support/RepoPrompt CE/Workflows/
```

Symlink each workflow there so the app picks up the tracked copy:

```bash
WF="$HOME/Library/Application Support/RepoPrompt CE/Workflows"
REPO="$(pwd)/.agents/workflows"   # run from the repo root (or paste your clone's absolute path)
mkdir -p "$WF"
ln -sfh "$REPO/Spec.md" "$WF/Spec.md"
ln -sfh "$REPO/Test.md"  "$WF/Test.md"
ln -sfh "$REPO/Loop.md"  "$WF/Loop.md"
ln -sfh "$REPO/Deep-Review.md" "$WF/Deep-Review.md"
ln -sfh "$REPO/Backlog.md"      "$WF/Backlog.md"
```

After restarting RepoPrompt CE, all five workflows should appear in the workflows picker. Edit them here in the repo — RepoPrompt CE follows the symlinks automatically.

> Note: the RepoPrompt CE Workflows directory also holds an app-managed `.DS_Store`; leave it alone. If you add a new workflow, drop the `.md` here and add a matching `ln -sfh` line above.
