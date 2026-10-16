---
title: Triage Work Skill — Conformance
issue: 11
spec: triage-work.md
audited: 2026-10-16
---

# Triage Work Skill — Conformance Matrix

Implementation audited: `.agents/skills/triage-work/SKILL.md` (guidance artifact; evidence = section/line citations), deployed to runtime discovery dirs via `scripts/install.sh` (symlinks verified `~/.claude/skills/triage-work`, `~/.agents/skills/triage-work` → canonical copy).

## Goals

| Goal | Verdict | Evidence |
|---|---|---|
| G1 repeatable ritual over full scope | Conformed | SKILL.md `## Intent` (8–12), `### 1` (16–20): fan-out per track-work, bodies mandatory, gaps stated |
| G2 evidence-driven mutation | Conformed | `### 2` (22–32): claim-vs-evidence rule, verification classes, comms grounding; `### 3` (34–39): evidence-in-close-out, commitment-boundary re-read |
| G3 explicit disposition + autonomy + intent | Conformed | `### 4` (41–43) intent verdicts; `### 5` (45–54) autonomy classes; Do/Don't (71–79) |
| G4 human authority preserved | Conformed | `### 3` judgment calls flagged; `### 5` decision rollup never auto-resolved; `### 4` never auto-close; Do/Don't (75–77) |
| G5 decision-ready output | Conformed | `### 6` (56–63) rubric + axes; `### 7` (65–69) report shape, quick wins, pick, hand-off |

## Scenarios

| Scenario | Verdict | Evidence |
|---|---|---|
| S-001 triage-shaped requests trigger; adjacent do not | Conformed | Frontmatter description (3): trigger phrases enumerated; exclusion clauses for track-work filing/intake, Backlog execution, mail/message triage |
| S-002 fan-out incl. cross-ledger; gaps reported | Conformed | `### 1` (16–20): external ledgers named/pinned, per-repo backend, diagnostics, "stated gap… never a silent omission" |
| S-003 body-grounded gathering | Conformed | `### 1` (18–20): "with full bodies", labels-carry-taxonomy-not-substance rationale, dimensions discovered per repo |
| S-004 ground-truth verification precedes mutation | Conformed | `### 2` (22–32): "verified this run" demand quoted, four verification classes + external-party comms grounding, disposition cites verification |
| S-005 evidence-verified closure + boundary re-read | Conformed | `### 3` close bullet (36): own-gate evidence (SHA, green-run list, soak, elapsed box), shared-ledger reconciliation |
| S-006 dedup folds nuance first | Conformed | `### 3` dedup bullet (37): fold-then-close, cross-link, "a bare close loses content" |
| S-007 taxonomy repair applied-or-flagged | Conformed | `### 3` repair bullet (38): clear-cut direct with why; judgment calls flagged and held |
| S-008 reserved follow-ups filed; no speculative stubs | Conformed | `### 3` follow-up bullet (39): reserved follow-up filed; trigger-note instead of stub |
| S-009 autonomy classification gates rankability | Conformed | `### 5` (45–54): four enumerated classes, derived-from-verified-state rule, "Only `autonomous` items are rankable" |
| S-010 decisions route to human rollup | Conformed | `### 5` (51–53): decision rollup with context, never spec/implement/relabel/close |
| S-011 default rubric mirrors Backlog Phase 1 | Conformed | `### 6` (58): bugs → p0–p3 → ease, "the same order Backlog's Phase 1 uses" |
| S-012 ease axis separates gated from sized | Conformed | `### 6` ease bullet (60–61): label-grounded-by-body, gated items listed separately with reason |
| S-013 parallel-safety axis | Conformed | `### 6` parallel bullet (62–63): overlap zone (theme/files/checkout; shared-checkout rule), in-flight exclusion, external-system safest, coordination points, not-tackleable |
| S-014 decision-ready report + hand-off + write-back | Conformed | `### 7` (65–69): full report shape, quick wins, pick/pairing, start-or-Backlog offer, audit-trail write-back |
| S-015 intent validation | Conformed | `### 4` (41–43): anchor source named in report, three-verdict enum, flagged section with conflict + recommended resolution, held out of ranking, never auto-closed |

## Proposed Surface

| Surface element | Verdict | Evidence |
|---|---|---|
| `.agents/skills/triage-work/SKILL.md` procedure | Conformed | The audited file itself; model-invoked via frontmatter description |
| Ledger operations via track-work only | Conformed | Description (3) "All ledger access flows through track-work"; `### 1` (17) delegates fan-out to track-work's section; Do/Don't (72) |
| Report (chat-delivered) shape | Conformed | `### 7` (65–69) enumerates every report element contracted in the spec |
| Audit-trail comments | Conformed | `### 7` (69): what/when/verdict comments, comms corrections, decision context left on items |

## Coverage proof

- **Audited:** Goals G1–G5, Scenarios S-001–S-015, all four Proposed Surface elements, Non-Goals (Intent ¶2 + description exclusions state the Backlog/track-work/mail boundaries), Context/Traceability (spec-internal).
- **Unreconciled:** `{}` — no Diverged or Not-built items.
