---
name: document
description: Use when reconciling documentation to code changes or auditing documentation drift in a repo. Applies whenever the user asks to update docs after code changes, check whether docs match code, run a documentation audit, or produce doc drift reports; defaults to dry-run proposals and requires explicit apply before writing.
---

# Document

## Purpose

Keep documentation aligned with code without inventing facts or silently rewriting contracts.

Use this skill in two modes:

- **sync**: reconcile docs affected by a code change.
- **audit**: scan existing docs for drift from code.

Documentation follows code. Do not modify code to match docs, create changelogs, bump versions, or author brand-new docs with no code basis.

## Inputs

- **mode**: `sync` or `audit`.
- **change**: for sync, defaults to the working-tree diff when omitted; may be overridden by a staged diff or commit range if the user supplies one.
- **scope**: optional path, doc type, or doc set; default is the whole repo.
- **apply**: optional approval to write edits; default is off. Without explicit `apply`, report only.

If mode is unclear, infer `sync` for “update docs for this change” requests and `audit` for “find/check doc drift” requests. Ask only when the request cannot be safely interpreted.

## Workflow

### 1. Discover documentation

Discover docs from the repo instead of relying on a fixed path list.

Minimum supported forms:

- Markdown (`.md`, `.mdx`): headings, paragraphs, lists, tables, code fences.
- Gherkin (`.feature`): features, scenarios, and steps.

Honor repo documentation conventions if present, such as README guidance, docs indexes, or frontmatter conventions. Directories that primarily hold agent instruction artifacts can still contain documentation files, such as README indexes or reference docs; include those docs unless the requested scope or repo convention excludes them. Apply `scope` before reporting or editing; ignore out-of-scope docs.

### 2. Classify docs

Classify each in-scope doc as **contract** or **current-state** in this priority order:

1. Per-doc frontmatter with `type: contract` or `type: current-state`, or a `status:` value that the repo convention maps to one of those types.
2. A repo docs convention or README that maps paths to a doc type.
3. A path containing `spec` means contract; when such specs exist, a path containing `plan` means current-state.
4. Otherwise, current-state.

For **current-state** docs, code is the source of truth and proposed edits may reconcile docs to code.

For **contract** docs, report conflicts with both sides and do not produce edits unless a human supplies a direction.

### 3. Establish code basis

Every drift item or proposed edit must cite a concrete code fact as its basis:

- file plus symbol, path, parameter, schema field, command, route, configuration key, or emitted/observed value;
- for behavior, the code path or reproducible observation that proves the behavior.

Do not propose edits for unsupported claims. If a doc claim has no reliable code basis, report that no basis was found instead of fabricating content.

Before applying any edit, re-check that its cited basis still exists and still supports the edit.

### 4. Sync mode

1. Determine the change: use the working-tree diff by default, or the explicit change input if provided.
2. Identify docs whose content depends on changed symbols, paths, parameters, schemas, commands, routes, config keys, or observed values.
3. Exclude unrelated docs.
4. For affected current-state docs, propose minimal reconciliation edits with basis.
5. For affected contract docs, report conflicts with doc side and code side; do not edit.

### 5. Audit mode

1. Scan in-scope docs for concrete claims about code: names, paths, parameters, allowed values, schemas, commands, routes, configuration, file locations, or observable behavior.
2. Check each claim against code.
3. Report drift for current-state docs with doc claim, code state, proposed fix, and basis.
4. Report contract conflicts with doc side and code side; do not edit.
5. Report dangling references to removed or renamed symbols, paths, or parameters.

### 6. Keep a progressive-disclosure docs index

Docs are only useful if agents (and humans) can find them. Maintain a single concise index of the repo's documentation so consumers load a small overview first and drill down on demand (progressive disclosure):

- One index file — a `docs` README by default; `llms.txt` only when the docs are published as a website (llms.txt is a website standard, not a code-repo convention).
- Each entry is a one-line summary plus a link to the detail doc; keep entries brief — the index is the entry point, not the content.
- In sync mode, when a doc is added, removed, or renamed, update the matching index entry so the index and the docs never drift.
- Do not fold detail into the index — it points to it. Large reference docs (>~300 lines) should carry their own table of contents.

Treat the index like any other current-state doc for basis and apply rules: an index edit must trace to a real doc that exists, and is dry-run unless `apply` is enabled.

## Output format

Always report:

- **Mode**: `sync` or `audit`.
- **Scope**: effective scope used.
- **Dry run or applied**: dry-run unless explicit `apply` was provided.
- **Current-state drift / proposed edits**:
  - `doc`
  - `location`
  - `doc_claim` or existing text
  - `code_state` or replacement text
  - `proposed_fix` / `edit`
  - `basis`
- **Contract conflicts**:
  - `doc`
  - `location`
  - `doc_side`
  - `code_side`
- **Unsupported claims**: doc locations skipped because no reliable basis was found.
- **Index updates** (sync mode): `{index_doc, action, entry, summary, link, basis}` when a doc is added, renamed, or removed — keeps the progressive-disclosure index in sync (step 6).

If no drift or affected docs are found, say so and write nothing.

## Apply rules

- Dry-run is the default.
- Only write docs when the user explicitly enables `apply`.
- Apply only the approved, in-scope current-state edits whose basis re-checks successfully.
- If `apply` follows a prior dry-run, apply only edits explicitly approved by the user or clearly covered by the current request.
- Never apply edits to contract conflicts without explicit human direction.
- After applying, report each written edit and its basis.
