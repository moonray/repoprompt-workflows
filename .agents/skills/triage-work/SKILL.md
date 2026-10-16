---
name: triage-work
description: Use when reviewing, triaging, or prioritizing open tracked work across repos — "triage my issues", "review open issues", "what's open / what should I work on next", "list issues by ease (or priority)", "which backlog items are safe to tackle while X runs in another session", "clean up needlessly open / stale issues", or checking that issues are still applicable, still needed, and still a good idea given repo intent. Verifies each item against ground truth before any mutation (landed commits, gate/CI history, time-boxes, live systems, comms records), closes evidence-verified items, repairs taxonomy, classifies every item's autonomy (agent-actionable vs needs-decision vs human-only vs blocked-external), and ranks by the default priority rubric or a requested axis. All ledger access flows through track-work. Not for filing one new item (track-work), creation-time intake rules (track-work), autonomous execution of the queue (Backlog workflow), or mail/message triage.
---

# Triage Work — the periodic ledger review

## Intent

Tracked items drift: gates get met but nothing closes, priorities rot, work gets blocked externally and the label never changes, decisions pile up unmade, and items outlive the repo's intent. Triage is the periodic pass that restores the ledger to reality: **verify every suspicious item against ground truth, close what's done, repair what's mislabeled, route what isn't agent work, and rank what remains.**

This is the interactive analyst layer. It sits between **track-work** (item CRUD, backend selection, intake) and the **Backlog** workflow (autonomous execution). Triage prepares and cleans; it never implements — no specs, no code, no tests for the items it reviews. Its output is a decision-ready report plus a cleaned queue an execution run can consume without re-deriving any of this.

## Procedure

### 1. Discover — fan out, never assume the primary repo

Scope is every ledger the question spans, resolved exactly as track-work's multi-repo fan-out section prescribes: every workspace repo, plus any external ledger the user names or a repo config pins (a client's or upstream's repo counts when in scope). Backend selection runs per repo (workspaces mix GitHub and file backends); report each ledger's backend + capability as diagnostics. An unreachable or missing ledger is a stated gap in the report, never a silent omission — a partial list presented as complete is the one failure this exists to prevent.

Gather open items **with full bodies**. Labels carry the taxonomy but rarely the substance: effort labels help ranking, but "is this closeable / stale / blocked" is answered by the body and current reality. Discover each repo's label dimensions from its actual labels/config.

### 2. Verify — ground truth before mutation

Before touching any item whose state is decision-relevant (possibly closeable, possibly stale, possibly blocked), verify it against current reality. A prior ticket comment, run-note, or transcript claim is a **claim** — the user's own standing demand is "did you verify this, or just assume from the last ticket update?", so the answer is always: verified this run. Verification means, as applicable to the item:

- **Landed-commit ancestry** — is the implementing commit an ancestor of the default branch (or the PR merged)?
- **Gate/CI history** — has the item's own gate (workflow, canary, matrix) been green since the relevant change?
- **Elapsed time-boxes** — watch-windows and soak periods the item named: have they closed with no regression?
- **Live systems / infra** — where the item names a site, host, or service: check the thing itself (HTTP status, SSH facts), read-only.
- **External-party claims** — "waiting on the client / upstream" is grounded in the authoritative comms/record source where one exists (archive, thread record, sent log): did they actually say that, when, and has anything newer arrived? A comms finding can overturn a ticket's own comments — write the corrected facts back.

Record what was checked and the result; the disposition cites the verification, not the prior comment.

### 3. Clean — evidence-first mutations, judgment calls flagged

- **Close** only against the item's own gate, with the evidence in the close-out (SHA, green-run list, soak result, elapsed box). Re-read the ledger at the commitment boundary — it is shared with humans and other agents, and concurrent closure must be reconciled, not duplicated.
- **Dedup** by folding first: any unique detail, criterion, or open comment in the duplicate lands in the canonical item *before* the duplicate closes, cross-linked. A bare close loses content.
- **Repair taxonomy**: label the unlabeled, correct drifted priority/status (backlog-but-actually-blocked, p1-no-longer). Clear-cut fixes apply directly with a one-line why; judgment calls are flagged in the report and wait for the user.
- **File reserved follow-ups**: a close-out that explicitly reserves a follow-up gets it filed as its own item. Unmaterialized future work does **not** get a speculative stub — record a trigger note on the relevant item ("create the item when details arrive") instead.

### 4. Validate against repo intent

Surviving items earn their place: check each against the repo's intent anchor — an explicit intent/mission doc where one exists, else the stated-purpose docs (README/AGENTS), naming the source used. Verdict per item: aligned / questionable / no-longer-applicable. Questionable or dead items go in a flagged section stating the specific conflict and a recommended resolution (keep with reason, narrow, close), are held out of ranking until the user resolves them, and are never auto-closed — deciding an item isn't worth doing is the owner's call.

### 5. Route and classify — autonomy is not obvious from labels

Give every reported item exactly one:

- `autonomous` — an agent can start it now;
- `needs-decision` — a human call is required first;
- `human-only` — the work is human-executed (calls, recordings, approvals); an agent prepares at most;
- `blocked-external` — waiting on an outside party; an agent chases or preps only.

Derive this from verified state, not labels: a recording task wears an ordinary type label; outreach is agent-supported but human-driven; blocked-on-client items are not always labeled blocked. `type:decision` items (and items whose disposition reduces to an unmade decision) route to a separate human-decision rollup with the verified context that would inform the call — triage never specs, implements, relabels, or closes them. Only `autonomous` items are rankable.

### 6. Rank — default rubric unless an axis was requested

**Default** (no requested axis, or a non-list ask): `type:bug` first, then priority p0→p3, then ease (labeled effort before unlabeled) — the same order Backlog's Phase 1 uses, so triage output and execution intake never disagree.

**Requested axis** — applies only when the ask is a list/ranking output:

- **Ease**: easiest-first over autonomous items, effort labels grounded by body assessment (label absent → assess from the body and say so). Items gated rather than sized — blocked, human-only, time-gated, open-ended design — list separately below the ranking with their gating reason, never forced into an effort position.
- **Parallel-safety** (work in flight elsewhere): define the overlap zone — items touching the same files, themes, or physical checkouts as the in-flight work (a single shared checkout with no worktrees counts as fully contended for file edits). Exclude items already owned by in-flight sessions. Rank external-system work (no repo edits) as safest; mark coordination points that must be timed around the other session (e.g. production-affecting steps); list blocked items as not-tackleable with their blocker.

### 7. Record and hand off

Report shape: ledger diagnostics (backend/capability per repo, gaps) → verified closures with evidence → taxonomy changes (applied vs flagged) → intent-questioned section → autonomy-classified ranking (or requested-axis list) with gated section → decision rollup → **quick wins** callout → **one recommended pick** (or pairing) with reasoning → offer to start the pick or hand the cleaned queue to an execution run.

Write findings back where they'll be seen next time: audit-trail comments on triaged items (what was checked, when, verdict), comms-derived corrections onto the affected items, decision items left carrying their context. The next triage run — or the human reading the ledger — starts from evidence, not archaeology.

## Do / Don't

- **Do** route every ledger read/write through track-work (backend selection, fan-out, close rules, redaction).
- **Do** verify before mutating, and cite the verification in the mutation.
- **Do** keep the report split: agent-actionable vs your-court, applied vs flagged.
- **Don't** implement, spec, or test the items being triaged — that's Backlog's job.
- **Don't** auto-resolve decisions, auto-close intent-questioned items, or create speculative stubs.
- **Don't** rank non-autonomous items or recommend a pick that's gated unresolved.
- **Don't** present a partial ledger as complete — gaps get stated.
