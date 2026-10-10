---
title: Live Dry-Run Skill — Conformance
issue: none
spec: live-dryrun.md
audited: 2026-10-10
---

# Live Dry-Run Skill — Conformance Matrix

Implementation audited: `.agents/skills/live-dryrun/SKILL.md` (guidance artifact; evidence = section/line citations). The skill is repo-independent by design — no repo artifacts are part of its surface (per its own Reference section, per-repo procedures live in the repos that own them).

## Matrix

| Section | Item | Status | Evidence | Note |
|---|---|---|---|---|
| Constraints | Read-only by default; consented mutating = one reversible op + restore + disclose | Conformed | `SKILL.md:18` | before-state capture, exercise, restore, verify, disclose residual; "zero net state" only when demonstrated |
| Constraints | Credentials: absolute-path `.env`, never print/commit, rotate captured passwords | Conformed | `SKILL.md:17, 19, 52, 64` | |
| Constraints | Throwaway script (`/tmp`/gitignored, never committed) | Conformed | `SKILL.md:52` | |
| Constraints | Preflight before batch runs | Conformed | `SKILL.md:31–40` | incl. "The preflight stays read-only" (:40) |
| Constraints | No destructive git with uncommitted fixes | Conformed | `SKILL.md:63` | |
| Scenarios | S-001 Fires on dry-run triggers; not UI / not pure logic | Conformed | `SKILL.md:3, 11–14` | description + When-to-run incl. negative cases |
| Scenarios | S-002 Done = live-verified; mocks not proof | Conformed | `SKILL.md:9, 62` | "Never claim 'live-verified' … 'Mocked tests pass' is not verification" |
| Scenarios | S-003 Missing creds reconciled then asked | Conformed | `SKILL.md:17` | determine-actual-requirement first; never silent skip; never claim verified |
| Scenarios | S-004 Throwaway script + absolute-path `.env` + cache off + singleton reset | Conformed | `SKILL.md:52–54` | procedure steps 2–4 |
| Scenarios | S-005 Coverage minimal but sufficient; op classes | Conformed | `SKILL.md:21–28` | "must exercise every live assumption … Cheap is subordinate to coverage"; executed / deferred / not-applicable |
| Scenarios | S-006 Preflight classification | Conformed | `SKILL.md:33–39` | ready / service_unreachable / authentication_rejected (policy inspection before code) / unexpected_contract |
| Scenarios | S-007 Real response printed before mapping; mismatch list | Conformed | `SKILL.md:55–56` | top-level type, keys, lengths, sample item before extraction; diff per op |
| Scenarios | S-008 Pagination probed with natural data | Conformed | `SKILL.md:55` | small page size; honored/clamped/ignored; staging records = mutating op needing consent |
| Scenarios | S-009 Semantic value checks, no both-sides normalization | Conformed | `SKILL.md:42–44` | escaping, timestamp basis, locale, enum casing, nullable-vs-empty; normalization in client only when its contract calls for it |
| Scenarios | S-010 Timeouts sized from measured tails | Conformed | `SKILL.md:46–48` | explicit budgets sized to measured tail; 2–6 s auth vs 5 s default example |
| Scenarios | S-011 Fixes land both sides; re-verify | Conformed | `SKILL.md:57–59` | fix extraction; mocks updated to REAL shapes + `test-quality`; re-run dry-run and suite green |
| Scenarios | S-012 Consented mutating op reversible + restored + disclosed | Conformed | `SKILL.md:18` | |
| Scenarios | S-013 Deferred ops = pending requirements, not evidence | Conformed | `SKILL.md:26–27, 29` | record safe command/prereqs/shape/acceptance; partial live-verified status; never folded in by handing commands over |
| Scenarios | S-014 Unconfirmable shape → unverified | Conformed | `SKILL.md:65` | "mark it unverified and say so; don't guess" |
| Scenarios | S-015 Cross-workspace by absolute path | Conformed | `SKILL.md:70` | read target's memory/procedure by absolute path; root-scoped tooling workaround; or run from target-rooted session |
| Scenarios | S-016 Secrets stay secret | Conformed | `SKILL.md:19, 64` | presence/length/redacted previews only; rotate captured passwords |
| Proposed Surface | Input: Target client + operation list | Conformed | `SKILL.md:51` | procedure step 1 lists ops, picks read-only ones |
| Proposed Surface | Input: Real credentials (repo `.env`) | Conformed | `SKILL.md:17, 52` | |
| Proposed Surface | Input: Consent (mutating ops, per-op) | Conformed | `SKILL.md:18` | |
| Proposed Surface | Input: Target-repo procedure (optional) | Conformed | `SKILL.md:67–68` | repo-owned docs; skill stays repo-independent |
| Proposed Surface | Output: Real-response prints | Conformed | `SKILL.md:55` | |
| Proposed Surface | Output: Mismatch list | Conformed | `SKILL.md:56` | |
| Proposed Surface | Output: Fixed client (incl. sized timeouts) | Conformed | `SKILL.md:46–48, 57` | |
| Proposed Surface | Output: Updated mocked tests (REAL shapes) | Conformed | `SKILL.md:58` | |
| Proposed Surface | Output: Verification status per op | Conformed | `SKILL.md:24–28` | three-class classification |

## Coverage proof

```yaml
audited:
  - Constraints: read-only/consent, credentials, throwaway script, preflight, destructive-git (all 5)
  - S-001 .. S-016 (all scenarios)
  - Surface: Target client+ops, Credentials, Consent, Target-repo procedure
  - Surface: Real-response prints, Mismatch list, Fixed client, Updated mocked tests, Verification status
unreconciled: []
```

Spec-governance constraint (stable `S-NNN` IDs) is satisfied by construction: IDs assigned at authoring (`2506c45`), unchanged since. Every scenario, Proposed Surface element, and behavioral constraint was checked against the skill body; none Diverged or Not-built.
