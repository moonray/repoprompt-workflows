---
name: chrometools
description: Use whenever driving or visiting a website with browser automation — the chrome-devtools MCP (dev chrometools: navigate_page, take_snapshot, evaluate_script), Playwright, or any headed browser under agent control — especially external, unfamiliar, or bot-defended sites. Carries the warm-up protocol (land on the site root and let it settle before any deep link; wait out managed challenges instead of clicking them), the navigator.webdriver automation-tell patch, rate-ban and fingerprint-consistency discipline, and the escalation ladder ending in human-in-the-loop, plus per-site override profiles. Trigger even when nobody says "warm-up" — any browser-automation session against a site you don't control is this skill. Not for plain HTTP fetches blocked by a bot wall (that is bot-wall), Cloudflare Radar analytics (cloudflare-radar), or verifying your own app's UI (user-testing).
---

# Driving websites with browser automation

## Why
A browser under agent control trips bot defenses in predictable ways: it arrives **cold** (no cookies, no history) and lands on deep links, it carries automation tells, and it probes repeatedly. Sites answer with challenges and 403s that a warmer, calmer session never sees. The fixes are cheap and ordered — but only if you diagnose first, because an apparent "wall" is often your own fingerprint mismatch or the site's own breakage, not a defense aimed at you.

## The default warm-up protocol
Apply to every browser-automation session against a site you don't control — before any challenge appears, not after:

1. **Land on the site root first** and let the page settle before following any deep link. Cold deep-links are the single most challenge-triggering pattern: defenses score the session on its first moves, and a fresh browser jumping straight to an interior page looks like a scraper.
2. **Warm once per host per session**, then reuse that tab/page for the session's navigations. A second warmed context buys nothing and doubles your footprint.
3. **When a managed challenge appears, wait for it to auto-clear before doing anything.** Never click a Turnstile checkbox (or any challenge widget) reflexively — most managed challenges resolve themselves, and clicking can restart or harden them. Interact only after waiting has visibly failed.
4. **Expect rolling clearance.** Many defenses (`__cf_bm`-class) issue short-lived cookies by design: a challenge you cleared an hour ago recurring now is the normal model, not a reset or a session failure. Re-warm and continue; don't re-diagnose from scratch.
5. **Verify real content, not load events.** A challenge interstitial can render as a "loaded" page. Check for challenge markers ("Just a moment…", "Checking your browser", a 1–2 KB body, CAPTCHA iframe) and for the content you actually came for before proceeding.

## Automation tells: patch `navigator.webdriver`, then stop
In a DevTools-attached headed Chrome, exactly one loud automation signal was observed in practice: `navigator.webdriver: true`, set by the automation launch flags. Everything else (GPU string, screen dimensions, headed window, genuine UA) already read as the daily browser.

- Patch it with the navigation tool's **init script** (e.g. `navigate_page`'s `initScript`), which runs on each new document *before* the page's own scripts: `Object.defineProperty(navigator, 'webdriver', {get: () => undefined})` — then verify on the live page that it reads `undefined`/`false` before trusting the rung.
- **Do not go further down the stealth path.** Some defenses detect the CDP instrumentation itself; patching around that is an arms race (puppeteer-stealth-class) that routinely loses. The next rung is a human, not more patches.

## Cheap moves before heavy ones
- **Try the other host variant.** An apex that 403s often serves via `www` (and vice versa) — proven with a real Chrome session where apex was walled and `www` loaded clean.
- **Rotate the fingerprint class before assuming a hard wall.** The most-used scraper fingerprint (Chrome's TLS/JA3) is sometimes denylisted specifically while Safari's or Firefox's passes. One attempt per variant, then stop.
- **Repeated probing bans you even with a valid fingerprint.** Rate bans set in after a burst and then reject everything, including what worked before. Slow down, space out attempts, and prefer a fresh window/context for a retry campaign — but treat a rate ban as a signal to do less, not more.
- **Keep your fingerprint consistent across every request to a host** — including "politeness" probes. Fetching `robots.txt` with a bot-ish default client seconds before an impersonated or browser request hands the WAF a mismatch and gets the IP banned: each request then looks like the bot the earlier probe advertised. Route all same-window traffic through the same fetcher.

## Diagnose before escalating
Three sites that all "look walled" can be three different things, and each has a different correct response:

| Apparent wall | Actual cause | Response |
|---|---|---|
| 403 after your earlier requests worked | **Your self-ban** (fingerprint mismatch in the window, or rate) | Fix your own request pattern; re-scan later |
| TLS errors / broken SSL on apex and www | **Their breakage** | Record as a data point (sometimes a targeting/rescue signal); don't siege |
| Consistent challenge under every variant | **A real defense** | Walk the ladder below |

## The escalation ladder
Climb one rung at a time; each rung is heavier than the one below and most tasks never leave the first:

1. **Plain fetch** — baseline; fixes nothing but costs nothing.
2. **curl_cffi browser impersonation** — fixes fingerprint-class walls (see the **bot-wall** skill; it owns this rung).
3. **DevTools-attached browser + warm-up + `webdriver` patch** (this skill's core) — executes challenge JS, presents as a real browser; fixes automation-flag and JS-challenge walls.
4. **Human-in-the-loop** — the operator solves the challenge once in the visible browser window (~30 seconds); the clearance cookie persists and the agent then reads/harvests normally. This is the real last ditch, and it beats any arms race.
5. **Hard walls** (DataDome-class with CDP detection, hard CAPTCHAs): nothing fieldable. Record the URL as a blind spot and move on — a hard-blocked domain is a data point, not a challenge to defeat.

## Site overrides
Defaults above are the general protocol; some sites warrant per-site tweaks (stricter settle times, known challenge behavior, variant quirks). Before driving a known target, check [`references/site-overrides.md`](references/site-overrides.md) for a profile and let its deltas override the defaults. When a session teaches you a site-specific fact, record it there — that file is the override/tweak layer, kept separate so the default stays general.

## Provenance
- 2026-10-08, dealer-site scan pilot (212 domains): the ladder, the lone `navigator.webdriver` tell, the www-variant fix, the robots-fingerprint self-ban, impersonation rotation, rate bans, human-in-the-loop finish — all demonstrated live.
- 2026-10-10, Crunchyroll: root-settle warm-up, rolling `__cf_bm` model, challenge auto-clear discipline — owner lesson, encoded as the first site override.
