# Plan — Deterministic track-work CLI adapter (#1)

Derived from `docs/spec/track-work.md` (S-033–S-040 + CLI Proposed Surface, added with this plan).
Spec scenarios S-001–S-032 keep their existing semantics; the CLI is the mechanical executor.

## Design decisions (bounded by the spec, made here)

- **Engine**: one python3 script `scripts/tw.py` in the track-work skill dir (ships with the skill
  through the existing installer; python3 already required by the hooks). POSIX sh stays for
  `issue.sh`. No package.json/pyproject — stdlib only.
- **File backend**: the CLI **wraps `issue.sh`** (subprocess, documented output formats pinned by
  tests) — its confinement/locking/atomicity are adversarially tested and are not reimplemented.
  Redaction runs in the CLI before any body file is written.
- **GitHub backend**: `gh` subprocess with explicit `-R owner/repo` on every repo-scoped call;
  mutations read back and compared; private body staging via `tempfile` (0600) after redaction.
- **Capability probing**: a `--gh` override (test seam) lets the suite inject a fake `gh` shim;
  production path resolves `gh` from PATH. Identity never derives from probe outcomes.
- **Tests**: `scripts/test_tw.py` (unittest, run `python3 -m unittest`) over temp git fixture repos
  + PATH/flag-injected gh shim. Maps every new scenario to at least one adversarial case.

## Ordered tasks

Scope note: scenarios S-001–S-032 are implemented today by the skill + `issue.sh` (per the current
conformance matrix) and get **no new implementation tasks** — T3–T6 adversarially re-cover the
named subset through the CLI path; T7 records the rest as still skill-owned.

- **T1 — Spec extension (landed with this plan).** S-033–S-040, CLI surface table, G8,
  MCP-wrapper non-goal + OQ. File: `docs/spec/track-work.md`.
- **T2 — CLI skeleton.** Envelope emission (one JSON object to stdout), exit codes (0/2/1),
  error taxonomy (`usage`, `origin-rejected`, `capability`, `blocked`, `unknown-label`,
  `cardinality`, `invalid-transition`, `not-found`, `wrong-repository`, `landed-evidence`,
  `conflict`), `--noninteractive`/`TW_NONINTERACTIVE`, dispatch for the six commands (each
  initially failing `blocked:not-implemented`). Tests: envelope/exit-code contract (S-033, S-039).
- **T3 — `resolve`.** Env override (`TRACK_WORK_BACKEND`) → config (`.agents/track-work.config.md`
  fenced yaml subset) → strict origin parse (exact https/git@ github forms; reject userinfo,
  lookalike hosts, multiple push URLs; `github` override requires `github.repo`) → file. Capability
  probes (gh presence/auth/repo view/Issues enabled) reported separately. Tests: deceptive remotes,
  ambiguity rejection, ambient `GH_REPO` irrelevance, probe failure classes, determinism (S-034;
  S-001/S-002/S-003 adversarially).
- **T4 — File backend commands.** `create`/`list`/`status`/`close` over `issue.sh`; deterministic
  redaction (secrets from config/env resolution without printing, absolute paths) before staging;
  close landed-evidence = a referencing commit exists (`git log --grep`) or exempt label. Tests:
  path traversal via `TW_ISSUES_DIR`, symlink refusal, concurrency (parallel creates → unique IDs,
  intact index), redaction determinism (S-036, S-037 partial, S-038 file half).
- **T5 — GitHub backend commands.** `list`/`create`/`status`/`close` with bound `-R`, label
  discovery + cardinality transition (remove conflicting prefix labels + add target, read back),
  `unknown-label` refusal, private staging, `wrong-repository` read-back check, close ancestry via
  `gh api` (commit on default branch or merged PR). Tests: hostile `GH_REPO`, wrong-repo shim,
  auth/network/permission shim failures, cardinality read-back, body isolation under concurrency
  (S-035, S-037 GitHub half, S-038 GitHub half, S-039).
- **T6 — `migrate`.** Journal at `docs/track-work-migrations/<ts>.md` written+committed before any
  mutation; rows `pending/created/verified` with `Migrated-from:` markers; `--status` prints row
  states; resume skips verified, re-checks created; `--retire-source` separate confirmation;
  dual-ledger prevention (existing items searched before create). Tests: partial-failure journal
  fixture → resume without duplicates; retirement gating (S-040, S-014 mechanics).
- **T7 — Integration flip.** SKILL.md: workflows drive `tw.py` (prompt keeps judgment: classify,
  dedup signature, triage; mechanics go to the CLI); Backlog.md status-authority note; hooks
  README/README toolchain lines; conformance matrix regenerated for S-033–S-040 **and the
  pre-existing G6/S-024 matrix gap repaired**; `docs/spec/README.md` row untouched (spec exists).
  `issue.sh` remains (CLI depends on it; skill documents it as the file engine).

## Risks / rollback

- `gh` output drift → read-backs compare parsed fields, shim tests pin shapes; wrapper stays thin.
- `issue.sh` output parse drift → formats pinned by `test_tw.py` + `test_issue.sh` unchanged.
- Backlog mid-transition breakage → CLI lands additive (T2–T6 change no consumer), flip is one
  commit (T7) revertable in isolation.
- Rollback: revert the implementation commit(s); spec scenarios are additive and harmless if
  unimplemented temporarily (conformance matrix records Not-built until T7).

## Toolchain

- Run tests: `python3 -m unittest discover -s .agents/skills/track-work/scripts -p 'test_tw.py'`
  (plus existing `sh scripts/test_issue.sh` for the file engine).
- Verification loop per task: targeted unittest → full tw suite → `test_issue.sh` → node hook
  suites (unchanged paths must stay green).

## Progress ledger (updated 2026-10-23)

- **T1 done** — spec S-033–S-040 + CLI surface + this plan: `8e99f3b`
- **T2 done** — skeleton, envelope/exit contract, 10 tests: `7108ca7`
- **T3 done** — resolve (identity ladder, capability probes, 22 adversarial tests,
  32/32 total): `2ee9b64`
- **T4 done** — file backend over `issue.sh` (create/list/status/close, redaction,
  S-037 file half, S-038 file half; engine gained `new --body-file` + `mkdir -p`
  race fix; 63/63, all four new guards mutation-verified): `fbe64f2`
- **T5 next** — GitHub backend commands (bound `-R`, cardinality transitions,
  wrong-repository, close ancestry).
- All commits LOCAL on main; origin/main sits at `badf779` — the user wants one
  batched push later (ask before pushing).

Operational notes for the implementing session (lessons already paid for):

- Commit immediately after a slice goes green — never hold uncommitted work while
  experimenting on the same files.
- Never mutation-test via `git checkout --` restore on uncommitted files (a prior
  session wiped T3 that way); mutate a COPY, or commit first.
- Write large new file content via Bash heredocs; two `apply_edits` calls with big
  payloads corrupted mid-flight earlier in this work.
- Verification loop: `python3 -m unittest discover -s .agents/skills/track-work/scripts
  -p 'test_tw.py'` → `sh .agents/skills/track-work/scripts/test_issue.sh` →
  `node --test .agents/hooks/*.test.mjs` (all green before commit).
- Mutation-verify with `… discover -s … -k <test_name>` — running
  `python3 -m unittest test_tw.Class.test` from the repo root import-fails
  (ModuleNotFoundError) and every mutation "kills" vacuously; that is not
  verification. Always inspect the failure is the intended assertion.
- `apply_edits` intermittently fails `ownershipLost` on this repo; the working
  fallback is a Bash python exact-replace with `assert count == 1` guards.
- macOS fixtures: the canonical repo root is `/private/var/...` while
  `tempfile` hands back `/var/...` — derive fixture repo-root paths via
  `git rev-parse --show-toplevel` when testing repo-root stripping.

## First safe task

T2 (skeleton, no consumer, no mutation paths wired) — DONE; see ledger.
