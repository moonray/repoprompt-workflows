---
title: Chrometools Skill — Conformance
issue: https://github.com/moonray/repoprompt-workflows/issues/5
spec: chrometools.md
audited: 2026-10-10
---

# Chrometools Skill — Conformance Matrix

Implementation audited: `.agents/skills/chrometools/SKILL.md` + `.agents/skills/chrometools/references/site-overrides.md` (guidance artifacts; evidence = section/line citations).

## Matrix

| Section | Item | Status | Evidence | Note |
|---|---|---|---|---|
| Constraints | Applies to browser-automation sessions against sites the agent does not control | Conformed | `chrometools/SKILL.md:12` | "every browser-automation session against a site you don't control"; own-app UI excluded in description (`:3`) |
| Constraints | Workspace portability — no repo-specific paths, clients, or projects | Conformed | full-text scan of `chrometools/SKILL.md` + `references/site-overrides.md` | grep for repo/project names and absolute paths: 0 matches; provenance carries dates + generic site names only |
| Constraints | General protocol carries no site-specific facts; overrides are deltas only | Conformed | `chrometools/SKILL.md:48–49`, `references/site-overrides.md` (Format section) | SKILL.md body names no site; Crunchyroll facts live only in the override profile |
| Goals | G1 warm-up by default | Conformed | S-001 below; `chrometools/SKILL.md:13–14` | |
| Goals | G2 challenge handling + rolling clearance | Conformed | S-002/S-003 below; `chrometools/SKILL.md:15–17` | |
| Goals | G3 webdriver patch, bounded | Conformed | S-004 below; `chrometools/SKILL.md:22–23` | explicit stop at stealth arms race |
| Goals | G4 cheap moves first | Conformed | S-005/S-006 below; `chrometools/SKILL.md:26–29` | |
| Goals | G5 diagnose before escalating | Conformed | S-007 below; `chrometools/SKILL.md:31–37` | three-cause table |
| Goals | G6 bounded ladder | Conformed | S-008 below; `chrometools/SKILL.md:39–46` | human-in-the-loop terminal; hard wall = blind spot |
| Goals | G7 per-site overrides | Conformed | S-009 below; `chrometools/SKILL.md:48–49` | |
| Scenarios | S-001 Warm-up default entry | Conformed | `chrometools/SKILL.md:13` (root first, before any deep link), `:14` (warm once, reuse tab), `:17` (settle criteria: challenge markers absent, expected content) | |
| Scenarios | S-002 Managed challenge discipline | Conformed | `chrometools/SKILL.md:15` (wait for auto-clear, no reflexive click), `:17` (verify real content) | |
| Scenarios | S-003 Rolling clearance routine | Conformed | `chrometools/SKILL.md:16` | recurring challenge = normal model, re-warm and continue |
| Scenarios | S-004 Automation-tell patch, bounded | Conformed | `chrometools/SKILL.md:22` (initScript before page scripts, verify reads `undefined`), `:23` (no deeper patching) | |
| Scenarios | S-005 Cheap variants before heavy ones | Conformed | `chrometools/SKILL.md:26` (www/apex), `:27` (fingerprint rotation, one attempt per variant), `:28` (rate bans → slow down, do less) | |
| Scenarios | S-006 Fingerprint consistency within a window | Conformed | `chrometools/SKILL.md:29` | robots.txt probe named explicitly as the self-ban vector |
| Scenarios | S-007 Diagnose before escalating | Conformed | `chrometools/SKILL.md:31–37` | self-ban / their-breakage / real-defense each with its response |
| Scenarios | S-008 Ladder termination | Conformed | `chrometools/SKILL.md:44` (human-in-the-loop, cookie persists), `:46` (hard wall = recorded blind spot) | |
| Scenarios | S-009 Site overrides | Conformed | `chrometools/SKILL.md:48–49` (check profile, deltas override, record facts), `references/site-overrides.md` (Format: record in the same change) | Crunchyroll profile present as first entry |
| Scenarios | S-010 Distinct from neighbor skills | Conformed | `chrometools/SKILL.md:3` | description carries explicit negatives for bot-wall, cloudflare-radar, user-testing |
| Proposed Surface | Input: Target site (required) | Conformed | `chrometools/SKILL.md:3` (trigger), `:12` (session scoping) | |
| Proposed Surface | Input: Site override profile (optional) | Conformed | `chrometools/SKILL.md:49`, `references/site-overrides.md` (`## crunchyroll.com`) | |
| Proposed Surface | Output: verified-real page / characterized outcome / appended profile facts | Conformed | `chrometools/SKILL.md:17` (content-verified), `:35–37` (characterized outcomes), `:46` (blind-spot record), `:49` (facts recorded) | |

## Coverage proof

```yaml
audited:
  - Constraints: external-site scope (SKILL.md:12)
  - Constraints: workspace portability (full-text scan)
  - Constraints: overrides are deltas only (SKILL.md:48-49, site-overrides Format)
  - Goals: G1..G7 (each mapped to scenarios)
  - S-001 .. S-010 (all scenarios)
  - Surface: Target site
  - Surface: Site override profile
  - Surface: Output
unreconciled: []
```

Every scenario, Proposed Surface element, stated constraint, and goal was checked; none Diverged or Not-built.
