# Loop Progress — backlog-2-loop (lineage rpw2, epoch L2-E2)

## Metadata

- **lineage:** rpw2
- **epoch:** L2-E2
- **lifecycle state:** `running` (steerable: no — orchestrated; terminal reports to Backlog)
- **pipeline phase:** phase-2-inputs-readiness (initialized)
- **invocation mode:** orchestrated (escalation principal = Backlog orchestrator; never ask end-user; return terminal blocked/handoff reports; wait for steer only after persisting live `paused`)
- **issue:** moonray/repoprompt-workflows#2 — test-quality Stop gate can't clear under Codex/opencode runtimes (status/labels owned by Backlog — Loop must not touch)
- **worktree (repo root for ALL file ops):** `/Users/bala/Sites/.repoprompt-worktrees/repoprompt-workflows/rp-worktree-backlog-2-test-quality-stop-gate-7532f48f-ce4fdf5c` (wizard-authorized route 2026-10-22: NO agent_run worktree binding; all ops via absolute paths; git via `git -C <worktree>`; never touch main checkout or other repos; no branch create/switch/rebase)
- **branch:** `backlog/2-test-quality-stop-gate-runtimes`
- **contract_commit / HEAD at init:** `f144a7db930c0701633d6d8108b57262dd386b85`
- **base_sha:** `588676e` (verified ancestor of contract commit)
- **implementation_base_sha:** `588676e`
- **Spec:** `docs/spec/test-quality-reminder.md` @ blob `ddc9763511bf71d6fff5f13e50e17c9041b82af8` (verified at f144a7d)
- **Plan:** `docs/plans/test-quality-stop-gate-runtimes.md` @ blob `70a990e6e173fc27824723b8539e7e295352d492` (verified at f144a7d)
- **tuple_key:** `rpw2:f144a7d`
- **predecessor maintenance_outcome:** committed_complete(f144a7d, preserved from Backlog run 2026-10-16, revalidated 2026-10-22); predecessor handoff record: E1 (2026-10-16) never dispatched (RPCE primary-root-only worktree-binding limitation); zero Loop turns ever ran on this contract; work area clean at f144a7d with contract intact
- **authorization:** revision 1, issuer backlog-wizard, issued_at 2026-10-22, effective_at 2026-10-22, git_scope repoprompt-workflows (this branch/worktree only), contract_maintenance workflow-only, contract_publication_scope with-issue-only, doc_edits true, issue_scope [moonray/repoprompt-workflows#2], conformance_acceptances [], stop false, granted_at 2026-10-22 wizard
- **responsibility:** preparation done-by-backlog (preserved f144a7d); deterministic_readiness done-by-backlog (PASS re-recorded on revalidated tuple); independent_readiness loop; implementation_evidence loop; publication/landing/status_close/replacement/cleanup backlog
- **constraints source:** orchestrated brief constraints field (2026-10-22), persisted verbatim-relevant below; repo hard rules = repoprompt-workflows repo rules + global rules (keryx-private overlay + canonical global.md as loaded in this session)
- **pre-existing dirtiness snapshot (at init):** none — `git status --porcelain=v1 -b` showed only `## backlog/2-test-quality-stop-gate-runtimes`, zero dirty/untracked paths
- **oracle:** status up-degraded-2/3 (codex lanes only; claude lane OAuth dead); degraded_ok FALSE → oracle gate mandatory while reachable; budgets: readiness rpw2 t1=0 (fresh this epoch; 2026-10-16 'implementable' verdict was for this exact tuple — cheap re-confirm, deterministic evidence suffices as supporting input), clarity n/a (issue long-clear); lineage ceilings orchestrated: 2 verdicts/4 attempts ordinary, classification 3/6
- **delegation topology (recorded at init):** agent_run worktree binding UNAVAILABLE for this repo (authoritative diagnosis, wizard route change 2026-10-22) → no mutation-capable subagent dispatch available in this session; oracle available (codex lanes) for independent readiness verdict, repeated-finding classification, and independent review; explore children read-only and root-scoped to loaded workspace roots (which exclude this worktree) → wizard-authorized route: direct execution in the owned worktree by this session, with oracle providing the independent-eyes roles (readiness, review). Mutation approval: unattended (2026-10-16 record).
- **toolchain (from brief, to be resolved/confirmed in phase-3):** codex-cli 0.162.1 (`codex --version`), opencode 1.18.35, python3 for hooks; hook-test invocation to be discovered from scripts/ and existing test layout (plan task records exact commands)

## Constraints (from brief, verbatim-relevant — binding)

- No destructive git; local commits within this work's scope allowed without ask — never sweep unrelated files.
- BINDING POLICY from the plan is not negotiable without a Backlog-issued amendment: preference ladder (1) route skill marker if observable, (2) explicit attestation step if Stop routed but skills invisible, (3) documented-unsupported if Stop not routed — NEVER a silent run-only clear.
- Claude-Code behavior must remain unchanged (regression-pinned).
- Minimalism — smallest change per the selected ladder rung.
- test-quality discipline on new tests (each names a plausible defect, exact observable outcomes).
- No AI-attribution lines in commits.
- Spec amendment (per-runtime scenarios) + conformance update required per plan task 5; conformance matrix required before merge_ready.
- Do NOT change the issue's status or labels (outer Backlog layer owns that).
- Sibling issue keryx#74 (keryxsolutions scripts/archive calendar fail-fast) — DIFFERENT repo, zero overlap; out of scope.

## Task ledger

(populated after Deep Plan read in phase 2)

## Review and escape ledger

(empty)

## Validation and resume log

- 2026-10-22 init: `git -C <wt> status --porcelain=v1 -b` → clean on `backlog/2-test-quality-stop-gate-runtimes`; `rev-parse HEAD` → f144a7db930c0701633d6d8108b57262dd386b85; spec blob → ddc9763511bf71d6fff5f13e50e17c9041b82af8 (matches brief); plan blob → 70a990e6e173fc27824723b8539e7e295352d492 (matches brief); `cat-file -e 588676e^{commit}` → exists; `merge-base --is-ancestor 588676e f144a7d` → true; contract commit == HEAD → true.
- **resume instruction:** progress doc is the resume point; if this session dies, successor re-validates identity tuple (HEAD/blobs/cleanliness), re-reads this doc, and continues at the current phase/task.

## Context exception log

(empty)

---

**initialization_complete** — 2026-10-22, lineage rpw2, epoch L2-E2, mode orchestrated, worktree/branch/base as above, pre-existing dirtiness: none, constraints + source persisted, authorization revision 1, responsibility owners persisted, Spec/Plan paths known + blob-verified, contract identity f144a7d recorded.

## Phase 2 — Readiness (inline deterministic gate)

**Inline verdict: PASS (implementable), with one recorded observation.**

### Deterministic checks
- Inputs readable, blobs verified at contract commit (see validation log). ✓
- Spec Open Questions: "None." ✓
- Scenarios: 8, each Given/When/Then with observable Then outcomes; keyed by stable unique titles (file predates S-NNN convention; plan task 5 explicitly says follow the file's existing format). Ledger shorthand below: SP-1..SP-8. ✓
- Proposed Surface sufficient: Hook Payload table (hook_event_name/cwd/tool_input.command) + Hook Output table. ✓
- Plan: ordered tasks 1–8, expected files named per task, dependency order, test strategy (task 6: existing hook test layout; no test file exists yet for this hook — confirmed via ls), validation commands = discover exact invocation in tasks 1–2 (toolchain section makes discovery explicit in-scope work with a record requirement), success criteria = binding policy + task 7. ✓
- Risk/rollback present (revert branch commits; tests pin Claude-Code path). Task touches multiple files (task 4) — risk note covers it. ✓
- Repo-context grounding: all plan-named surfaces exist at contract commit (.agents/hooks/test-quality-reminder.py, scripts/install.sh, .codex/hooks.json, .opencode/plugins/repoprompt-hooks.mjs, .agents/hooks/README.md, docs/spec/ + .conformance.md layout). ✓
- Spec↔Plan contradiction: none (plan treats spec as existing, amendment in-scope). ✓

### Recorded observation (not a blocker; feeds task 5)
Pre-existing spec↔implementation drift on the Claude-Code skill half: spec scenario SP-5 ("edit→run→stop is allowed") vs hook docstring/behavior (Stop blocks until the later of {run, test-quality Skill invocation}; commit/clean always escapes). The runtime-gap amendment (task 5) is the sanctioned place this gets reconciled/recorded; conformance matrix at closeout will surface it explicitly.

### Scenario-to-test map (SP-n = shorthand; layers per repo's .mjs stdin-fixture pattern)
| Scenario | Layer | Why |
|---|---|---|
| SP-1 run records marker + nudges | provider/adapter/entrypoint (hook via stdin fixture) | observable marker write + emitted reminder |
| SP-2 non-run command no-op | entrypoint unit | negative fixture |
| SP-3 help/version/install not runs | entrypoint unit | negative fixture |
| SP-4 Stop blocks dirty-since-run | filesystem integration (temp repo, mtime) | git-state + marker mtime interplay |
| SP-5 edit→run→stop allowed | filesystem integration | mtime ordering (NOTE: impl now also requires skill marker — drift above) |
| SP-6 commit/clean clears | filesystem integration (clean tree) | git-state |
| SP-7 docs not tests | filesystem integration (docs/spec file) | DOC_FILE_RE filter |
| SP-8 malformed payload exits 0 | entrypoint unit | robustness |
| NEW per-runtime scenarios (T5) | entrypoint/adapter fixtures per runtime payload shape + wiring assertions | ladder rung behavior |

### Task-to-scenario map
- T1 investigate Codex (read-only) → diagnosis; informs NEW runtime scenarios
- T2 investigate opencode (read-only) → same
- T3 record findings + select rung → same
- T4 implement (hook + wiring) → NEW per-runtime scenarios; preserves SP-1..SP-8 (Claude-Code regression-pinned)
- T5 spec amendment + conformance update → authors NEW scenarios; reconciles recorded drift
- T6 regression tests → SP-1..SP-8 pinned + NEW per-runtime scenarios covered
- T7 verify (full suite + lint; CC matcher unchanged) → all
- T8 commit(s) → process

### Bidirectional coverage
Existing scenarios SP-1..SP-8 → T6 (Verify-mode: impl exists; tests currently MISSING for this hook — confirmed). Runtime-gap (the issue) → T1–T5, T6. No scenario lacks a task; no task untraceable. **Coverage: complete** (new scenario IDs materialize at T5 per plan).

**first_safe_task:** Plan task 1 (read-only investigation of Codex wiring) — matches plan's declared first safe task.

### Mode decisions per task loop
- SP-1..SP-8 (existing behavior): **Verify mode** (impl exists; audit + pin with tests, no reimplementation unless gap).
- Runtime-gap work (T1–T6): **Implement mode** (red → green → review → refactor).

## Phase 2 — Oracle readiness verdict (budget key readiness:rpw2:f144a7d)

- **Attempt 1 (of 2 per tuple), 2026-10-22:** one ask_oracle group call → codex lane gpt-6.1-sol-high: verdict **blocked**; codex lane gpt-6-astra-medium: verdict **blocked** (convergent); claude lane: provider OAuth failure (pre-declared degraded-2/3 topology — not an attempt failure of the substantive verdict). **Substantive verdict (1) consumed: BLOCKED.**
- **Blocking gap (both lanes, converged):** spec scenario "edit→run→stop is allowed" (SP-5) contradicts the plan's binding policy (never a silent run-only clear) + "Claude-Code behavior must remain unchanged" (current CC impl requires test-quality skill invocation for the gate to clear). Plan orders the reconciliation (T5 spec amendment) AFTER implementation (T4), so T4's contract is contradictory on its face.
- **Oracle-authorized scope:** T1–T3 read-only investigation + contract reconciliation may proceed; tests/implementation remain BLOCKED on tuple rpw2:f144a7d pending readiness review of an amended tuple. (Both lanes' first_safe_task = T1 read-only.)

### Path decision (recorded 2026-10-22)
1. Execute T1–T3 read-only (oracle-authorized; no tests/code/delegations).
2. Perform sanctioned contract maintenance to resolve the blocker: **spec amendment** (reconcile SP-5 to the binding policy with CC behavior as the pinned truth + add per-runtime scenarios from T1–T3 evidence) — this is exactly plan task 5's scope, executed early under the oracle's required_resolution; authorization includes `contract_maintenance: workflow-only` + `doc_edits: true`. **The plan document stays byte-identical** (no input repair in-loop); the execution-order deviation (task-5 substance before task 4) is recorded here and in the amendment ledger as oracle-mandated, with the binding policy untouched and enforced.
3. Commit contract-only change → new tuple → fresh inline gate + oracle readiness verdict #2 (lineage ordinary budget: 2 verdicts/4 attempts orchestrated; consumed 1/1; this will be 2/2 — final review must then rely on the per-task review evidence + delegated review lanes within remaining budget, or block).
4. If amended tuple passes → continue T4–T8 this epoch. If it blocks again or the amendment exceeds scope → terminal blocked report to Backlog with all evidence (no further budget games).

**State: running; tests/code blocked pending amended-tuple readiness. No tests, code, or implementation delegations issued on tuple rpw2:f144a7d.**

## Tasks 1–3 — Runtime investigation, findings, rung selection (read-only, oracle-authorized)

### T1 — Codex (evidence)
- **Codex CLI 0.162.1** (`codex --version`). Feature flags: `hooks` stable=true; skills are first-class (`skill_search` stable).
- **Stop IS routed and can block:** `.codex/hooks.json` (this repo, contract commit) wires `Stop` → test-quality-reminder.py (timeout 30); `~/.codex/config.toml` `[hooks.state]` shows trusted entries `…/.codex/hooks.json:stop:0:0` for keryxsolutions AND repoprompt-workflows (codex loads + trusts these hooks in practice).
- **Official codex hooks reference** (learn.chatgpt.com/docs/hooks, fetched 2026-10-22): 12 events incl. `PostToolUse` and `Stop`; PostToolUse payload carries `tool_name` — "Canonical hook tool name, such as `Bash`, `apply_patch`, or an MCP name" — shell execution and unified exec BOTH report `tool_name: "Bash"` with `tool_input.command`; matcher is a regex on tool names; Stop consumes stdout JSON `{"decision":"block","reason":…}` as a continuation prompt (or exit 2 + stderr).
- **Skill invocations are NOT observable:** the hooks reference documents no hook event for skill invocation; tool coverage is shell/unified-exec, apply_patch, MCP tools, some local function tools; hosted tools fire no hooks; skills are not listed as hook-emitting. `~/.codex/skills/` exists (skills are consumed as files), but no event marks their use.
- Conclusion: **run detection works under Codex** (matcher "Bash" matches, tool_input.command present); **the vet/skill half can never clear** (no observable skill invocation) → Stop blocks until commit/clean once tests are dirty — exactly issue #2's symptom.

### T2 — opencode (evidence)
- **opencode 1.18.35** (`opencode --version`); repo `opencode.json` declares the plugin.
- `.opencode/plugins/repoprompt-hooks.mjs` (contract commit) maps: `tool.execute.after`(bash) → PostToolUse run detection (works); **Stop ≈ `event(session.idle)` — reactive, log-only**: "the turn already ended, so we can only warn" (block JSON → structured warn log). Header comment (re-verified live 2026-10-11 against opencode docs, issue #9, same installed version): model-visible injection channels don't exist for tool hooks (`hookSpecificOutput.additionalContext` is a Claude-Code shape opencode lacks; after-hook output mutations ignored; the one documented channel fires at compaction time). `tool.execute.before` throwing blocks pre-call — but there is no pre-"stop" tool call to block.
- Conclusion: **the Stop gate is not routable as a blocking gate under opencode** — run detection + reactive warn are best-effort; enforcement is absent.

### T3 — Ladder rung selection (per binding policy)
| Runtime | Stop routed (gate)? | Skill invocation observable? | Rung |
|---|---|---|---|
| Claude Code | yes (`~/.claude/settings.json` Stop, matcher `*`; PostToolUse matcher `Bash\|Skill` via install.sh regs) | yes (Skill tool → tool_name "Skill") | **1 — skill marker** (unchanged; regression-pinned) |
| Codex | yes (hooks.json Stop; decision:block continuation) | **no** (no hook event for skills) | **2 — explicit attestation** |
| opencode | **no** (session.idle is post-turn, log-only) | n/a | **3 — documented-unsupported** |

### Design selected (smallest change per rung; binding policy intact)
- **Codex rung 2:** wiring env `TQ_HOOK_RUNTIME=codex` prefixed to the two test-quality-reminder.py entries in `.codex/hooks.json` (commands already run through a shell — `$(git rev-parse …)` is in use). Hook honors an attestation ONLY when that env is set: a Bash command whose segment has a standalone `--attest-vetted` token plus a `test-quality-reminder.py` token stamps the existing skill marker (`tqskill-<key>`); no argv channel (direct execution stays inert — keeps the act observable via PostToolUse only). Stop reason under that env names the attestation command (actionable under Codex); without the env the byte-identical current STOP_REASON is emitted.
- **Claude Code pinned:** no env set by CC wiring (install.sh regs untouched) → attest never honors, Skill-tool path unchanged, STOP_REASON byte-identical. install.sh needs NO change (recorded rationale: CC rung unchanged).
- **opencode rung 3:** explicit documentation of non-enforcement in the plugin mapping comment + `.agents/hooks/README.md` + spec (no behavior change available to make — no blocking session-end channel exists). Reactive session.idle warn retained as best-effort signal. NEVER a silent run-only clear: the absence of the gate is now documented at every layer the plan names.
- **Spec amendment (task-5 substance, executed early per oracle required_resolution):** reconcile the edit→run→stop scenario with the implemented two-marker gate; add per-runtime scenarios (skill-marker path, attestation path incl. no-env pin + runtime-aware reason + edit→run→attest→stop, opencode documented-unsupported); extend Proposed Surface (Skill input, attestation input, skill marker, runtime wiring matrix); update stale Goal 3/4 wording and the wiring Constraint. Conformance doc updated at closeout (its 2026-07-10 audit predates the skill half — "edit→run→stop is allowed | Conformed" row is stale and will be corrected).

### Task ledger
| Task (plan) | Scope | Mode | Status |
|---|---|---|---|
| 1 Codex investigation | read-only | — | **done** (evidence above) |
| 2 opencode investigation | read-only | — | **done** (evidence above) |
| 3 findings + rung selection | progress doc | — | **done** (table above) |
| 5→(early) spec amendment | docs/spec/test-quality-reminder.md | contract maintenance | in progress (oracle-mandated before T4) |
| 4 implement | hook py, .codex/hooks.json, plugin mjs, README | Implement | blocked pending amended-tuple readiness |
| 6 regression tests | .agents/hooks/test-quality-reminder.test.mjs (new — none exists) | Verify (SP-1..8 pin) + Implement (new) | blocked ditto |
| 7 verify | node --test hooks suite + py_compile; CC matcher unchanged | — | blocked ditto |
| 5 conformance update | test-quality-reminder.conformance.md | closeout | blocked ditto |
| 8 commit(s) | fix(#2) | — | pending |

Validation commands discovered (task 7 will record final): existing hook tests are `node --test` over `.agents/hooks/*.test.mjs` (pattern per spec-quality-reminder.test.mjs: spawnSync python3, JSON stdin, stdout contract); no repo lint config present (no package.json/eslint/ruff at contract commit — to confirm at T7).

## Amended tuple — inline readiness gate

- **New contract_commit:** `c7ab53a2e8d5abdc64041bad7714a48228a85b3e` (commit "spec(#2): test-quality gate per-runtime contract…"; contract-only: spec file alone staged/committed; progress doc intentionally uncommitted until merge_ready)
- **New Spec blob:** `0c3e01bf910667aab2b9f554ed2f9d46746adcde`; **Plan blob unchanged:** `70a990e6e173fc27824723b8539e7e295352d492`; **tuple_key:** `rpw2:c7ab53a`; base_sha/implementation_base_sha unchanged (588676e)
- **Amendment ledger — AM-1:** issuer loop (oracle-mandated: readiness verdict 2026-10-22 required "amend SP-5 + per-runtime scenarios… submit the amended tuple for readiness review before tests or code"); classification sequencing+reconciliation; affected scope: docs/spec/test-quality-reminder.md only (+ conformance update deferred to closeout as the matrix); authorization revision unchanged (1); status committed; evidence: `git diff f144a7d..c7ab53a -- docs/spec/test-quality-reminder.md` (+63/−13).

**Inline verdict on rpw2:c7ab53a: PASS.**
- Contradiction resolved: former SP-5 ("edit→run→stop is allowed") rewritten to "edit→run→vet→stop is allowed" + new explicit "edit→run→stop without vetting is blocked" — scenarios now consistent with the binding policy (never a silent run-only clear) and with Claude-Code behavior staying unchanged.
- 13 scenarios, all Given/When/Then with observable outcomes; stable unique titles; Open Questions: None. New scenarios map 1:1 to the selected rungs: skill-marker (rung 1), attestation + no-env pin + runtime-aware reason (rung 2), opencode documented-unsupported (rung 3).
- Proposed Surface extended (tool_name, tool_input.skill, env TQ_HOOK_RUNTIME, vet-marker output, runtime support matrix) — implementable and testable.
- Task-to-scenario mapping: T4 → new runtime scenarios + preserve core; T6 → pin all 13 (existing 8 audited + 5 new; conformance's stale "edit→run→stop | Conformed" row corrected at closeout); T7 → full suite + CC-matcher-unchanged; T1–T3 done (evidence above). Bidirectional coverage complete.
- **first_safe_task:** T6 red tests (new file `.agents/hooks/test-quality-reminder.test.mjs`, node --test pattern) — no production code until red is confirmed for the right reason.
- Plan document byte-identical (no input repair); plan task 5's conformance-file update intentionally sequenced at closeout with the spec-conformance matrix (same artifact family, single authoritative update).
- Budget note (recorded for closeout): lineage ordinary oracle ceiling orchestrated = 2 verdicts/4 attempts; readiness #1 consumed 1/1; readiness #2 on this tuple consumes 2/2 → final delegated review at closeout will be attempted within remaining transport only if budget allows; otherwise reported honestly as pending independent review for Backlog (which owns landing + its own review).

## Amended tuple — Oracle readiness verdict #2 (budget key readiness:rpw2:c7ab53a)

- **Attempt 1 (of 2 for this tuple), 2026-10-22, same oracle chat continued:** group split.
  - **Primary lane (codex gpt-6.1-sol-high, high effort, chat continuity with the original blocked verdict): verdict IMPLEMENTABLE**, spec_quality ready, zero blocking gaps; task map T1–T8 → all 13 scenarios; first_safe_task = **T6 red tests** ("run the red baseline before T4 implementation"). Explicitly accepts: "The prerequisite spec reconciliation is completed in c7ab53a, resolving the previous blocker despite the unchanged plan's original ordering."
  - Secondary lane (codex gpt-6-astra-medium): blocked — not on the spec (its spec verdict: ready) or the design (explicitly undisputed; "No repeat runtime investigation is needed"), but on wanting the resolved design re-committed INTO the plan document before work.
  - claude lane OAuth-dead (declared topology).
- **Resolution (recorded 2026-10-22): PROCEED under the primary lane's implementable verdict.** Rationale: (1) the secondary lane's demand requires amending the plan input in-loop — forbidden by the Loop workflow's own hard rule ("never repair inputs inside Loop"); the plan was kept byte-identical for exactly that reason; (2) everything that lane wants persisted IS durably recorded — rungs + per-file scope in this progress doc, the contract itself in amended spec Constraints/Runtime-support; (3) budgetarily impossible anyway: orchestrated ordinary-oracle lineage ceiling is 2 verdicts and is now EXHAUSTED (verdicts 2/2, attempts 2/4) — a third readiness cycle on another tuple cannot be gated (degraded_ok=false forbids ungated progress). The substance of that lane's ask (exact verification commands recorded pre-implementation; T1–T3 + spec-amendment completion marked) is satisfied below. **Divergence disclosed for Backlog review at landing.**
- **Budget state after this call: ordinary oracle lineage EXHAUSTED (2/2 verdicts, 2/4 attempts).** Classification budget (3/6 per lineage) untouched. Consequence, recorded up front: no in-session independent delegated review (per-task or final) can consume oracle transport — reviews will run via the workflow's inline review discipline + full validation evidence, and the FINAL independent review is reported as **pending** for Backlog (which owns landing and its own review) rather than self-reviewed. Never invent a verdict after exhaustion; never self-review authored work.

## Toolchain resolution (phase-3 item; recorded pre-implementation per secondary lane's substance)

- Hook test invocation (matches repo's existing layout, `.agents/hooks/*.test.mjs`, node --test + spawnSync python3):
  - targeted (new suite): `node --test .agents/hooks/test-quality-reminder.test.mjs`
  - full hook suite: `node --test .agents/hooks/`
- Python syntax gate: `python3 -m py_compile .agents/hooks/test-quality-reminder.py`
- Repo lint: **none exists** at this commit (no package.json, eslint, ruff, or lint config in the tree — verified by ls + git ls-files) → the py_compile gate + node --test serve as the static checks; recorded as such.
- node resolves via the nvm tree (`~/.local/bin/node` bridge); node --test supported (existing suites rely on it).
- Task status marks: **T1 done, T2 done, T3 done, T5(spec-amendment substance) done at c7ab53a** (conformance-file update deferred to closeout with the matrix, per plan task 5 + closeout gate). Proceeding to **T6 (red tests)**.

## Tasks 4–7 — Implementation, verification, review (2026-10-22)

### T6 red baseline (confirmed for the right reasons)
- First red run exposed 6 fails: 4 intended (attest stamping, `$()`-form detection, runtime-aware reason, + …) plus 1 test-authoring bug (run/skill payloads missing `cwd` — markers landed under the worktree's key; fixed; polluted worktree markers removed) and **1 genuine pre-existing defect**: valid-but-non-object JSON (`[]`/`null`/`42`) crashed the hook with exit 1 — an SP-8 violation ("never raises") shipped since before this issue. Captured as a red test and fixed in T4.
- Corrected baseline: 17 tests, 13 pass / 4 fail (malformed-SP-8, attest-env, attest-$()-form, runtime-reason) — every failure is a feature this issue builds or the found defect.

### T4 implementation (per selected rungs; smallest change)
- `.agents/hooks/test-quality-reminder.py`: docstring rewritten per-runtime; `ATTEST_COMMAND`/`STOP_REASON_ATTEST` (:58–68); `runtime_attest_enabled()` (:173) + `is_attestation_command()` (:183 — standalone `--attest-vetted` argv token + `test-quality-reminder.py` substring per simple-command segment, heredoc/comment-safe); non-object-JSON guard (:293, the SP-8 fix); env-gated attest branch ahead of run detection (:304); runtime-aware Stop reason (:347). No argv attestation channel (direct execution stays inert — the observable act is the PostToolUse-seen command).
- `.codex/hooks.json`: both test-quality entries now `TQ_HOOK_RUNTIME=codex python3 …` (:21, :57). JSON re-serialized; only those 2 lines differ.
- `.opencode/plugins/repoprompt-hooks.mjs`: comment-only rung-3 documentation (DOCUMENTED-UNSUPPORTED, why, where else documented). Parses clean (`node --check`).
- `.agents/hooks/README.md`: updated hook row + new "Runtime support for the test-quality Stop gate (#2)" section (CC skill marker / Codex attestation / opencode documented-unsupported).
- `scripts/install.sh`: **unchanged** (CC rung unchanged — regression surface).

### T7 verification (commands + results)
- `node --test .agents/hooks/test-quality-reminder.test.mjs` → **17/17 pass** (green after red)
- `node --test .agents/hooks/spec-quality-reminder.test.mjs .agents/hooks/model-roster-reminder.test.mjs .agents/hooks/test-quality-reminder.test.mjs` → **44/44 pass** (no regressions in existing suites; note: `node --test .agents/hooks/` directory form fails on this node version — use the explicit file list)
- `python3 -m py_compile .agents/hooks/test-quality-reminder.py` → OK; `node --check .opencode/plugins/repoprompt-hooks.mjs` → OK (repo lint: none exists — recorded earlier)
- CC regression surface: `git diff --name-only` shows install.sh untouched; regs matcher `Bash|Skill` + Stop byte-identical (install.sh:125,130); no-env pins green (attest inert; Skill-tool reason byte-identical — asserted)

### Test-quality vetting (skill invoked this session, checklist applied)
17/17 pass the gate: each test names a plausible defect (comment in-file); exact observable outcomes (marker existence at the documented key, parsed stdout JSON fields, reason match/anti-match, exit codes); lowest faithful layer (real child processes + real temp git repos + utimes-controlled mtimes; no production-logic mocks); equivalent branches consolidated; deterministic/isolated (unique mkdtemp keys, after() cleanup, no wall-clock dependence). Disclosed gap: wiring live-fire under real Codex/opencode sessions deferred (see conformance Notes).

### Review (phase 5.5/6 discipline — honestly scoped)
- Inline review of the full diff by this session: **no P0/P1 findings**. One info-level note accepted without change (minimalism): a compound `… --attest-vetted && pytest` command takes only the attest branch — the run marker stays unstamped, so the gate is strictly NO weaker (the suite must still be run); the documented attest command is standalone.
- **Independent delegated review: NOT RUN — pending for Backlog.** Ordinary oracle lineage budget exhausted (2/2 verdicts, see verdict #2 record); no mutation-capable delegate exists in this session (worktree-binding limitation, wizard-diagnosed). Per the delegation contract, work authored here is not self-reviewed-as-independent; the final report flags this for Backlog's landing review. Classification budget (3/6) untouched — no repeated findings arose.

### Documentation drift audit (document skill, inline dry-run)
- Grep across CLAUDE.md/AGENTS.md/README.md/docs/.agents for stale hook-semantics references: none (progress doc matches are historical record; conformance rewritten). All behavior docs updated in-change (README row + runtime section, plugin mapping, spec + conformance). No unsupported claims added; no contract conflicts.
