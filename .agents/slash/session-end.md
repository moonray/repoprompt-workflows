---
description: Evidence-backed session closeout — answer the standing questions from the session's actual state
---

# Session closeout

Run at the end of a session, at the operator's request. Review the session's ACTUAL record — its timeline, the git state, the ledgers — and answer every standing question with evidence (file paths, commit SHAs, issue/IDs, tool output) or an explicit "nothing to do". A bare assertion is not an answer.

1. **Changed** — enumerate what this session changed, from evidence not memory: `git status` + diff against the session's start, files touched, commands that mutated anything. Group by intent. Name the uncommitted and unpushed state explicitly — anything left "riding along" gets named, not buried.
2. **Docs & specs** — for each behavior-affecting change: were the paired documents updated — specs, runbooks/procedures/operations docs, conformance matrices? Name each updated file, or flag the drift as still open (flag, do not silently fix mid-closeout). Distinguish "no doc pairs with this" from "I didn't check".
3. **Tracked work** — every unit of work from this session has its tracking item; statuses current; ledger consistent with commit/push reality. No orphan work, no stale in-progress items.
4. **Client comms** — if the session touched client work: communications synced into the archive, requests/obligations captured, and any outbound client claim live-verified as of send time (stale claims are client-facing mistakes).
5. **Verification** — user-facing changes exercised through the real rendered UI (or the deferral recorded with a reason); code changes tested with the run recorded. Tests-passed is not user-verified.
6. **Handoff** — what must the next session know: pending decisions, blocked items, in-flight work, where each is recorded. Write down the one place the next session will find it — the next session starts from evidence, not archaeology. Close with a one-paragraph state-of-the-session summary: what landed, what's loose, the next natural step.

Answer all six even when the answer is "nothing to do" — the operator is confirming coverage, not hunting for what was skipped.
