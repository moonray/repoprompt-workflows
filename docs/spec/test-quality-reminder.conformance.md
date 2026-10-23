# Spec Conformance — Test Quality Reminder Hook

- **Spec:** `docs/spec/test-quality-reminder.md` (amended at c7ab53a — per-runtime contract, issue moonray/repoprompt-workflows#2)
- **Implementation:** `.agents/hooks/test-quality-reminder.py` + wiring (`.codex/hooks.json`, `.opencode/plugins/repoprompt-hooks.mjs`, `scripts/install.sh` for Claude Code)
- **Audited:** 2026-10-22 (Loop rpw2 epoch L2-E2)
- **Method:** every Goal + scenario + Proposed Surface element mapped to its realization; evidence = `file:line` / branch + the covering test in `.agents/hooks/test-quality-reminder.test.mjs` (17 tests, all green in the full hook suite, 44/44).

## Matrix

| Section | Item | Status | Evidence |
|---|---|---|---|
| Goals | G1 detect genuine runs, ignore non-command-position runner words | Conformed | `is_test_run_command` (test-quality-reminder.py:161) + `_segment_tokens`/`_strip_heredocs`/`_subcommand_is_test`; tests "real runner invocation…", "runner words outside command position…", "help/version and install…" |
| Goals | G2 per-repo last-run marker keyed by repo root | Conformed | `lastrun_path` (:257) + `repo_root`; test asserts marker lands at the temp repo's key |
| Goals | G3 block Stop while a dirty test edit outruns the later of {run, vetting} | Conformed | Stop branch (:341–348) `newest_edit > lastrun_ts or newest_edit > skill_ts` → block; tests "dirty test file with no markers…", "markers older than the edit are stale" |
| Goals | G4 nudge test-quality on each suite run | Conformed | `VET_REMINDER` printed in run branch (:315–322); test asserts envelope `hookSpecificOutput.additionalContext` + `/TEST QUALITY/` |
| Goals | G5 documentation files are not tests | Conformed | `DOC_FILE_RE` skip in `dirty_test_files` (:281); test "clean repo stops freely; docs/spec dirt is not test dirt" |
| Goals | G6 degrade honestly per runtime; never a silent run-only clear | Conformed | rungs wired: CC skill marker (install.sh:125 matcher `Bash\|Skill`, :130 Stop — both unchanged this issue), Codex attestation (hooks.json:21,57 `TQ_HOOK_RUNTIME=codex`; hook :304), opencode documented-unsupported (plugin :10–13, :144–153 log-only); tests pin run-only blocked + attest paths |
| Scenario | Running a suite records a run and nudges vetting | Conformed | run branch :304–322 (touch `lastrun_path` :315 + reminder); test "real runner invocation…" |
| Scenario | Non-run command does nothing | Conformed | detection returns False → no marker/output; test (heredoc/comment/string fixtures) |
| Scenario | Help/version and install invocations are not runs | Conformed | `_HELP_FLAGS` skip + `_PM_NO_RUN`; test |
| Scenario | Invoking the test-quality skill stamps the vet marker (other skills: nothing) | Conformed | :324 `elif tool_name == "Skill" and ti.get("skill") == _TEST_QUALITY_SKILL` → touch `skill_path`; tests "Skill invocation…", "a different skill stamps nothing" |
| Scenario | Stop is blocked when a test file is dirty since the last run or vetting | Conformed | :346; tests (no markers / stale markers → block) |
| Scenario | edit→run→vet→stop is allowed | Conformed | both marker mtimes ≥ edit → no block; test |
| Scenario | edit→run→stop without vetting is blocked | Conformed | `skill_ts` 0/stale → block; test "run alone never clears" |
| Scenario | Attestation stamps the vet marker on a skill-invisible runtime | Conformed | :304 `runtime_attest_enabled() and is_attestation_command(cmd)` → touch `skill_path` (:183 detection survives `$(…)` paths; no run marker); tests "attestation command stamps…", "attestation detection survives shell substitution paths…" |
| Scenario | Attestation is inert where skills are observable | Conformed | `runtime_attest_enabled()` (:173) false without env → attest branch never taken; test pin "attestation is inert without TQ_HOOK_RUNTIME" |
| Scenario | Stop reason names the vetting act the runtime can perform | Conformed | :347 `STOP_REASON_ATTEST if runtime_attest_enabled() else STOP_REASON`; test asserts `--attest-vetted` present + `Skill tool` absent under env, and the inverse without |
| Scenario | Committing or cleaning test changes clears the gate | Conformed | `dirty_test_files` empty → exit 0; test (clean repo) |
| Scenario | Documentation files are not counted as tests | Conformed | :281; test (dirty `docs/spec/foo.md` → no block) |
| Scenario | Malformed payload exits cleanly | Conformed | json.load guard (:291–294) **+ non-object guard (:293)** — the pre-#2 code raised (exit 1) on `[]`/`null`; found red by the new test and fixed this issue; test covers invalid + non-object shapes |
| Scenario | opencode does not enforce the Stop gate (documented-unsupported) | Conformed | plugin `session.idle` handler (:144–153) logs warn, never throws (blocking channel doesn't exist); documented at plugin :10–13, hooks README "Runtime support" section (:16), spec runtime matrix. *Flag: wiring-level invariant, covered by inspection — no automated test drives the plugin JS (noted, accepted: the plugin path is declarative and the hook side is fully entrypoint-tested)* |
| Surface | `hook_event_name` / `cwd` inputs | Conformed | :295–296 (+ `repo_root`); every test drives these |
| Surface | `tool_input.command` inspected for runs/attestation | Conformed | :303; run + attest tests |
| Surface | `tool_name` `Bash`/`Skill`; `tool_input.skill` must equal `test-quality` | Conformed | :324 (+ :71 `_TEST_QUALITY_SKILL`); hook is deliberately lenient about `tool_name` for command inspection (tolerance, not divergence) |
| Surface | env `TQ_HOOK_RUNTIME` gates attestation + Stop reason | Conformed | :173, :304, :347; set only by `.codex/hooks.json` (:21, :57); absent from install.sh/CC wiring (unchanged :125, :130) |
| Surface | outputs: run → additionalContext; skill/attestation → silent + marker; Stop dirty → decision:block + reason; else silent exit 0 | Conformed | run branch print; attest/skill branches silent; Stop block; tests assert each exact shape incl. exit codes |
| Surface | runtime support matrix (CC enforced / Codex enforced / opencode not enforced) | Conformed | as G6 evidence above |

## Coverage proof

- **audited:** Goals 1–6; all 13 scenarios; Proposed Surface (payload inputs incl. env; outputs; runtime support matrix)
- **unreconciled:** []

## Notes

- The 2026-07-10 matrix row "edit→run→stop is allowed | Conformed" audited the pre-skill-marker implementation and was stale against the shipped two-marker gate; the 2026-10-22 spec amendment (c7ab53a) reconciled the scenario and this audit re-proves it. A latent SP-8 violation (non-object JSON raising exit 1) was found by the new tests and fixed in this issue.
- Deferred validation (disclosed, not a divergence): the wiring effect of `TQ_HOOK_RUNTIME=codex` was verified as file content + entrypoint behavior with the env set; a live-fire probe under a real Codex session (hook trust for a new worktree path required) was not run this issue.
