# Agent Skills

Reusable, model-invokable guidance shared across the workflows in this repo. Each skill is a directory with a `SKILL.md`; skills are intentionally generic so they work across repositories and agent runtimes.

The workflows inline the discipline from these skills so they run deterministically even when a skill is not installed; each skill is the canonical standalone version for out-of-workflow use.

## Skills

| Skill | Location | Use when |
|---|---|---|
| `test-quality` | [`test-quality/SKILL.md`](test-quality/SKILL.md) | Creating, changing, reviewing, or deciding whether to add tests, fixtures, mocks, integration tests, end-to-end tests, smoke checks, or test plans in any language or stack. |
| `spec-quality` | [`spec-quality/SKILL.md`](spec-quality/SKILL.md) | Drafting, reviewing, repairing, or validating scenario-based specs while keeping them contract-level, observable, non-redundant, grounded in repo context, and free of implementation planning. |
| `spec-plan-readiness` | [`spec-plan-readiness/SKILL.md`](spec-plan-readiness/SKILL.md) | Checking whether a Spec plus Deep Plan is implementable before tests, code, or implementation delegation begin. |
| `spec-conformance` | [`spec-conformance/SKILL.md`](spec-conformance/SKILL.md) | Auditing whether an implementation actually matches its spec — a section-by-section Conformed/Diverged/Not-built matrix with coverage proof; required before closing a spec-driven feature. |
| `review-quality` | [`review-quality/SKILL.md`](review-quality/SKILL.md) | Producing, consuming, triaging, or revalidating code-review findings; enforces structured evidence, prompt-grounding, a revalidation gate, and stable-signature triage/dedup/rerank. |
| `review-depth` | [`review-depth/SKILL.md`](review-depth/SKILL.md) | Selecting how deep a code review should go (quick/standard/deep) from a change's size, spread, risk, and blast radius; deterministic, with an explicit-override escape. |
| `maintainability-review` | [`maintainability-review/SKILL.md`](maintainability-review/SKILL.md) | The thermo-nuclear maintainability lens (abstraction quality, giant files, spaghetti growth, code-judo). Vendored from upstream and version-tracked; re-sync via `scripts/sync-maintainability-review.mjs`. |
| `document` | [`document/SKILL.md`](document/SKILL.md) | Syncing documentation to code changes or auditing documentation drift, with dry-run proposals, cited code basis, and contract-doc conflict reporting. |
| `user-testing` | [`user-testing/SKILL.md`](user-testing/SKILL.md) | Verifying a frontend feature actually works for the user — exercise real workflows end-to-end with screenshots or a user hand-off; automated tests are necessary but not sufficient. |
| `track-work` | [`track-work/SKILL.md`](track-work/SKILL.md) | Create/update one tracking item per unit of work (GitHub Issues, or a file-based `.agents/issues/` backlog when there is no GitHub). Used first when work is about to start. |

## Discovery and install

Inside this repo, skills under `.agents/skills/` are discovered automatically by every backend RPCE drives — **Claude Code**, **Codex**, **opencode**, and **pi** all read `.agents/skills`. To make a skill global — available in other repos — symlink it into the backend's user home:

```bash
REPO="$(pwd)"   # run from the repo root
ln -sfn "$REPO/.agents/skills/test-quality" "$HOME/.agents/skills/test-quality"   # Codex user scope
ln -sfn "$REPO/.agents/skills/test-quality" "$HOME/.claude/skills/test-quality"   # Claude Code
```

How runtimes discover skills (verified against each runtime's own docs):

- **Claude Code** reads `.agents/skills` (project) and `~/.claude/skills` (user).
- **Codex** scans `.agents/skills` from `$CWD` up to `$REPO_ROOT`, plus `~/.agents/skills` (user scope).
- **opencode** and **pi** read `.agents/skills`.

One source of truth, read by every runtime — symlink rather than copy.

> **Skill-count budget:** Codex loads only each skill's name + description initially and shortens or omits descriptions when many skills are installed. Keep descriptions concise, front-load trigger words, and avoid proliferating overlapping skills: too many degrades triggering.

## Adding or updating skills

- Prefer a directory with `SKILL.md` for cross-runtime skills.
- Keep `SKILL.md` concise: frontmatter for discovery, then only durable workflow guidance.
- Put scripts, references, or assets in subdirectories only when they directly support the skill.
- Do not put README files inside individual skill folders; document repository-level install or discovery notes here instead.
- If a skill should be globally available, add or update symlinks rather than copying the skill into multiple homes.
- If a skill is maintained upstream, vendor it with provenance and a sync script rather than hand-editing (see `maintainability-review`).
- Run the distinctness check below before merging a new or renamed skill.

## Extracting reusable parts from workflows into skills

Workflows and skills have different jobs; discipline about what lives where keeps both lean and reusable.

- **A skill is canonical, reusable guidance** — independent of any one workflow, usable by any agent or runtime.
- **A workflow is an orchestrated procedure.** It may inline a skill's discipline so it runs deterministically even when the skill is not installed, while referencing the skill as the canonical source.

Because a workflow inlines a skill's discipline, the two must stay in sync: **change a skill → update every workflow that inlines it; change an inlined discipline inside a workflow → update the source skill.** Don't let the inline copy and the skill drift.

Extract a piece of a workflow into its own skill when it is **all** of:

1. **Reusable beyond the workflow** — another workflow, an ad-hoc agent task, or another repo would plausibly want it.
2. **Self-contained** — clear trigger, inputs, and output; does not depend on the workflow's phase state.
3. **Stable** — durable discipline, not one-off steps that change with the task.

Keep it inline when it is specific to that workflow's sequencing or phase gates, a thin restatement of a global rule (point at `rules/global.md` instead), or only meaningful inside that workflow.

## Distinctness check (when adding or renaming a skill)

A skill's `description` is the primary trigger. A new skill that overlaps an existing one gets picked for the wrong task. When adding or renaming:

1. **Quick check:** read every existing skill's `description`; give the new one a unique trigger. Keep the `review-*` and `spec-*` families distinct with role/phase words ("governs findings", "selects depth", "is a lens"; "well-formedness" vs "implementability").
2. **Authoritative check:** validate with trigger evals (~20 should-/should-not-trigger queries whose negatives are genuine near-misses), then iterate the description against a held-out set.
