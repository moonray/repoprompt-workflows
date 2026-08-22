---
title: Document Skill
issue: 3
status: draft
---

# Document Skill

## Problem

The skill's two modes, `sync` and `audit`, run the same checking machinery from two entry points but are defined, invoked, and described as separate modes — they cannot be composed ("this change, plus pre-existing drift nearby"), and a bare invocation gives no predictable default. Three gaps sit outside both modes entirely:

1. **Intent drift is invisible.** A repo's stated intent (mission, non-goals) drifts from its accumulated work silently — a PRD that never learns a second provider exists, merged work no intent clause traces to, adjacent additions that collectively erode a stated non-goal. No skill mode reviews work against intent.
2. **Agent-steering docs are unclassified.** CLAUDE.md/AGENTS.md, rules, workflows, and skills are policy (not derived from code) yet machine-editable (unlike contracts). Today they fall into `current-state`, so edits get no quality checks: trigger info gets lost, near-miss rules accumulate, incident-reportage hardens into policy, mission prose gets copied until stale copies contradict the ratified anchor.
3. **Mission prose duplicates.** When intent statements live in several docs, every copy but the anchor goes stale after the first ratification and actively misleads agents that read them.

## Goals

1. One `code` mode for docs ⇄ code truth with two composable entry points and sane defaults: change-driven reconciliation (`--change`, default the working-tree diff) and corpus drift scan (`--full`), composable in one run.
2. Classify agent-steering docs (by path) as a third class whose proposed edits are **checked** against steering disciplines — trigger preservation, near-miss overlap, incident-overfit, unreferenced content — with failed checks reported as findings that accompany the proposal.
3. Detect and remediate mission-echo: intent prose duplicated outside the anchor range is flagged and reconciled to a pointer to the anchor (by path).
4. A capability-boundary change (new provider, surface, or top-level module) reports intent-lag — whether the repo's intent anchor knows about the new capability.
5. An `intent` mode that discovers the repo's intent anchor, reviews a bounded window of the work record against it, and produces evidence-cited verdicts: lineages `aligned`/`adjacent`/`orphaned`, anchor freshness, promised-but-absent as `deferred?`, and detect-and-skip checks for intent-adjacent artifacts (decision records, roadmap items, conformance portfolio, non-goal erosion, success metrics).
6. Intent findings remediate without human gating everywhere except the intent anchor: doc-side drift becomes applied edits under the normal `apply` grant (regardless of the doc's code-mode classification); work-side findings are recorded in **one idempotent alignment-summary tracking item** with finding-level signatures. Optional later promotion to linked items does not gate or replace the summary.
7. Anchor governance: an agent may draft an anchor-range edit but never land one — anchor changes land only by human action.
8. Every proposed edit traces to a concrete basis appropriate to its action; edits are scope-bounded and approval-gated; contract conflicts in code mode are surfaced, never auto-resolved (unchanged from the implemented skill).
9. Operate on whatever doc files a repo contains, discovered per-repo; keep the progressive-disclosure docs index in sync (unchanged).

## Non-Goals

- Authoring brand-new documentation with no code or work basis.
- Modifying code to match documentation; documentation follows code.
- Generating changelogs, release notes, or version bumps; performing git operations (commit, push, merge, PR) — remediation produces edits, drafts, and ledger items; the user lands them.
- Landing intent-anchor edits autonomously, under any grant.
- Re-checking code facts from `intent` mode — that is `code` mode's job; intent verdicts cite the work record and doc lines, not code internals.
- An overall repo health score, or a combined mode bundling code + intent; a quarterly bundle is a call-site invoking both modes, not a mode.
- Skill eval/benchmark machinery (baselines, viewers, optimization loops) — that stays in skill-creator; steering checks are edit-time findings only.
- Mandating repo conventions: every intent-adjacent check must skip silently when its artifact class is absent; a repo without decisions ledgers, conformance matrices, or metrics stays fully reviewable.

## Constraints

- **Doc classification** (priority order): (a) per-doc frontmatter `type:`/`status:` mapped by repo convention; (b) repo docs convention/README path mapping; (c) `agent-steering` when the path is CLAUDE.md/AGENTS.md or under rules/, workflows/, skills/, .agents/, .claude/; (d) `spec` paths are contract, `plan` paths current-state when specs exist; (e) otherwise current-state.
- **Anchor boundary.** The intent anchor is an identified range `{doc, range}`, not necessarily a whole file. `anchor_identity` is that anchor's stable semantic identity — normalized repo-relative doc path plus discovery tier plus range selector (heading/section identity) — excluding observed line numbers, so identity survives line movement while `anchor_fingerprint` changes track content changes. Discovery is one shared operation used by both modes (first found wins; `code` mode resolves it lazily when mission-echo or a capability-boundary candidate needs it): `docs/intent.md` → the PRD's Vision/Overview section → the CLAUDE.md/AGENTS.md purpose statement. Only the identified mission/non-goals range is contract-class and draft-only; content outside that range in the same file keeps its normal classification and apply policy. Other intent-shaped docs are intent-adjacent, subject to the coherence check, never anchors. In `intent` mode, no anchor found is itself the finding; the mode stops — there is nothing to align to. In `code` mode with no anchor, mission-echo has no candidates (no findings), and a capability-boundary candidate produces an Unsupported item (basis absent) — never a fabricated intent-lag verdict.
- **Anchor content altitude**: mission + non-goals; no schedules, roadmaps, or feature commitments. `deferred?` verdicts exist only for promises the anchor actually makes.
- **Gating is mode-specific.** In `code` mode, contract-vs-code conflicts are reported with both sides and not edited. In `intent` mode, `apply` writes every basis-supported doc-side remediation outside the anchor range, regardless of the doc's code-mode classification; only the anchor range is draft-only. `apply` never enables git operations or landing an anchor edit.
- **Capability boundary (decision rules).** New provider: a newly registered adapter/provider following an existing registry or configuration pattern. New surface: a newly externally invocable command, route, tool, or public schema. New top-level module: a new first-level product source package, excluding docs, tests, fixtures, generated files, and configuration. If a capability candidate cannot be established from changed paths/symbols, report no basis rather than an intent-lag item.
- **Verdict rules.** Classify work items into lineages before grouping: `aligned` requires a cited anchor clause; `adjacent` requires an explicit mission-support justification and no conflict with a stated non-goal; `orphaned` has neither. Mixed groups split.
- **Baseline-aware window resolution.** Compute an `anchor_fingerprint` as SHA-256 over the exact anchor-range bytes after CRLF→LF normalization. Do not classify edits as substantive or editorial: any fingerprint change is a new anchor revision. The default window is two-state: (1) no completed baseline receipt matching `{anchor_identity, anchor_fingerprint}` in the authoritative ledger (or receipt lookup fails) → the default window is repo start through the current review head, reported as a required re-baseline, with any lookup failure disclosed; (2) a matching completed receipt exists → the default cutoff is the latest commit whose diff overlaps the current anchor range, falling back to the latest commit touching the containing file with the fallback disclosed. An explicit `--since`/`--last N` may narrow a run but never establishes a baseline receipt; `--all` forces repo start even when a receipt exists. The cutoff applies inclusively to every work-record source. Source precedence: sources aggregate with deduplication by work identity — track-work ledger records first; then merged PRs not represented in ledger records; then commit subjects not represented by either. A source item is in-window when its own merge/commit ref falls within the window boundaries. Every report states its start/end boundaries, sources, fingerprint, receipt state, and any fallback.
- **Filing contract.** An intent run files or updates **one alignment-summary tracking item** per `{anchor_identity, anchor_fingerprint}` in the authoritative ledger (summary signature derived from those two fields). Each work-side finding appears once in the summary with a finding signature derived from `{anchor_identity, anchor_fingerprint, finding_kind, sorted evidence IDs}` plus its evidence and its work state — `merged` (current divergence to reconcile) or `planned` (decision to make before building). Re-running against the same revision updates the summary and reuses entries; a closed summary receiving a new unresolved finding is reopened, never duplicated. Promoting a finding to an individual item is optional downstream triage via normal ledger tooling (a GitHub native sub-issue, or a reciprocally linked item in the file-backed ledger), preserving the finding signature; the summary closes only when every entry has a recorded terminal disposition. On ledger failure, report the failure — never silently fall back to a second ledger.
- **Baseline receipt.** The alignment summary doubles as the durable baseline receipt. After an `apply` run completes a repo-start-to-review-head baseline, the summary records `baseline_complete: true`, the anchor identity and fingerprint, sources, and `reviewed_through`. A completed matching receipt is an alignment summary with the same `anchor_identity` and `anchor_fingerprint` recording `baseline_complete: true` and `reviewed_through` — independent of whether unresolved findings keep the summary open. A narrowed, interrupted, or failed run must not mark the baseline complete; a baseline with no findings still records a resolved receipt. If receipt filing fails, report it — a later run conservatively re-baselines. Receipt persistence happens only under `apply`; read-only runs never mutate the repo (so repeated full dry runs before an applied receipt are expected).
- **Basis discipline is action-based.** Code-claim reconciliation cites a code fact (file + symbol/path/parameter/observed value); mission-coherence edits cite the anchor range and duplicate doc locations; intent verdicts and ledger items cite work-record or doc-line evidence. When required basis is absent, emit an Unsupported item and produce no edit, verdict, or ledger action.
- **Guidance dedupes; enforcement references**: remediated mission-echo replaces duplicated prose with a pointer to the anchor by path; rules and steering docs reference the anchor by path, never by quoting its content.
- **Bounded windows**: every intent review has concrete start and end boundaries — a required re-baseline uses the finite repo-start-to-review-head range; otherwise the normal or explicitly overridden cutoff (`--all`, `--since <ref>`, `--last N`) applies. Never an unbounded "everything ever".
- Dry-run is the default in both modes; discovery is content- and convention-based (Markdown, Gherkin `.feature`, repo conventions), not path-list-based.

## Scenarios

### Scenario S-001: Change-driven run identifies affected docs
- **Given** Doc A documents a parameter `foo`, Doc B documents an unrelated area, and a code change renames `foo` to `bar`
- **When** the skill runs a change-driven reconciliation over that change
- **Then** the report includes Doc A's parameter location and excludes Doc B

### Scenario S-002: Change-driven run proposes basis-cited reconciliation edits
- **Given** an affected current-state doc location and the code change
- **When** the skill proposes an edit
- **Then** the edit reconciles the doc to the code's current state and carries the specific code fact it is based on

### Scenario S-003: Unaffected docs are untouched
- **Given** a change and a doc whose content does not depend on the changed code
- **When** the skill runs a change-driven reconciliation
- **Then** that doc is left unchanged

### Scenario S-004: No fabricated content
- **Given** affected doc content with no corresponding code fact to reconcile against
- **When** the skill would propose an edit
- **Then** no edit is produced for the unsupported content, and an Unsupported item reports that no basis was found

<!-- S-006 folded into S-005 (value/enum mismatch is a concrete instance of stated-value drift); ID retired, never reused. -->

### Scenario S-005: Corpus scan detects existing drift
- **Given** a current-state doc whose stated value (including an enumerated allowed value), parameter, or behavior no longer matches the code
- **When** the skill runs a corpus drift scan over the repo
- **Then** it reports the drift location with the doc's claim, the code's actual state or emitted value, and a proposed fix carrying its basis

### Scenario S-007: Corpus scan flags dangling references
- **Given** a doc referencing a symbol, path, or parameter that no longer exists in the code
- **When** the corpus scan runs
- **Then** the dangling reference is reported with its doc location and the proposed removal or update

### Scenario S-008: Contract-doc conflict is surfaced, not edited
- **Given** a contract doc conflicting with the code's actual behavior
- **When** the skill encounters the conflict at either code entry point
- **Then** it reports the conflict with the doc side and the code side and produces no edit

### Scenario S-009: Scope limits the run
- **Given** drift inside and outside a requested scope (path, doc type, or doc set)
- **When** the skill runs with that scope
- **Then** only in-scope docs are scanned, reported, or edited

### Scenario S-010: Edits are dry-run by default
- **Given** the skill has produced proposed edits
- **When** `apply` is not enabled
- **Then** no doc file is written and the proposals are presented for review

### Scenario S-011: Apply writes only approved edits
- **Given** proposed edits whose bases are valid and `apply` is enabled
- **When** the skill applies them
- **Then** only those proposed edits are written and each written edit is reported

### Scenario S-012: Repo-agnostic doc discovery
- **Given** a repo whose documentation includes both Markdown and Gherkin `.feature` files
- **When** code mode runs
- **Then** it discovers and operates on both file types with no repo-specific path configuration

### Scenario S-013: Instruction artifact directories can contain docs
- **Given** an agent instruction artifact directory containing README or reference Markdown files
- **When** the skill runs without a scope excluding that directory
- **Then** those documentation files are included in discovery and evaluated for code claims

### Scenario S-014: No drift yields a clean no-op
- **Given** all in-scope docs already match the code
- **When** code mode runs
- **Then** it reports an empty result set and writes nothing

### Scenario S-015: Doc lifecycle changes keep the index in sync
- **Given** a run that adds, renames, or removes a doc, and a repo docs index exists (or is conventionally expected)
- **When** the change-driven run completes
- **Then** an added doc gains a one-line summary plus link, a renamed doc's entry is updated, and a removed doc's entry is dropped — each index edit carries its basis and is dry-run unless `apply` is enabled

### Scenario S-016: Bare invocation has a sane default
- **Given** a code-mode invocation with neither entry-point flag
- **When** the skill runs
- **Then** it behaves as change-driven reconciliation over the working-tree diff — never an error, never a required flag

### Scenario S-017: Entry points compose in one run
- **Given** an explicit change and pre-existing drift in docs near that change
- **When** the skill runs with both the change input and the corpus flag
- **Then** one report covers the change-complete set and the nearby pre-existing drift, each item labeled with which entry point produced it

### Scenario S-018: Agent-steering docs are classified by path
- **Given** a doc at CLAUDE.md, AGENTS.md, or under rules/, workflows/, skills/, .agents/, or .claude/, with no higher-precedence classification signal (frontmatter `type:`/`status:`, repo docs-convention mapping) and outside the intent anchor range
- **When** classification runs
- **Then** the doc is classified agent-steering — policy, machine-editable under `apply`, with every proposed edit checked against the steering disciplines

### Scenario S-019: Steering edit proposals preserve trigger information
- **Given** a proposed edit to an agent-steering doc that would drop or bury the doc's when-to-use trigger
- **When** the proposal is produced
- **Then** it is accompanied by a finding requiring the trigger to stay on the always-loaded surface

### Scenario S-020: Steering edits flag near-miss rules
- **Given** a proposed new steering rule that could fire on the same situations as an existing sibling rule
- **When** the proposal is produced
- **Then** a near-miss finding requires merging the rules or stating precedence between them

### Scenario S-021: Steering edits flag incident-overfit rules
- **Given** a proposed steering rule that restates one incident rather than a general policy
- **When** the proposal is produced
- **Then** an incident-overfit finding accompanies it

### Scenario S-022: Mission-echo is flagged and reconciled to a pointer
- **Given** the intent anchor exists and another doc restates the mission or non-goals in its own words
- **When** either code-mode run or the intent coherence check encounters the copy
- **Then** the copy is reported as mission-echo drift with a proposed replacement that points to the anchor by path, carries no duplicated prose, and cites the anchor range and the duplicate location as its basis

### Scenario S-023: Capability-boundary changes report intent-lag
- **Given** a change that adds a provider, surface, or top-level module per the decision rules, and an intent anchor that does not mention that capability
- **When** the change-driven run completes
- **Then** the report includes an intent-lag item naming the anchor, the new capability, and the recommendation to ratify an anchor update

### Scenario S-024: Intent anchor is discovered in priority order
- **Given** a repo with `docs/intent.md`
- **When** intent mode runs
- **Then** that file is the anchor, and other intent-shaped docs (PRD vision, CLAUDE.md purpose) are treated as intent-adjacent subjects of the coherence check — never as co-equal anchors

### Scenario S-025: Missing anchor is the finding
- **Given** a repo with no `docs/intent.md`, no PRD vision section, and no CLAUDE.md/AGENTS.md purpose statement
- **When** intent mode runs
- **Then** it reports "no intent anchor found; drift risk unbounded" and stops without verdicts

### Scenario S-026: An unrecognized anchor revision triggers a full re-baseline
- **Given** the current anchor fingerprint has no completed baseline receipt — because the anchor changed, was never reviewed, or receipt lookup failed
- **When** intent mode runs without a window override
- **Then** it reviews repo start through the current review head, reports the anchor fingerprint and re-baseline status (disclosing any lookup failure), and does not require the user to supply `--all`

### Scenario S-027: Lineage verdicts follow the decision rules and cite evidence
- **Given** the merged work in the window
- **When** intent mode classifies it into lineages
- **Then** each lineage carries a verdict per the verdict rules — `aligned` with the cited anchor clause, `adjacent` with its mission-support justification, or `orphaned` with neither — and every verdict cites its issues, PRs, or doc lines

### Scenario S-028: Promised-but-absent reads as deferred, not drift
- **Given** an anchor promise with no corresponding work in the window
- **When** the verdict is produced
- **Then** it is reported `deferred?` with the anchor's exact promise, never as misalignment

### Scenario S-029: Intent-adjacent checks degrade silently
- **Given** a repo with an anchor but no decision ledger, no conformance matrices, and no success metrics
- **When** intent mode runs
- **Then** those checks skip without findings or warnings, and the core checks still run

### Scenario S-030: Doc-side intent drift remediates under apply
- **Given** an intent finding whose fix is an edit outside the anchor range — a stale mission echo or an incoherent intent claim, whatever the doc's code-mode classification
- **When** `apply` is enabled
- **Then** the edit is written with its basis re-checked — no human ratification beyond the existing `apply` grant

### Scenario S-031: Work-side findings file as one idempotent alignment summary
- **Given** one or more work-side findings for the current anchor revision
- **When** `apply` is enabled
- **Then** one alignment-summary item is created or updated in the authoritative ledger, every finding appears exactly once with its signature, evidence, and merged-or-planned work state, and a repeated run duplicates neither the summary nor its entries

### Scenario S-032: Anchor edits are drafted, never landed
- **Given** an intent-staleness finding whose fix is a change to the anchor range itself
- **When** `apply` is enabled
- **Then** the skill produces a draft edit (proposed text or diff) and stops; no grant causes the anchor range to be written or the change to be landed — landing is a human action

### Scenario S-033: The anchor range is contract regardless of path
- **Given** an intent anchor range located outside `spec` paths (e.g. `docs/intent.md`, or a PRD vision section)
- **When** any code-mode run touches docs near it
- **Then** the anchor range is treated as a contract doc — conflicts are reported with both sides, never edited — while content outside the range in the same file keeps its normal classification and apply policy

### Scenario S-034: Steering edits flag unreferenced content
- **Given** existing steering content that no workflow, skill, or rule references
- **When** a steering edit proposal touches that area
- **Then** an unreferenced-content finding accompanies the proposal

### Scenario S-035: Ledger failure reports, never falls back
- **Given** work-side remediation whose authoritative ledger is unreachable or rejects the filing
- **When** `apply` attempts the filing
- **Then** the failure is reported with diagnostics, no item is created in any other ledger, and no baseline receipt is recorded

### Scenario S-036: A completed baseline receipt prevents repeated re-baselines
- **Given** a repo-start review completed under `apply`, with its alignment summary recording a completed receipt matching the current anchor fingerprint
- **When** intent mode later runs without a window override
- **Then** it uses the normal latest-anchor-touching cutoff rather than repo start; if the fingerprint changes, the receipt no longer matches and the S-026 re-baseline applies

## Proposed Surface

### Inputs

| Input | Mode | Required | Description |
|-------|------|----------|-------------|
| mode | both | no | `code` (docs ⇄ code) or `intent` (anchor ⇄ work record). Inferred from the request when omitted, in precedence order: mission/alignment question → `intent`; change-shaped request → `code` change-driven; drift question → `code --full`. |
| change | code | no | The change to reconcile to; defaults to the working-tree diff when omitted. |
| full | code | no | Corpus drift scan (claim-complete, dangling references); composes with `change`. |
| scope | code | no | A path, doc type, or doc set to limit the run; defaults to the whole repo. |
| apply | both | no | Approval to write doc-side edits and file ledger items; defaults to off. Never enables anchor-range edits or git operations. |
| window | intent | no | Work-record window: the baseline-aware default (re-baseline when no matching receipt); `--all` forces repo start, `--since <ref>` / `--last N` narrow (never establishing a receipt). |

### Outputs — code mode

| Output | Shape |
|--------|-------|
| Drift report / proposed edits | Current-state docs: `{doc, location, doc_claim, code_state, proposed_fix, basis}`. |
| Contract conflicts | `{doc, location, doc_side, code_side}` — no edit until a human direction is supplied. |
| Steering-discipline findings | On agent-steering edit proposals, failed checks only: `{doc, location, finding, requirement}` — trigger preservation, near-miss, incident-overfit, unreferenced content. |
| Mission-echo items | `{doc, location, duplicated_claim, pointer_edit, basis}` — proposed replacement points to the anchor by path. |
| Intent-lag items | `{anchor, new_capability, recommendation}` when a change crosses a capability boundary. |
| Index updates | `{index_doc, action, entry, summary, link, basis}` on doc add/rename/remove. |
| Unsupported | Items where required basis was absent: `{doc, location, claim, what_basis_was_sought}` — no edit produced. |

### Outputs — intent mode

| Output | Shape |
|--------|-------|
| Alignment report | `{anchor: {doc, range}, anchor_ref, anchor_fingerprint, baseline: {required, receipt_found, baseline_complete, reviewed_through}, window: {start, end, sources, fallback_used}, lineages: [{theme, evidence, verdict, intent_clause, basis}], intent_staleness: [{anchor_claim, reality, basis}], deferred: [{promise, basis}], recommendation}`. `anchor_ref` is the commit touching the anchor range when resolvable, otherwise a content hash plus `working-tree`; `anchor_fingerprint` is the normalized range-bytes hash. |
| Detect-and-skip check results | Intent-docs coherence, decision-record supersession, roadmap orphans, conformance-portfolio staleness, non-goal erosion, metrics liveness — each `{finding, evidence}` or silently skipped when the artifact class is absent. |
| Remediation actions | Doc-side: proposed edits, applied under `apply`. Work-side: `{summary_signature, anchor_fingerprint, baseline_receipt, findings: [{finding_signature, kind, work_state, evidence, linked_item?}]}` — one alignment summary created/updated under `apply`; `linked_item` is optional downstream triage. Anchor-side: `{draft_edit, rationale}` — draft only, never applied. |
| Unsupported | Items where required basis was absent: `{doc, location, claim, what_basis_was_sought}` — no edit, verdict, or ledger action produced. |

`basis` is action-appropriate per the basis-discipline constraint: a code fact for code-claim reconciliation, the anchor range plus duplicate locations for mission-coherence edits, work-record/doc-line citations for intent verdicts and ledger items.

## Open Questions

1. **Should the intent-lag check fire only on capability-boundary changes or any change touching a doc the anchor references?** Recommendation: capability boundaries only (the proven case from the source chat); broaden only with field evidence.
2. **Does the steering-discipline finding set need a severity ordering?** Recommendation: no — findings are requirements attached to proposals, all blocking an unflagged apply; ordering is presentation detail.
