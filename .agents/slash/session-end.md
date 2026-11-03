---
description: Session closeout gate — verify nothing is left from evidence, then present numbered open items with lettered options (reply like "1 a, 2 c, 4 ignore")
---

# Session closeout

Run when the operator signals intent to end the session. The session is NOT declared over: first verify from evidence that nothing remains; then **push back** with everything that is not yet done, as numbered items with lettered options, and let the operator choose. Every answer cites evidence (file paths, commit SHAs, issue IDs, tool output) or states "nothing to do" — never a bare assertion from memory.

**Format rules for every section:** a one-glance verdict line first (`✅ nothing to do` / `⚠️ N items: <five-word gist>`), then compact detail with the load-bearing words bolded. No walls of prose: a reader should tell at a glance what a section is about to say before reading it.

1. **Changed** — what this session touched. Verdict line, then the inventory: `git status` + diff against the session's start, files touched, grouped by intent; uncommitted and unpushed work named explicitly, never buried.
2. **Docs & specs** — paired documents for behavior-affecting changes. Verdict line, then per change: specs/runbooks/procedures/operations docs/conformance matrices updated (name each file) or the drift flagged as open (flag, do not silently fix mid-closeout). Distinguish "no doc pairs with this" from "I didn't check".
3. **Tracked work** — ledger consistency. Verdict line, then: every unit of work has its item, statuses current, ledger consistent with commit/push reality; no orphans, no stale in-progress, nothing "riding along" unnamed.
4. **Client comms** — for sessions touching client work. Verdict line, then: communications synced into the archive, requests/obligations captured, outbound client claims live-verified as of send time.
5. **Verification** — proof the work works. Verdict line, then: user-facing changes exercised through the real rendered UI (or the deferral recorded with a reason); code changes tested with the run recorded. Tests-passed is not user-verified.
6. **Open items — the push-back** — the closeout gate. Collect EVERYTHING the sections above found unfinished, plus known session leftovers (pending decisions, deferred work, loose ends the operator named earlier). One numbered block per item:

   **N. <item>** — <one line: what it is + why it matters>
   - **a)** <option> *(recommended — say why in a clause)*
   - **b)** <option>
   - **c)** <option>

   Option rules: small, closely-related items → offer **finish now in this session** and recommend it; large or cleanly separable items → offer **create a tracking issue** and recommend that; always leave **defer to next session** (name where it gets recorded) and **ignore** (with the reason recorded) available — the operator may answer with letters or words, e.g. `1 a, 2 c, 4 ignore`. Never silently drop an item; never pre-decide for the operator.

   If genuinely nothing remains: `✅ nothing to do` and a **one-paragraph end-of-session summary** (what landed, what's loose if anything, the next natural step) in place of the list.

Then: wait for the operator's picks, execute them, and **re-verify** the affected sections before declaring the session ended. If picks create new loose ends, they join the list.
