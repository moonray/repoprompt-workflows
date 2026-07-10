# Agent Guide — repoprompt-workflows

This repo ships an agent workflow system for RepoPrompt CE: five **workflows**, the ten **skills** they invoke, slash **commands**, cross-cutting **rules**, enforcing **hooks**, and the dogfooded **specs** that document them.

`CLAUDE.md` is a symlink to this file — edit here, not there.

> The hard rules — git safety, stable identifiers, minimalism, and the reconciliation / frontend / delegated-work verification gates — live in [`.agents/rules/global.md`](.agents/rules/global.md) and apply to all work here. Read it first.

## Layout

- `.agents/workflows/` — five RPCE workflows: `Spec`, `Test`, `Loop`, `Deep-Review`, `Backlog`.
- `.agents/skills/` — ten skills, each `<name>/SKILL.md`.
- `.agents/slash/` — slash commands (`document.md`).
- `.agents/rules/global.md` — cross-cutting hard rules (canonical).
- `.agents/hooks/` — Python hook scripts enforcing those rules.
- `docs/spec/` — dogfooded specs + conformance matrices for each workflow/skill.
- `scripts/install.sh` — idempotent, scan-driven installer (symlinks workflows/skills/commands; `--dry-run`, `--uninstall`).
- `scripts/sync-maintainability-review.mjs` — re-syncs the vendored `maintainability-review` lens.

## Editing rules (what an agent must preserve)

- **Inline-sync contract.** Each workflow inlines the discipline of the skills it depends on so it runs deterministically without the skill installed, and names the skill as canonical. When you change a skill's discipline, update every workflow that inlines it — and vice versa. Don't let the inline copy and the skill drift.
- **Vendored lens is sync-managed.** `maintainability-review` (the skill and the `Deep-Review` inline block) is bounded by `BEGIN/END` markers and synced from upstream by `scripts/sync-maintainability-review.mjs`. Never hand-edit between the markers — run `node scripts/sync-maintainability-review.mjs --update`.
- **Stable identifiers.** Spec scenarios use `S-NNN` IDs; review findings carry stable signatures. Never renumber or reuse; if one is removed, mark it, don't shift the rest.
- **Skill descriptions are triggers.** A skill's frontmatter `description` is what makes it fire. Before adding or renaming a skill, run the distinctness check in [`.agents/skills/README.md`](.agents/skills/README.md) — overlapping descriptions misfire.
- **Hooks are runtime-agnostic Python.** Keep guarantee logic in `.agents/hooks/*.py` (JSON on stdin); register per backend. Prefer a reminder over a gate unless the guarantee is observably enforceable.
- **Keep specs in sync.** `docs/spec/<name>.md` (with its `.conformance.md`) is the contract for workflow/skill `<name>`. A behavior change is reflected in its spec; status reflects reality (these are all `implemented`).

## Verifying changes

This is a content repo — no build, no test suite. Verify by:

- Reading changed markdown end-to-end.
- `grep` to confirm cross-references resolve (skill names a workflow references exist as skill dirs; internal links resolve).
- For the vendored lens: `node scripts/sync-maintainability-review.mjs` (no `--update`) reports drift.
- `git diff` before declaring done.

## Don't

- Don't commit, push, or open PRs unless explicitly asked.
- Don't hand-edit between the vendored `BEGIN/END` markers.
- Don't weaken a gate or skip validation to make something pass.
- Don't renumber stable identifiers.
