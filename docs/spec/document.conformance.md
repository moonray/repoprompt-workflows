# Spec Conformance — Document Skill (Loop #3 final audit)

- **Spec:** `docs/spec/document.md` — final text after the AM-3 review errata (F3: code-mode Outputs gains the `Unsupported` row; F5: Anchor-boundary constraint reads `{doc, range}`), audit-time state of this worktree.
- **Implementation:** `.agents/skills/document/SKILL.md` (rewritten two-mode skill @ `ecddf41`), routed by `.agents/slash/document.md`, with anchor-landing enforcement mirrored in `.agents/rules/global.md:28` (Git Safety anchor-ratification bullet).
- **Battery:** `/tmp/document-skill-battery` GREEN run 2026-08-21 — 47/47 PASS (`run/results.tsv`), evidence in `run/observations/` (24 observation files; red run archived under `run/red/`).
- **Method:** every spec section, scenario, and Proposed Surface element mapped to implementation evidence (file:line) plus the battery item that exercised it. Battery failures would appear as Diverged rows — there were none.

## Matrix — Problem

| Item | Status | Evidence | Note |
|---|---|---|---|
| Problem: sync/audit split → one `code` mode, composable entry points, predictable default | Conformed | SKILL.md:14, 72–79 (one workflow, two entry points; L76 bare-invocation default) | Battery B1 (S-016), B2 (S-017) |
| Problem gap 1: intent drift invisible → intent mode | Conformed | SKILL.md:15, 132–188 | Battery B9–B16 |
| Problem gap 2: agent-steering docs unclassified → third class + disciplines | Conformed | SKILL.md:45–57, 107–116 | Battery B12 |
| Problem gap 3: mission prose duplicates → mission-echo → pointer | Conformed | SKILL.md:120–122 | Battery B13, B3 |

## Matrix — Goals

| Item | Status | Evidence | Note |
|---|---|---|---|
| G1 one code mode, two composable entry points, sane defaults | Conformed | SKILL.md:14, 21–26, 74–79 | B1, B2 (composition does not narrow corpus — F7 pin) |
| G2 agent-steering class, edits checked against steering disciplines, failed checks as findings | Conformed | SKILL.md:49, 57, 107–116 | B12 (S-018–S-021, S-034) |
| G3 mission-echo flagged and reconciled to pointer by path | Conformed | SKILL.md:120–122, 199 | B13 (dry), B3 (applied) |
| G4 capability-boundary change reports intent-lag | Conformed | SKILL.md:124–130, 200 | B14 (7 cases incl. no-anchor discipline) |
| G5 intent mode: bounded window, evidence-cited verdicts, freshness, deferred?, detect-and-skip | Conformed | SKILL.md:132–176, 208 | B9, B10, B15, B16 |
| G6 doc-side remediation under apply + ONE idempotent alignment summary with finding-level signatures | Conformed | SKILL.md:180–188, 220 | B3, B4, B10.1, B10.4 (reopen) |
| G7 anchor governance: draft never lands | Conformed | SKILL.md:59, 140, 184, 221; global.md:28 | B5, B6; global rule hard-gates landing |
| G8 action-appropriate basis, scope-bounded, approval-gated, contract conflicts surfaced | Conformed | SKILL.md:61–70, 215–222, 55 | B11 (S-002/S-004/S-008/S-009/S-010/S-011) |
| G9 repo-agnostic discovery + progressive-disclosure index | Conformed | SKILL.md:32–41, 96–105 | B11 (S-012/S-013/S-015) |

## Matrix — Non-Goals

| Item | Status | Evidence | Note |
|---|---|---|---|
| No brand-new doc authoring without basis | Conformed | SKILL.md:17, 68 | B11 S-004 (behavior.md Unsupported) |
| No code modification to match docs | Conformed | SKILL.md:17 ("Documentation follows code") | B11-apply: src/ hash-unchanged under apply |
| No changelogs/version bumps/git ops — edits, drafts, ledger items only | Conformed | SKILL.md:17, 25, 221 | B4/B7 filings only; battery's fixture commits are executor-side bookkeeping, disclosed (RESULTS.md assumption 2) |
| No autonomous anchor-edit landing, under any grant | Conformed | SKILL.md:184, 221; global.md:28 | B5 (draft only; range byte-identical after apply) |
| No code-fact re-checking from intent mode | Conformed | SKILL.md:17, 213 | B16 verdicts cite work record + doc lines only |
| No repo health score / combined mode; bundle = call-site | Conformed | SKILL.md:17 | slash/document.md routes per-mode only |
| No skill eval/benchmark machinery; steering checks are edit-time findings | Conformed | SKILL.md:17, 109 | B12 findings attached to proposals |
| No mandated repo conventions; absent artifact classes skip silently | Conformed | SKILL.md:17, 176 | B16 (S-029; fixture nuance disclosed) |

## Matrix — Constraints

| Item | Status | Evidence | Note |
|---|---|---|---|
| Doc classification priority order (frontmatter → convention → agent-steering path → spec/plan → current-state) | Conformed | SKILL.md:45–51 | B11 (api.md contract via frontmatter), B12 (paths), B6 (default) |
| Anchor boundary: range `{doc, range}` (F5), identity composition, shared lazy discovery, range-only contract class, intent-adjacent docs, no-anchor behaviors | Conformed | SKILL.md:59, 120, 136 (uses `{doc, range}`), 141 | B5/B6 (range split), B13, B14 (no-anchor), B15 (discovery order) |
| Anchor content altitude: mission + non-goals; deferred? only for actual promises | Conformed | SKILL.md:136 | B16 (payslip deferred?; no fabricated deferred) |
| Mode-specific gating: contract conflicts unedited in code mode; intent apply writes all basis-supported doc-side outside range; apply never enables git ops | Conformed | SKILL.md:55, 219–221 | B11-S008, B3, B13 (F6 pin: contract-class echo reported-not-written), B5 |
| Capability-boundary decision rules (provider/surface/module + exclusions + no-basis) | Conformed | SKILL.md:124–130 | B14 all 7 cases |
| Verdict rules (aligned/adjacent/orphaned; mixed split; citations) | Conformed | SKILL.md:158–166 | B16 (S-027) |
| Baseline-aware window resolution (fingerprint, two-state default, inclusive cutoff, source precedence, per-item in-window rule, report fields) | Conformed | SKILL.md:142, 145–156 | B9.1/B9.2 (state 1), B10.2 (state 2, inclusive boundary, git log -L verified); fallback branch textually specified (L150) and its disclosure field exercised — the fallback path itself is not forced by any fixture (see Remarks) |
| Filing contract (one summary per {identity, fingerprint}; finding signatures; merged/planned; reuse; reopen; optional promotion; close condition; ledger failure) | Conformed | SKILL.md:186 | B4 (exactly-once, idempotent), B10.4 (reopen), B7 (failure path); promotion wording simplified to "normal ledger tooling (reciprocally linked)" — semantics preserved (see Remarks) |
| Baseline receipt (summary doubles as receipt; complete fields; narrowed/interrupted/failed never complete; failure → conservative re-baseline; apply-only persistence) | Conformed | SKILL.md:188, 149 | B10.1 (recorded), B9.3 (narrowed never sets), B7 (failed run, no receipt) |
| Basis discipline is action-based (code fact / anchor range + duplicate locations / work-record or doc-line citations; Unsupported when absent) | Conformed | SKILL.md:61–70, 213 | B11-S002, B13 (dual-location basis), B4/B16 (citations), B11-S004 + B14 (Unsupported) |
| Guidance dedupes; enforcement references (pointer by path; rules/steering reference anchor by path, never quote) | Conformed | SKILL.md:116, 122 | B13 (pointer edits carry no duplicated prose) |
| Bounded windows (concrete start/end; never unbounded) | Conformed | SKILL.md:147 | B9.1/B10.2/B9.3 (all windows concrete) |
| Dry-run default both modes; content- and convention-based discovery (Markdown, Gherkin), not path-list-based | Conformed | SKILL.md:32–41, 217 | B8, B11 (S-012/S-013/S-014) |

## Matrix — Scenarios

| Scenario | Status | Evidence | Battery |
|---|---|---|---|
| S-001 change-driven run identifies affected docs | Conformed | SKILL.md:76, 81–86 | B11-sync PASS |
| S-002 basis-cited reconciliation edits | Conformed | SKILL.md:61–66 | B11-sync PASS |
| S-003 unaffected docs untouched | Conformed | SKILL.md:84 | B11-sync/apply PASS (hash-unchanged) |
| S-004 no fabricated content → Unsupported | Conformed | SKILL.md:68, 202 | B11-audit PASS |
| **S-006 — retired** (folded into S-005; ID never reused) | retired | spec tombstone comment (scenarios section) | not audited — recorded as retired per Stable Identifiers |
| S-005 corpus scan detects existing drift (value/enum) | Conformed | SKILL.md:88–93 | B11-audit PASS |
| S-007 dangling references flagged | Conformed | SKILL.md:94 | B11-audit PASS |
| S-008 contract conflict surfaced, not edited | Conformed | SKILL.md:55, 86, 93 | B11-audit PASS |
| S-009 scope limits the run | Conformed | SKILL.md:24, 41 | B11-scope PASS |
| S-010 dry-run by default | Conformed | SKILL.md:217 | B8 PASS |
| S-011 apply writes only approved edits | Conformed | SKILL.md:215–222 | B11-apply PASS (exactly 5 written) |
| S-012 repo-agnostic discovery (md + Gherkin) | Conformed | SKILL.md:36–40 | B11-sync PASS |
| S-013 instruction-artifact dirs contain docs | Conformed | SKILL.md:41 | B11-sync PASS |
| S-014 no drift → clean no-op | Conformed | SKILL.md:204 | B11-scope PASS |
| S-015 index in sync on lifecycle | Conformed | SKILL.md:96–105 | B11-apply PASS |
| S-016 bare invocation sane default | Conformed | SKILL.md:76; slash:7 | B1 PASS |
| S-017 entry points compose in one run | Conformed | SKILL.md:79, 196 | B2 PASS (per-item labels) |
| S-018 agent-steering classified by path | Conformed | SKILL.md:49 | B12 PASS |
| S-019 trigger preservation finding | Conformed | SKILL.md:111 | B12 PASS |
| S-020 near-miss finding | Conformed | SKILL.md:112 | B12 PASS |
| S-021 incident-overfit finding | Conformed | SKILL.md:113 | B12 PASS |
| S-022 mission-echo → pointer | Conformed | SKILL.md:120–122 | B13 PASS |
| S-023 capability-boundary intent-lag | Conformed | SKILL.md:124–130 | B14 PASS (7 cases) |
| S-024 anchor discovered in priority order | Conformed | SKILL.md:120, 134–136 | B15 PASS (p1 tier-1, p2 tier-2) |
| S-025 missing anchor is the finding | Conformed | SKILL.md:136 | B15 PASS (exact string + stop) |
| S-026 unrecognized revision → full re-baseline | Conformed | SKILL.md:145–152 | B9.1/B9.2/B9.3 PASS |
| S-027 lineage verdicts + citations | Conformed | SKILL.md:158–166 | B16 PASS |
| S-028 deferred?, not drift | Conformed | SKILL.md:172 | B16 PASS |
| S-029 intent-adjacent checks degrade silently | Conformed | SKILL.md:174–176 | B16 PASS (nuance: fixture's 0002 decision record ran the supersession check cleanly) |
| S-030 doc-side intent drift under apply | Conformed | SKILL.md:182, 220 | B3 PASS (incl. agent-steering-path doc) |
| S-031 one idempotent alignment summary | Conformed | SKILL.md:186 | B4 PASS |
| S-032 anchor edits drafted, never landed | Conformed | SKILL.md:140, 184, 221; global.md:28 | B5 PASS |
| S-033 anchor range is contract regardless of path | Conformed | SKILL.md:59, 136 | B6 PASS |
| S-034 unreferenced-content finding | Conformed | SKILL.md:114 | B12 PASS |
| S-035 ledger failure reports, never falls back | Conformed | SKILL.md:186 | B7 PASS (diagnostics, no fallback, no receipt) |
| S-036 completed receipt prevents repeated re-baselines | Conformed | SKILL.md:150–152, 188 | B10.1–B10.4 PASS |

## Matrix — Proposed Surface

### Inputs

| Item | Status | Evidence | Battery |
|---|---|---|---|
| mode (both; optional; inference precedence) | Conformed | SKILL.md:21, 28; slash:11 | B1 (inferred), B3 (explicit intent), B9–B16 |
| change (code; defaults to WT diff) | Conformed | SKILL.md:22, 76; slash:8 | B1, B11 |
| full (code; corpus scan; composes with change) | Conformed | SKILL.md:23, 79; slash:8 | B2 |
| scope (code; path/type/doc set; default whole repo) | Conformed | SKILL.md:24, 41; slash:8 | B11-scope, B13 (F6 scoped sub-case) |
| apply (both; default off; never enables anchor/git) | Conformed | SKILL.md:25, 217–221; slash:10 | B8 (off), B3/B4/B11 (on) |
| window (intent; baseline-aware default; --all/--since/--last narrow, never establish) | Conformed | SKILL.md:26, 149–152; slash:9 | B9.3 (--last 1), B10.2 (default) |

### Outputs — code mode

| Item | Status | Evidence | Battery |
|---|---|---|---|
| Drift report / proposed edits `{doc, location, doc_claim, code_state, proposed_fix, basis}` | Conformed | SKILL.md:196 | B11-sync/audit |
| Contract conflicts `{doc, location, doc_side, code_side}` — no edit | Conformed | SKILL.md:197 | B11-audit (S-008) |
| Steering-discipline findings (failed checks only) `{doc, location, finding, requirement}` | Conformed | SKILL.md:109, 198 | B12 |
| Mission-echo items `{doc, location, duplicated_claim, pointer_edit, basis}` | Conformed | SKILL.md:122, 199 | B13 |
| Intent-lag items `{anchor, new_capability, recommendation}` | Conformed | SKILL.md:130, 200 | B14 |
| Index updates `{index_doc, action, entry, summary, link, basis}` | Conformed | SKILL.md:101–105, 201 | B11-apply (S-015) |
| Unsupported `{doc, location, claim, what_basis_was_sought}` — no edit produced (F3 erratum row) | Conformed | SKILL.md:68, 202 | B11-audit (S-004), B14 (indeterminate, noanchor-provider) |

### Outputs — intent mode

| Item | Status | Evidence | Battery |
|---|---|---|---|
| Alignment report `{anchor, anchor_ref, anchor_fingerprint, baseline{…}, window{…}, lineages[…], intent_staleness[…], deferred[…], recommendation}`; anchor_ref both forms; fingerprint = normalized range-bytes hash | Conformed | SKILL.md:141–143, 208 | B9.1/B10.2 (full field set observed: fp 01f9edb5/d9acf80; anchor_ref d21be01 and d9acf80…+working-tree) |
| Detect-and-skip check results `{finding, evidence}` or silently skipped | Conformed | SKILL.md:176, 209 | B16 (S-029) |
| Remediation actions (doc-side edits; work-side `{summary_signature, anchor_fingerprint, baseline_receipt, findings:[{finding_signature, kind, work_state, evidence, linked_item?}]}`; anchor-side `{draft_edit, rationale}`) | Conformed | SKILL.md:180–188, 210 | B3/B4/B5/B10.4 (signatures observed: 77d770ce2828; 63c7c17d69e6/e484816c8424/3e90085a8cea/2f04b16ef39a) |
| Unsupported `{doc, location, claim, what_basis_was_sought}` — no edit, verdict, or ledger action | Conformed | SKILL.md:211 | B14 (noanchor-provider: exactly one, no verdict) |
| `basis` action-appropriate per basis-discipline constraint | Conformed | SKILL.md:213 | B11-S002, B13, B4/B16 |

## Coverage proof

**audited:**

- Sections: Problem; Goals (G1–G9); Non-Goals (all 8); Constraints (all 13); Scenarios; Proposed Surface — Inputs; Proposed Surface — Outputs — code mode; Proposed Surface — Outputs — intent mode.
- Scenarios: S-001, S-002, S-003, S-004, S-005, S-007, S-008, S-009, S-010, S-011, S-012, S-013, S-014, S-015, S-016, S-017, S-018, S-019, S-020, S-021, S-022, S-023, S-024, S-025, S-026, S-027, S-028, S-029, S-030, S-031, S-032, S-033, S-034, S-035, S-036 — 35 active scenarios, each with implementation evidence + a green battery row; **S-006 retired** (folded into S-005; tombstone recorded, ID not reused).
- Inputs: mode, change, full, scope, apply, window (6/6).
- Outputs — code mode: drift report/proposed edits, contract conflicts, steering-discipline findings, mission-echo items, intent-lag items, index updates, Unsupported (7/7 incl. the F3 erratum row).
- Outputs — intent mode: alignment report, detect-and-skip check results, remediation actions, Unsupported, plus the trailing `basis`-appropriateness statement (5/5).
- Battery cross-check: 47/47 items PASS (`run/results.tsv`), item set identical to the red run (33 FAIL-red→PASS, 14 PASS→PASS); tally reconciliation recorded in `RESULTS.md` (the brief's 46/32 premise did not match ground truth — red artifacts already agreed at 47/33).

**unreconciled:** [] — no Diverged, no Not-built.

## Remarks

- The `repoprompt-workflows` distribution mirror is deliberately out of scope for Loop #3 (deployment concern, not a spec scenario); it is not a Diverged row.
- Window-resolution fallback branch (range-overlap miss → containing-file fallback with disclosure) is specified (SKILL.md:150) and its `fallback_used` disclosure field is exercised green (B10.2, reported not-used), but no fixture forces the fallback path itself — flagged as a test-coverage gap, not a conformance gap (carried from the battery's authored assumption 4).
- Filing-contract promotion wording: the spec enumerates "(a GitHub native sub-issue, or a reciprocally linked item in the file-backed ledger)"; SKILL.md:186 says "normal ledger tooling (reciprocally linked)". Semantics identical (optional downstream promotion preserving the finding signature); wording altitude differs only.
- Battery execution disclosures (harness, not skill): checklist-authored sequencing notes, the executor-side fixture bookkeeping commits, the staged F6 sub-case in B13, and the S-029 decision-record nuance are recorded in `/tmp/document-skill-battery/RESULTS.md` (Blockers/assumptions 2–8).
