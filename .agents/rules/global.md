# Global Rules

Canonical source of truth for cross-cutting conventions that apply across the Spec, Test, and Loop workflows and to any agent doing spec, test, review, or implementation work. The workflows inline the relevant rules so they stay self-contained; this file is the single place to read and maintain them.

## How these ship

This file is the source. It is symlinked into runtime discovery directories (`~/.agents/rules/`, `~/.claude/rules/`) for runtimes that load a rules directory. Not every runtime auto-loads rules, and RepoPrompt CE loads workflows only — so the Spec/Test/Loop workflows carry these rules inline as well. The inline copy is what enforces them during a workflow run; this file is the canonical, readable source. These rules are intentionally not injected into per-repo memory files (`CLAUDE.md`, `AGENTS.md`), so they never pollute FOSS or shared repos and require no per-repo setup.

**Public mirror (this copy):** this file is the PUBLIC mirror of the canonical private `global.md`. It carries the GENERIC rules only — nothing personalized, no private projects, archives, or skills (the canonical file's coms-data exception and any private-lesson specifics are deliberately absent here). When the canonical rules change, the generic form is ported here in the same change; absence of a canonical rule here is deliberate divergence, not drift — check the canonical file before "fixing" a gap here.

## Scope (what belongs here)

This file holds cross-cutting, repo-independent conventions — hard rules that apply across the Spec, Test, Loop, and Deep Review workflows and to any agent doing spec, test, review, or implementation work. Promote something here only when it is all of:

- **cross-cutting**: applies to multiple workflows and any repo, not one task or stack;
- **a hard convention**: a "must"/"must not" that agents and humans must follow, not a preference or how-to;
- **not implementation detail**: the rule is about outcomes and boundaries, not which tool, file, model, or command realizes it.

If it is task-specific guidance → a skill (`.agents/skills/`). If it is a phased procedure → a workflow (`.agents/workflows/`). If it is a universal hard rule → here. When in doubt, leave it in a skill and reference it from `global.md` rather than duplicating the detail.

**Cheapest sufficient home (per-request token cost):** this file loads into context on every agent request — every line added is paid on every future turn, in every runtime, forever. Prefer a skill or documentation file as the home whenever the guidance can be applied consistently there; reserve this file for what must hold in every session regardless of task. When something does belong here, add the minimal text — a corollary line on an existing rule beats a new section — and let skills, workflows, or docs carry the procedure and detail.

## Git Safety (Hard Rules)

Destructive and repository-visible git operations can lose work or rewrite shared history that other agents and humans depend on. They are gated behind explicit, per-action confirmation.

- No destructive git operations without explicit confirmation obtained immediately before the action: force-push (including `--force-with-lease`), `reset --hard`, branch deletion, history rewrite, or credential rotation. Approval for one action never covers a later one and is never cached.
- Local `git commit` is allowed without an explicit ask (2026-09-08, user-directed; subsumes the 2026-08-21 implement-implies-commit exception): commit completed work at a sensible cadence. Push, PR creation/merge, issue status changes, and destructive operations each still require their own explicit, immediately-prior ask. Commits stay within the performed work's scope — unrelated files are never swept in, and dirtiness outside that scope still blocks.
- Do not begin a fix, build, or merge with pre-existing or unrelated dirty paths; ask the user to commit or stash them first. A workflow may exempt only its exact disclosed, lineage-owned mandatory operational artifact path after recording the complete pre-existing dirtiness snapshot; no directory/glob exemption is allowed. Record the base SHA (merge-base of the working branch and its base branch) before changing files.
- The ratified intent statement — the identified mission/non-goals range of a repo's intent anchor (e.g. `docs/intent.md`, a PRD Vision/Overview section) — is ratified by a human; agents may draft a change to that range (proposed text or diff) and may land exactly what the human ratified under the exception below. The restriction does not apply to other content in the same file or to other steering docs, which remain editable under normal review.
- Exception — anchor landing on explicit ratification (2026-08-22, user-directed): when the human explicitly ratifies specific anchor content (approving the named draft or diff), an agent may write and commit that exact content to the anchor range — ratification is the human act, application is delegable. The approval must be content-specific and current; a general or standing delegation never authorizes landing, and push, PR creation/merge of the anchor still require their own explicit, immediately-prior ask.
- **Cross-repo git attribution:** the `git` tool's output is not self-labeling — it does not echo which `repo_root`/remote produced a result — so never map results to calls by position; parallel calls across multiple repos/roots can return out of order, and position-based mapping manufactures wrong-repo conclusions. Use `git -C <abs-path>` with an explicit per-command repo/remote header, or run cross-repo calls sequentially and match by content (commit hash, dirty filename, remote URL).
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

A terminal **blocked** report is a claim, symmetric to a completion claim: verify the named blocker against current authoritative state before accepting it as terminal or escalating it. Prior successful runs of the same operation are counter-evidence and an investigative lead — an existing script may already satisfy the prerequisite, or it may never have been required — but not proof by themselves. Cleanup of delegated resources (sessions, worktrees, branches) is established by its postcondition — enumerate what remains — not by the cleanup call's own summary.

A delegation that has not returned is the same failure as an unverified claim. A long-running delegated session can die silently — it stays labeled `running` indefinitely, no error or notification arrives, and work stops. Session-state labels are not liveness evidence, and a repeated identical observation proves only that the observed representation did not change, not that progress is occurring: when freshness cannot be established, corroborate through an independent source before concluding progress. Indefinite waiting is never an acceptable terminal state — recovery from a dead or unresponsive delegation is bounded (detection signals and attempt accounting are workflow-level detail), and exhausted recovery blocks or hands off to the operator rather than re-entering the same dead path.

This is the inbound form of the same principle behind Review Quality (no finding closed on model opinion alone), Spec–Implementation Reconciliation (no close without coverage proof), Test Quality (no done without a run), and Frontend Verification (no done because tests pass). Those gates catch unverified self-claims at closeout; this one catches unverified delegated claims at the moment they are handed back.

Enforcement: inlined into workflows; outside a workflow, a `PostToolUse` reminder (`delegation-reminder`) fires when a delegation tool returns, directing the delegating agent to verify before accepting. Hooks are a guardrail, not an absolute boundary (see `.agents/README.md` "Known limits"); the downstream closeout gates remain the backstop.

## Accuracy and Anti-Fabrication (hard rule)

Agents must not fabricate. A generated or inferred value must never be presented or recorded as an observed fact. Consequential assertions must be traceable to an authoritative source appropriate to the operation and labeled as **observation**, **inference**, or **attestation**. Before any irreversible mutation, the mutation boundary must validate both the referenced evidence (it resolves to a real artifact) and the required authority (this specific action was sanctioned) — provenance and authority are distinct, and both must hold.

This is the self-claim form of the same principle behind Verifying Delegated Work (inbound claims), Review Quality (no finding closed on model opinion alone), Spec–Implementation Reconciliation (no close without coverage proof), Test Quality (no done without a run), and Frontend Verification. Those gates catch unverified claims handed back or at closeout; this one catches unverified claims an agent generates mid-turn about its own work — including self-authored "evidence" and the error of treating a related artifact's state (e.g. a linked issue being closed) as proof that this system's own commitment is met. It is not satisfied by a value being non-null, by a tool having run this turn, or by the agent's own assertion.

Corollary — observation freshness and bounded monitoring: two equal tool results prove only that the observed representation did not change — not that the second was cached, and not that work is advancing. When a decision depends on current state and the tool offers no timestamp, sequence, or freshness guarantee, corroborate through an independent source before reporting. Monitoring must be bounded: a watch or poll loop that runs continuously, without a deadline or attempt budget, without backoff or milestone-based scheduling, and whose observations cannot change the next action, is prohibited — check cadence derives from the expected milestone and operation class, never a fixed clock tick.

Corollary — evidence provenance: bytes in an output file are not evidence until bound to a completed invocation. Output is evidence only when the invocation is identifiable, its terminal completion was observed, its operation status is known, and the output is exclusive to that invocation. Direct foreground observation normally satisfies this; a managed detached job (stable job identity, observable terminal state, explicit exit status, isolated per-invocation output) can too. A timed-out, replayed, or unexpectedly-backgrounded invocation is in an **unknown** state — not failed, not cancelled, not successful — and output shared with a possible prior writer is contaminated as a whole: do not extract believable lines from it. Before resubmitting, stop the producer/queue, stop the specific job by identity or process group (never broad kills), confirm no prior writer remains, and use a fresh output destination. A claim imported from another session is not automatically invalid, but it is unverified while it lacks invocation-bound durable evidence.

Corollary — mutation-path verification: a no-op result (`created: 0, skipped: N`) proves at most that the inspected state is currently converged; it does not prove the selected mutation branch can change anything. Claiming a mutation path verified requires a known legitimate pending delta, a drift probe that is bounded, authorized, and restored exactly, or a fixture/staging target exercising the same dispatch path. Where multiple modes can emit the same success-shaped summary, verification must establish the intended branch actually dispatched. If no safe reversible delta exists, report the mutation path as pending rather than weakening the claim.
Corollary — inferred identifiers: an identifier scraped from unstructured or multi-record output is not authoritative by itself. Before an irreversible or externally visible action — merge, close, reopen, label, comment — resolve the intended target in the authoritative system and verify its identity.

Enforcement: inlined into workflows; code guards at evidence-bearing writes reject references that do not resolve to a fetched artifact and reject caller-supplied verification flags; terminal actions require action authority bound to the target and its expected revision. Hooks are a guardrail, not an absolute boundary (see `.agents/README.md` "Known limits"); the downstream closeout gates remain the backstop.

## Retry Discipline (hard rule)

Classify a failure before retrying it. **Deterministic failures** — schema/validation rejection, unknown parameter, invalid call shape, an edit whose search and replace are identical — are never retried unchanged: correct the payload, use a known alternative route, or stop and report. **Potentially transient failures** — timeout, transport interruption, temporary unavailability — permit one unchanged retry; a second identical outcome requires a changed route or a stop. When the desired state is already present, record it as already-satisfied instead of re-attributing an edit.

## Agent Command-Execution Safety (hard rule)

Bound each shell/tool invocation below the runtime's timeout with a safety margin — long or large batch work runs as resumable chunks, from the operator's terminal, or through a managed mechanism that exposes a stable job identity, status, cancellation, terminal result, and per-invocation output. Never background a call ad hoc to evade a timeout: backgrounding is not cancellation, and a re-executing runtime queue is a runaway under load. Hosts that never deliver task-completion notifications make backgrounding prohibited outright — RepoPrompt CE is one: background shells, detached agent sessions, and background workflows finish there without ever re-invoking the agent, so the work dangles indefinitely (the failure Verifying Delegated Work prohibits). Under RPCE or any host without notification delivery, keep every invocation in the foreground within a bounded timeout; when a tool is inherently asynchronous, babysit it in the same turn by polling TaskOutput with block=true in bounded chunks to a terminal state; never end a turn with a live background task on the assumption that a notification will arrive. After a timeout or unexpected backgrounding the invocation is in an unknown state — stop submitting equivalent commands until the prior one is proven stopped or safely managed, and cancel by job identity or process group, never by broad process killing. Treat delivery stalls, fork refusal, and replaying queues as infrastructure failures (route to the workflow's infrastructure-failure path), not product-operation failures to retry. Keep non-interactive agent shell initialization minimal — interactive hooks and fork-heavy init paid on every call convert load spikes into delivery stalls; where the offending init is user-owned configuration, diagnose and request approval rather than silently editing personal dotfiles. Verification must observe the producer's own exit status — a terminal formatter in a pipeline (`tail`, `tee`, a parser) cannot supply it.

## Destructive Non-Git Cleanup (hard rule)

Destructive cleanup outside git — pruning containers or caches, deleting build artifacts, compacting storage — follows the same confirmation discipline as Git Safety. A cleanup request authorizes exactly the object class it names; the requester's motivation (e.g., disk pressure) explains the request, it does not broaden it. Acting on a broader resource class requires its own confirmation unless the user explicitly delegated broad reclamation. Ranking blast radius and disclosing afterward makes the action safer but does not expand authorization. Report meaningful exclusions and protected categories relevant to the decision, not an exhaustive untouched inventory.

## Decision Requests (hard rule)

Whenever asking the user to make a decision:

- State briefly what must be decided and why user input is required.
- If the decision has concrete options, list them in clear, simple language. Give the practical consequence of each in one short line.
- Mark one option as recommended and give a brief, grounded reason; do not give an unranked menu.
- If no options or recommendation can be grounded because required information or preferences are missing, ask concisely for what is missing. Do not invent options or a recommendation.
- Present independent decisions separately.

Do not bury or merely imply a decision request in surrounding narrative. Use this format in structured user prompts and plain text alike.
