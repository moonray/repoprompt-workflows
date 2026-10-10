# Conformance: chat-mining spec vs implementation

**Spec:** `docs/spec/chat-mining.md` · **Audited:** 2026-10-07, post-#46 implementation · **Audited at:** the #46 commits (skill/ledger/spec/plan)

## Scenario matrix

| Scenario | Verdict | Evidence |
|---|---|---|
| S-001 trigger / exclusion | Conformed | Skill description carries the trigger examples and the "Not for reading one specific session's log to resume work" exclusion; discriminated live by the 2026-10-07 #42 validation probe (positive + negative controls both answered from the description). |
| S-002 scope | Conformed | Skill step 1 (one-workspace vs ALL-workspaces for cross-cutting processes); exercised by today's keryxsolutions run and the cross-workspace Indy sweep. |
| S-003 watermark | Conformed | Skill step 1 "Watermark first (S-003)" (read marker, candidates-newer-than, scope labeling) + step 5 "advance … only on a completed sweep"; ledger exists at `.agents/mining-ledger.md` seeded with three runs. Probe quoted both clauses verbatim. (Spec amended 2026-10-07 post spec-quality audit: "successful close" now defined — declared scope fully processed.) |
| S-004 deterministic pre-pass | Conformed | Skill step 2 "rank the candidates WITHOUT transcript reads first (S-004)" with the four named signals; explicitly heuristic-for-ordering, never findings. Probe restated all four. (Spec amended post-audit: signals framed as examples of the contract — metadata-only ranking before any transcript read.) |
| S-005 sweep terms + final-turn-first | Conformed | Skill step 2 carries retrospective + decision + friction term lists, the structural-friction layer (repeated failed calls, re-reads, suite re-runs, regenerations, high turn/small diff), and the "FINAL turn … first" instruction. (Spec amended post-audit to include the structural layer, closing a coverage gap against the skill.) |
| S-006 ground-truth verification | Conformed | Skill step 3; the 2026-10-07 run's core activity (every candidate checked against issues/code/git; already-landed section in its report). |
| S-007 friction discriminator | Conformed | Skill step 3 path-not-outcome + durable-artifact test with the irreducible-discovery carve-out. |
| S-008 durable homes + scope ladder | Conformed | Skill step 4 with the explicit ladder (repo-local docs → shared skill/workflow in the matching shared repo — public machinery repo for generic/public, the org repo for org-specific — → `global.md` last) and repo-independence hard rule; exercised by #42's landing decisions (G3/G4 folded to skills). |
| S-009 retention | Conformed | Skill step 5 retention map + issue-filing sentence; exercised by #42/#44/#45 filings from the 2026-10-07 run. |
| S-010 report shape | Conformed | Skill step 6 (ranked, status labels, already-landed section, user-gated separate); matches the 2026-10-07 report's actual shape. |
| S-011 subagent validation w/ negative controls | Conformed | Applied-changes requirement in the #42 draft's application requirements (binding) + both 2026-10-07 probes (skills/rules probe and cycle-update probe) ran with negative and fabrication controls, read-only, reports verified via verbatim-quote spot-checks. |
| S-012 cadence | Conformed | Skill step 5 cadence status + ledger `next-due` column + the no-auto-start design ("Use when asked"); probe's negative control confirmed no automatic-run authorization exists. (Spec amended 2026-10-07 at session close: surfacing rides mining-run reports + open issues in the briefing's existing Project-work sweep — no dedicated briefing wiring; the original conformance row overclaimed that half.) |

## Proposed Surface matrix

| Element | Verdict | Evidence |
|---|---|---|
| `.agents/skills/chat-mining/SKILL.md` | Conformed | Exists canonically, README-indexed, runtime-symlinked (created #42, updated #46). |
| `.agents/mining-ledger.md` | Conformed | Created with the S-003/S-012 columns (workspace, mined-through, scope, recorded, next-due, notes); seeded with three runs, historical markers labeled attested. |
| Deterministic pre-pass | Conformed (as skill-specified signal list) | The spec's metadata-based ranking; a standalone script is deliberately deferred (plan's deferral note) — not a divergence: S-004 contracts the ranking, not an implementation artifact. |
| Report | Conformed | Step 6 contract; matches the run reports produced 2026-10-07. |

## Coverage proof

- **audited:** S-001..S-012 (all scenarios), all four Proposed Surface elements, trigger/description surface.
- **unreconciled:** [] (none).
