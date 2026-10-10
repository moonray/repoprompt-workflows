---
title: Bot Wall Skill — Conformance
issue: none
spec: bot-wall.md
audited: 2026-10-07
---

# Bot Wall Skill — Conformance Matrix

Implementation audited: `.agents/skills/bot-wall/SKILL.md` (guidance artifact; evidence = section/line citations).

## Matrix

| Section | Item | Status | Evidence | Note |
|---|---|---|---|---|
| Constraints | curl_cffi importable by the fetching interpreter; install if absent | Conformed | `bot-wall/SKILL.md:18` | probe-first, install into that environment (`pip`/`uv pip`) |
| Constraints | Workspace portability — no repo-specific paths | Conformed | full-text scan of `bot-wall/SKILL.md` | grep for repo paths/names: 0 matches |
| Scenarios | S-001 Default client walled → impersonated fetch | Conformed | `bot-wall/SKILL.md:12–16` (symptom triggers), `:21` (`impersonate="chrome"` code) | symptom list covers urllib/requests/curl/agent fetch tool |
| Scenarios | S-002 Verify by content, not status alone | Conformed | `bot-wall/SKILL.md:28` | 200 challenge page treated as still-walled |
| Scenarios | S-003 Library missing, ad-hoc fetch | Conformed | `bot-wall/SKILL.md:18` | probe → install → retry; no unbacked claim of the fix |
| Scenarios | S-004 Library missing, long-lived script | Conformed | `bot-wall/SKILL.md:30` | try/except `ImportError` fallback + per-request fetcher self-report |
| Scenarios | S-005 Bounded escalation | Conformed | `bot-wall/SKILL.md:33–36` | one attempt per step; browser automation "use only what the task needs" ≡ "when the task needs rendered content"; terminal outcome fetched content or hard-blocked record |
| Scenarios | S-006 Politeness envelope | Conformed | `bot-wall/SKILL.md:39` | robots.txt, pacing delay, public pages only, stops at prohibition |
| Scenarios | S-007 Distinct from cloudflare-radar | Conformed | `bot-wall/SKILL.md:3` | description carries the explicit negative clause |
| Proposed Surface | Input: Walled URL (required) | Conformed | `bot-wall/SKILL.md:3` (trigger), `:26` (`<walled-url>` probe placeholder) | |
| Proposed Surface | Input: Fetch context (optional retrofit) | Conformed | `bot-wall/SKILL.md:30` | retrofit guidance targets existing fetching scripts |
| Proposed Surface | Output: content-verified fetch with fetcher identified, or hard-blocked record | Conformed | `bot-wall/SKILL.md:28` (content check), `:30` (fetcher identified), `:36` (hard-blocked record; challenge interstitial never treated as content) | |

## Coverage proof

```yaml
audited:
  - Constraints: importability (SKILL.md:18)
  - Constraints: workspace portability (full-text scan)
  - S-001 .. S-007 (all scenarios)
  - Surface: Walled URL
  - Surface: Fetch context
  - Surface: Output
unreconciled: []
```

Every scenario, Proposed Surface element, and stated constraint was checked; none Diverged or Not-built.
