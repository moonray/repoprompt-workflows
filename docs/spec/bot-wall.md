---
title: Bot Wall Skill
issue: none
status: implemented
---

# Bot Wall Skill

## Problem
Research and scanning fetches of publicly served sites get blocked by bot walls (403s, Cloudflare-style challenge pages) because default HTTP clients present non-browser TLS fingerprints. Agents need one known, verified response so every runtime and repo handles the wall the same way instead of rediscovering or working around it ad hoc.

## Goals
1. Recognize a bot wall from observable symptoms (status code + challenge-page body markers) on a site that serves real browsers.
2. Apply the standard fix: a curl_cffi fetch with browser impersonation.
3. Verify the fix by content, not status code alone.
4. Escalate bounded (alternate impersonation target → real browser automation → record hard-blocked) without hammering the site.
5. Keep fetching polite and within public-content limits.

## Non-Goals
- Defeating access controls (login walls, paywalls, ToS-prohibited content).
- Cloudflare Radar analytics or URL-scan API work (the `cloudflare-radar` skill).
- Proxy rotation or scraping infrastructure beyond the single-fetch fix.

## Constraints
- curl_cffi must be importable by the interpreter performing the fetch; if absent it is installed into that environment.
- The skill is workspace-portable: no repo-specific paths or scripts inside it.

## Scenarios

### S-001: Default client walled
- **Given** a fetch of a publicly served site returns 403/503/"Access Denied" or a challenge-page body from urllib/requests/curl/the agent fetch tool
- **When** the wall is recognized
- **Then** the next fetch uses curl_cffi with `impersonate="chrome"`

### S-002: Verify by content
- **Given** an impersonated fetch returns HTTP 200
- **When** the body is checked
- **Then** success is declared only if challenge markers are absent and expected content is present; a 200 challenge page is treated as still-walled

### S-003: Library missing, ad-hoc fetch
- **Given** curl_cffi is not importable in the interpreter that will perform an ad-hoc fetch
- **When** the fix is applied
- **Then** the library is installed into that interpreter (after an import probe) and the impersonated fetch is retried — never a claim of the impersonated fix without it

### S-004: Library missing, long-lived script
- **Given** a script that may run in environments without curl_cffi
- **When** the script is written or retrofitted
- **Then** it imports curl_cffi behind try/except with a plain-fetcher fallback, and every fetch result records which fetcher served it

### S-005: Impersonation insufficient
- **Given** the chrome-impersonated fetch is still walled
- **When** escalation runs
- **Then** at most one fetch attempt is made per escalation step (alternate impersonation target, then browser automation when the task needs rendered content), and the terminal outcome is either fetched content or the URL recorded as hard-blocked in the run's output

### S-006: Politeness envelope
- **Given** any walled-site fetching
- **When** the fix is used
- **Then** robots.txt is respected, requests are paced, only public pages are fetched, and explicit prohibition ends the attempt

### S-007: Distinct from cloudflare-radar
- **Given** a request about Cloudflare Radar analytics or URL-scan API checks
- **When** skills are considered
- **Then** this skill does not fire (no fetch is blocked); `cloudflare-radar` serves it

## Proposed Surface

### Inputs

| Input | Required | Description |
|---|:---:|---|
| Walled URL | yes | The publicly served URL whose fetch is blocked. |
| Fetch context | no | The fetching client/script to retrofit, when the wall appears inside existing code. |

### Output
Fetched real content via impersonation (with the fetcher identified), or an explicit hard-blocked record — never challenge-page content treated as page content.
