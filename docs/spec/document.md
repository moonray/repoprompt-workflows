---
title: Document Skill
issue: none
status: implemented
---

# Document Skill

## Problem

Documentation drifts from code silently. The current document skill is a single line — "update documentation to reflect changes" — with no process: it does not determine which docs a change affects, cannot detect drift that already exists, applies edits without a traceable basis, and gives no scope control. In practice this means docs go stale unnoticed (a recent spec listed a field's allowed values as `waiting_for_input` while the code emitted `waitingForApproval` — drift caught only by a later manual audit), and ad-hoc doc edits either miss affected docs or invent content. A documentation skill needs two deterministic behaviors — reconcile docs to a change, and detect existing drift — with edits that always trace to a real code fact, that never silently rewrite a contract, and that respect an explicit scope and an explicit apply step.

## Goals

1. In sync mode, given a code change, identify the docs whose content depends on that change; propose edits that reconcile **current-state docs** to the code, and surface **contract docs** that conflict with the code rather than editing them.
2. In audit mode, scan the repo to find docs already out of sync with the code; report each discrepancy with a proposed fix for current-state docs and as a conflict for contract docs.
3. Every proposed edit traces to a concrete code fact (a symbol, path, parameter, or observed behavior) — no fabricated content.
4. Edits are scope-bounded and approval-gated: only affected, in-scope docs are touched, nothing is applied without an explicit apply step, and contract conflicts are surfaced, not auto-resolved.
5. Operate on whatever doc files a repo contains, discovered per-repo rather than hardcoded.
6. Keep docs discoverable by agents through a concise progressive-disclosure index — one small index file listing each doc with a one-line summary and link — kept in sync when docs are added, removed, or renamed.

## Non-Goals

- Authoring brand-new documentation with no code basis — that belongs to dedicated spec/plan authoring skills, which this skill complements.
- Managing documentation lifecycle states (draft, implemented, archived) or a phase workflow.
- Modifying code to match documentation; documentation follows code, not the reverse.
- Generating changelogs, release notes, or version bumps.
- Performing git operations (commit, push); it produces edits, the user commits.

## Constraints

- A doc is classified **contract** or **current-state** deterministically, in priority order: (a) per-doc frontmatter with an explicit `type: contract` or `type: current-state` (or a `status:` value the repo's docs convention maps to one of these); (b) else a docs convention/README in the repo that maps paths to a doc type; (c) else, docs under a directory whose name contains `spec` are contracts, and when such specs exist, docs under a directory whose name contains `plan` are current-state; (d) all other docs are current-state. For current-state docs, code is the source of truth and edits reconcile to it. For contract docs, a conflict with the code is reported with both sides and no edit is produced until a human supplies a direction.
- Every proposed edit carries its basis: the code fact (file and symbol/path/parameter, or an observed value) it reconciles against. Edits with no basis are not produced.
- Proposed changes are dry-run by default; `apply` is the approval mechanism — no doc is written unless `apply` is explicitly enabled.
- Discovery is content- and convention-based, not path-list-based. The minimum recognized doc forms are Markdown (headings, tables, lists) and Gherkin `.feature` (scenarios and steps); a repo's docs convention may extend this set. Directories that primarily hold agent instruction artifacts can still contain documentation files, such as README indexes or reference docs, and those documentation files remain in scope unless excluded by the requested scope or repo convention.

## Scenarios

### Scenario: Sync identifies docs affected by a change
- **Given** Doc A documents a parameter `foo`, Doc B documents an unrelated area, and a code change renames `foo` to `bar`
- **When** the skill runs in sync mode over that change
- **Then** the report includes Doc A's parameter location and excludes Doc B

### Scenario: Sync proposes reconciliation edits for current-state docs
- **Given** an affected current-state doc location and the code change
- **When** the skill proposes an edit
- **Then** the edit reconciles the doc to the code's current state and is accompanied by the specific code fact (symbol/path/parameter/observed value) it is based on

### Scenario: Sync does not touch unaffected docs
- **Given** a change and a doc whose content does not depend on the changed code
- **When** the skill runs in sync mode
- **Then** that doc is left unchanged

### Scenario: No fabricated content
- **Given** a change for which some affected doc content has no corresponding code fact to reconcile against
- **When** the skill would propose an edit for that content
- **Then** it produces no edit for the unsupported content and reports that a basis could not be found

### Scenario: Audit detects existing drift in current-state docs
- **Given** a current-state doc whose stated value, parameter, or behavior no longer matches the code
- **When** the skill runs in audit mode over the repo
- **Then** it reports the drift location with the doc's claim, the code's actual state, and a proposed fix carrying its basis

### Scenario: Audit catches a value/enum mismatch
- **Given** a doc that enumerates the allowed values of a field while the code emits a value outside that enumeration
- **When** audit runs
- **Then** the mismatch is reported with the doc's enumeration and the code's actual emitted value

### Scenario: Audit flags a removed or renamed reference
- **Given** a doc that references a symbol, path, or parameter that no longer exists in the code
- **When** audit runs
- **Then** the dangling reference is reported with its doc location and the proposed removal or update

### Scenario: Contract-doc conflict is surfaced, not edited
- **Given** a doc classified as a contract doc by the detection rule conflicts with the code's actual behavior
- **When** the skill encounters the conflict in either mode
- **Then** it reports the conflict with the doc side and the code side and produces no edit to the doc

### Scenario: Scope limits the run
- **Given** a repo with drift inside and outside a requested scope (a path, doc type, or doc set)
- **When** the skill runs with that scope
- **Then** only in-scope docs are scanned, reported, or edited; out-of-scope docs are not touched

### Scenario: Edits are dry-run by default
- **Given** the skill has produced proposed edits
- **When** `apply` is not enabled
- **Then** no doc file is written and the proposals are presented for review

### Scenario: Apply writes only approved edits
- **Given** proposed edits whose bases are valid and `apply` is enabled
- **When** the skill applies them
- **Then** only those proposed edits are written and each written edit is reported

### Scenario: Repo-agnostic doc discovery
- **Given** a repo whose documentation includes both Markdown and Gherkin `.feature` files
- **When** the skill runs in either mode
- **Then** it discovers and operates on both file types with no repo-specific path configuration

### Scenario: Instruction artifact directories can contain docs
- **Given** a repo has an agent instruction artifact directory that contains README or reference Markdown files
- **When** the skill runs without a scope that excludes that directory
- **Then** those documentation files are included in discovery and evaluated for code or tooling claims

### Scenario: No drift yields a clean no-op
- **Given** a repo (audit) or a change (sync) for which all in-scope docs already match the code
- **When** the skill runs
- **Then** it reports an empty result set and writes nothing

### Scenario: Sync keeps the docs index in sync
- **Given** a sync adds a new doc, renames one, or removes one, and a repo docs index exists (or is conventionally expected)
- **When** the skill runs in sync mode
- **Then** the index is updated with a concise one-line summary plus link for the new doc, updated for the rename, and dropped for the removal — and the index edit carries its basis (the doc it points to) and is dry-run unless `apply` is enabled

## Proposed Surface

### Inputs

| Input | Mode | Required | Description |
|-------|------|----------|-------------|
| mode | both | yes | `sync` (reconcile to a change) or `audit` (detect existing drift). |
| change | sync | no | The change to reconcile to; defaults to the working-tree diff when omitted. |
| scope | both | no | A path, doc type, or doc set to limit the run; defaults to the whole repo. |
| apply | both | no | Approval to write edits; defaults to off (dry-run / report only). |

### Outputs

| Output | Mode | Shape |
|--------|------|-------|
| Drift report | audit | Current-state docs: `{doc, location, doc_claim, code_state, proposed_fix, basis}`. |
| Proposed edits | sync | Current-state docs: `{doc, location, edit, basis}`. |
| Conflicts | both | Contract docs conflicting with code: `{doc, location, doc_side, code_side}` — no edit until a human direction is supplied. |
| Index updates | sync | `{index_doc, action, entry, summary, link, basis}` when a doc is added, renamed, or removed, keeping the progressive-disclosure index in sync. |

`basis` is always a concrete code fact (file + symbol/path/parameter, or an observed value); entries with no basis are omitted rather than fabricated.

## Open Questions

1. **What backstops fabricated or wrong edits beyond the basis requirement?** Recommendation: require each edit to cite its basis in the output and to re-check that basis against the code at apply time.
2. **Should sync auto-derive its change from git, or require an explicit change input?** Recommendation: default to the working-tree diff, overridable for staged or commit-range changes.
3. **Should the docs index be a `docs` README (repo convention) or `llms.txt`?** Recommendation: a `docs` README by default (README is the universal code-repo entry point); emit `llms.txt` only when the docs are published as a website, since llms.txt is a website standard, not a code-repo one.
