---
title: Chrome Skill
issue: https://github.com/moonray/repoprompt-workflows/issues/6
status: implemented
---

# Chrome Skill

## Problem
Browser automation (chrome-devtools MCP / dev chrometools, Playwright, headed browsers under agent control) trips bot defenses in predictable ways — cold deep links, automation tells, inconsistent fingerprints, repeated probing — so sessions get challenged or banned by sites they were entitled to read. The response was previously either ad hoc rediscovery or a global always-loaded rule paid on every request. Agents need one known, field-verified protocol, invoked exactly when browser automation is actually in use. Two gaps remain on top of that protocol: some sites have an extensively field-tested method that protocol deltas cannot carry, and skill invocation is probabilistic — nothing today protects the session's first navigation, which is exactly the move warm-up governs.

## Goals
1. Warm up by default: root landing and settle before any deep link, once per host per session, before any challenge appears.
2. Handle managed challenges correctly: wait for auto-clear, never reflexively click challenge widgets, treat recurring challenges after prior clearance as the rolling-clearance model.
3. Patch the one loud automation tell (`navigator.webdriver`) via a pre-page-script init script, verified live, without descending into a stealth arms race.
4. Spend cheap moves before heavy ones: host variants, fingerprint-class rotation, pacing after rate bans, fingerprint consistency across all same-window requests including robots.txt probes.
5. Diagnose an apparent wall (self-ban vs their breakage vs real defense) before escalating.
6. Escalate bounded — plain fetch → curl_cffi (bot-wall) → DevTools browser + patches → human-in-the-loop — and terminate hard walls as recorded blind spots.
7. Support per-site overrides layered on the general defaults.
8. Carry extensively-tested per-site methods as a separate progressive-disclosure layer (`references/sites/<domain>.md`), reached from the overrides index, without copying owning repos' implementation code.
9. Enforce skill consultation at the moment of use: a one-shot PreToolUse gate denies the session's first chrome-devtools MCP tool call with a reason directing the agent to this skill (or to proceed under user-testing for own-app UI).
10. Register that gate per backend from one shared script, and document — never paper over — backends that cannot deliver pre-tool events.

## Non-Goals
- Defeating access controls (login walls, paywalls, ToS-prohibited content); politeness limits carry over from bot-wall.
- Plain HTTP fetch blocked by a bot wall (the bot-wall skill owns that rung).
- Cloudflare Radar analytics / URL-scan API work (cloudflare-radar skill).
- Verifying the agent's own app UI end-to-end (user-testing skill).
- Puppeteer-stealth-class CDP-evasion patching beyond `navigator.webdriver`.
- Policing beyond the one-shot nudge: the gate reminds once per session; it does not monitor or block thereafter.
- Pre-call gating on pi until that runtime exposes pre-tool events (documented gap).

## Constraints
- Applies to browser-automation sessions against sites the agent does not control; an agent's own app is out of scope.
- Workspace-portable: no repo-specific paths, clients, or projects inside the skill; site specifics live in `references/site-overrides.md` as behavioral facts only.
- The general protocol carries no site-specific facts; overrides are deltas only.
- The gate fires at most once per session and fails open — a broken or missing gate must never disable browsing.
- Site method files carry the transferable method; canonical implementations stay in their owning repos, cited as source.
- The gate's reason must carve out own-app UI sessions (user-testing scope) so the nudge never blocks legitimate work.

## Scenarios

### S-001: Warm-up is the default entry
- **Given** a browser-automation session is about to start against an external site
- **When** the first navigation is chosen
- **Then** it targets the site root, the page is allowed to settle (challenge markers absent, expected root content present), and no deep link is followed before that; subsequent navigations reuse the warmed tab

### S-002: Managed challenge discipline
- **Given** a managed challenge (e.g. Turnstile) appears during a session
- **When** it is handled
- **Then** the agent waits for auto-clear before any interaction, clicks no challenge widget reflexively, and verifies real content (not a challenge interstitial) before proceeding

### S-003: Rolling clearance is routine
- **Given** a challenge recurs after the same session previously cleared one
- **When** the recurrence is interpreted
- **Then** it is treated as the rolling-clearance model — re-warm and continue — not as a reset, a failure, or a reason to change strategy

### S-004: Automation-tell patch, bounded
- **Given** a DevTools-attached Chrome is used against a defensive site
- **When** automation tells matter
- **Then** `navigator.webdriver` is patched via the navigation tool's init script (running before page scripts) and verified to read `undefined` on the live page; no deeper stealth patching is attempted

### S-005: Cheap variants before heavy ones
- **Given** a 403 or challenge on one variant/fingerprint
- **When** escalation is considered
- **Then** the other host variant (www/apex) and alternate fingerprint classes are each tried at most once, pacing is slowed after rate bans, and a banned pattern is not resubmitted unchanged

### S-006: Fingerprint consistency within a window
- **Given** a scan window mixes politeness probes (robots.txt) with impersonated or browser requests to a host
- **When** those requests are issued
- **Then** all of them present the same fetcher/fingerprint class, so no request advertises a bot the others disown

### S-007: Diagnose before escalating
- **Given** a site appears walled
- **When** the response is chosen
- **Then** the cause is characterized first: self-ban (fix own pattern), their breakage e.g. broken SSL (record as data), or a real defense (walk the ladder)

### S-008: Ladder termination
- **Given** a hard wall (DataDome-class CDP detection or a hard CAPTCHA) persists after the ladder's browser rung
- **When** the terminal outcome is recorded
- **Then** it is either human-in-the-loop (operator clears once; clearance persists; agent harvests) or the URL recorded as a blind spot — never an arms race or hammering

### S-009: Site overrides
- **Given** the target host has a profile in `references/site-overrides.md`
- **When** the session is planned
- **Then** the profile's deltas override the defaults for that host; and site-specific facts learned during a session are recorded as profile deltas in the same change

### S-010: Distinct from neighbor skills
- **Given** a blocked plain HTTP fetch, a Cloudflare Radar analytics request, or verification of the agent's own app UI
- **When** skills are considered
- **Then** this skill does not fire as the primary: bot-wall, cloudflare-radar, or user-testing respectively own those tasks

### S-011: Site method via progressive disclosure
- **Given** the target domain has a `references/sites/<domain>.md` method file routed from the overrides index
- **When** a session plans to drive that domain
- **Then** the agent reads the site method file and applies its tested sequence (warm-up shape, waits, signals, failure handling) in place of the generic defaults, with the profile's deltas still applying

### S-012: Method-not-code boundary
- **Given** a site's extensively-tested implementation lives in an owning repo outside this skill
- **When** its site method file is authored
- **Then** the file carries the transferable method with a source citation, and no implementation code is copied into the skill

### S-013: One-shot PreToolUse gate
- **Given** a registered backend and a session whose first `mcp__chrome-devtools__*` tool call is issued
- **When** the gate runs
- **Then** the call is denied with a reason directing the agent to load the `chrome` skill (stating own-app UI sessions may proceed under user-testing), and every subsequent `mcp__chrome-devtools__*` call in that session executes without gate interference

### S-014: Cross-runtime registration with honest gaps
- **Given** the shared gate script ships in this repo's hook infrastructure
- **When** a runtime is wired
- **Then** Claude Code and Codex register the gate (installer settings registration and `.codex/hooks.json` respectively), opencode registers it pre-call via the plugin's `tool.execute.before` (declared in the repo's `opencode.json`; validated live on opencode 1.18.35, 2026-10-11, #9), and any backend without pre-tool-event delivery (pi) carries a documented gap rather than a claimed parity

## Proposed Surface

### Inputs

| Input | Required | Description |
|---|:---:|---|
| Target site | yes | The host/URL the browser-automation session will drive. |
| Site override profile / method file | no | A matching `<domain>` section in `references/site-overrides.md`, routing to `references/sites/<domain>.md` when an extensively-tested method exists; applied as deltas over the defaults. |

### Output
A settled, verified-real page (snapshot/content harvested through the warmed session), or an explicit characterized outcome (self-ban / their-breakage / hard-wall blind spot), with any new site-specific facts appended to the override profiles.
