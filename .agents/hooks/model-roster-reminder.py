#!/usr/bin/env python3
"""model-roster-reminder — detection-gated PostToolUse nudge for the model-routing skill.

Fires on roster/oracle tool calls (RPCE app_settings / agent_manage / ask_oracle).
Reads the canonical picks from the model-routing skill's table plus the runtimes'
available-model caches, and emits a reminder ONLY when a pick is missing from its
provider's cache or a strictly newer provider generation exists. Silent otherwise —
the common case costs zero model-context tokens (months pass between releases).
Fails open on any error; env overrides exist for tests.
"""
import json
import os
import re
import sys

TOOL_RE = re.compile(r"^mcp__RepoPromptCE__(?:app_settings|agent_manage|ask_oracle)$")

GPT_NAME_RE = re.compile(r"^GPT-(\d+(?:\.\d+)?)\s+(\S+)$")
CLAUDE_NAME_RE = re.compile(r"^Claude\s+(\S+)\s+(\d+(?:\.\d+)?)$")
GPT_VER_RE = re.compile(r"^gpt-(\d+(?:\.\d+)?)-")
CLAUDE_VER_RE = re.compile(r"^claude-[a-z0-9]+-(\d+(?:-\d+)?)$")


def _candidates_for_skill(cwd):
    cands = [
        os.path.expanduser("~/.claude/skills/model-routing/SKILL.md"),
        os.path.expanduser("~/.agents/skills/model-routing/SKILL.md"),
    ]
    if cwd:
        cands.append(os.path.join(cwd, ".agents", "skills", "model-routing", "SKILL.md"))
    return cands


def _load_skill(cwd):
    path = os.environ.get("MODEL_ROUTING_SKILL")
    if not path:
        for c in _candidates_for_skill(cwd):
            if os.path.isfile(c):
                path = c
                break
    if not path or not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _parse_picks(skill_md):
    """Normalized (provider, slug) picks from the routing table's Model column."""
    picks = []
    in_table = False
    for line in skill_md.splitlines():
        if line.startswith("## "):
            in_table = line.startswith("## Recommended RepoPrompt Architecture")
            continue
        if not in_table or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0] in ("Role", "") or set(cells[0]) <= {"-", " ", ":"}:
            continue
        for name in re.split(r",\s+or\s+", cells[2]):
            name = name.strip()
            m = GPT_NAME_RE.match(name)
            if m:
                picks.append(("gpt", f"gpt-{m.group(1)}-{m.group(2).lower()}"))
                continue
            m = CLAUDE_NAME_RE.match(name)
            if m:
                picks.append(("claude", f"claude-{m.group(1).lower()}-{m.group(2).replace('.', '-')}"))
    return picks


def _collect_strings(node, key, out):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key and isinstance(v, str):
                out.append(v)
            else:
                _collect_strings(v, key, out)
    elif isinstance(node, list):
        for v in node:
            _collect_strings(v, key, out)


def _load_cache(path_env, default_path, key, prefix):
    path = os.environ.get(path_env, "") or default_path
    if os.path.isdir(path):
        # model-catalog is a directory of per-surface caches; the CC one ends -cc.json
        ccs = sorted(
            (f for f in os.listdir(path) if f.endswith("-cc.json")),
            key=lambda f: os.path.getmtime(os.path.join(path, f)),
        )
        path = os.path.join(path, ccs[-1]) if ccs else ""
    if not path or not os.path.isfile(path):
        return []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            data = json.load(fh)
    except Exception:
        return []
    ids = []
    _collect_strings(data, key, ids)
    return [i for i in ids if i.startswith(prefix)]


def _ver(slug, provider):
    if provider == "gpt":
        m = GPT_VER_RE.match(slug)
        part = m.group(1) if m else ""
    else:
        m = CLAUDE_VER_RE.match(slug)
        part = m.group(1).replace("-", ".") if m else ""
    if not part:
        return None
    return tuple(int(p) for p in part.split("."))


def detect(picks, codex_ids, cc_ids):
    """Return a one-line drift reason, or '' when current."""
    caches = {"gpt": codex_ids, "claude": cc_ids}
    findings = []
    for provider, slug in picks:
        if slug not in caches[provider]:
            findings.append(f"pick '{slug}' not found in the {provider} available-model cache")
    for provider, ids in caches.items():
        pick_vers = [_ver(slug, prov) for prov, slug in picks if prov == provider]
        pick_vers = [v for v in pick_vers if v]
        cache_vers = [(v, s) for s in ids for v in [_ver(s, provider)] if v]
        if pick_vers and cache_vers:
            best_v, best_s = max(cache_vers)
            if best_v > max(pick_vers):
                findings.append(f"newer {provider} generation available: '{best_s}' postdates every {provider} pick")
    return "; ".join(findings)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict) or payload.get("hook_event_name") != "PostToolUse":
        return 0
    if not TOOL_RE.match(str(payload.get("tool_name") or "")):
        return 0
    try:
        skill_md = _load_skill(str(payload.get("cwd") or ""))
        if not skill_md:
            return 0  # skill not installed here — nothing to compare against
        picks = _parse_picks(skill_md)
        if not picks:
            return 0  # unparseable table — stay silent rather than guess
        codex_ids = _load_cache(
            "MODEL_ROSTER_CODEX_CACHE",
            os.path.expanduser("~/.codex/models_cache.json"),
            "slug",
            "gpt-",
        )
        cc_ids = _load_cache(
            "MODEL_ROSTER_CC_CACHE",
            os.path.expanduser("~/.claude/cache/model-catalog"),
            "id",
            "claude-",
        )
        reason = detect(picks, codex_ids, cc_ids)
        if reason:
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        f"MODEL ROUTING DRIFT: {reason}. Surface this to the user and suggest "
                        "the model-routing skill's re-evaluation; do not silently re-route."
                    ),
                }
            }))
    except Exception:
        return 0  # fail open — detection must never break the tool call
    return 0


if __name__ == "__main__":
    sys.exit(main())
