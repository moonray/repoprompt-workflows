#!/usr/bin/env python3
"""Claude Code hook: block closing a spec without a conformance matrix.

PostToolUse on file edits. When a spec-like file is edited to a terminal lifecycle status
(implemented/shipped/done/...) and no conformance matrix artifact or reference exists, the
hook blocks, directing the agent to run the spec-conformance skill first.

Broad spec detection (works across varied repos): path under spec/specs/specifications, or
*.spec.md, or frontmatter `type` in {spec, specification, contract, feature-spec, featurespec}.
Matrix satisfied by: a sibling `<base>.conformance.*` file, or a frontmatter key
conformance/conformed/audited referencing one.

Scope: catches frontmatter-status closes (a file edit). GitHub-issue-based closes that don't
touch a spec file need a separate issue-close hook in that repo — documented, not handled here.

Source: `.agents/hooks/spec-conformance-gate.py` in this repo (symlink it into your runtime's hooks directory, e.g. `~/.claude/hooks/`).
"""
import json
import os
import re
import sys

_TERMINAL = {
    "implemented", "shipped", "done", "closed", "complete", "completed",
    "resolved", "final", "released", "verified", "approved",
}
_SPEC_TYPES = {"spec", "specification", "contract", "feature-spec", "featurespec"}
_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


_PATCH_FILE_RE = re.compile(
    r"^\*\*\*\s+(?:Add|Update|Delete)\s+File:\s*(.+?)\s*$", re.MULTILINE
)


def _paths_from_patch(command):
    """Codex/opencode deliver file edits as an apply_patch command (no path field)."""
    if not isinstance(command, str):
        return []
    return _PATCH_FILE_RE.findall(command)


def _paths_from_payload(p):
    """All edited paths — a path field (Claude) or an apply_patch command (Codex)."""
    ti = p.get("tool_input")
    if not isinstance(ti, dict):
        return []
    paths = []
    for k in ("file_path", "path", "filePath", "notebook_path"):
        v = ti.get(k)
        if isinstance(v, str) and v:
            paths.append(v)
    paths.extend(_paths_from_patch(ti.get("command")))
    return paths


def _is_spec_path(path):
    n = path.replace("\\", "/")
    return (
        re.search(r"(^|/)(spec|specs|specifications)(/|$)", n) is not None
        or n.endswith(".spec.md")
    )


def _frontmatter(text):
    m = _FRONTMATTER_RE.match(text or "")
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip().lower()] = v.strip().strip('"').strip("'").lower()
    return fm


def _matrix_present(path, fm):
    # explicit frontmatter reference?
    for k in ("conformance", "conformed", "audited", "conformance_matrix"):
        if fm.get(k):
            return True
    # sibling matrix file <stem>.conformance.*  (stem strips both .spec.md and .md)
    d = os.path.dirname(path)
    base = os.path.basename(path)
    if base.endswith(".spec.md"):
        stem = base[:-8]
    elif base.endswith(".md"):
        stem = base[:-3]
    else:
        stem = base
    if not d or not os.path.isdir(d):
        return False
    prefix = stem.lower() + ".conformance"
    for f in os.listdir(d):
        if f.lower().startswith(prefix):
            return True
    return False


def _evaluate(path):
    """Return a block dict if this single edited path trips the closeout gate, else None.

    Factored out of main() so an apply_patch touching several files can check each.
    """
    if not path or not os.path.isfile(path):
        return None
    try:
        head = open(path, encoding="utf-8", errors="ignore").read(4000)
    except OSError:
        return None
    fm = _frontmatter(head)
    if not (_is_spec_path(path) or fm.get("type") in _SPEC_TYPES):
        return None
    if fm.get("status", "") not in _TERMINAL:
        return None
    if _matrix_present(path, fm):
        return None
    stem = os.path.basename(path)[:-3] if path.endswith(".md") else os.path.basename(path)
    return {
        "decision": "block",
        "reason": (
            f"Spec-closeout gate: '{os.path.basename(path)}' is marked status='{fm.get('status')}' "
            f"but has no conformance matrix. Run the spec-conformance skill on this spec to produce "
            f"{stem}.conformance.md (or add a frontmatter 'conformance:' reference) before closing. "
            f"Green tests are not sufficient — they assert code contracts, not spec conformance."
        ),
    }


def main():
    try:
        p = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if p.get("hook_event_name") != "PostToolUse":
        sys.exit(0)
    for path in _paths_from_payload(p):
        block = _evaluate(path)
        if block:
            print(json.dumps(block))
            break
    sys.exit(0)


if __name__ == "__main__":
    main()
