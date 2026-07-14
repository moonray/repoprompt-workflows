---
title: Backlog Workflow
issue: none
status: implemented
---

# Backlog Workflow

## Problem

Backlog is an orchestrator that processes tracked work items — up to three at a time — each isolated in its own worktree and implemented by a worktree-isolated **Loop** subagent. Like Loop before it had a spec, Backlog lives only as an operational workflow prompt that mixes the behavioral contract (the autonomy guarantee, the authorization boundary, the verify-before-close gate) with implementation mechanics (which MCP op, which branch slug, which wizard field). Two things now force a separated contract:

1. The workflow is being hardened for **hands-off autonomy** — "only ask at the start." That is a strong behavioral guarantee (zero mid-run user questions) that needs Given/When/Then observables, not prose.
2. The repo's own Spec–Implementation Reconciliation closeout gate requires a spec to conform against, and Backlog is itself the workflow that enforces conformance matrices — a workflow with no spec of its own is an untenable asymmetry.

A stable contract is needed so future changes are made against what Backlog guarantees, independent of how each phase is realized.

## Goals

1. Define Backlog's contract — the autonomy boundary, authorization scope, isolation, verify-before-close gate, and escalation ladder — independent of mechanism, as the single source of truth.
2. Guarantee the Phase-2 wizard is the **only** `ask_user` of a run; every later decision is made autonomously (policy + oracle) or recorded-as-blocked-and-skipped — never a mid-run user question.
3. Guarantee git-visible actions never exceed what the wizard authorized, and that the authorization is informed (concrete actions enumerated) and bounded (to the triaged issue set).
4. Guarantee one unique worktree + branch per issue, with orphaned sessions/worktrees from prior interrupted runs reconciled before any new dispatch.
5. Guarantee closeout is never trusted on a subagent's report — the orchestrator independently reads the diff, re-runs the targeted tests, and confirms the conformance matrix before closing.
6. Guarantee exempt and decision items are handled without spawning a subagent or asking — exempt items via a wizard-confirmed close batch; decisions routed to human triage, never auto-resolved.
7. Guarantee a run is resumable after interruption by reconstructing flight state and the persisted authorization from the progress doc, without asking the user.

## Non-Goals

- Implementation detail of any individual issue — that is delegated to **Loop**.
- Choosing agent model, validation lane, or repo-specific toolchain values — those are plan-level / brief-carried.
- Authoring specs or deep plans — chained via track-work when missing; their creation is a separate, referenced process.
- The runtime's approval/permission-inheritance mechanism — Backlog probes capability and degrades; it does not own runtime semantics (see Open Questions).

## Constraints

- Discovery, blocked-marking, and closing all go through **track-work** so the GitHub and file (`.agents/issues/`) backends are handled uniformly; Backlog never calls `gh` or reads issues directly for discovery.
- At most **3** Loop subagents are in flight; independent issues fill the flight set by default (S-035) and only genuinely contended work serializes (S-015, S-035); excess issues queue. The ceiling is per run: global RPCE/provider load from other windows may be invisible, so shared-capacity risk is captured in the wizard and may lower the local default.
- One unique worktree + branch per issue, named from the immutable track-work ID (`backlog/<id>-<slug>`); branches are never deleted.
- Only the outer layer changes issue status; Loop subagents move their progress doc only.
- Git-visible actions stay inside the wizard-selected completion path; that selection is the explicit, scoped authorization. Destructive git is prohibited and is **not** grantable via any scope.
- Subagents escalate to the orchestrator, never to the end-user.
- These workflows are global/canonical (symlinked to every runtime): repo-specific values (toolchain paths, data locations, the specific browser tool) enter only via the dispatch brief, never hardcoded in the contract.

## Scenarios

### Scenario S-001: Discovery is backend-agnostic via track-work
- **Given** a run is starting
- **When** Backlog discovers open work items
- **Then** it uses track-work noninteractively, which selects backend from trusted override/origin identity, binds GitHub operations to the canonical repository, and blocks on unavailable capability without prompting or reading a fallback ledger

### Scenario S-002: Triage order is bugs, then priority, then ease
- **Given** the discovered open, non-exempt items
- **When** Backlog triages
- **Then** `type:bug` items come first, then by `priority` p0→p3, then by ease (small/labeled-effort before large; unlabeled last)

### Scenario S-003: Exempt items are a close-candidate batch, not silently dropped
- **Given** discovered items include exempt items (`wontfix`, `duplicate`) already carrying the human-decision label
- **When** Backlog finishes discovery
- **Then** it emits two lists — a work queue and an exempt-close batch — and the exempt batch is shown in the wizard for one-shot close confirmation, with `duplicate` closes cross-linking the canonical issue; it is never silently dropped nor spawned a subagent

### Scenario S-004: The wizard is the only ask of the run
- **Given** a run is in progress past Phase 2
- **When** a decision is needed mid-run
- **Then** it is resolved autonomously (policy, then oracle) or recorded-as-blocked-and-skipped, and `ask_user` is never called again; if the Phase-2 wizard times out, the run halts and resumes on reply rather than proceeding

### Scenario S-005: Git-visible actions never exceed the wizard authorization
- **Given** the wizard captured a completion path and the user confirmed it after the wizard enumerated the concrete git actions it implies (push branch / open PR / merge to default)
- **When** Backlog performs git-visible actions during the run
- **Then** it never exceeds that path, the authorization is persisted with the run (path, doc-edits flag, triaged issue set, timestamp), and merges are bounded to the triaged issue set only

### Scenario S-006: Capability gaps surface in the wizard or trigger a restart ask — never a mid-run surprise
- **Given** a capability the run depends on (oracle, subagent unattended-approval mode, a required MCP tool such as chrome-devtools for UI issues, tracking-backend CLI auth, git remote for push-bearing paths)
- **When** Backlog probes each via a **call-based test** before the wizard is rendered
- **Then** each gap is shown in the wizard with its consequence or the affected issues are auto-annotated blocked, AND if a required MCP tool is unreachable the user is asked to **restart the runtime** before proceeding — never discovered as a mid-run surprise

### Scenario S-007: Spec generation requires both clarity gates
- **Given** an issue lacks a linked spec and/or deep plan
- **When** Backlog decides whether to spec it
- **Then** it runs a deterministic pre-check and an independent oracle clarity verdict, and chains Spec → Deep Plan only if both pass; otherwise the issue is blocked with the reason

### Scenario S-008: Oracle-down degrades existing-spec issues and blocks spec-needing ones
- **Given** the oracle is unreachable
- **When** Backlog processes the queue
- **Then** issues with an existing spec+plan proceed with deterministic gates authoritative (brief marked degraded, verdict recorded), issues needing spec generation are blocked, and the orchestrator owns all scope decisions for degraded issues

### Scenario S-009: One unique worktree and branch per issue
- **Given** an issue is about to be dispatched
- **When** Backlog allocates a worktree
- **Then** no two Loop subagents ever share a worktree or branch, and the branch is named from the immutable track-work ID

### Scenario S-010: Pre-dispatch sweep reconciles orphans
- **Given** prior interrupted runs may have left orphaned `backlog/*` sessions/worktrees/branches
- **When** Backlog allocates a worktree before dispatch
- **Then** it reconciles them first (resume if live; clean the dead session if expired/idle, keeping PR-open/local-only worktrees), reusing a branch only after verifying it is at base **and unbound**, quarantining any branch still bound to a dead session whose cleanup skipped, and never reusing an in-use worktree

### Scenario S-011: Dispatch calls are isolated in their own tool batch
- **Given** Backlog is about to start a Loop subagent
- **When** it issues `agent_run op=start`
- **Then** that start is the only call in its tool batch — never batched with `gh`, board/status moves, `cleanup_sessions`, or verify/test commands — so a rejection cannot cascade into a half-provisioned session

### Scenario S-012: Every dispatch attempt is reconciled, including starts that return no handle
- **Given** a detached `start` may be rejected, interrupted, or timed out after provisioning tab+worktree+branch but before returning a usable `session_id` or launching the provider
- **When** Backlog evaluates the attempt
- **Then** before each `start` it persists the incremented attempt number + deterministic session name + branch, polls a returned handle or inventories sessions/worktrees by that identity when no handle exists, adopts a discovered `running`/`waiting_for_input` session, and safely cleans attributable half- or partial-provisioning before retrying; every `start` invocation and every non-live terminal result consumes an attempt, it never abandons or blindly retries an unknown outcome, never steers a providerless session, and blocks after the second attempt that does not reconcile to a live provider

### Scenario S-013: Concurrent issues are sibling-aware
- **Given** more than one Loop is in flight
- **When** each is briefed
- **Then** each brief names the other in-flight issues/areas so agents avoid logical conflicts even though worktrees are isolated

### Scenario S-014: At most three issues are in flight
- **Given** the queue has more than three independent issues
- **When** Backlog dispatches
- **Then** it holds the flight set to ≤3 and queues the rest; reaching the cap or draining the queue moves to rollup with no "continue?" ask

### Scenario S-015: Issues sharing a target spec serialize
- **Given** two queued issues target the same spec (and thus likely shared surface)
- **When** Backlog schedules them
- **Then** they do not fly concurrently, so the canonical `<spec>.conformance.md` path is never contended

### Scenario S-016: Closeout is verified independently, not trusted
- **Given** a Loop subagent reports done
- **When** Backlog verifies before closing
- **Then** it reads the load-bearing diff itself (including a grep for each amendment's requested change), re-runs the targeted test commands in the issue's worktree itself, confirms a conformance matrix exists with every Diverged/Not-built item accepted, and steers for a focused follow-up rather than closing on insufficient evidence

### Scenario S-017: Verify overlaps the next dispatch but never precedes close or cleanup
- **Given** a Loop has landed and is being verified
- **When** the next issue could be dispatched
- **Then** the freed flight slot may be refilled while verifying, but the issue's close strictly follows verify and `cleanup_sessions` strictly follows close — never the reverse

### Scenario S-018: CI failure on merge parks without asking
- **Given** the completion path authorizes merge and a merge is attempted
- **When** the close_gate/CI is red
- **Then** the issue is left at `branch+pr` with `status:review` and flagged in the rollup — never merged and never the subject of a mid-run "merge anyway?" ask

### Scenario S-019: Merge conflicts regenerate derived docs or block
- **Given** a per-issue serial rebase-merge hits a conflict
- **When** Backlog resolves it
- **Then** conflicts limited to allowlisted derived/append-only closeout docs (conformance matrices, progress entries, spec-README index) are regenerated on the rebased tree; any code/test/spec/plan conflict aborts the rebase to `status:blocked` with branch+worktree kept — "take canonical" is never applied to source

### Scenario S-020: Decision items are never auto-resolved
- **Given** a queued item is `type:decision`
- **When** Backlog processes it
- **Then** it is never auto-closed or spec'd by a subagent; it goes to the rollup as a human-triage item

### Scenario S-021: The ledger captures reconstructable flight state
- **Given** a run is in progress
- **When** any issue changes state
- **Then** the progress-doc ledger records `session_id`, `worktree_id`, branch, base SHA, lifecycle state, amendments, and accepted divergences for it; a `cleanup_sessions` skip is tolerated (the session is routed around, not revived)

### Scenario S-022: Resume reconstructs flight state without asking
- **Given** a run is restarted after interruption
- **When** Backlog resumes
- **Then** it reconstructs the flight set and the persisted authorization from the ledger joined with `list_sessions` + `git worktree list` + `git branch --list 'backlog/*'`, reuses the prior grant without re-running the wizard, and blocks any issue unreconcilable with reality

### Scenario S-023: Escalation decides or blocks, never asks
- **Given** a mid-run decision falls outside the never-autonomous set (actions beyond authorization scope; destructive git; weakening any gate; credentials/spend; deciding a decision item's content)
- **When** Backlog escalates
- **Then** oracle-decidable matters are decided and recorded with rationale; everything else (including the entire never-autonomous set) is set `status:blocked` via track-work and accumulated for the rollup — no branch reaches `ask_user`

### Scenario S-024: The rollup records outcomes, divergences, and resume
- **Given** the queue has drained or the issue cap is reached
- **When** Backlog rolls up
- **Then** it reports per-issue outcome (done/blocked/skipped + reason), worktree+branch, PR/commit ref, accepted divergences, degraded-mode entries, kept-vs-removed worktrees, and an exact resume instruction

### Scenario S-025: Browser user-testing is concurrent-safe via isolated profiles (or serialized)
- **Given** more than one in-flight issue needs browser-based user-testing
- **When** Backlog dispatches their user-testing
- **Then** each runs against its own isolated/throwaway browser profile (chrome-devtools-mcp `--isolated`, or `--experimentalPageIdRouting` for a shared-server runtime) so they do not collide on the default shared profile; absent either, browser user-testing serializes one at a time

### Scenario S-026: Resume syncs the tree before retroactive verify
- **Given** a resumed run will retroactively verify or user-test items that already merged
- **When** Backlog resumes
- **Then** it fetches and fast-forwards local `<default>` to `origin/<default>` (`--ff-only`) and grep-confirms each to-be-verified fix is present in the tree before any verify/user-testing — never testing a stale, pre-fix tree

### Scenario S-027: Retroactive user-testing after a merge that skipped the frontend gate
- **Given** an item merged without the user-testing gate (e.g. recovered on resume)
- **When** Backlog detects the gap
- **Then** it runs the `user-testing` skill against the synced merged tree with a throwaway data location and records the result on the issue/progress doc — a recovery path, not a substitute for pre-merge UT

### Scenario S-028: Item status is authoritative from track-work only
- **Given** a human-curated input run-note makes status claims about items
- **When** Backlog builds the work queue
- **Then** it treats track-work status as authoritative and re-verifies each item's real state rather than trusting the run-note

### Scenario S-029: Orchestrator finishes an incomplete git flow
- **Given** a Loop stops before completing the steps its `git_scope` authorizes (e.g. stops at commits)
- **When** Backlog detects the incomplete flow
- **Then** the orchestrator finishes push/PR/merge within scope itself and records it, rather than leaving the issue half-done

### Scenario S-030: Close-keyword mandate on GitHub merge
- **Given** the GitHub backend and a `git_scope` that covers merge
- **When** Backlog or Loop squash-merges
- **Then** the squash-merge subject carries `(#N)` and the PR body carries `Closes #N`, so both GitHub auto-close and the close-gate fire

### Scenario S-031: Browser-isolation is detected before concurrent user-testing
- **Given** more than one in-flight issue needs browser user-testing
- **When** Backlog decides whether to run them concurrently
- **Then** it confirms the browser MCP is `--isolated`/`--experimentalPageIdRouting` (config inspection or a two-caller probe) before concurrent use; if isolation cannot be confirmed, it serializes

### Scenario S-032: Repo hard-constraints ride in the brief
- **Given** a repo declares hard rules (e.g. in `CLAUDE.md`/`AGENTS.md`)
- **When** Backlog dispatches a Loop
- **Then** the brief carries a `constraints` field populated from those repo rule docs verbatim (never hardcoded in the workflow), and the Loop treats them as non-negotiable

### Scenario S-033: End-of-run doc sync
- **Given** the queue has drained after one or more merges
- **When** Backlog rolls up
- **Then** it runs the `document` skill in sync mode over the session's merged PRs (dry-run → drift report → apply only if `doc_edits` is granted) and records the result

### Scenario S-034: End-of-run cleanup reaps worktrees and sessions, keeps branches
- **Given** the queue has drained and the rollup is finalizing
- **When** Backlog runs the end-of-run cleanup pass (unless `retain_for_inspection` is on)
- **Then** it dismisses every closed-issue Loop session and removes every merged-issue worktree in one batched pass, keeps all `backlog/*` branches (the backup), and records the cleaned/retained set in the ledger — worktrees are not removed per-issue the instant an issue closes

### Scenario S-035: Independent issues fly concurrently by default, gated by conflict risk
- **Given** the flight set is below the concurrency ceiling and the queue holds issues not yet in flight
- **When** Backlog selects the next issue to dispatch into a free slot
- **Then** it picks an issue whose target spec and source area (files/functions/concerns named in its linked plan) are disjoint from the in-flight set and dispatches it concurrently (back-to-back isolated detached starts, not one-at-a-time serialization); an issue sharing a target spec with an in-flight issue (S-015) or whose plan edits the same function/concern as an in-flight branch is held for a later slot, while same-file/different-function overlap is *adjacent* and flies (merge-last); borderline overlap is resolved by oracle (`independent/adjacent/contended`), defaulting to concurrent-but-merge-last when the oracle is down; an issue skipped for contention is not starved by lower-priority bypass work

### Scenario S-036: Concurrent branches close via serial rebase-onto-default
- **Given** two or more issues flew concurrently and their Loops have landed
- **When** Backlog closes them
- **Then** it merges them one at a time — most-independent first, overlapping-source last — rebasing each not-yet-merged branch onto the default as updated by the prior merge before its own merge, so any conflict surfaces at a single seam and is resolved (regenerate derived docs) or blocked (source conflict) per S-019, rather than batch-merging into multi-way conflicts

### Scenario S-037: Tool rejection text is not user intent and dispatch recovery stays autonomous
- **Given** a `start` result contains generic harness text implying the user rejected or stopped the tool, but no separate explicit user message says to stop
- **When** Backlog handles the failed or unknown dispatch outcome
- **Then** it treats the text as a technical result rather than a user decision, reconciles and retries under S-012 without a mid-run question, and only changes run intent in response to an explicit user instruction

### Scenario S-038: Cross-window orchestration risk is captured before dispatch
- **Given** other RPCE windows/workspaces may share provider or provisioning resources that this run cannot inventory reliably
- **When** Backlog renders its single wizard
- **Then** it asks whether another orchestrator is active and, when the answer is `yes` or `unknown`, defaults this run to one dispatch at a time unless the user explicitly selects a higher local ceiling

### Scenario S-039: Provisioning wedge stops dispatches and requires restart recovery
- **Given** read-only RPCE calls remain responsive while provisioning hangs/times out, or repeated zero-turn/no-worktree sessions and cleanup skips accumulate
- **When** Backlog reconciles a dispatch attempt
- **Then** it classifies the condition conservatively as an RPCE provisioning wedge without asserting an exact root cause, stops all new starts rather than retrying into it, preserves the ledger and consumed-attempt counts, marks affected rows `restart-required`, safely awaits/checkpoints already-live agents and completes the rollup without another ask, and requires other orchestrators to be serialized plus RPCE restarted before dispatch resumes; after restart the resume sweep includes these blocked ledger rows, clears the infrastructure block only when the wedge is absent, and retries only when the preserved two-attempt budget permits it

### Scenario S-040: Cleanup skip quarantines the dead session's branch binding
- **Given** cleanup of a dead/expired session is skipped and the session remains associated with its dispatch branch
- **When** Backlog prepares a retry even if the orphan worktree was removed and the branch is at base
- **Then** it treats that branch as still occupied, records it as quarantined, and dispatches on the next unused suffix rather than assuming worktree removal released the binding

### Scenario S-041: Dispatch diagnosis separates evidence from hypotheses
- **Given** a dispatch fails with ambiguous harness text or an empty session
- **When** Backlog explains and recovers from the failure
- **Then** it reports observed state separately from hypotheses, does not assert user cancellation, permissions, hooks, capacity, or branch collision without direct evidence, and does not ask the user to choose a speculative remedy or re-authorize a routine retry covered by the Phase-2 grant

## Proposed Surface

### Inputs (Phase-2 wizard — the single input point)

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| Confirmed triage order | yes | — | Bugs → priority → ease list for confirmation/adjustment. |
| Exempt-close batch | yes | — | `wontfix`/`duplicate` items proposed for one-shot close (decisions excluded). |
| Completion path | yes | `branch+pr+merge` | `local-only` / `branch+pr` / `branch+pr+merge` / `push-to-default`; selection authorizes exactly the concrete git actions the wizard enumerates. |
| Close policy | yes | auto-close | Auto-close on verified completion, or present evidence only. |
| Per-issue role | no | `pair` | `pair` or `engineer`, threaded into each dispatch. |
| Escalation policy | no | `autonomous` | `autonomous` (decide-or-block) or `conservative` (treat oracle-decidable ambiguities as blocked). |
| Max issues this run | no | drain | Cap or full drain; this is the autonomy contract — no "continue?" ask exists. Local dispatch ceiling defaults to 1 when other orchestration is active/unknown unless explicitly raised. |
| Concurrent orchestration elsewhere | yes | `unknown` | `none` / `yes` / `unknown`; records shared RPCE/provider-capacity risk that this run cannot reliably discover itself. |
| Retain for inspection | no | off | When off, the end-of-run pass reaps closed-issue sessions + merged-issue worktrees (default-clean); when on, defers removal to a manual ledger-driven sweep. Branches kept either way. |

### Authorization scope (persisted; excerpted into every brief)

| Field | Description |
|-------|-------------|
| `git_scope` | The wizard completion path; bounds all git-visible actions. |
| `doc_edits` | `false` unless the wizard authorizes documentation edits (Loop's doc sync stays dry-run/report-only otherwise). |
| `issue_scope` | The triaged track-work IDs merges may apply to. |
| `granted_at` | Timestamp of the wizard grant. |

### Dispatch brief contract (producer/consumer seam with Loop)

Every field optional; absent = Loop's standalone behavior.

| Field | Carries |
|-------|---------|
| `authorization` | `git_scope`, `doc_edits` (§5 of the plan). |
| `toolchain` | Repo-specific test/build commands + env (absolute paths). |
| `oracle` | `status: up|down`, `degraded_ok`. |
| `user_testing` | `tool`, throwaway `data_location`. |
| `escalation` | `principal: orchestrator`. |
| `amendments` | Pending amendment instructions. |
| `siblings` | Other in-flight issues and the source areas each touches. |

### Gates enforced

| Gate | When | Blocking condition |
|------|------|---------------------|
| Single wizard input | Whole run | A second `ask_user` is attempted (S-004). |
| Authorization boundary | Any git-visible action | Action exceeds `git_scope` or falls outside `issue_scope`; destructive git (S-005). |
| Isolation | Per dispatch | Shared worktree/branch; unreconciled orphan; or reuse of a branch quarantined by a skipped dead-session cleanup (S-009, S-010, S-040). |
| Dispatch isolation | Per `start` | Start batched with other mutations or verify commands (S-011). |
| Liveness | Per dispatch attempt | Returned handle is not live, or a no-handle outcome has not been inventoried and reconciled by deterministic session name + branch (S-012, S-037); provisioning-wedge signature stops further dispatch and routes to restart recovery (S-039). |
| Independent verify | Before close | Closeout evidence insufficient (S-016). |
| Conflict safety | Per merge | Non-allowlisted conflict auto-resolved as source (S-019). |

### Never-autonomous set (always blocked, never decided by oracle)

Actions beyond `authorization.git_scope`; destructive git; weakening any gate; credentials or spend; deciding the content of a `type:decision` item.

### Artifacts produced

| Artifact | Required content |
|----------|------------------|
| Run progress doc (`docs/progress/backlog-<run>.md`) | Wizard answers + authorization scope; per-issue ledger (`session_id`, `worktree_id`, branch, base SHA, lifecycle state, amendments, divergences); rollup; resume instruction. |
| Rollup | Per-issue outcome, accepted divergences, blocked reasons, kept/removed worktrees, resume pointer. |

## Open Questions

1. **What is the runtime's subagent approval/permission-inheritance model?** AF1 is encoded as a capability probe. **RPCE — probed 2026-07-06: `unattended` confirmed.** A dispatched subagent ran a mutating Bash op with no approval surfacing (session reached `Completed`, not `waiting_for_input`) and inherited the main agent's connected MCP servers (RepoPromptCE, `4_5v_mcp`, `web_reader` all visible to the subagent). So the wizard pre-flight may fast-path to `unattended` on RPCE; the capability probe is retained as the fallback for the other three runtimes (Claude Code, Codex, OpenCode), which remain unverified. **chrome-devtools is NOT reachable from RPCE subagents (definitive call-based test, 2026-07-06).** A subagent could not construct `mcp__chrome-devtools__list_pages` — the tool is absent from its schema; corroborated by the main RPCE session's own tool inventory (`RepoPromptCE`, `4_5v_mcp`, `web_reader` only — no chrome-devtools). chrome-devtools is registered globally for the Claude Code CLI in `~/.claude.json` and works there; **after an RPCE restart/reconfig on 2026-07-06 it is also reachable inside RepoPrompt CE** — `mcp__chrome-devtools__list_pages` returned a real page (`about:blank`) from the main RPCE session, and the confirmed permission-inheritance propagates MCP servers to subagents, so Loop subagents can do real-browser user-testing (S-022) in RPCE runs as well as Claude Code runs. (Before that reconfig, RPCE surfaced a different MCP set and chrome-devtools was absent there — an MCP-config gap, not an inheritance failure.) The W4/S-006 capability probe is runtime-conditional by design and now finds chrome-devtools in both runtimes → user-testing proceeds. Provenance/lesson stands: a call-based test is the only valid reachability proof; `ListMcpResourcesTool` lists resources only and never shows a tools-only server like chrome-devtools. To enable real-browser user-testing from Loop subagents, add chrome-devtools to the **RepoPrompt CE MCP configuration** (or the host's subagent tool allowlist). Until then, S-022 blocks UI closeout with reason (safe degradation). Provenance/lesson: two prior readings were wrong for different reasons — an initial resources-listing check (wrong instrument) and a resources-vs-tools rebuttal that flipped the record on a relay without a definitive test; a call-based test is the only valid reachability proof.
2. **Is `accept_with_amendment` command-approval-only?** Suspected but unverified. **Moot on RPCE under `unattended` mode** (no approvals surface, so the amendment path is never exercised there). Relevant only to `attended-fallback` runtimes; resolve there via one live skill-approval + one command-approval trial and record the restriction precisely. The conservative cap-1-then-accept/decline policy is correct under either behavior, so the restriction stays recorded as observed-runtime behavior rather than contract.
3. **Resolved (one-shot, 2026-07-06):** the exempt-close batch closes on a single wizard confirmation of the whole batch, not per-item — the `wontfix`/`duplicate` labels are pre-existing human decisions, so per-item re-confirmation is ceremony.
