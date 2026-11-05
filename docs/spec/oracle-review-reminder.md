---
title: Oracle-Review Reminder Hook
status: implemented
---

# Oracle-Review Reminder Hook

## Problem

Oracle consultations (`ask_oracle`) collapsed outside the explicit workflows: a 2026-11-05
cross-workspace chat-mining sweep found ~2 self-triggered uses in two months across 150+
sessions, while the same window's workflow-gated moments (Spec Phase 6, Loop readiness,
Backlog clarity, Deep-Review tie-breaks) show effectively total compliance — some workflow
sessions ran 2–6 oracle rounds. Ad-hoc sessions (the majority of session shapes since
~September) load no workflow, so the only when-to-use guidance they see is a soft line in
the harness system prompt, which is reliably outranked by in-flight context. The miss is
concentrated at two moments: committing a substantial ad-hoc change set, and writing a
spec/plan outside the Spec workflow (a 56-turn spec "gotcha review" ran entirely
self-reviewed, zero oracle). The positive control from the same sweep: the one ad-hoc
session that did consult caught 6 independently verified findings, including a
claimed-but-never-run evidence gap. This is a trigger gap, not a knowledge gap — the same
shape as the doc-freshness close-audit gap.

## Goals

1. Detect the "declaring this change done" moment in ad-hoc sessions: a successful
   `git commit` shell command.
2. Nudge — once per session — when that moment arrives with a substantial change set
   (≥3 distinct non-doc files edited this session, or any write under `docs/spec/` /
   `docs/plans/`) and no `ask_oracle` consultation observed in the session.
3. The nudge directs a bounded act: one `ask_oracle` review pass over the diff/summary,
   routed per the `model-routing` skill, findings folded or the skip reasoned — never a
   blocking gate.
4. Stay silent on small/mechanical/doc-only work, on sessions that consulted, after the
   first nudge, and on failed calls.
5. Fail open — malformed input or a crashed hook never traps the agent.

## Non-Goals

- No gate/blocking and no verification that the review ran (no marker machinery beyond the
  one-shot nudge flag); the downstream closeout gates remain the backstops.
- No line-count sizing: distinct-file count is the proxy; `review-depth`'s line bands stay
  the canonical sizing for explicit review runs, decoupled from this trigger.
- No Stop-channel trigger: Stop fires every turn, so it would nudge mid-flight work; the
  commit is the observable wrap-up signal (same surface choice as doc-freshness for closes).
- No coverage of bash/heredoc-written files (only edit-tool and apply-patch paths are
  observed) — accepted residual, fails silent.
- No per-repo scoping: state is session-scoped (keyed by `session_id`, falling back to
  `cwd`), so cross-repo work inside one session shares one change-set picture. On runtimes
  whose events carry no session identifier and no resolvable per-session field (opencode
  when its event lacks `sessionID`), state is effectively per-repo — documented-unsupported
  isolation, not a per-session guarantee.

## Constraints

- PostToolUse-only; the runtime matcher is the first filter, the in-script detection is the
  precise gate. Registered on shell events, edit-shaped events, and `ask_oracle`.
- Oracle observation matches the MCP-qualified tool name ending in `ask_oracle`; any
  successful or failed consultation still counts as consulted (the agent sought an
  independent lane — a transport failure is not a skip).
- Edit events are counted only when the runtime does not report the call failed
  (`is_error`/`isError` true, truthy `error`, `status: "error"`, `ok`/`success` false);
  absent or unrecognized response shapes count (nudges are cheap; misses are not).
- Doc-ish extensions (`.md`, `.markdown`, `.mdx`, `.txt`, `.rst`, `.adoc`) never count
  toward the 3-file threshold, EXCEPT steering markdown — paths under
  `.agents/(skills|workflows|rules|slash)/` and any `SKILL.md` count as non-doc (in
  agent-machinery repos those files are the behavior-defining surface); paths under
  `docs/spec/`, `docs/specs/`, or `docs/plans/` set the spec/plan flag regardless of
  extension.
- Paths are lexically normalized (`\` → `/`, `./` prefixes, duplicate slashes, trailing
  `/`) before counting; absolute vs repo-relative spellings of one file may still count
  twice (accepted residual — resolving against a base would corrupt workspace-root-relative
  paths; the duplicate direction only over-nudges, bounded by the one-shot).
- Commit detection is adjacency-based on shell-tool events (`tool_name` `Bash`/`bash`/
  `shell`): `git commit`, including `git -C <path> commit`, `--no-pager`/`--git-dir=X`
  global-flag forms, and `&&`-chained segments; `git commit-tree`, `git commit-graph`,
  and `--dry-run` (a non-writing mode) are not commits; prose embedding an exact
  `git commit` sequence fires (accepted residual — same class as doc-freshness S-006).
  `gh pr close`, `git push`, `git add` are not commits.
- State is a per-key JSON file written by atomic replace under an exclusive `flock` held
  around the whole load-modify-save transaction (parallel tool events cannot lose edits
  or tear a read); state older than the TTL resets on load (prune-on-write alone never
  clears an actively reused key).
- Token-economy gate: oracle is for changes where an independent lane pays for its
  premium tokens, not for every multi-file commit. When the trigger fires without the
  spec/plan flag, the hook measures the just-landed commit (`git show --shortstat HEAD`
  in the event's `cwd`) and stays silent at or below `review-depth`'s S/M boundary
  (≤150 changed lines — the change sizes `quick`, and quick reviews carry no oracle
  lane). Commits redirected via `-C`/`--git-dir`/`--work-tree` (landed outside `cwd`, so
  `cwd` stats would measure the wrong commit) and unmeasurable cases fail toward the
  nudge, never toward silence. Spec/plan writes bypass the gate: document-shaped
  consultations are the cheapest, highest-yield lane. The one-shot flag is not consumed
  by a silent gate — a later substantial commit in the same session still nudges.
- Exactly one nudge per session (`nudged` flag persists in session state); a nudge is
  emitted only on a successful commit.
- Session state lives in a cache dir (`~/.cache/oracle-review-hook`, overridable via
  `ORACLE_REVIEW_STATE_DIR` for tests); stale state files (>7 days) are pruned on write.
- Reminder-only; the script never deliberately exits non-zero.

## Scenarios

### Scenario S-001: Commit of a ≥3-file change set with no consultation nudges
- **Given** a session whose state records ≥3 distinct non-doc file edits (from edit-tool paths or apply-patch command headers) and no `ask_oracle` call
- **When** a successful `git commit` shell event fires
- **Then** the hook emits exactly one nudge directing one `ask_oracle` review pass routed per the `model-routing` skill, with confirmed findings folded or the skip reasoned

### Scenario S-002: Commit after a spec/plan write with no consultation nudges
- **Given** a session whose state records an edit under `docs/spec/` or `docs/plans/` (any file count) and no `ask_oracle` call
- **When** a successful `git commit` shell event fires
- **Then** the hook emits exactly one oracle-review nudge

### Scenario S-003: A consulted session stays silent at commit
- **Given** session state with a ≥3-file change set or spec/plan write, and an `ask_oracle` PostToolUse event arrived at any point earlier
- **When** a successful `git commit` shell event fires
- **Then** no nudge

### Scenario S-004: Below-threshold work stays silent
- **Given** session state with ≤2 distinct non-doc file edits and no spec/plan write
- **When** a successful `git commit` shell event fires
- **Then** no nudge

### Scenario S-005: The nudge is one-shot per session
- **Given** a session that already emitted the nudge at an earlier qualifying commit
- **When** another successful `git commit` fires in the same session
- **Then** no further nudge

### Scenario S-006: Failed edits do not count toward the threshold
- **Given** edit events whose tool responses carry an explicit failure indicator
- **When** a successful `git commit` fires
- **Then** those paths are absent from the counted set (a session with only 2 successful non-doc edits stays silent)

### Scenario S-007: Doc-only change sets stay silent
- **Given** ≥3 edit events all on doc-ish files outside `docs/spec|specs|plans` and outside the steering paths (`.agents/(skills|workflows|rules|slash)/`, `SKILL.md`)
- **When** a successful `git commit` fires
- **Then** no nudge

### Scenario S-013: Steering markdown counts as non-doc
- **Given** edit events on ≥3 distinct steering paths (e.g. `SKILL.md` files, workflow or rules markdown under `.agents/`)
- **When** a successful `git commit` fires
- **Then** the hook emits the nudge (S-001's Then applies)

### Scenario S-015: Quick-band cwd commits stay silent; spec writes and redirected commits bypass the gate
- **Given** a qualifying ≥3-file change set with no consultation, and a landed commit measurable in the event's `cwd` with ≤150 changed lines
- **When** the hook runs on that successful commit
- **Then** no nudge and the one-shot is not consumed — while the same small commit still nudges when the session wrote a spec/plan doc (document lane bypasses the gate), and a `-C <path>` commit (unmeasurable from `cwd`) also still nudges

### Scenario S-014: Commit look-alikes and dry-runs do not trigger or consume the one-shot
- **Given** shell commands `git commit-tree …`, `git commit-graph …`, or `git commit --dry-run …`
- **When** the hook runs on their successful events
- **Then** no nudge and the one-shot flag is not consumed — a subsequent real qualifying commit still nudges

### Scenario S-008: Non-commit shell commands never nudge
- **Given** any shell event that is not a `git commit` shape (`git status`, `git add`, `git push`, `gh pr close`, test runs)
- **When** the hook runs
- **Then** no nudge regardless of accumulated state

### Scenario S-009: A failed commit stays silent
- **Given** a `git commit` shell event whose tool response carries an explicit failure indicator
- **When** the hook runs
- **Then** no nudge, and the one-shot flag is not consumed

### Scenario S-010: Chained and flagged commit forms are detected
- **Given** `git add -A && git commit -m "…"` or `git -C /path commit -m "…"`
- **When** the hook runs on the successful event
- **Then** the commit trigger applies (S-001–S-005 evaluate normally)

### Scenario S-011: Foreign events are ignored
- **Given** a hook event other than PostToolUse (e.g. Stop, with or without a `session_id` — absent ids key state by `cwd`), or a PostToolUse edit event carrying no recognizable path form
- **When** the hook runs
- **Then** exit 0 with no output and no nudge

### Scenario S-012: Malformed input exits cleanly
- **Given** stdin that is not valid JSON, or valid JSON that is not an object
- **When** the hook runs
- **Then** exit 0 with no output

## Proposed Surface

### Hook Payload

| Input | Required | Description |
|---|---|---|
| `hook_event_name` | yes | Must be `PostToolUse`. |
| `session_id` | no | Session key for state; falls back to `cwd` hash when absent. |
| `tool_name` | yes-ish | Oracle observation on names ending `ask_oracle`; commit detection on shell events. |
| `tool_input.file_path` / `path` / `filePath` / `notebook_path` | edit events | Scalar edited path(s) accumulated into the session set. |
| `tool_input.command` apply-patch forms | edit events | `*** Add/Update/Delete File: <path>` header lines parsed for paths. |
| `tool_name` | shell events | Commit detection applies only to shell tool names (`Bash`/`bash`/`shell`) carrying a `command`. |
| `tool_input.command` | shell events | Matched against the commit adjacency shapes; `--dry-run` anywhere in the command suppresses the trigger. |
| `tool_response` | no | Explicit failure indicators suppress that event's contribution. |

### Hook Output

| Field | Description |
|---|---|
| qualifying commit, unconsulted, not yet nudged | `hookSpecificOutput.additionalContext` carrying the oracle-review nudge; exit 0. |
| otherwise | no output; exit 0. |

## Open Questions

None.
