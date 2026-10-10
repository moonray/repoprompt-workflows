# Spec: chat-mining — retrospective session analysis and continuous improvement cycle

**Status:** Active · **Created:** 2026-10-07 · **Tracking:** #46 (cycle updates), #42 (original landing) · **Skill:** `.agents/skills/chat-mining/SKILL.md`

## Context

Session transcripts accumulate defects, lessons, friction, and pending decisions that die with the transcript. The `chat-mining` skill recovers them retrospectively: inventory a workspace's session history, sweep it with themed searches, verify every candidate claim against ground truth, and map each surviving finding to its durable home. This spec contracts that behavior plus the continuous-improvement cycle (#46): a mined-through watermark so runs are incremental, a deterministic pre-pass so LLM reading is spent only on flagged candidates, and a cadence so the loop runs standing instead of ad hoc.

Provenance: derived from three real runs (vyasa-puja 2026-08-20, mymp3pool 2026-08-20, keryxsolutions 2026-10-07) and the fleet repo's session-analysis architecture (deterministic-first detection, normalized findings) — portable principles only.

## Goals

1. Recover process improvements from session history with bounded cost, never re-mining what a prior run covered.
2. Every reported finding is ground-truth-verified; a transcript's narrative is a claim, not evidence.
3. Findings land in durable homes per the scope ladder and repo-placement policy; nothing validated dies in the report.
4. The loop is continuous: watermark + cadence + deterministic pre-pass.

## Non-Goals

- Replacing inline quality gates (test-quality/review-quality hooks, closeout gates) — chat-mining is the retrospective sweep that catches what they missed.
- Reading one specific session's log to resume work (explicitly out of scope).
- Automatic filing or editing without the applicable skill/trigger and user authorization.
- A new findings database — retention flows through track-work issues, commits, rules, and skills.

## Proposed Surface

| Element | Contract |
|---|---|
| `.agents/skills/chat-mining/SKILL.md` | The procedure (trigger, sweep, verification, mapping, report). Model-invoked. |
| `.agents/mining-ledger.md` | The per-workspace watermark ledger (mined-through marker + next-due), living in each mined workspace's own repo and created on its first completed sweep. Read at run start, written at run close. |
| Deterministic pre-pass | A ranking computed from `history list_sessions` metadata (turn counts, durations, files-touched) + themed-search hit counts — no LLM reads before it. |
| Report | Chat-delivered: ranked findings with validation-status labels, an already-landed section, user-gated items separate, ledger update. |

## Scenarios

### Scenario S-001: mining-shaped requests trigger the skill; resume requests do not
- **Given** the available-skills listing and a user request
- **When** the request asks to mine/analyze past session chats for defects, lessons, process improvements, or friction ("what can we learn from workspace X's chats")
- **Then** the chat-mining skill is loaded and followed; a request to re-read one specific session's log to resume work does NOT trigger it (the description's exclusion clause governs)

### Scenario S-002: scope — one workspace or all
- **Given** a mining request
- **When** the subject is one workspace
- **Then** the sweep covers that workspace; when the subject is a cross-cutting process (billing, tooling, a skill's behavior), the sweep covers ALL workspaces — the same lesson often surfaces independently in several

### Scenario S-003: the watermark makes runs incremental
- **Given** `.agents/mining-ledger.md` carrying a mined-through marker for workspace W, and sessions newer than that marker
- **When** a run for W starts
- **Then** only sessions after the marker are candidates; the run does not re-mine covered history; on successful close the marker advances to the last fully-processed session with a timestamp — "successful close" means the run processed every session in its declared candidate scope (a thematic sweep declares its scope in the ledger and covers that scope fully; a run that abandons its scope mid-way leaves the marker unchanged)

### Scenario S-004: deterministic pre-pass ranks before any LLM read
- **Given** the candidate session set from S-002/S-003
- **When** reads are planned
- **Then** candidates are first ranked using only signals computable without transcript reads — for example themed-search hit count, turn-count vs files-touched ratio, duration, or single-turn decision-shaped sessions — and no session transcript is read before this ranking exists; the ranking orders reads (top-ranked first) and is never itself a finding

### Scenario S-005: themed sweep includes decision-language and friction terms; final turn read first
- **Given** the sweep over candidate sessions
- **When** search terms are chosen
- **Then** they include retrospective language ("lesson", "takeaway", "next time", "improve"), decision language ("decision", "your call", "say the word", "want me to"), friction language ("no-op", "construction error", "re-read", "fixing my own", "regenerat"), and domain terms; friction is often NOT narrated at all, so transcript structure is also examined — repeated failed calls, the same file read multiple times, suite re-runs after self-introduced defects, multiple regenerations of one artifact, high turn counts over small landed diffs; each hit session's FINAL turn is read before deeper reads

### Scenario S-006: every claim is verified against ground truth
- **Given** a candidate finding extracted from a transcript
- **When** it is assessed
- **Then** it is re-checked against current code, docs, git, and issue state before being reported; "done/fixed/verified" in a transcript is never accepted as fact; each finding is labeled still-pending, already-landed, or user-gated

### Scenario S-007: friction is judged by path, discriminated by the durable-artifact test
- **Given** a session that reached a correct outcome through suspected wasted motion
- **When** it is assessed
- **Then** the path is judged, not the outcome; the finding stands only if a durable artifact (rule, template, test, tooling, encoded procedure) would have prevented the waste — that artifact is the deliverable; irreducible discovery in unfamiliar territory is not a finding

### Scenario S-008: findings map to durable homes per the scope ladder
- **Given** a verified finding
- **When** its home is chosen
- **Then** cheapest-first: the affected repo's own memory/contributing docs → a shared skill or workflow in the matching shared repo (public machinery repo when generic and public-appropriate; the organization's own repo when org-specific — non-public content never goes to the public repo) → `global.md` last (per-request cost; corollary on an existing rule, never a new section when a corollary suffices); full-match artifacts (only-for-one-project) home in that project's repo; the mined workspace is provenance, never content

### Scenario S-009: retention — nothing validated dies in the report
- **Given** the run's findings
- **When** the run closes
- **Then** each lands in or is recommended to a durable home, recorded in a retention map with its full/partial classification; findings not immediately actionable get a filed or updated tracking issue (with user authorization); the watermark advances (S-003)

### Scenario S-010: report shape
- **Given** the run's verified findings
- **When** reported
- **Then** they are ranked by impact × effort with a quick-wins tier; each carries its validation status; an explicit already-landed section prevents re-proposal; user-gated items are visible but separate from agent-actionable ones

### Scenario S-011: applied changes are validated by isolated subagent with negative controls
- **Given** a rule/skill/workflow change produced by a mining run
- **When** it is validated
- **Then** an isolated read-only subagent probes it; the probe includes a negative control (old text fails, or an adjacent no-trigger case stays untriggered) so it can discriminate; the subagent's report is verified independently, never accepted as-is; destructive testing requires explicit user permission for that specific action — non-destructive routes (dry-run, read-back, isolated fixtures) are always preferred

### Scenario S-012: cadence is ledger-driven
- **Given** the ledger's next-due field for a workspace
- **When** a mining request arrives, or an open tracking issue carries the cycle standing item
- **Then** the run reports cadence status (current / overdue with sessions-accumulated count); the default cadence is quarterly or ~150 new sessions, whichever comes first; the cadence is a prompt, never an automatic run without user initiation. Surfacing today rides the existing machinery: any mining run reports status, and standing follow-ups are ordinary open tracking items in the workspace's own ledger — no dedicated briefing wiring exists (2026-10-07 amendment: the original wording implied dedicated briefing wiring; the implemented contract is this one).

## Traceability

| Goal / Surface | Scenarios |
|---|---|
| G1 bounded, incremental recovery | S-002, S-003, S-004, S-005 |
| G2 verified findings | S-006, S-007, S-011 |
| G3 durable homes | S-008, S-009 |
| G4 continuous cycle | S-003, S-004, S-012 |
| skill trigger/exclusions | S-001 |
| report surface | S-010 |
| ledger surface | S-003, S-012 |
