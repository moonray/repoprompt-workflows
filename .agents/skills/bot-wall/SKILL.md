---
name: bot-wall
description: Use whenever an HTTP fetch of an external site is blocked by a bot wall — 403/Access Denied/"Request unsuccessful" on a site that clearly serves real browsers, a Cloudflare "Just a moment…" / "Checking your browser" challenge, a CAPTCHA or "Enable JavaScript" interstitial, or python requests/urllib/curl/the agent's own fetch tool failing during scraping, research, or site scanning. The fix is a curl_cffi fetch with browser impersonation (impersonate="chrome"), which corrects the TLS/JA3 fingerprint that User-Agent spoofing cannot. Trigger even when nobody says "bot wall" — any blocked, walled, or forbidden fetch of a publicly served page is this skill. Not for Cloudflare Radar analytics or URL-scan API work (that is the cloudflare-radar skill).
---

# Bot walls — fetch with curl_cffi browser impersonation

## Why
Bot walls block non-browser clients at the **TLS layer**: the handshake's JA3 fingerprint identifies urllib/requests/plain curl as automation before a single header is sent, so spoofing a browser User-Agent changes nothing. `curl_cffi` performs the handshake with a real browser's TLS fingerprint (`impersonate="chrome"`), making the request consistent with the browser it claims to be. This is the standard FOSS fix ([lexiforest/curl_cffi](https://github.com/lexiforest/curl_cffi), MIT) — adopted 2026-10-07 after a GitHub options survey and verified live.

## When this applies
Any of these, on a site that clearly serves real browsers:
- 403 / 503 / "Access Denied" / "Request unsuccessful" from urllib, `requests`, plain `curl`, or the agent's own fetch tool
- The response body is a challenge page: "Just a moment…", "Checking your browser", "Attention Required! | Cloudflare", "Enable JavaScript and cookies", a CAPTCHA, or a few KB of challenge JS instead of real content (a `cf-mitigated: challenge` response header is definitive)
- The page loads in a browser but every scripted fetch is walled

## The fix
1. Make curl_cffi importable by the interpreter that will run the fetch — probe first, and install into that environment if missing (`pip install curl_cffi` / `uv pip install curl_cffi`):
   ```python
   from curl_cffi import requests
   r = requests.get(url, timeout=15, impersonate="chrome")
   print(r.status_code, len(r.text))
   ```
   Quick shell probe (substitute the walled URL):
   ```bash
   python3 -c "from curl_cffi import requests; r=requests.get('https://<walled-url>', timeout=15, impersonate='chrome'); print(r.status_code); print(r.text[:300])"
   ```
2. **Verify real content, not just status 200** — challenge pages can also return 200. Check the body for the challenge markers above and for the content you expected before calling the wall cleared.

For scripts that may run where curl_cffi is absent, degrade gracefully (try/except `ImportError` with a plain-fetcher fallback) and self-report which fetcher served each request — a silent fallback hides the wall.

## If impersonation alone does not clear it
Escalate one step at a time, one attempt each — repeating an identical blocked request is noise, not progress:
1. A different impersonation target: `"safari"`, `"firefox"`, or a newer pinned Chrome version exposed by the installed curl_cffi.
2. Real browser automation (it executes the challenge JS): browser tools or Playwright — the **chrome** skill owns that rung (warm-up protocol, `navigator.webdriver` patch, human-in-the-loop finish). Heavier — use only what the task needs.
3. Still walled → record the URL as hard-blocked and move on. Do not hammer the site, and never treat a challenge interstitial as page content in downstream analysis.

## Politeness and limits
This corrects the misclassification of a polite research fetch; it does not defeat access control. Keep fetching polite: respect robots.txt, pace requests with a delay, fetch only public pages, and stop at explicit prohibition — a ToS or login wall means the content is not public. In bulk scans a hard-blocked domain is a data point, not a challenge to defeat.

## Provenance
- Library: https://github.com/lexiforest/curl_cffi
- Adopted 2026-10-07 (GitHub options survey + live verification: impersonated fetch returned 200 with real content where default clients were walled).
