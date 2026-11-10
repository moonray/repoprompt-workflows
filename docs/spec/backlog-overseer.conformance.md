# Spec Conformance — Backlog-Overseer Workflow

- **Spec:** `docs/spec/backlog-overseer.md` (Backlog-Overseer Workflow)
- **Implementation:** `.agents/workflows/Backlog-Overseer.md`
- **Audited:** 2026-11-10
- **Method:** one row per scenario and atomic Proposed Surface field/enum/constraint; evidence uses workflow line ranges; where available, behavioral evidence cites the 2026-11-09 first run (`docs/progress/backlog-2026-11-09.md` in keryxsolutions) and its probe record (`docs/progress/backlog-overseer-probe.md`).

## Matrix

| Item | Status | Evidence |
|---|---|---|
| S-101 Settings resolve at launch, before any mutation | Conformed | `.agents/workflows/Backlog-Overseer.md:18-45,62-66` (parse-or-block + Phase 0.1 first). Behavior: 2026-11-09 run resolved empty `go` → all DEFAULTS and persisted the run doc before any mutation (`backlog-2026-11-09.md` Phase 0.1) |
| S-102 An empty launch is non-publishing | Conformed | `:22` (Git-visible settings NOT auto-applied), `:24-42` (DEFAULTS table). Behavior: run completed with zero push/PR/merge/status-change; five branches left local-only (`backlog-2026-11-09.md` rollup) |
| S-103 Authorization is persisted, user-owned, and never self-minted | Conformed | `:45` (Authorization framing), `:145-147` (amendments explicit-user-only). Behavior: run declined the oracle's suggestion to self-issue revision 2 (`backlog-2026-11-09.md` rollup, recording-correction note) |
| S-104 Zero routine asks | Conformed | `:49` (touchpoint list), `:84` (Phase 2 nothing to ask), `:149-153` (ladder). Behavior: run's only touchpoints were the scope card and the operator-attended probe |
| S-105 Substrate selection is evidence-driven with a complete fallback | Conformed | `:51` (wake-mode preconditions + complete fallback definition + substrate notes). Behavior: run degraded to fallback with v1 waits/teardown after probe failure. *Wake-mode branch awaits behavioral evidence from the first successful re-probe* |
| S-106 The probe ends no turn before verification | Conformed | `:72-77` (0.4: in-turn probe completion, operator-attended wake test, record fields). *Behavioral evidence pending first successful re-probe (2026-11-09 probe was denied before the wake test)* |
| S-107 Placement-denied scopes degrade without in-grant retry | Conformed | `:70` (placement-unresolved playbook). Behavior: denial, inventory check, release, fallback, `probe: fallback` record with evidence, operator recovery disclosed (`backlog-overseer-probe.md`; `backlog-2026-11-09.md` substrate record) |
| S-108 Grants are verified against the request | Conformed | `:68` (verify-the-grant paragraph). Behavior: run recorded the unrequested `destructive` capability verbatim, disclosed it, never used it |
| S-109 Lanes are link-confirmed before a turn ends | Conformed | `:54` (lane-link invariant), `:119` (§3c.6 confirm step). *Behavioral evidence pending wake-mode run* |
| S-110 Wake events route by type | Conformed | `:121-131` (event handler table + verify beats). *Behavioral evidence pending wake-mode run; fallback-path equivalents exercised 2026-11-09 (verify → close → capacity → refill in-run)* |
| S-111 Live wake confirmation — backstop-only arrival is failure | Conformed | `:52` (first-report-as-confirmation clause). *Behavioral evidence pending wake-mode run* |
| S-112 Capacity is released per completed issue | Conformed | `:55` (guardrail ceiling: live allocations, checkpoint on exhaustion), `:133` (capacity release order + supersession note), `:166` (teardown order). Behavior (fallback analog): merged-path probes cleaned per issue; retained worktrees disclosed and counted |
| S-113 Session history is retained | Conformed | `:51` (dismissal terminal, retention verified 2026-11-09), `:166` (never recommend deletion). Behavior: dismissed lanes verified fully indexed in session history (keryx84/keryx82 E1 lanes, 2026-11-10 check) |
| S-114 Non-primary-root issues route serialized in-checkout | Conformed | `:56` (known RPCE limit + routing). Behavior: rpw #19/#17/#18 and website #5/#7 routed branch-in-checkout single-flight (`backlog-2026-11-09.md` route decision + ledger) |
| S-115 Triage excludes blocked, invalid, and decision items | Conformed | `:82` (Phase 1 exclusions). Behavior: keryx#6 excluded (blocked); #73/#1 routed as decisions; in-progress/review items of other actors excluded |
| S-116 Conservative escalation blocks oracle-decidable ambiguity | Conformed | `:152` (ladder rung 2). Default-autonomous branch exercised 2026-11-09 (route decision, amendment ratifications); conservative branch text-conformed only |
| S-117 Resume re-probes a re-granted scope and re-checks the wedge | Conformed | `:156-158` (resume: re-grant → re-probe, wedge-absence check, attempt counts, ff-sync). Behavior: fallback-path resume elements exercised in prior v1 runs (inherited); re-probe limb pending a wake-mode resume |
| S-118 Contract generation is dispatch-sized | Conformed | §3a amendment (2026-11-10): effort-sized contract-lane dispatch (Spec/Deep Plan via `workflow_name`) for medium/large, inline allowed for small; three-way separation; readiness tuple unchanged. Anti-pattern row guards the inline path. *Behavioral evidence pending the first medium/large generation after this amendment — the 2026-11-09/10 runs authored inline under the pre-amendment text* |

### Proposed Surface coverage

| Surface element | Status | Evidence |
|---|---|---|
| Launch Contract (`$ARGUMENTS` keys + DEFAULTS table) | Conformed | `:18-45` (grammar `:43`, defaults `:24-42`); S-101/S-102 rows |
| Authorization Revision fields | Conformed | `:45`; S-103 row; behavior in run doc revision block |
| Oversight Grant (capabilities, guardrails, verbatim record) | Conformed | `:68`; S-105/S-108 rows |
| Probe Record fields | Conformed | `:72-77`; artifact exists at `docs/progress/backlog-overseer-probe.md` (keryxsolutions) with all fields |
| Lane Brief fields | Conformed | `:104-118` (dispatch JSON); exercised on every 2026-11-09 dispatch |
| Contract Lane (dispatch type, effort sizing) | Conformed | §3a amendment text + S-118 row |
| Event Handler Table | Conformed | `:121-131`; S-110 row |
| Capacity Release order | Conformed | `:133`; S-112 row |
| Teardown Order | Conformed | `:166`; S-112/S-113 rows |
| Run Progress Doc fields | Conformed | `:62-66,141-143,160-165`; artifact `backlog-2026-11-09.md` carries all listed fields |
| Gates (inherited) | Conformed | `:57-58,90-96,137-139` + `docs/spec/backlog.conformance.md` (inherited rows); verify beats exercised on all four implemented issues 2026-11-09 |

### Inheritance and supersession

| Backlog (v1) scenario | Status | Disposition |
|---|---|---|
| S-003 exempt batch in wizard | Superseded | By S-101/S-102/S-115: exempt-close executes only when `close=auto` is explicitly named (`:42,82`) |
| S-004 wizard is the only solicited ask | Superseded | By S-104: no wizard exists; naming git-visible settings in `$ARGUMENTS` is the ask (`:22,49`) |
| S-014 at most three in flight | Superseded | By S-105/S-112: pace (default 1, ceiling 3) enforced via scope guardrails on live allocations (`:55`) |
| S-055 deferred-cleanup limb | Superseded | By S-112: per-issue capacity release after verify+close+land (`:133`); resume/replacement limbs inherited via `:145-147,156-158` |
| All other v1 scenarios (S-001–S-059 not listed above) | Inherited | Restated in the v2 workflow at `:50` (status authority), `:57-60` (invariants), `:90-96` (contract prep/readiness), `:98-119` (dispatch/reconciliation incl. wedge `:113-115`), `:121-135` (verify/liveness), `:137-139` (close/merge), `:156-158` (resume); conformance detail in `docs/spec/backlog.conformance.md` |

## Coverage proof

- **audited:** S-101, S-102, S-103, S-104, S-105, S-106, S-107, S-108, S-109, S-110, S-111, S-112, S-113, S-114, S-115, S-116, S-117, S-118; every Proposed Surface element (11); v1 supersession set (4) and inherited remainder (by reference to `docs/spec/backlog.conformance.md`)
- **unreconciled:** [] — with disclosed annotations: wake-mode behavioral evidence (S-105 wake branch, S-106 wake test, S-109, S-110 wake routing, S-111, S-117 re-probe limb) is pending the first successful re-probe; the workflow text fully implements each and the fallback paths carried the 2026-11-09 run end-to-end.
