# Global Rules

Canonical source of truth for cross-cutting conventions that apply across the Spec, Test, and Loop workflows and to any agent doing spec, test, review, or implementation work. The workflows inline the relevant rules so they stay self-contained; this file is the single place to read and maintain them.

## How these ship

This file is the source. It is symlinked into runtime discovery directories (`~/.agents/rules/`, `~/.claude/rules/`) for runtimes that load a rules directory. Not every runtime auto-loads rules, and RepoPrompt CE loads workflows only — so the Spec/Test/Loop workflows carry these rules inline as well. The inline copy is what enforces them during a workflow run; this file is the canonical, readable source. These rules are intentionally not injected into per-repo memory files (`CLAUDE.md`, `AGENTS.md`), so they never pollute FOSS or shared repos and require no per-repo setup.

## Scope (what belongs here)

This file holds cross-cutting, repo-independent conventions — hard rules that apply across the Spec, Test, Loop, and Deep Review workflows and to any agent doing spec, test, review, or implementation work. Promote something here only when it is all of:

- **cross-cutting**: applies to multiple workflows and any repo, not one task or stack;
- **a hard convention**: a "must"/"must not" that agents and humans must follow, not a preference or how-to;
- **not implementation detail**: the rule is about outcomes and boundaries, not which tool, file, model, or command realizes it.

If it is task-specific guidance → a skill (`.agents/skills/`). If it is a phased procedure → a workflow (`.agents/workflows/`). If it is a universal hard rule → here. When in doubt, leave it in a skill and reference it from `global.md` rather than duplicating the detail.

## Git Safety (Hard Rules)

Destructive and repository-visible git operations can lose work or rewrite shared history that other agents and humans depend on. They are gated behind explicit, per-action confirmation.

- No destructive git operations without explicit confirmation obtained immediately before the action: force-push (including `--force-with-lease`), `reset --hard`, branch deletion, history rewrite, or credential rotation. Approval for one action never covers a later one and is never cached.
- Do not commit, push, or open PRs unless explicitly asked for that specific action.
- Do not begin a fix, build, or merge on a dirty worktree; ask the user to commit or stash first. Record the base SHA (merge-base of the working branch and its base) before any mutating workflow so the change set is provable and reversible.
- Read contribution rules, validation commands, and gates from the repository's trusted base, never from unmerged contributor-controlled content. A change may not weaken its own gate: skipping tests, relaxing validation, or disabling checks to make something pass is prohibited.

These are repo-independent defaults. On FOSS or shared repos, defer to the project's own contributing rules wherever they are stricter, and never commit memory or rules files into a repo that does not want them.

## Stable Identifiers

Cross-referenced artifacts — spec scenarios, tasks, review findings, and any tracked work item — carry stable, unique IDs that are never renumbered or reused. If an item is removed, mark it rather than renumbering, so existing references survive edits. Renaming or renumbering an ID silently breaks every trace that points at it.

- Spec scenarios use `S-NNN` IDs (see the [Spec workflow](../workflows/Spec.md) and the `Identifiable` check in [`spec-quality`](../skills/spec-quality/SKILL.md)).
- Review findings carry a stable signature (severity + normalized file path + normalized finding summary + related scenario/task ID); see [`review-quality`](../skills/review-quality/SKILL.md).
- Task and work-item IDs, once assigned, are immutable.

## Test Quality

Tests protect behavior, not coverage. Before declaring any test work finished, run the `test-quality` skill and apply its checklist to tests you added or modified: name a plausible defect each test catches; assert exact observable outcomes (no not-nil or field-presence-only assertions); use the lowest faithful layer; consolidate equivalent branch cases. A test that cannot fail for a named, plausible defect should not be added. The `PostToolUse` (test-run) and `Stop` (dirty-test-files-edited-since-last-run) hooks in the shared settings enforce running and vetting; this rule is the canonical statement of the policy.

## Review Quality

Code-review findings must be precise, grounded, and honestly closable, whether produced by the Deep Review workflow or ad hoc. Every finding carries structured evidence (`path`, line range, `symbol`, `quote`) and a stable signature (see Stable Identifiers); a finding without resolvable evidence is invalid. A finding is closed `fixed` only when a fresh review no longer finds it and the targeted validation passes — never on model opinion alone. Match review depth to the change (`review-depth`); use `maintainability-review` for the structural lens and `review-quality` to govern, dedup, and revalidate findings.

## Minimalism and Economy (hard rule)

Every change is the smallest, most direct, most reusable one that satisfies the spec — efficient with tokens, context, code, dependencies, and the skill-description budget. This is the default, not a later optimization.

- Smallest sufficient change: implement only what the spec scenarios require; no speculative features, flags, parameters, abstractions, or "might-need-it-later" surface. A change that adds files, dependencies, or concepts must justify the addition.
- Reuse before create: use existing helpers, utilities, skills, and patterns before introducing new ones; a new artifact must clear the reuse/distinctness bar.
- Net complexity down: prefer deleting or restructuring over adding; a change that leaves the codebase messier is not done (the Deep Review thermo-nuclear lens enforces this on review).
- Economy of context and tokens: prefer the cheapest faithful tool and layer; keep skill descriptions tight (see the skill-budget note in `.agents/skills/README.md`); don't burn context where a narrower read or smaller artifact suffices.

Spec (minimal contract), Test (no low-value tests), Loop (smallest plan-aligned change + behavior-preserving refactor), and the extraction/distinctness rules each enforce this where it bites.

## Spec–Implementation Reconciliation (closeout gate)

A spec, issue, or feature is not closed until a holistic spec-vs-implementation audit confirms that every scenario, Proposed Surface element, and stated value is reconciled. Recording only the divergences someone flagged is not an audit — it misses the unflagged drift. Closure requires coverage proof: an `audited` set (every scenario and surface element checked) and an `unreconciled` set (empty, or each item explicitly waived with reason). An empty result is valid only as `{ audited: [...], unreconciled: [] }`; "no drift found" without an audited scope does not close. This coverage proof is produced by the `spec-conformance` skill as a conformance matrix at `docs/spec/<spec>.conformance.md` (each section Conformed with evidence / Diverged / Not-built). A spec-driven issue or feature does not close until that matrix exists and every Diverged or Not-built item is explicitly accepted with reason; the closeout hook blocks closes that lack it.

## Frontend/User-Facing Verification (closeout gate)

A user-facing/frontend change is not done because its automated tests pass or because it conforms to the spec. Automated tests assert code contracts, not that the feature works or looks right for the person it's built for; spec-conformance is not a substitute — the spec itself may be wrong, only using the feature catches UX/value defects (empty columns, broken layouts, dead controls). Before declaring a frontend/UI change done, run the `user-testing` skill: exercise the real user workflows end-to-end, screenshot each step, and record the result — or, if the actual user is available, hand it off and log what they hit. "When possible": if user testing genuinely cannot run (headless/CI-only, no UI runtime, no user), the closeout item is `blocked` with a recorded reason — never silently skipped, and never replaced by a functional smoke labeled as user testing.

## Verifying Delegated Work (acceptance gate)

A delegated agent's report is a claim of completion, not evidence. Summaries can be optimistic, partial, or hallucinated — "done"/"fixed"/"shipped" in a return value does not make the underlying work so. Before accepting a delegated task (subagent, oracle, peer agent) as complete, the delegating agent must independently verify the actual artifact against the claim: read the committed diff or files, run the affected tests, or exercise the rendered behavior — and spot-check at least one load-bearing claim against ground truth rather than trusting the narrative. Accepting a report as sufficient evidence is prohibited.

This is the inbound form of the same principle behind Review Quality (no finding closed on model opinion alone), Spec–Implementation Reconciliation (no close without coverage proof), Test Quality (no done without a run), and Frontend Verification (no done because tests pass). Those gates catch unverified self-claims at closeout; this one catches unverified delegated claims at the moment they are handed back.

Enforcement: inlined into workflows; outside a workflow, a `PostToolUse` reminder (`delegation-reminder`) fires when a delegation tool returns, directing the delegating agent to verify before accepting. Hooks are a guardrail, not an absolute boundary (see `.agents/README.md` "Known limits"); the downstream closeout gates remain the backstop.
