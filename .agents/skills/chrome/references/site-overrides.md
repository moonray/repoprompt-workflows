---
name: chrometools-site-overrides
description: Per-site override profiles for the chrometools skill. Not a skill itself — a reference file read by it.
---

# Site overrides

The `chrometools` SKILL.md carries the general protocol. This file is the **override/tweak layer**: per-site profiles whose deltas override the defaults for that host, kept separate so the default stays general.

## Format

One `## <domain>` section per site. Record **only deltas** from the default protocol — a fact that matches the default belongs nowhere. Each profile ends with a `Source` line naming the owner lesson or session that established it, so a future reader can tell hardened observation from guess. When a session teaches a site-specific fact (settle behavior, challenge pattern, variant quirks), append or amend the profile in the same change that used the lesson.

---

## crunchyroll.com

- **Rolling clearance, always.** Crunchyroll runs the `__cf_bm` rolling-cookie model: there is **no durable clearance**. Challenges recur by design for every session and periodically within one — a recurring challenge is routine operation, not a reset, a failure, or a signal that the warm-up was wrong. Re-warm and continue.
- **Root-settle is mandatory, not advisory.** On this site a cold deep link is *the* challenge trigger: land on the root and let it fully settle before any interior navigation, every session, even when the last session ended clean.
- **Wait out managed challenges; never click the checkbox.** When a Turnstile/managed challenge appears, wait for it to auto-clear before any click. Clicking the checkbox reflexively is the known way to make it worse here.

*Source: owner lesson 2026-10-10 (Crunchyroll history tooling — the warmVisit routine and its spec scenario carry the code-level encoding).*
