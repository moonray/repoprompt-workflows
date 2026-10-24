# Spec Conformance — Track Work Skill

- **Spec:** `docs/spec/track-work.md` (Track Work Skill)
- **Implementation:** `.agents/skills/track-work/SKILL.md` (judgment layer), `scripts/tw.py` + `scripts/test_tw.py` (deterministic CLI), `scripts/issue.sh` + `scripts/test_issue.sh` (file engine), and `scripts/place_on_board.sh`
- **Audited:** 2026-10-24
- **Method:** each goal, stable scenario, and Proposed Surface element mapped to the skill/CLI/engine; evidence names the implementing section, function, or test class.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| G1 one work item per unit in one place | Conformed | Intent; Step 0 prevents capability failure from creating a second ledger; CLI refuses file fallback for a GitHub identity (`TestGithubCapability.test_gh_missing_never_creates_a_file_ledger`) |
| G2 deterministic backend identity and repo taxonomy | Conformed | Step 0 selects override/origin identity before capability; Step 1 and GitHub step 0 govern taxonomy; `tw.py:_resolve_identity`/`_parse_origin` (`TestResolve`) |
| G3 entry gate before any work | Conformed | Intent entry-gate statement; GitHub and file workflows |
| G4 link detail rather than duplicate narrative | Conformed | GitHub step 4; body template |
| G5 lifecycle; close means landed on default | Conformed | Status lifecycle; Closing; `cmd_close_file`/`cmd_close_github` landed-evidence checks (`TestFileClose`, `TestGithubClose`) |
| G6 workspace-level questions span every repo | Conformed | SKILL.md "Workspace scope — multi-repo fan-out": enumerate the repo set before querying, per-repo backend selection, per-repo binding with repo-labeled aggregation, unreachable ledgers reported as gaps; consumed by the `triage-work` skill (gap repaired this audit — see Notes) |
| G7 creation-time triage baseline | Conformed | Triage (creation-time rules) section: entry states, priority defaults, decision routing, signature dedup |
| G8 deterministic CLI executor | Conformed | `tw.py` implements `resolve`/`list`/`create`/`status`/`close`/`migrate`; one JSON envelope per invocation, typed errors, exit 0/2/1; the skill's "The CLI is the mechanical executor" section routes mechanics through it while keeping judgment in the prompt (`TestEnvelopeContract`, full `test_tw.py` suite) |
| S-001 backend follows durable repository identity | Conformed | Step 0 selection order; `tw.py:_resolve_identity` ladder with capability never participating (`TestResolve`) |
| S-002 GitHub capability failure stops | Conformed | Step 0 stop-before-write rule; `_probe_capability` + `_capability_stop` with no file fallback (`TestGithubCapability`) |
| S-003 disabled Issues requires explicit choice | Conformed | Step 0 treats `hasIssuesEnabled=false` as a stop; probe class `issues-disabled` (`test_issues_disabled_stops_without_fallback`) |
| S-004 conventions and GitHub labels discovered | Conformed | Step 1; `gh label list` authority (`_gh_labels`); config dimensions for the file backend |
| S-005 tracking item precedes work | Conformed | Intent entry gate; Do/Don't |
| S-006 search before create | Conformed | GitHub step 2 (via `tw list`, judged by review signature); migration marker search (`_migrate_dest_search_*`) |
| S-007 label cardinality without surprise mutation | Conformed | GitHub step 0 confirmation before seeding; `_check_cardinality` + `_validate_gh_labels`/`_validate_file_labels`; no implicit label creation |
| S-008 detail files linked, not duplicated | Conformed | GitHub step 4; body template |
| S-009 file items use immutable IDs in committed backlog | Conformed | File backend workflow; engine ID allocation (`next_id`), index sync, gitignore warning |
| S-010 close means landed on default | Conformed | Closing; `cmd_close_*` verify referencing commit/merged PR or exempt label before mutating (`TestFileClose`, `TestGithubClose`) |
| S-011 secrets and local paths redacted | Conformed | Privacy/redaction section (judgment) + `_redact` on every write path incl. titles, bodies, close reasons; public visibility tightens to placeholders (`TestFileCreate` redaction tests) |
| S-012 configured optional GitHub features | Conformed | GitHub step 5; persona handling |
| S-013 backend selection observable | Conformed | Step 0 envelope reporting; `cmd_resolve` returns backend/selected_by/target/capability; deterministic output test |
| S-014 migration journaled and recoverable | Conformed | Ledger migration steps + `cmd_migrate`: committed journal before mutation, source revisions, idempotency markers, read-back-advanced rows, resumability, separate retirement confirmation (`TestMigrate`) |
| S-015 GitHub operations bound to canonical repo | Conformed | Step 0 normalizes exact origin forms; every `gh` call in `tw.py` carries explicit `-R`; `_gh_url_repo` read-back checks; Project helper requires canonical issue URL |
| S-016 file operations confined/serialized/atomic | Conformed | `issue.sh` validates IDs/scalars/path, rejects symlinks (dir, item, body), locks mutations, atomically renames same-directory temporaries; `tw.py:_run_issue` maps engine refusals to typed errors; `test_issue.sh` + `TestFileConfinement` |
| S-017 full lifecycle on both backends | Conformed | `cmd_status_file`/`cmd_status_github` (blocked bookkeeping via engine `previous_status`/explicit targets), open = every non-closed state in `cmd_list_*`; close only via `close` (`TestFileStatus`, `TestGithubLabels`) |
| S-018 private isolated body staging | Conformed | `_stage_body` (0600 uniquely named temp, guaranteed cleanup) after `_redact`, on both backends and migration; concurrent agents cannot exchange bodies (`TestFileConcurrency`, `TestGithubBodies`) |
| S-019 unattended callers never prompt | Conformed | Caller mode section; `--noninteractive`/`TW_NONINTERACTIVE` → `blocked` on confirmations and capability failures, no mutation (`TestNoninteractiveMode`, `TestGithubCapability`, `test_interactive_migrate_blocks_without_journal`) |
| S-020 Tracked means explicitly owned | Conformed | SKILL.md Do/Don't ("verify explicit ownership before claiming work is tracked") |
| S-021 Ledger rereads at commitment boundaries | Conformed | SKILL.md Do/Don't (re-read at commitment boundaries); `cmd_status_*`/`cmd_close_*` re-read state at the boundary and read back after mutating |
| S-022 Mitigated is not fixed | Conformed | SKILL.md Do/Don't ("track the root defect, not only the mitigations") |
| S-023 Local personal exposure requires confirmation | Conformed | SKILL.md Do/Don't (interactive confirm / noninteractive blocked-pending) |
| S-024 workspace fan-out enumerates before querying | Conformed | SKILL.md "Workspace scope" bullets: repo set enumerated before any ledger query, per-repo binding, repo-labeled aggregate, gaps reported, only explicit user narrowing reduces the set (gap repaired this audit — see Notes) |
| S-025 decisions route to humans at creation | Conformed | Triage — "Decisions route to humans" bullet |
| S-026 birth states draft/backlog only | Conformed | Triage — "Birth states" bullet; `tw create` always births draft (engine frontmatter); migration destination items born draft with source status in the row note |
| S-027 batch items carry parent link | Conformed | Triage — "Batch/summary items carry a parent link" bullet |
| S-028 priority defaults by finding kind | Conformed | Triage — priority defaults table + `triage.priority_defaults` config override |
| S-029 signature dedup before create | Conformed | Triage — "Dedup by signature before create" bullet; GitHub step 2 runs on the signature |
| S-030 atoms named not restated | Conformed | Triage intro names the four atoms with the `.agents/rules/global.md` pointer |
| S-031 per-repo triage config override | Conformed | Config schema `triage:` block; "When to add a config" `triage` row |
| S-032 consumption triage unchanged | Conformed | Triage boundary sentence names Backlog Phase 1 + triage-work; section contains no consumption-time logic |
| S-033 CLI emits one machine-readable envelope | Conformed | `tw.py:main`/`envelope`; exactly one JSON object on stdout, exit 0/2/1; unexpected internal errors still emit a typed envelope (`TestEnvelopeContract`) |
| S-034 resolve reports identity and capability separately | Conformed | `cmd_resolve` (backend/selected_by/repo/issues_dir/capability); identical inputs → identical envelopes (`TestResolve`, incl. deceptive remotes, ambiguity rejection, ambient `GH_REPO` irrelevance) |
| S-035 mutations bound and read back from one repository | Conformed | explicit `-R` on every repo-scoped call; `_gh_url_repo` read-back verification failing `wrong-repository`; cross-repo refs rejected pre-mutation (`TestGithubBinding`, argv-log proven under hostile `GH_REPO`) |
| S-036 redaction mechanical on the write path | Conformed | `_redact` before any staging on titles/bodies/reasons; envelope reports applied classes; no unredacted staged copy survives (`test_create_redacts_before_staging_and_cleans_up`, `test_redaction_is_deterministic`, `test_public_visibility_tightens_path_redaction`) |
| S-037 labels cardinality-safe and verified | Conformed | `_validate_file_labels`/`_validate_gh_labels` (`unknown-label` with proposal, no implicit creation); status transition = one `issue edit` removing conflicting prefix labels + adding target, label set read back (`TestGithubLabels`, `TestFileCreate` label tests) |
| S-038 close refuses without landed evidence | Conformed | `cmd_close_file` (digit-bounded `ISSUE-NNN`/`ISSUE-N` commit reference or exempt label), `cmd_close_github` (default-branch commit via bounded `gh api` walk, merged PR, exempt label); `status` cannot set closed (`TestFileClose`, `TestGithubClose`) |
| S-039 noninteractive blocks instead of prompting | Conformed | `_capability_stop` (blocked noninteractive / capability interactive); migrate refuses interactively without creating a journal; no invocation waits on stdin (`TestNoninteractiveMode`) |
| S-040 migration resumes without duplicates | Conformed | `cmd_migrate` journal machinery: verified skipped, created re-checked via marker only, verified after read-back, sources preserved on failure, retirement separate (`TestMigrate`, incl. partial-failure resume and marker-dedup) |
| Surface inputs | Conformed | Step 1 request and repo conventions |
| Surface outputs item, links, status, backend | Conformed | Body template; lifecycle; envelope fields (`item`, `labels`, `redaction`, `evidence`, `backend`) |
| Surface CLI: resolve row | Conformed | `cmd_resolve`; `TestResolve` |
| Surface CLI: list row | Conformed | `cmd_list_file`/`cmd_list_github` (items[] with id/title/status/labels/repo; `--status`/`--label` filters; bad scope `not-found`); `TestFileList` |
| Surface CLI: create row | Conformed | `cmd_create_file`/`cmd_create_github` (item id/path or number/url, applied labels, redaction summary; `unknown-label`/`cardinality`); `TestFileCreate`, `TestGithubBinding` |
| Surface CLI: status row | Conformed | `cmd_status_file`/`cmd_status_github` (`from`→`to`, labels read back; `invalid-transition` incl. closed; `not-found`); `TestFileStatus`, `TestGithubLabels` |
| Surface CLI: close row | Conformed | `cmd_close_file`/`cmd_close_github` (closed item + the evidence check that passed; `landed-evidence`/`not-found`); `TestFileClose`, `TestGithubClose` |
| Surface CLI: migrate row | Conformed | `cmd_migrate` (journal path + row states; `blocked`, journal write failure → typed error); `TestMigrate` |

## Coverage proof

- **audited:** Goals 1–8; S-001–S-040; Proposed Surface inputs, outputs, and all six CLI table rows; all three helper scripts and both test suites
- **unreconciled:** []

## Notes

The 2026-07-14 re-audit admitted the executable helpers after adversarial review; the 2026-10-22 re-audit added the creation-time Triage contract (G7; S-025–S-032) and disclosed — rather than repaired — a pre-existing matrix gap: the spec carried G6 and S-024 with no matrix rows. **This audit repairs that gap** (both rows above, evidenced by the skill's "Workspace scope" section and its consumption via triage-work) and adds the CLI surface (G8; S-033–S-040 plus the six CLI rows), implemented by `scripts/tw.py` per plan `docs/plans/track-work-cli.md` (#1, T2–T7). The 2026-10-23 scope disclosure (matrix covered the skill surface only while the CLI was in progress) is closed by this audit: the matrix now covers spec, skill, CLI, engine, and both suites.

Division of labor after the T7 flip: the skill text carries judgment (classification, signature dedup, triage, confirmations, body composition, what to redact *into* scope); `tw.py` carries mechanics (identity, binding, redaction execution, staging, label transitions, landed evidence, journals); `issue.sh` remains the file engine the CLI wraps. Label seeding, persistent overrides, migration, and source retirement still require explicit authorization; unattended callers block instead of prompting.
