---
name: chrome-site-overrides
description: Per-site override profiles for the chrometools skill. Not a skill itself — a reference file read by it.
---

# Site overrides

The `chrome` SKILL.md carries the general protocol. This file is the **override/tweak layer**: per-site profiles whose deltas override the defaults for that host, kept separate so the default stays general.

## Format

One `## <domain>` section per site. Record **only deltas** from the default protocol — a fact that matches the default belongs nowhere. Each profile ends with a `Source` line naming the owner lesson or session that established it, so a future reader can tell hardened observation from guess. When a session teaches a site-specific fact (settle behavior, challenge pattern, variant quirks), append or amend the profile in the same change that used the lesson. A domain whose method has been extensively field-tested earns a second file, `sites/<domain>.md`, carrying the full tested sequence; the profile routes to it with a `Tested method:` line — deltas live here, the method lives there.

---

## crunchyroll.com

- **Rolling clearance, always.** Crunchyroll runs the `__cf_bm` rolling-cookie model (**~30-minute cookie**). A durable `cf_clearance` was long absent here, but 2026-11-16 automated sessions (MCP and agent-browser with the recipe) each received one — treat it as possible but never relied upon. Challenges still recur by design for every session and periodically within one — a recurring challenge is routine operation, not a reset, a failure, or a signal that the warm-up was wrong. Re-warm and continue.
- **Root-settle is mandatory, not advisory.** On this site a cold deep link is *the* challenge trigger: land on the root and let it fully settle before any interior navigation, every session, even when the last session ended clean.
- **Wait out managed challenges; never click the checkbox.** When a Turnstile/managed challenge appears, wait for it to auto-clear before any click. Clicking the checkbox reflexively is the known way to make it worse here.

Tested method: [`sites/crunchyroll.md`](sites/crunchyroll.md) — the field-tested warm-up + harvest sequence.

*Source: owner lesson 2026-10-10 (Crunchyroll history tooling — the warmVisit routine and its spec scenario carry the code-level encoding).*

---

## amazon.com (Prime Video)

- **No challenge ladder — auth is the gate.** Field-tested sessions see no Cloudflare-class wall; the failure modes are auth expiry and multi-profile mixups. One-time headed human login into a persistent profile directory; later runs are autonomous. A needs-re-auth exit means rerun the human login, not re-diagnose a wall.
- **Assert profile identity before any parse (mandatory).** Multi-profile households: select the profile by its stable actor OID, then assert the page's inline current-profile id and abort on mismatch — wrong-profile data is silent, so the assert is the only guard.
- **Harvest the platform's own paginated JSON API, not the DOM** (the internal watch-history endpoint); DOM scraping is the fallback, not the path.
- **Read-only against the service:** never click destructive settings UI ("Episodes watched" and friends).

*Source: owner's Prime watch-history lane (`prime-history.mjs` + `lane-lib`), design verified live 2026-10-08.*

## netflix.com

- **Full history is the viewing-activity "Download all" export** — a full-account CSV (title|date, newest-first, day granularity, no episode numbers or playheads). Prefer the export over scrolling any rendered surface.
- **Auth detection needs a positive logged-in signal only.** The login flow passes through non-login URLs (email-code steps), so logged-out URL-pattern matching yanks the page away mid-flow.
- **No challenge ladder observed.** One-time headed human login into a persistent profile; autonomous harvests after.

*Source: owner's Netflix lane (`netflix-history.mjs`, probe preserved), field-tested 2026-11-16.*

## hulu.com

- **No full watch history exists** — only the Continue Watching presence surface. Treat presence as a signal, never as progress.
- **Navigation contract (do not reorder):** warm up on the root; hydrate Home by polling `data-uia` (never fixed sleeps); dismiss the Parental Controls welcome modal (role=dialog, CLOSE DIALOG) and **reload Home** — the modal blocks personalized rows from rendering; the privacy "preference center" dialog ignores dismissal — try once, then ignore; find the Continue Watching row by polling across gentle scrolls (it lazy-loads near the top on the first/second scroll; the header is not guaranteed to be an `h2` — match any leaf element whose text or aria-label is exactly "Continue Watching"), then click that row's View All link — **never deep-link the collection URL** (it intermittently renders as a blank SPA shell); on the collection page dismiss **only** parental-controls-style dialogs — blanket dismissal closes tile expandos and bounces back to Home.
- **No challenge ladder observed.** One-time headed human login into a persistent profile.

*Source: owner's Hulu sensor lane (`hulu-history.mjs`, probe preserved), field-tested 2026-11-16.*
