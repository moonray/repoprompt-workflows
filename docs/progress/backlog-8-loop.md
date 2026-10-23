# Loop Progress — backlog-8 (port-matrix provenance slice)

## Metadata

| field | value |
|---|---|
| lineage | rpw8 |
| epoch | L8-E1 |
| state | blocked (readiness) — new epoch after Backlog resolution of DR-1 |
| pipeline phase | Phase 2 — readiness BLOCKED by oracle verdict rpw8:t1 (2026-10-22); no tests/code/spec writes this epoch |
| invocation mode | orchestrated (escalation principal = Backlog orchestrator; never ask end-user; terminal blocked/handoff reports returned to Backlog) |
| repo / branch | /Users/bala/Sites/repoprompt-workflows on `backlog/8-port-matrix-provenance` (wizard-authorized 2026-10-22: NO worktree, no branch create/switch/rebase) |
| contract_commit | db715a2 (= HEAD at init) |
| base_sha | 588676e (parent of db715a2; merge-base with main) |
| implementation_base_sha | 588676e |
| issue | moonray/repoprompt-workflows#8 — PROVENANCE SLICE ONLY (fixture-hardening and manage()-consolidation slices explicitly OUT of scope; issue stays open, no status/label changes, no close) |
| spec | docs/spec/port-matrix-provenance.md @ blob 8ae4a627414cd5aa6ebb85d03b237f88d4038012 |
| plan | docs/plans/port-matrix-provenance.md @ blob 66376af60bb9b68a2bdb7fbe19c47881d06bf86a |
| tuple_key | rpw8:db715a2 |
| authorization | revision 1, issuer backlog-wizard, issued/effective 2026-10-22, git_scope=repoprompt-workflows (this branch only), contract_maintenance=workflow-only, contract_publication_scope=with-issue-only, doc_edits=true, issue_scope=[#8 provenance slice], conformance_acceptances=[], stop=false |
| responsibility | preparation=done-by-backlog; deterministic_readiness=done-by-backlog (PASS recorded); independent_readiness=loop; implementation_evidence=loop; publication/landing/status_close/replacement/cleanup=backlog |
| predecessor | none (maintenance_outcome=committed_complete(db715a2)) |
| pre-existing dirtiness | NONE — `git status --porcelain` empty at init; docs/progress/ did not exist (created by this epoch; the only disclosed owned write pre-init-complete) |

### Constraints (persisted from orchestrated brief constraints field + repo hard rules)

- No destructive git (no force-push, reset --hard, branch deletion, history rewrite).
- Local commits within this work's scope allowed without ask; never sweep unrelated files.
- Minimalism: exactly the three labeled fixes plus closeout artifacts; no scope creep into #8's other two slices.
- No AI-attribution lines in commit messages or PR descriptions.
- Conformance matrix at docs/spec/port-matrix-provenance.conformance.md required before merge_ready (spec-conformance skill produces it).
- Toolchain: verification = read-only grep/sed oracles pinned in the spec Constraints section; NO test suite applies (doc-only slice); `git -C /Users/bala/Sites/repoprompt-workflows diff --stat` must stay inside docs/.
- Route: never touch /Users/bala/Sites/keryxsolutions or any other repo; git only via `git -C /Users/bala/Sites/repoprompt-workflows`.
- Do NOT change issue #8 status/labels; do NOT close it; no progress comment on the issue (outer Backlog layer's job).

### Oracle budgets (durable, keyed)

- readiness key `rpw8:t1`: **CONSUMED 2026-10-22** — 1 substantive verdict returned (**blocked**, unanimous across both completing codex lanes: gpt-6.1-sol-high @high, gpt-6-astra-medium @medium); attempt 1 of 2 used; 2nd attempt deliberately NOT spent (verdict unambiguous — re-asking would be verdict-shopping). claudeCode lane failed (OAuth expired) as briefed.
- clarity: consumed by orchestrator (Backlog) — 0 remaining.
- lineage ceiling (orchestrated): 2 verdicts / 4 attempts ordinary; classification cap 3/6 per lineage.

### Delegation topology (persisted per contract)

- oracle: **available (degraded-2/3)** — codex lanes only; claude lane OAuth dead. `degraded_ok: false` → oracle verdict still REQUIRED (no ungated proceed).
- read-only explore children (agent_explore): **available** — used for independent review/verification probes (fresh sessions, read-only).
- mutation-capable subagent: **unavailable** — no worktree binding for this repo (primary-root-only limitation; brief forbids attempting), and no mutation-capable subagent tool exposed in this runtime. Per brief route ("operate on files via absolute paths under /Users/bala/Sites/repoprompt-workflows/") + unattended mutation approval (2026-10-16 record), the coordinator performs file mutations, with independent review delegated to fresh read-only explore children and oracle. Recorded as a standing topology note, not a per-task exception.

## initialization_complete

Recorded 2026-10-22 (epoch L8-E1): branch/HEAD/base verified as above; pre-existing dirtiness snapshot = empty; constraints persisted; authorization revision 1 active; owned progress path created (this file). Inputs (spec + plan) exist at pinned paths — proceeding to Phase 2 full contract reads.

## Readiness (Phase 2, 2026-10-22)

**Inline deterministic gate: PASS.** Spec + plan readable at pinned blobs; Open Questions = none; S-001–S-003 have stable IDs + observable outcomes; Proposed Surface sufficient (three named files with exact expected forms); plan has ordered tasks, files, validation commands, test strategy, success criteria, risk/rollback; no divergence from repo context — every cited line anchor verified against the worktree (see validation log).

**Scenario-to-test map** (layer for all: read-only grep/sed oracle — lowest faithful layer for a doc-only slice):

| scenario | oracle | red evidence (2026-10-22) |
|---|---|---|
| S-001 | (a) `grep -nE '(^|[^/a-zA-Z0-9])#[0-9]+'` over both chat-mining files → zero bare hits after fix | RED: 7 bare-ref instances — chat-mining.md L3 (#46, #42), L7 (#46); conf L3 (post-#46, the #46), L9 (#42), L16 (#42's), L17 (#42/#44/#45 series), L26 (#42, #46) |
| S-002 | (b) `grep -n '2506c45' docs/spec/live-dryrun.conformance.md` → labeled `keryxsolutions@2506c45` | RED: L58 carries bare `` (`2506c45`) `` |
| S-003 | (c) `sed -n '8p' .agents/skills/rpce-tool-gotchas/SKILL.md` contains "provenance" AND conformance row cites `:8` | HALF-RED: SKILL.md L8 verifiably contains the provenance sentence (L9 empty) — anchor already true; row at gotchas.conformance.md L22 cites `SKILL.md:9` — RED |

**Task-to-scenario map:** T1→S-001 (chat-mining.md), T2→S-001 (chat-mining.conformance.md), T3→S-002+S-003, T4→closeout verification (no scenario; gates only). Bidirectional coverage complete: every scenario has ≥1 task; every task traces to a scenario or an explicit non-implementation rationale (T4 = closeout gate). `first_safe_task` = **T1** (single file, no deps, trivially revertible).

**Readiness notes (non-blocking):** (1) plan T2 header says "(6 refs)" but enumerates 7 ref instances incl. the L17 `#42/#44/#45` series — the enumerated transformations + the "re-grep the whole file" catch-all govern; count discrepancy is cosmetic. (2) L17 prescribed labeled form is the compact series `keryxsolutions#42/#44/#45` (single prefix for the series) — satisfies S-001 via plan-prescribed form; the `/#44` `/#45` members are slash-shielded from oracle (a) by design. Recorded for the conformance matrix.

(2) L17 prescribed labeled form is the compact series `keryxsolutions#42/#44/#45` (single prefix for the series) — satisfies S-001 via plan-prescribed form; the `/#44` `/#45` members are slash-shielded from oracle (a) by design. Recorded for the conformance matrix. **[This inline triage was OVERRULED by the oracle verdict — see Readiness BLOCK below.]**

### Readiness BLOCK — oracle verdict rpw8:t1 (2026-10-22)

**Verdict: blocked** (both completing codex lanes unanimous; claude lane OAuth-dead as briefed degraded-2/3). One substantive verdict consumed; second transport attempt deliberately not spent.

**Gap (source: both):** S-001 requires "every originating-workspace reference appears as `keryxsolutions#NN`; no bare keryxsolutions-origin `#NN` remains", but plan T2 prescribes L17 → `keryxsolutions#42/#44/#45 filings`, leaving `#44`/`#45` bare under the strict per-reference form. Pinned oracle (a) `grep -nE '(^|[^/a-zA-Z0-9])#[0-9]+'` cannot discriminate: `/`-preceded members are excluded by design, so the compact form passes verification while violating S-001's observable outcome under the strict reading — a spec/plan contradiction in outcomes (an inline-gate blocker category; the inline gate mis-triaged it as cosmetic and was corrected by the independent gate).

**Decision request DR-1 to Backlog** — reconcile the contract:
- **A (recommended): amend the PLAN only** — T2 L17 becomes `keryxsolutions#42/keryxsolutions#44/keryxsolutions#45 filings`. Consequence: strict S-001 honored unchanged; one plan line changes; pinned oracles pass as-is; smallest contract delta.
- **B: amend the SPEC** — S-001/Constraints explicitly bless single-prefix series shorthand. Consequence: plan implements verbatim; spec text changes; oracle (a) stays blind to series members (acceptable only because the spec blesses them).
- **C: A + strengthen oracle (a)** — add a Constraints grep covering `/`-shielded members (e.g. `(^|[^/a-zA-Z0-9])/#[0-9]+` → zero hits). Consequence: strongest enforcement; touches both spec and plan; larger amendment.

Recommendation grounded in: the spec is the behavior contract, the plan is derived and yields; A touches minimal contract surface with no spec edit.

## Task ledger

| task | source | files | owner | oracle | status | evidence |
|---|---|---|---|---|---|---|
| T1 | plan T1 | docs/spec/chat-mining.md | coordinator (mutation topology note) | (a) | pending — red captured | RED: L3 ×2 refs, L7 ×1 ref confirmed 2026-10-22 |
| T2 | plan T2 | docs/spec/chat-mining.conformance.md | coordinator | (a) | pending — red captured | RED: 5 lines / 7 ref instances confirmed 2026-10-22 |
| T3 | plan T3 | docs/spec/live-dryrun.conformance.md L58; docs/spec/rpce-tool-gotchas.conformance.md L22 | coordinator | (b)+(c) | pending — red captured | RED: bare (`2506c45`) L58; `SKILL.md:9` cite at L22; SKILL.md:8 anchor verified |
| T4 | plan T4 | oracle re-runs; docs/spec/port-matrix-provenance.conformance.md; single implementation commit | coordinator + explore-child independent review | all three green | pending | README row pre-confirmed at docs/spec/README.md L7 |

## Review and escape ledger

(empty — no implementation diff this epoch; no review cycle entered)

## Amendment ledger

| id | issuer | classification | scope | before→after auth | status | timestamp | evidence |
|---|---|---|---|---|---|---|---|
| (none received) | — | — | — | — | decision request pending | 2026-10-22 | DR-1 (see Readiness BLOCK) awaiting Backlog; amendments accepted only from Backlog/user |

## Validation and resume log

| when | command | result |
|---|---|---|
| init | `git -C /Users/bala/Sites/repoprompt-workflows status --porcelain=v1` | clean (empty) |
| init | `git -C ... rev-parse HEAD` / `branch --show-current` | db715a20bb733f9d5c36f0522179f007f32acd37 / backlog/8-port-matrix-provenance |
| init | blob verify: `rev-parse HEAD:docs/{spec,plans}/port-matrix-provenance.md` + `hash-object` worktree copies | spec 8ae4a62…, plan 66376af… — all four match brief pins |
| init | `merge-base --is-ancestor 588676e HEAD` / `db715a2 HEAD` | yes / yes |

| 2026-10-22 | oracle (a) red run `grep -nE '(^|[^/a-zA-Z0-9])#[0-9]+' chat-mining.md chat-mining.conformance.md` | RED — hits at chat-mining.md L3,L7; conf L3,L9,L16,L17,L26 (7 bare refs) |
| 2026-10-22 | oracle (b) red run `grep -n '2506c45' docs/spec/live-dryrun.conformance.md` | RED — L58 bare form |
| 2026-10-22 | oracle (c) red run `sed -n '8p;9p' SKILL.md` + `grep -n 'SKILL.md:' gotchas.conformance.md` | L8 contains "provenance", L9 empty (anchor true); cite at L22 = `SKILL.md:9` (RED) |
| 2026-10-22 | plan anchor verification (sed L3/L7/L9/L16/L17/L26/L58/L22 + README row) | all anchors match plan exactly; spec README L7 row exists |

| 2026-10-22 | oracle transport (ask_oracle group 983D642E, mode chat, new chat): codex lane 1 gpt-6.1-sol-high @high → **blocked**; codex lane 3 gpt-6-astra-medium @medium → **blocked** (same core gap); claudeCode lane OAuth-expired failure (as briefed) | verdict consumed for key rpw8:t1: blocked, 1 substantive verdict, attempt 1/2 |

**Resume instruction (blocked terminal):** Epoch L8-E1 ended blocked at readiness. A new epoch (L8-E2) may begin only after Backlog resolves DR-1 via an issued amendment landing committed_complete; then re-enter Phase 2 readiness on the amended tuple (new contract_commit + blob pins) with a FRESH readiness oracle key (rpw8:t1 is consumed). No tests, code, or spec-file writes were made this epoch; the only write is this progress doc (committed alone, pathspec-scoped).

## Context exception log

(empty)
