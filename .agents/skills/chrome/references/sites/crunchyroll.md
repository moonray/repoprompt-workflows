# crunchyroll.com — extensively field-tested method

Distilled from the owner's Crunchyroll ingest lanes (the `warmVisit` routine plus the shared lane library, verified 2026-10-09/10). That code is the canonical implementation; this file carries the transferable method for any agent-driven browser session against this domain.

## Warm-up sequence (do not reorder)
1. Navigate to `https://www.crunchyroll.com/` — `domcontentloaded` is sufficient; do not wait for full network idle. Let it settle **~4s**.
2. Only then navigate to the deep target (e.g. `/history`). Settle **~4s** again before reading anything.

## Clearance model
- Rolling `__cf_bm`: **~30-minute lifetime, no durable `cf_clearance`**. Expect a fresh challenge per session and periodically within one — recurring challenge is routine operation, not a failure. Re-warm and continue; don't re-diagnose.

## Challenge detection — explicit signals only
- Title contains `just a moment`; body contains `verify you are human`, `cf-chl`, or `cf-turnstile`.
- Deliberately **no fuzzy text heuristics** — a footer "Log In" link must never hold a wait loop open.

## Managed challenges
- Waits precede any verdict: poll the explicit signals on a bounded loop (field-tested shape: ~5s intervals, up to a few minutes). Most managed challenges auto-clear — never click the widget.
- If an automated context stays challenged after the bounded wait: **one** retry in a fresh (preferably headed) context, re-running the warm-up, again waiting for auto-clear. Involve the human (interactive challenge solve / login) only when the challenge persists past that.

## Data harvest
- Harvest the platform's own authenticated in-page requests (XHR/fetch) rather than constructing auth. If the SPA is lazy about firing them, nudge (scroll) and wait bounded for the request.

*Source: owner's Crunchyroll ingest lanes — `warmVisit` routine + shared lane library (`lane-lib`), lane-pattern spec scenario; verified live 2026-10-09/10.*
