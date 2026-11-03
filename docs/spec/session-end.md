---
title: Session-End Command
issue: 15
status: implemented
---

# Session-End Command

## Problem

End-of-session questions ("did you update docs/specs", "is everything committed", "what's left") were asked ad hoc, answered from memory, and produced prose reports that were hard to scan and easy to accept uncritically. Worse, a "handoff" framing declared the session over and deferred leftovers to a future session that would have to reconstruct them — exactly the drift-and-archaeology pattern the workspace's other closeout gates exist to prevent (operator redesign directive, 2026-11-03, after first real use).

## Goals

1. Trigger on the operator's intent to end the session, and treat that intent as a gate to verify — not a farewell to execute.
2. Answer every standing closeout question from evidence (git state, ledgers, logs, verifications), each section led by a one-glance verdict line.
3. Push back with a numbered list of open items, each carrying lettered options for how to resolve it, so the operator can answer compactly (e.g. `1 a, 2 c, 4 ignore`).
4. Route items by size and relatedness: small closely-related work is offered (and recommended) as finish-now; large or separable work as a tracking issue; defer and ignore are always available and never silently dropped.

## Non-Goals

- No autonomous execution of the options: the operator picks; the session executes.
- No session-telemetry capture beyond what the sections already inspect (git, ledgers, comms records, verification state).
- Not a Stop hook or gate: this is an operator-invoked command; automatic enforcement stays with the hook family.

## Constraints

- Evidence or explicit "nothing to do" for every section; bare memory assertions are out of contract.
- Every section's first line is a scannable verdict (`✅ nothing to do` / `⚠️ N items: <gist>`); detail follows, load-bearing words bolded.
- Open items aggregate findings from ALL sections plus known session leftovers (pending decisions, deferred work, operator-named loose ends).
- After the operator's picks are executed, affected sections are re-verified before the session is declared ended; new loose ends from the picks join the list.

## Scenarios

### Scenario S-001: Intent to end triggers a gate, not a farewell
- **Given** the operator invokes the command (or signals the session is ending)
- **When** the command runs
- **Then** it verifies state and presents open items rather than declaring the session over; the session ends only after the operator resolves the list (or it is genuinely empty)

### Scenario S-002: Evidence-first answers with verdict lines
- **Given** any section (Changed / Docs & specs / Tracked work / Client comms / Verification)
- **When** it is rendered
- **Then** its first line is a one-glance verdict, and every claim beneath cites evidence or states "nothing to do"

### Scenario S-003: Open items are numbered with lettered options and an ignore path
- **Given** one or more unfinished items found across the sections or named earlier in the session
- **When** the push-back list is rendered
- **Then** each item is a numbered block with a one-line description, two to four lettered options with at most one marked recommended, and defer/ignore always available; the operator can answer with letters or words (`1 a, 2 c, 4 ignore`)

### Scenario S-004: Options route by size and relatedness
- **Given** an open item
- **When** options are composed
- **Then** small closely-related items offer finish-now (recommended), large or cleanly separable items offer a tracking issue (recommended), and the recommendation carries a one-clause reason

### Scenario S-005: Picks are executed, then re-verified
- **Given** the operator's picks
- **When** they are executed
- **Then** the affected sections are re-verified before the session is declared ended, and any new loose ends the picks create join the open-items list

### Scenario S-006: The empty path renders a summary
- **Given** no open items anywhere
- **When** section 6 renders
- **Then** it shows `✅ nothing to do` and a one-paragraph end-of-session summary (what landed, what's loose, next natural step) instead of a list

## Proposed Surface

| Element | Description |
|---|---|
| Command file `.agents/slash/session-end.md` | Frontmatter description carrying the trigger + reply grammar; six sections with format rules; the push-back gate as section 6. |
| Output grammar | Verdict lines (`✅`/`⚠️`) heading every section; numbered items with lettered options; operator replies like `1 a, 2 c, 4 ignore`. |
| Deployment | `scripts/install.sh` links the command into every runtime home (`~/.claude/commands`, `~/.agents/slash`). |

## Open Questions

None.
