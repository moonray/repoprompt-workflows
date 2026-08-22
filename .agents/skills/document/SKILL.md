---
name: document
description: Use when reconciling documentation to code changes or auditing documentation drift in a repo. Applies whenever the user asks to update docs after code changes, check whether docs match code, run a documentation audit, or produce doc drift reports; also reviews accumulated work against the repo's mission/intent anchor for alignment; defaults to dry-run proposals and requires explicit apply before writing.
---

# Document

## Purpose

Keep documentation aligned with code without inventing facts or silently rewriting contracts, and keep accumulated work aligned with the repo's stated intent without ever landing an intent-anchor change.

Use this skill in two modes:

- **code**: reconcile docs ⇄ code truth, from two composable entry points — change-driven reconciliation (default: the working-tree diff) and a corpus drift scan.
- **intent**: review a bounded window of the work record against the repo's intent anchor and remediate the findings.

Documentation follows code. Do not modify code to match docs, create changelogs, bump versions, author brand-new documentation with no code or work basis, or perform git operations (commit, push, merge, PR) — remediation produces edits, drafts, and ledger items; the user lands them. Never land an intent-anchor edit, under any grant. `intent` mode does not re-check code facts — that is `code` mode's job; intent verdicts cite the work record and doc lines, not code internals. There is no combined code+intent mode and no overall repo health score — a bundle is a call-site invoking both modes, not a mode. No skill eval/benchmark machinery; steering checks are edit-time findings only. Do not mandate repo conventions: every intent-adjacent check must skip silently when its artifact class is absent — a repo without decision ledgers, conformance matrices, or metrics stays fully reviewable.

## Inputs

- **mode**: `code` (docs ⇄ code) or `intent` (anchor ⇄ work record).
- **change** (code): the change to reconcile to; defaults to the working-tree diff when omitted; may be a staged diff or commit range if the user supplies one.
- **full** (code): corpus drift scan (claim-complete check, dangling references); composes with `change` in one run.
- **scope** (code): optional path, doc type, or doc set; default is the whole repo.
- **apply** (both): approval to write doc-side edits and file ledger items; default is off. Never enables anchor-range edits or git operations.
- **window** (intent): work-record window — the baseline-aware default (re-baseline from repo start when no matching receipt); `--all` forces repo start; `--since <ref>` / `--last N` narrow a run and never establish a baseline receipt.

When mode is omitted, infer it from the request in this precedence order: a mission/alignment question → `intent`; a change-shaped request → `code` change-driven; a drift question → `code --full`. Ask only when the request cannot be safely interpreted.

## Workflow

### 1. Discover documentation

Discover docs from the repo instead of relying on a fixed path list.

Minimum supported forms:

- Markdown (`.md`, `.mdx`): headings, paragraphs, lists, tables, code fences.
- Gherkin (`.feature`): features, scenarios, and steps.

Honor repo documentation conventions if present, such as README guidance, docs indexes, or frontmatter conventions. Directories that primarily hold agent instruction artifacts can still contain documentation files, such as README indexes or reference docs; include those docs unless the requested scope or repo convention excludes them. Apply `scope` before reporting or editing; ignore out-of-scope docs.

### 2. Classify docs

Classify each in-scope doc as **contract**, **current-state**, or **agent-steering** in this priority order:

1. Per-doc frontmatter with `type: contract` or `type: current-state`, or a `status:` value that the repo convention maps to one of those types.
2. A repo docs convention or README that maps paths to a doc type.
3. **agent-steering** when the path is `CLAUDE.md`/`AGENTS.md` or under `rules/`, `workflows/`, `skills/`, `.agents/`, or `.claude/`.
4. A path containing `spec` means contract; when such specs exist, a path containing `plan` means current-state.
5. Otherwise, current-state.

For **current-state** docs, code is the source of truth and proposed edits may reconcile docs to code.

For **contract** docs, report conflicts with both sides and do not produce edits unless a human supplies a direction.

**agent-steering** docs (CLAUDE.md/AGENTS.md, rules, workflows, skills) are policy — not derived from code — yet machine-editable: proposed edits reconcile them like current-state docs, and every edit proposal is **checked** against the steering disciplines (step 5), with failed checks reported as findings that accompany the proposal.

The **intent anchor range** (steps 6–7) is contract-class regardless of its path — conflicts are reported with both sides, never edited. Content outside that range in the same file keeps its normal classification and apply policy.

### 3. Establish code basis

Every drift item or proposed edit must cite a concrete code fact as its basis:

- file plus symbol, path, parameter, schema field, command, route, configuration key, or emitted/observed value;
- for behavior, the code path or reproducible observation that proves the behavior.

Do not propose edits for unsupported claims. If a doc claim has no reliable code basis, report that no basis was found instead of fabricating content. When any required basis is absent, emit an Unsupported item and produce no edit, verdict, or ledger action.

Before applying any edit, re-check that its cited basis still exists and still supports the edit.

### 4. Code mode

One workflow, two composable entry points:

- **change-driven**: reconcile docs affected by the change — the working-tree diff by default, or the explicit change input if provided. A bare invocation with no entry-point flag is change-driven over the working-tree diff: never an error, never a required flag, never a clarifying question.
- **corpus** (`full`): scan in-scope docs for existing drift.

When both run in one invocation, produce ONE report covering the change-complete set plus the pre-existing drift near the change, with each item labeled with which entry point produced it. Composing the two entry points does not narrow the corpus scan — `scope` is the only limiter; the "near the change" drift is the change-adjacent subset of the one report, not a filter.

Change-driven procedure:

1. Identify docs whose content depends on changed symbols, paths, parameters, schemas, commands, routes, config keys, or observed values.
2. Exclude unrelated docs.
3. For affected current-state docs, propose minimal reconciliation edits with basis.
4. For affected contract docs (including the anchor range), report conflicts with doc side and code side; do not edit.

Corpus procedure:

1. Scan in-scope docs for concrete claims about code: names, paths, parameters, allowed values, schemas, commands, routes, configuration, file locations, or observable behavior.
2. Check each claim against code.
3. Report drift for current-state docs with doc claim, code state, proposed fix, and basis.
4. Report contract conflicts with doc side and code side; do not edit.
5. Report dangling references to removed or renamed symbols, paths, or parameters.

#### Keep a progressive-disclosure docs index

Docs are only useful if agents (and humans) can find them. Maintain a single concise index of the repo's documentation so consumers load a small overview first and drill down on demand (progressive disclosure):

- One index file — a `docs` README by default; `llms.txt` only when the docs are published as a website (llms.txt is a website standard, not a code-repo convention).
- Each entry is a one-line summary plus a link to the detail doc; keep entries brief — the index is the entry point, not the content.
- In change-driven runs, when a doc is added, renamed, or removed, keep the index in sync: an added doc gains a one-line summary plus link, a renamed doc's entry is updated, a removed doc's entry is dropped — the index and the docs never drift.
- Do not fold detail into the index — it points to it. Large reference docs (>~300 lines) should carry their own table of contents.

Treat the index like any other current-state doc for basis and apply rules: an index edit must trace to a real doc that exists, and is dry-run unless `apply` is enabled.

### 5. Steering-discipline findings (agent-steering edit proposals)

Check every proposed edit to an agent-steering doc against these disciplines. Report only failed checks, as findings `{doc, location, finding, requirement}` attached to the proposal. Findings are requirements with no severity ordering — an apply that does not address them is blocked.

- **Trigger preservation**: the proposal must not drop or bury the doc's when-to-use trigger; the trigger stays on the always-loaded surface.
- **Near-miss overlap**: a proposed rule that could fire on the same situations as an existing sibling rule requires merging the rules or stating precedence between them.
- **Incident-overfit**: a proposed rule that restates one incident rather than a general policy is flagged.
- **Unreferenced content**: when a proposal touches an area of steering content that no workflow, skill, or rule references, flag that content.

Guidance, not findings: prefer explaining why over stacking MUSTs; keep progressive-disclosure budgets — ~100-word level-1 description, under ~500-line body, references loaded on demand. Steering docs reference the intent anchor by path, never by quoting its content.

### 6. Mission-echo and intent-lag

Anchor discovery is one shared operation used by both modes — first found wins: `docs/intent.md` → the PRD's Vision/Overview section → the CLAUDE.md/AGENTS.md purpose statement. `code` mode resolves it lazily, only when mission-echo or a capability-boundary candidate needs it.

**Mission-echo.** Intent prose (mission or non-goals) duplicated outside the anchor range — encountered by either code-mode entry point or by the intent coherence check — is reported as mission-echo drift `{doc, location, duplicated_claim, pointer_edit, basis}`. The proposed replacement points to the anchor by path, carries no duplicated prose, and cites the anchor range and the duplicate location as its basis.

**Intent-lag** fires only on capability-boundary changes:

- **New provider**: a newly registered adapter/provider following an existing registry or configuration pattern.
- **New surface**: a newly externally invocable command, route, tool, or public schema.
- **New top-level module**: a new first-level product source package — docs, tests, fixtures, generated files, and configuration are excluded.

When the anchor exists and does not mention the capability, emit `{anchor, new_capability, recommendation}` recommending that an anchor update be ratified. If a capability candidate cannot be established from changed paths/symbols, report no basis (an Unsupported item) rather than an intent-lag item. With no anchor: mission-echo has no candidates and reports no findings; a capability-boundary candidate produces an Unsupported item (basis absent) — never a fabricated intent-lag verdict.

### 7. Intent mode

#### Discover the anchor; stop when absent

Run the shared discovery order (step 6). The first hit is the anchor; the other intent-shaped docs (PRD vision, CLAUDE.md/AGENTS.md purpose) are intent-adjacent — subjects of the coherence check, never co-equal anchors. The anchor is the identified mission/non-goals **range** `{doc, range}`, not necessarily a whole file. Its content altitude is mission plus non-goals — no schedules, roadmaps, or feature commitments; `deferred?` verdicts exist only for promises the anchor actually makes. If no anchor is found, report "no intent anchor found; drift risk unbounded" and stop without verdicts.

#### Anchor identity, classification, and fingerprint

- The anchor range is contract-class (step 2): drafted, never landed — anchor changes land only by human action (see Remediation).
- `anchor_identity` is the anchor's stable semantic identity — normalized repo-relative doc path plus discovery tier plus range selector (heading/section identity), excluding observed line numbers — so identity survives line movement while fingerprint changes track content changes.
- `anchor_fingerprint` is SHA-256 over the exact anchor-range bytes after CRLF→LF normalization. Do not classify anchor edits as substantive or editorial: any fingerprint change is a new anchor revision.
- `anchor_ref` is the commit touching the anchor range when resolvable, otherwise a content hash plus `working-tree`.

#### Resolve the review window (baseline-aware, two-state)

Every intent review has concrete start and end boundaries — never an unbounded "everything ever".

1. **No completed baseline receipt** matching `{anchor_identity, anchor_fingerprint}` in the authoritative ledger — because the anchor changed, was never reviewed, or receipt lookup failed → the default window is repo start through the current review head, reported as a required re-baseline, with any lookup failure disclosed. The user is not required to supply `--all`.
2. **A matching completed receipt exists** → the default cutoff is the latest commit whose diff overlaps the current anchor range, falling back to the latest commit touching the containing file, with the fallback disclosed.

A completed matching receipt is an alignment summary with the same `anchor_identity` and `anchor_fingerprint` recording `baseline_complete: true` and `reviewed_through` — independent of whether unresolved findings keep the summary open. `--since <ref>` / `--last N` may narrow a run but never establish a baseline receipt; `--all` forces repo start even when a receipt exists. The cutoff applies inclusively to every work-record source.

#### Gather work-record sources

Aggregate sources with deduplication by work identity: the repo's track-work ledger records first; then merged PRs not represented in ledger records; then commit subjects not represented by either. A source item is in-window when its own merge/commit ref falls within the window boundaries.

#### Classify lineages (verdict rules)

Classify work items into lineages before grouping:

- `aligned` requires a cited anchor clause;
- `adjacent` requires an explicit mission-support justification and no conflict with a stated non-goal;
- `orphaned` has neither.

Mixed groups split. Every verdict cites its issues, PRs, or doc lines.

#### Core checks

- **Anchor freshness** (`intent_staleness`): anchor claims vs the accumulated reality — e.g. a merged capability that erodes a stated non-goal.
- **Work → intent**: the lineage verdicts above.
- **Intent → work**: an anchor promise with no corresponding work in the window reads `deferred?`, quoting the anchor's exact promise — never as misalignment.

#### Detect-and-skip checks

Each runs only when its artifact class exists and otherwise skips silently — no findings, no warnings: intent-docs coherence (other intent-shaped docs vs the anchor; mission-echo is its reconciliation), decision-record supersession, roadmap orphans, conformance-portfolio staleness, non-goal erosion, metrics liveness.

#### Remediation

| Finding side | Remediation | Gating |
|---|---|---|
| Doc-side, outside the anchor range | proposed edit, applied under `apply` regardless of the doc's code-mode classification, with its basis re-checked | `apply` |
| Work-side | one alignment-summary tracking item (below) | `apply` |
| Anchor range itself | a draft edit (proposed text or diff) with rationale | never landed under any grant |

**Alignment summary.** File or update **one** alignment-summary tracking item per `{anchor_identity, anchor_fingerprint}` in the authoritative ledger (the summary signature derives from those two fields). Each work-side finding appears exactly once, with a finding signature derived from `{anchor_identity, anchor_fingerprint, finding_kind, sorted evidence IDs}`, plus its evidence and its work state — `merged` (current divergence to reconcile) or `planned` (decision to make before building). Re-running against the same anchor revision updates the summary and reuses entries; a closed summary that receives a new unresolved finding is reopened, never duplicated. Promoting a finding to an individual item is optional downstream triage via normal ledger tooling (reciprocally linked), preserving the finding signature; the summary closes only when every entry has a recorded terminal disposition. On ledger failure, report the failure with diagnostics — never silently fall back to a second ledger.

**Baseline receipt.** The alignment summary doubles as the durable baseline receipt. After an `apply` run completes a repo-start-to-review-head baseline, the summary records `baseline_complete: true`, the anchor identity and fingerprint, sources, and `reviewed_through`. A narrowed, interrupted, or failed run must not mark the baseline complete; a baseline with no findings still records a resolved receipt. Receipt persistence happens only under `apply` — read-only runs never mutate the repo.

## Output format

Always report: **Mode** (`code` or `intent`); effective **scope** (code) or **window** (intent); **dry run or applied** — dry-run unless explicit `apply` was provided.

### Code mode

- **Current-state drift / proposed edits**: `doc`, `location`, `doc_claim` or existing text, `code_state` or replacement text, `proposed_fix`/`edit`, `basis` — plus the producing entry point when both entry points ran.
- **Contract conflicts**: `doc`, `location`, `doc_side`, `code_side` — no edit until a human direction is supplied.
- **Steering-discipline findings** (failed checks only): `{doc, location, finding, requirement}` on agent-steering edit proposals.
- **Mission-echo items**: `{doc, location, duplicated_claim, pointer_edit, basis}` — the proposed replacement points to the anchor by path.
- **Intent-lag items**: `{anchor, new_capability, recommendation}` when a change crosses a capability boundary.
- **Index updates** (change-driven runs): `{index_doc, action, entry, summary, link, basis}` when a doc is added, renamed, or removed.
- **Unsupported**: `{doc, location, claim, what_basis_was_sought}` — no edit produced.

If no drift or affected docs are found, say so and write nothing.

### Intent mode

- **Alignment report**: `{anchor: {doc, range}, anchor_ref, anchor_fingerprint, baseline: {required, receipt_found, baseline_complete, reviewed_through}, window: {start, end, sources, fallback_used}, lineages: [{theme, evidence, verdict, intent_clause, basis}], intent_staleness: [{anchor_claim, reality, basis}], deferred: [{promise, basis}], recommendation}`.
- **Detect-and-skip check results**: each `{finding, evidence}`, or silently skipped when the artifact class is absent.
- **Remediation actions**: doc-side proposed edits, applied under `apply`; work-side `{summary_signature, anchor_fingerprint, baseline_receipt, findings: [{finding_signature, kind, work_state, evidence, linked_item?}]}` — one alignment summary created/updated under `apply`, `linked_item` is optional downstream triage; anchor-side `{draft_edit, rationale}` — draft only, never applied.
- **Unsupported**: `{doc, location, claim, what_basis_was_sought}` — no edit, verdict, or ledger action produced.

`basis` is action-appropriate: a code fact for code-claim reconciliation; the anchor range plus duplicate doc locations for mission-coherence edits; work-record or doc-line citations for intent verdicts and ledger items.

## Apply rules

- Dry-run is the default in both modes; write only when the user explicitly enables `apply`.
- Apply only approved, in-scope edits whose basis re-checks successfully. If `apply` follows a prior dry-run, apply only edits explicitly approved by the user or clearly covered by the current request.
- **Code mode**: apply current-state and agent-steering edits whose steering findings have been addressed; never edit contract conflicts — including the anchor range — without explicit human direction. Mission-echo remediation in code mode follows the doc's classification — a mission-echo edit proposed against a contract-class doc (non-anchor) is reported with the proposal and not written; intent mode's apply grant (below) is what writes basis-supported remediation regardless of classification.
- **Intent mode**: `apply` writes every basis-supported doc-side remediation outside the anchor range, regardless of the doc's code-mode classification; files or updates the one alignment summary in the authoritative ledger; and records the baseline receipt when the run completes a repo-start-to-review-head baseline.
- `apply` never enables: edits to the anchor range (draft only — landing is a human action), baseline-receipt writes on non-applied runs, or git operations.
- After applying, report each written edit and its basis, and each ledger filing.
