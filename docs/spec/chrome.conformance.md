---
title: Chrome Skill — Conformance
issue: https://github.com/moonray/repoprompt-workflows/issues/6
spec: chrome.md
audited: 2026-10-10
---

# Chrome Skill — Conformance Matrix

Implementation audited: `.agents/skills/chrome/SKILL.md` + `references/` + `.agents/hooks/chrome-gate.py` + registrations (guidance artifact + hook; evidence = section/line citations and live probes).

## Matrix

| Section | Item | Status | Evidence | Note |
|---|---|---|---|---|
| Constraints | Applies to browser-automation sessions against sites the agent does not control | Conformed | `chrome/SKILL.md:12–13` | own-app UI excluded in description (`:3`) |
| Constraints | Workspace portability — no repo-specific paths, clients, or projects | Conformed | full-text scan of skill + references | grep for repo/project names and absolute paths: 0 matches; site sources cite owner tooling generically |
| Constraints | General protocol carries no site-specific facts; overrides are deltas only | Conformed | `chrome/SKILL.md:50–51`, `references/site-overrides.md` (Format) | SKILL.md body names no site; Crunchyroll facts live in profile + `sites/` file |
| Constraints | Gate fires at most once per session, fails open | Conformed | `chrome-gate.py` (marker `O_EXCL` claim; every error path returns allow) | script-level probe: deny-once → silent allow → non-matching untouched; live probe: first call denied, retry passed |
| Constraints | Site method files carry the method; canonical implementations stay with owning repos | Conformed | `references/sites/crunchyroll.md` (method + source line, no code) | |
| Constraints | Gate reason carves out own-app UI | Conformed | `chrome-gate.py` `REASON` ("If this is your own app's UI (user-testing scope), proceed as you were") | |
| Goals | G1–G7 (protocol, challenge handling, webdriver patch, cheap moves, diagnose, ladder, overrides) | Conformed | S-001–S-010 below | unchanged from #5 closeout, re-cited |
| Goals | G8 per-site tested method layer | Conformed | S-011/S-012 below; `chrome/SKILL.md:50–51`, `references/sites/crunchyroll.md` | |
| Goals | G9 one-shot gate at moment of use | Conformed | S-013 below; live probe this session | |
| Goals | G10 per-backend registration with honest gaps | Conformed with waived divergence | S-014 below | Codex delivery unverified — see waiver in coverage proof |
| Scenarios | S-001 Warm-up default entry | Conformed | `chrome/SKILL.md:14` (root first), `:15` (warm once, reuse tab), `:18` (settle criteria) | |
| Scenarios | S-002 Managed challenge discipline | Conformed | `chrome/SKILL.md:16` (wait for auto-clear), `:18` (verify real content) | |
| Scenarios | S-003 Rolling clearance routine | Conformed | `chrome/SKILL.md:17`; `references/sites/crunchyroll.md` (~30-min `__cf_bm` concrete) | |
| Scenarios | S-004 Automation-tell patch, bounded | Conformed | `chrome/SKILL.md:20–25` (initScript patch + stop) | |
| Scenarios | S-005 Cheap variants before heavy ones | Conformed | `chrome/SKILL.md:26–30` (www/apex, rotation, rate bans) | |
| Scenarios | S-006 Fingerprint consistency within a window | Conformed | `chrome/SKILL.md:30` (robots.txt self-ban named) | |
| Scenarios | S-007 Diagnose before escalating | Conformed | `chrome/SKILL.md:32–38` (three-cause table) | |
| Scenarios | S-008 Ladder termination | Conformed | `chrome/SKILL.md:47` (human-in-the-loop), `:48` (blind spot) | |
| Scenarios | S-009 Site overrides | Conformed | `chrome/SKILL.md:50–51`, `references/site-overrides.md` (Format: same-change recording) | |
| Scenarios | S-010 Distinct from neighbor skills | Conformed | `chrome/SKILL.md:3` (negatives for bot-wall, cloudflare-radar, user-testing) | |
| Scenarios | S-011 Site method via progressive disclosure | Conformed | `chrome/SKILL.md:50–51` (routing to `sites/<domain>.md`), `site-overrides.md` Crunchyroll `Tested method:` line, `sites/crunchyroll.md` (full tested sequence) | |
| Scenarios | S-012 Method-not-code boundary | Conformed | `sites/crunchyroll.md` (sequence/waits/signals/failure handling + source citation; no implementation code; canonical code stays with owner) | |
| Scenarios | S-013 One-shot PreToolUse gate | Conformed | Live probe (this session): first `mcp__chrome-devtools__list_pages` denied with reason; after loading the `chrome` skill, retry passed with no interference. Registration: `~/.claude/settings.json` PreToolUse `^mcp__chrome-devtools__` via installer (+1, backup taken); `chrome-gate.py` script-level probe deny-once/allow-after | Claude Code end-to-end verified |
| Scenarios | S-014 Cross-runtime registration with honest gaps | Diverged (waived, see below) | Conformed: Claude Code registration verified live; installer `regs` entry (`scripts/install.sh` `register_claude_settings`), `.codex/hooks.json` PreToolUse block (dual-form matcher), `.agents/hooks/README.md` row + manual block; opencode/pi documented gaps in spec Non-Goals. Diverged: Codex — wiring shipped in the sanctioned shape but no gate denial observed in `codex exec` 0.148 across two matcher forms (`^mcp__chrome-devtools__`, `+|^chrome-devtools/`); a wildcard-logger diagnostic hung >240s and was aborted inconclusive | Waiver reason in coverage proof |
| Proposed Surface | Input: Target site (required) | Conformed | `chrome/SKILL.md:3`, `:12–13` | |
| Proposed Surface | Input: Site override profile / method file (optional) | Conformed | `chrome/SKILL.md:50–51`, `site-overrides.md`, `sites/crunchyroll.md` | |
| Proposed Surface | Output: verified-real page / characterized outcome / appended profile facts | Conformed | `chrome/SKILL.md:18`, `:35–38`, `:48`, `:51` | |

## Coverage proof

```yaml
audited:
  - Constraints: external-site scope (SKILL.md:12-13)
  - Constraints: workspace portability (full-text scan)
  - Constraints: deltas-only overrides (SKILL.md:50-51)
  - Constraints: gate once-per-session + fail-open (chrome-gate.py + probes)
  - Constraints: method-not-code (sites/crunchyroll.md)
  - Constraints: own-app carve-out in gate reason (chrome-gate.py REASON)
  - Goals: G1..G10 (each mapped to scenarios)
  - S-001 .. S-014 (all scenarios)
  - Surface: Target site
  - Surface: Site override profile / method file
  - Surface: Output
unreconciled:
  - item: S-014 (Codex delivery half)
    status: Diverged — waived
    reason: Codex 0.148 exec showed no gate denial across two matcher variants
      (2026-10-10, rpw repo, --dangerously-bypass-hook-trust, chrome-devtools
      list_pages passed through); the decisive wildcard-logger diagnostic hung
      past its 240s bound and was aborted, so MCP-tool PreToolUse delivery
      (and payload/tool naming) in codex is UNVERIFIED, not disproven. The
      fail-open wiring ships harmlessly in .codex/hooks.json; enforcement on
      Codex is blocked-on-verification, tracked on issue #6. Accepted because
      Claude Code (the primary runtime) is verified end-to-end and the spec's
      own S-014 requires documenting rather than papering over the gap.
```

Every scenario, Proposed Surface element, stated constraint, and goal was checked; the single divergence is the waived, tracked Codex-delivery item above.
