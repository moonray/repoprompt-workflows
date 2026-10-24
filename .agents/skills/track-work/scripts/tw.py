#!/usr/bin/env python3
"""tw — deterministic track-work CLI adapter (issue #1; spec S-033–S-040, docs/spec/track-work.md).

Contract (S-033): every command invocation prints exactly ONE machine-readable JSON
envelope on stdout — {"ok": true|false, "command": <name>, ...} plus a typed
{"error": {"code", "message"}} on failure. Exit codes: 0 success, 2 usage errors,
1 every other failure. --help prints human text instead (documented exception).

Noninteractive (--noninteractive or TW_NONINTERACTIVE=1, S-039): any operation that
would require a confirmation or hits a failed capability probe returns error.code
"blocked" — never a prompt.

Test seam: --gh <path> overrides the gh executable (used by the adversarial suite;
identity never derives from probe outcomes, S-034).

Status: T4 — file backend commands (create/list/status/close) over issue.sh,
deterministic redaction (S-036), file-half label validation (S-037), close
landed-evidence (S-038 file half). GitHub commands land in T5, migrate in T6
(docs/plans/track-work-cli.md).
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

COMMANDS = ("resolve", "list", "create", "status", "close", "migrate")

ERROR_CODES = (
    "usage", "origin-rejected", "capability", "blocked", "unknown-label",
    "cardinality", "invalid-transition", "not-found", "wrong-repository",
    "landed-evidence", "conflict",
)

_GITHUB_OWNER_REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_VALID_BACKENDS = ("auto", "github", "file")


class TwError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


class UsageError(TwError):
    def __init__(self, message):
        super().__init__("usage", message)


class Context:
    """One command invocation: parsed global flags + the command's own args."""

    def __init__(self, command, args, noninteractive, gh):
        self.command = command
        self.args = args
        self.noninteractive = noninteractive
        self.gh = gh


def split_global_flags(argv):
    """Pull global flags (--noninteractive, --gh PATH) from anywhere; keep the rest in order."""
    noninteractive = os.environ.get("TW_NONINTERACTIVE", "") == "1"
    gh = "gh"
    rest = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--noninteractive":
            noninteractive = True
        elif a == "--gh":
            i += 1
            if i >= len(argv):
                raise UsageError("--gh requires a path")
            gh = argv[i]
        else:
            rest.append(a)
        i += 1
    return noninteractive, gh, rest


def envelope(ok, command, payload=None, error=None, **extra):
    env = {"ok": ok, "command": command}
    env.update(extra)
    if payload:
        env.update(payload)
    if error is not None:
        env["error"] = {"code": error.code, "message": error.message}
    return env


# ---------------------------------------------------------------- T3: resolve

def _git(args, cwd=None):
    r = subprocess.run(["git", *args], capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout.strip()


def _run_quiet(argv):
    """Run a probe command; an unexecutable/missing binary is rc 127, never a crash
    (S-002: a missing gh is a reported capability failure, not a traceback)."""
    try:
        r = subprocess.run(argv, capture_output=True, text=True)
        return r.returncode, r.stdout
    except (FileNotFoundError, OSError):
        return 127, ""


def _repo_root():
    rc, out = _git(["rev-parse", "--show-toplevel"])
    if rc != 0:
        raise UsageError("tw must run inside a git repository (resolve needs repo identity)")
    return out


def _origin_urls(root):
    """All push URLs for origin, else all fetch URLs; None if no origin.

    Reads git config directly (`--get-all`): `git remote get-url --push` prints only
    the FIRST pushurl, which would hide multi-push ambiguity (S-015)."""
    rc, out = _git(["config", "--get-all", "remote.origin.pushurl"], cwd=root)
    if rc != 0 or not out:
        rc, out = _git(["config", "--get-all", "remote.origin.url"], cwd=root)
    if rc != 0 or not out:
        return None
    return [u for u in out.splitlines() if u] or None


def _parse_origin(urls):
    """Classify origin per the exact-forms rule (S-001/S-015).

    Returns ("github", "owner/repo") | ("non-github", host) | ("rejected", reason).
    A GitHub-shaped origin that fails strict parsing (userinfo, lookalike host,
    multiple push URLs, unaccepted form) is REJECTED — never treated as non-GitHub,
    never silently selecting the file backend (the second-ledger failure).
    """
    if len(urls) > 1:
        return "rejected", "multiple push URLs for origin are ambiguous — keep exactly one push URL"
    url = urls[0]
    m = re.match(r"^https://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    if not m:
        m = re.match(r"^git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$", url)
    if m:
        repo = "%s/%s" % (m.group(1), m.group(2))
        if _GITHUB_OWNER_REPO.match(repo):
            return "github", repo
        return "rejected", "owner/repo has unsupported characters: %s" % repo
    # Not an accepted form — classify the failure before ever calling it non-GitHub.
    host, had_userinfo = None, False
    m = re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://([^/@]*@)?([^/:]+)", url)
    if m:
        # `git@` is the standard ssh user, not credentials: only real userinfo
        # (anything else, incl. user:pass@) marks the URL as credential-bearing.
        had_userinfo = m.group(1) is not None and m.group(1) != "git@"
        host = m.group(2).lower()
    elif ":" in url.split("/", 1)[0]:  # scp-like git@host:owner/repo
        hostpart = url.split(":", 1)[0]
        had_userinfo = "@" in hostpart
        host = hostpart.rsplit("@", 1)[-1].lower()
    if host == "github.com":
        if had_userinfo:
            return ("rejected",
                    "userinfo in the GitHub origin URL is not accepted — strip it from the remote URL, "
                    "or pin backend: github + github.repo in .agents/track-work.config.md")
        return ("rejected",
                "GitHub origin is not one of the two accepted forms "
                "(https://github.com/OWNER/REPO[.git] | git@github.com:OWNER/REPO[.git]) — "
                "normalize the remote URL, or pin backend: github + github.repo in config")
    if host and "github" in host:
        return ("rejected",
                "lookalike host '%s' is not github.com — if this really is your GitHub remote, pin "
                "backend: github + github.repo in .agents/track-work.config.md" % host)
    return "non-github", (host or "unparsed-remote")


def _parse_flow_list(value):
    """`[a, b]` -> ['a', 'b']; returns None when the value is not a flow list."""
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        return None
    inner = value[1:-1].strip()
    if not inner:
        return []
    return [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]


def _read_config(root):
    """Trusted-base config subset the CLI needs, from the first ```yaml fence of
    .agents/track-work.config.md: backend, issues_dir, github.repo (T3) plus
    labels.dimensions, close_gate.exempt_labels, redaction.{repo_visibility,
    secrets, redact_absolute_paths} (T4). A bounded yaml subset — fixed key
    shapes at fixed indentation; unknown keys and unparseable lines are skipped."""
    cfg = {}
    path = os.path.join(root, ".agents", "track-work.config.md")
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return cfg
    m = re.search(r"```yaml\n(.*?)```", text, re.DOTALL)
    if not m:
        return cfg
    section = None      # top-level block key: github:, labels:, close_gate:, redaction:
    subsection = None   # labels.dimensions
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if indent == 0:
            key, _, value = stripped.partition(":")
            value = value.strip()
            section = key if not value else None
            subsection = None
            if key in ("backend", "issues_dir") and value:
                cfg[key] = value
            continue
        key, _, value = stripped.partition(":")
        value = value.strip()
        if section == "github" and indent == 2:
            if key == "repo" and value:
                cfg["github_repo"] = value
            continue
        if section == "labels":
            if indent == 2 and key == "dimensions" and not value:
                subsection = "dimensions"
            elif subsection == "dimensions" and stripped.startswith("-"):
                dm = re.match(r"-\s*\{\s*prefix:\s*([A-Za-z0-9_-]+)\s*,\s*count:\s*([A-Za-z0-9_]+)\s*\}",
                              stripped)
                if dm:
                    cfg.setdefault("dimensions", []).append((dm.group(1), dm.group(2)))
            continue
        if section == "close_gate" and indent == 2 and key == "exempt_labels":
            parsed = _parse_flow_list(value)
            if parsed is not None:
                cfg["exempt_labels"] = parsed
            continue
        if section == "redaction" and indent == 2:
            red = cfg.setdefault("redaction", {})
            if key == "repo_visibility" and value in ("public", "private"):
                red["repo_visibility"] = value
            elif key == "secrets":
                parsed = _parse_flow_list(value)
                if parsed is not None:
                    red["secrets"] = parsed
            elif key == "redact_absolute_paths":
                red["redact_absolute_paths"] = value.lower() != "false"
            continue
    return cfg


def _resolve_identity(ctx):
    """The identity ladder (S-001/S-034): env override > config override > origin > file.
    Capability never participates (S-002): probes run after identity is fixed."""
    root = _repo_root()
    cfg = _read_config(root)

    env_backend = os.environ.get("TRACK_WORK_BACKEND", "").strip()
    if env_backend and env_backend not in _VALID_BACKENDS:
        raise UsageError("TRACK_WORK_BACKEND must be one of auto|github|file, got: %s" % env_backend)
    cfg_backend = cfg.get("backend", "")
    if cfg_backend and cfg_backend not in _VALID_BACKENDS:
        raise UsageError("config backend must be one of auto|github|file, got: %s" % cfg_backend)

    urls = _origin_urls(root)
    origin_kind, origin_val = None, None
    if urls:
        origin_kind, origin_val = _parse_origin(urls)
        if origin_kind == "rejected":
            raise TwError("origin-rejected", origin_val)

    backend = selected_by = repo = None
    if env_backend in ("github", "file"):
        backend, selected_by = env_backend, "env-override"
    elif cfg_backend in ("github", "file"):
        backend, selected_by = cfg_backend, "config-override"
    elif origin_kind == "github":
        backend, selected_by, repo = "github", "origin", origin_val
    else:
        backend = "file"
        selected_by = "no-origin" if origin_kind is None else "non-github-origin"

    if backend == "github" and repo is None:
        pinned = cfg.get("github_repo", "")
        if origin_kind == "github":
            repo = origin_val
        elif pinned and _GITHUB_OWNER_REPO.match(pinned):
            repo = pinned
        elif pinned:
            raise UsageError("github.repo in config is not owner/repo: %s" % pinned)
        else:
            raise UsageError("backend 'github' selected without a GitHub origin and without "
                             "github.repo: owner/repo in .agents/track-work.config.md")

    return {
        "root": root,
        "backend": backend,
        "selected_by": selected_by,
        "repo": repo,
        "issues_dir": cfg.get("issues_dir", ".agents/issues") if backend == "file" else None,
    }


def _probe_capability(ctx, repo):
    """Capability probes (S-002/S-003) — reported, never identity-changing. Every
    repo-scoped call is bound to the normalized repo (S-015)."""
    checked = []
    rc, _out = _run_quiet([ctx.gh, "--version"])
    checked.append("gh-present")
    if rc != 0:
        return {"ok": False, "failed": "gh-present", "error_class": "gh-missing"}
    rc, _out = _run_quiet([ctx.gh, "auth", "status"])
    checked.append("gh-auth")
    if rc != 0:
        return {"ok": False, "failed": "gh-auth", "error_class": "gh-auth"}
    rc, out = _run_quiet(
        [ctx.gh, "repo", "view", repo, "--json", "nameWithOwner,hasIssuesEnabled"])
    checked.append("gh-repo-view")
    if rc != 0:
        return {"ok": False, "failed": "gh-repo-view", "error_class": "gh-api"}
    try:
        data = json.loads(out)
    except ValueError:
        return {"ok": False, "failed": "gh-repo-view", "error_class": "gh-api",
                "note": "unparseable repo view output"}
    if data.get("nameWithOwner") != repo:
        return {"ok": False, "failed": "gh-repo-view", "error_class": "wrong-repository",
                "note": "repo view resolved to %r" % data.get("nameWithOwner")}
    if not data.get("hasIssuesEnabled"):
        return {"ok": False, "failed": "gh-issues-enabled", "error_class": "issues-disabled"}
    return {"ok": True, "checked": checked}


def cmd_resolve(ctx):
    ident = _resolve_identity(ctx)
    return {
        "backend": ident["backend"],
        "selected_by": ident["selected_by"],
        "repo": ident["repo"],
        "issues_dir": ident["issues_dir"],
        "capability": _probe_capability(ctx, ident["repo"]) if ident["backend"] == "github" else None,
    }


def dispatch(ctx):
    """Execute one command; return its payload dict (success) or raise TwError."""
    if ctx.command == "resolve":
        return cmd_resolve(ctx)
    if ctx.command == "migrate":
        raise TwError("blocked", "migrate is not implemented yet (lands in T6)")
    ident = _resolve_identity(ctx)
    if ident["backend"] != "file":
        raise TwError("blocked", "%s on the GitHub backend lands in T5 (resolved: %s); file "
                      "commands need a file backend — TRACK_WORK_BACKEND=file override or "
                      "migrate first" % (ctx.command, ident["repo"] or "github"))
    handler = {"list": cmd_list_file, "create": cmd_create_file,
               "status": cmd_status_file, "close": cmd_close_file}[ctx.command]
    return handler(ctx, ident)


def main(argv):
    try:
        noninteractive, gh, rest = split_global_flags(argv)
        if rest and rest[0] in ("-h", "--help"):
            print(__doc__)
            return 0
        if not rest:
            raise UsageError("missing command; one of: %s" % ", ".join(COMMANDS))
        command = rest[0]
        if command not in COMMANDS:
            raise UsageError("unknown command: %s (one of: %s)" % (command, ", ".join(COMMANDS)))
        ctx = Context(command, rest[1:], noninteractive, gh)
        payload = dispatch(ctx)
        env = envelope(True, command, payload, noninteractive=noninteractive)
        code = 0
    except UsageError as e:
        attempted = rest[0] if rest else None
        env = envelope(False, attempted, error=e)
        code = 2
    except TwError as e:
        env = envelope(False, command, error=e, noninteractive=noninteractive)
        code = 1
    print(json.dumps(env))
    return code

# ---------------------------------------------------------------- T4: file backend
# The file backend WRAPS issue.sh (locking, ID allocation, atomic writes stay in the
# engine); the CLI adds the typed contract, redaction, label validation, read-backs,
# and landed-evidence. Real file items are referenced in commit messages as
# ISSUE-NNN (padded) or ISSUE-N (unpadded) — both accepted, digit-bounded.

ISSUE_SH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "issue.sh")

_FILE_STATES = ("draft", "backlog", "in-progress", "review", "blocked", "closed")
_DEFAULT_LABEL_VALUES = {
    "type": ("bug", "feature", "enhancement", "decision"),
    "priority": ("p0", "p1", "p2", "p3"),
    "status": ("draft", "backlog", "in-progress", "review", "blocked"),
}
_DEFAULT_DIMENSIONS = (("type", "exactly1"), ("priority", "exactly1"))
_DEFAULT_EXEMPT_LABELS = ("wontfix", "duplicate", "invalid", "type:decision", "type:question")
_ITEM_REF = re.compile(r"^ISSUE-[0-9]{3,}$")
_ABS_PATH = re.compile(r"(?<![\w:./-])/(?:[A-Za-z0-9_.@+-]+/)*[A-Za-z0-9_.@+-]+")
_LOCK_ATTEMPTS = 60
_LOCK_SLEEP = 0.05


def _issue_env(ident):
    """issue.sh reads TW_ISSUES_DIR from its environment: an ambient value wins
    (explicit runtime override, like TRACK_WORK_BACKEND), else the config value."""
    env = dict(os.environ)
    env.setdefault("TW_ISSUES_DIR", ident["issues_dir"] or ".agents/issues")
    return env


def _map_issue_failure(message):
    """issue.sh failures carry no codes — classify by their pinned messages."""
    if "must be a repo-relative path" in message:
        raise UsageError("TW_ISSUES_DIR rejected by the file engine: %s" % message)
    if "refusing symlink" in message or "must not contain symlinks" in message:
        raise TwError("conflict", message)
    if "issues path component is not a directory" in message:
        raise TwError("not-found", "bad issues-dir scope: %s" % message)
    if "not found:" in message:
        raise TwError("not-found", message)
    if ("another track-work mutation" in message or "issue already exists" in message
            or "missing frontmatter field" in message or "could not write" in message
            or "could not create" in message):
        raise TwError("conflict", message)
    if ("invalid " in message or "unknown argument" in message or "missing value" in message
            or "unsupported" in message or "usage:" in message):
        raise UsageError(message)
    raise TwError("blocked", "file engine failed: %s" % message)


def _run_issue(ident, args, retry_lock=True):
    """Run issue.sh in the repo root; map failures onto the typed taxonomy.
    Lock contention is the one transient failure class — bounded retry (the same
    convention as the engine's own test suite); everything else is deterministic
    and never retried unchanged."""
    cmd = ["sh", ISSUE_SH, *args]
    for attempt in range(_LOCK_ATTEMPTS + 1):
        r = subprocess.run(cmd, capture_output=True, text=True,
                           cwd=ident["root"], env=_issue_env(ident))
        if r.returncode == 0:
            return r.stdout
        message = r.stderr.strip() or r.stdout.strip()
        if ("another track-work mutation" in message) and retry_lock and attempt < _LOCK_ATTEMPTS:
            time.sleep(_LOCK_SLEEP)
            continue
        _map_issue_failure(message.splitlines()[-1] if message else "")
    raise TwError("conflict", "issues-dir lock did not clear after %d retries" % _LOCK_ATTEMPTS)


def _show_item(ident, ref):
    """Read one item through the engine (format- and symlink-refusing); parse
    frontmatter fields plus the body below it."""
    text = _run_issue(ident, ["show", ref])
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        raise TwError("conflict", "unreadable frontmatter for %s" % ref)
    end = lines.index("---", 1)
    fields = {}
    for line in lines[1:end]:
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    fields["title"] = fields.get("title", "").strip('"')
    raw_labels = fields.get("labels", "").strip().strip("[]")
    fields["labels"] = [x.strip() for x in raw_labels.split(",") if x.strip()]
    fields["_body"] = "\n".join(lines[end + 1:])
    return fields


def _validate_file_labels(labels, cfg):
    """S-037 (file half): labels come from the repo's discovered set (defaults,
    config dimensions, exempt labels) and honor configured cardinality. A label
    outside the set fails unknown-label with the valid set shown; no label is
    ever created implicitly."""
    dimensions = cfg.get("dimensions") or list(_DEFAULT_DIMENSIONS)
    exempt = cfg.get("exempt_labels") or list(_DEFAULT_EXEMPT_LABELS)
    custom = [p for p, _ in dimensions if p not in _DEFAULT_LABEL_VALUES]
    for label in labels:
        if label in exempt:
            continue
        prefix, sep, value = label.partition(":")
        if sep and prefix in _DEFAULT_LABEL_VALUES:
            if value in _DEFAULT_LABEL_VALUES[prefix]:
                continue
            raise TwError("unknown-label",
                          "label '%s' is not in the repo's set; valid %s:* labels: %s"
                          % (label, prefix, ", ".join(_DEFAULT_LABEL_VALUES[prefix])))
        if sep and prefix in custom:
            continue
        known = sorted(set(list(_DEFAULT_LABEL_VALUES) + custom))
        raise TwError("unknown-label",
                      "label '%s' is not in the repo's set; known prefixes: %s; exempt labels: %s"
                      % (label, ", ".join(known), ", ".join(exempt)))
    for prefix, count in dimensions:
        have = [l for l in labels if l.partition(":")[0] == prefix]
        if count == "exactly1" and len(have) != 1:
            raise TwError("cardinality",
                          "prefix '%s' requires exactly1 label, got %d (%s)"
                          % (prefix, len(have), ", ".join(have) or "none"))
        if count == "at_least1" and len(have) < 1:
            raise TwError("cardinality",
                          "prefix '%s' requires at_least1 label, got none" % prefix)


def _redact(text, red, root):
    """S-036: mechanical, deterministic redaction — configured secret values
    (resolved from the environment, never printed), then absolute paths: private
    repos keep meaning by stripping the repo-root prefix (repo-relative); public
    visibility tightens to placeholders for every absolute path."""
    summary = {"classes": [], "secrets_redacted": [], "absolute_paths_redacted": 0}
    for name in red.get("secrets", []):
        value = os.environ.get(name, "")
        if value and value in text:
            text = text.replace(value, "[redacted:%s]" % name)
            summary["secrets_redacted"].append(name)
    if summary["secrets_redacted"]:
        summary["classes"].append("secrets")
        summary["secrets_redacted"].sort()
    if red.get("redact_absolute_paths", True):
        stripped = 0
        if red.get("repo_visibility", "private") != "public" and root + "/" in text:
            stripped = text.count(root + "/")
            text = text.replace(root + "/", "")
        remaining = len(_ABS_PATH.findall(text))
        if remaining:
            text = _ABS_PATH.sub("[redacted:absolute-path]", text)
        if stripped + remaining:
            summary["classes"].append("absolute-paths")
            summary["absolute_paths_redacted"] = stripped + remaining
    return text, summary


def _merge_redaction(a, b):
    return {
        "classes": list(dict.fromkeys(a["classes"] + b["classes"])),
        "secrets_redacted": sorted(set(a["secrets_redacted"]) | set(b["secrets_redacted"])),
        "absolute_paths_redacted": a["absolute_paths_redacted"] + b["absolute_paths_redacted"],
    }


def _stage_body(content):
    """S-018: private (0600) uniquely named temporary body; the caller must unlink."""
    fd, path = tempfile.mkstemp(prefix="tw-body.", suffix=".md",
                                dir=os.environ.get("TMPDIR") or None)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def _item_envelope(ident, item_id, **extra):
    payload = {
        "backend": "file",
        "issues_dir": ident["issues_dir"],
        "item": {"id": item_id,
                 "path": os.path.join(ident["issues_dir"], item_id + ".md")},
    }
    payload.update(extra)
    return payload


def _parse_create_args(args):
    title = type_ = priority = body_file = None
    labels = []
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("--title", "--type", "--priority", "--label", "--body-file"):
            if i + 1 >= len(args):
                raise UsageError("missing value for %s" % a)
            value = args[i + 1]
            if a == "--title":
                title = value
            elif a == "--type":
                type_ = value
            elif a == "--priority":
                priority = value
            elif a == "--label":
                labels.extend(l.strip() for l in value.split(",") if l.strip())
            else:
                body_file = value
            i += 2
        else:
            raise UsageError("unknown argument for create: %s" % a)
    if not title:
        raise UsageError("create requires --title")
    if not type_:
        raise UsageError("create requires --type (bug|feature|enhancement|decision)")
    if not priority:
        raise UsageError("create requires --priority (p0|p1|p2|p3)")
    if type_ not in _DEFAULT_LABEL_VALUES["type"]:
        raise UsageError("invalid type: %s (one of %s)"
                         % (type_, "|".join(_DEFAULT_LABEL_VALUES["type"])))
    if priority not in _DEFAULT_LABEL_VALUES["priority"]:
        raise UsageError("invalid priority: %s (one of %s)"
                         % (priority, "|".join(_DEFAULT_LABEL_VALUES["priority"])))
    return title, type_, priority, labels, body_file


def cmd_create_file(ctx, ident):
    title, type_, priority, extra_labels, body_file = _parse_create_args(ctx.args)
    cfg = _read_config(ident["root"])
    labels = ["type:%s" % type_, "priority:%s" % priority] + extra_labels
    _validate_file_labels(labels, cfg)
    red = cfg.get("redaction") or {}
    body_path = None
    try:
        r_title, summary = _redact(title, red, ident["root"])
        body_args = []
        if body_file is not None:
            try:
                with open(body_file, encoding="utf-8") as f:
                    content = f.read()
            except OSError as e:
                raise UsageError("cannot read --body-file: %s" % e)
            content, body_summary = _redact(content, red, ident["root"])
            summary = _merge_redaction(summary, body_summary)
            body_path = _stage_body(content)
            body_args = ["--body-file", body_path]
        out = _run_issue(ident,
                         ["new", r_title, "--type", type_, "--priority", priority,
                          "--label", ",".join(labels), *body_args])
        m = re.search(r"ISSUE-[0-9]+", out)
        if not m:
            raise TwError("conflict", "engine output did not name the new item: %r" % out.strip())
        item_id = m.group(0)
        item = _show_item(ident, item_id)  # read-back before reporting success
        for key, expected in (("title", r_title), ("status", "draft"),
                              ("type", type_), ("priority", priority)):
            if item.get(key) != expected:
                raise TwError("conflict", "read-back mismatch on %s: expected %r, got %r"
                              % (key, expected, item.get(key)))
        if sorted(item.get("labels", [])) != sorted(labels):
            raise TwError("conflict", "read-back mismatch on labels: expected %r, got %r"
                          % (labels, item.get("labels")))
        return _item_envelope(ident, item_id, labels=labels, redaction=summary)
    finally:
        if body_path is not None:
            try:
                os.unlink(body_path)
            except OSError:
                pass


def cmd_list_file(ctx, ident):
    status_filter = None
    label_filters = []
    i = 0
    while i < len(ctx.args):
        a = ctx.args[i]
        if a == "--status":
            if i + 1 >= len(ctx.args):
                raise UsageError("--status requires a value")
            status_filter = ctx.args[i + 1]
            i += 2
        elif a == "--label":
            if i + 1 >= len(ctx.args):
                raise UsageError("--label requires a value")
            label_filters.append(ctx.args[i + 1])
            i += 2
        else:
            raise UsageError("unknown argument for list: %s" % a)
    valid = ("open",) + _FILE_STATES
    if status_filter is not None and status_filter not in valid:
        raise UsageError("--status must be one of %s, got: %s" % ("|".join(valid), status_filter))
    out = _run_issue(ident, ["list"] + (["--status", status_filter] if status_filter else []))
    items = []
    for line in out.splitlines():
        if not line:
            continue
        parts = line.split("\t", 2)  # titles may contain tabs — maxsplit keeps them intact
        if len(parts) != 3:
            continue
        item_id, status, title = parts
        labels = _show_item(ident, item_id).get("labels", [])
        if label_filters and not all(l in labels for l in label_filters):
            continue
        items.append({"id": item_id, "title": title, "status": status,
                      "labels": labels, "repo": os.path.basename(ident["root"])})
    return {"backend": "file", "issues_dir": ident["issues_dir"], "items": items}


def cmd_status_file(ctx, ident):
    if len(ctx.args) != 2:
        raise UsageError("usage: tw status <ISSUE-NNN> <draft|backlog|in-progress|review|blocked>")
    ref, state = ctx.args
    if not _ITEM_REF.match(ref):
        raise UsageError("malformed file item ref: %s (expected ISSUE-NNN)" % ref)
    if state not in _FILE_STATES:
        raise UsageError("invalid state: %s (one of %s)" % (state, "|".join(_FILE_STATES)))
    if state == "closed":
        raise TwError("invalid-transition",
                      "status cannot set closed — use close, which verifies landed evidence first")
    before = _show_item(ident, ref)  # re-read at the commitment boundary (S-021)
    _run_issue(ident, ["status", ref, state])
    after = _show_item(ident, ref)
    if after.get("status") != state:
        raise TwError("conflict", "read-back mismatch: status expected %r, got %r"
                      % (state, after.get("status")))
    return _item_envelope(ident, ref, **{"from": before.get("status"), "to": state,
                                         "labels": after.get("labels", [])})


def _referencing_commit(root, item_id):
    """The landed-evidence commit (S-038 file half): a commit whose message
    references the item — padded or unpadded numeric form, digit-bounded so
    ISSUE-001 never matches an ISSUE-0010 reference. HEAD is the file backend's
    trunk (non-GitHub repos are trunk-based; the skill commits before closing)."""
    base, _, num = item_id.partition("-")
    num = num.lstrip("0") or "0"
    grep = []
    for pattern in (item_id, "%s-%s" % (base, num)):
        grep += ["--grep", pattern]
    rc, out = _git(["log", *grep, "--format=%H%x1f%B%x1e"], cwd=root)
    if rc != 0:
        return None
    rx = re.compile(r"(?<![0-9])%s-0*%s(?![0-9])" % (re.escape(base), num))
    for record in out.split("\x1e"):
        if not record.strip():
            continue
        sha, _, message = record.partition("\x1f")
        if rx.search(message):
            return sha.strip()
    return None


def cmd_close_file(ctx, ident):
    ref = None
    reason = None
    i = 0
    while i < len(ctx.args):
        a = ctx.args[i]
        if a == "--reason":
            if i + 1 >= len(ctx.args):
                raise UsageError("--reason requires a value")
            reason = ctx.args[i + 1]
            i += 2
        elif ref is None and not a.startswith("--"):
            ref = a
            i += 1
        else:
            raise UsageError("close takes one <ISSUE-NNN> and optional --reason; got: %s" % a)
    if ref is None:
        raise UsageError("close requires an item ref (ISSUE-NNN)")
    if not _ITEM_REF.match(ref):
        raise UsageError("malformed file item ref: %s (expected ISSUE-NNN)" % ref)
    cfg = _read_config(ident["root"])
    item = _show_item(ident, ref)  # not-found / symlink refusal surface here
    exempt = cfg.get("exempt_labels") or list(_DEFAULT_EXEMPT_LABELS)
    matching = [l for l in exempt if l in item.get("labels", [])]
    if matching:
        evidence = {"check": "exempt-label", "label": matching[0]}
    else:
        sha = _referencing_commit(ident["root"], ref)
        if sha is None:
            raise TwError("landed-evidence",
                          "no commit referencing %s found in the log and the item carries no "
                          "exempt label (%s) — land the change with a commit message referencing "
                          "%s, or apply an exempt label" % (ref, ", ".join(exempt), ref))
        evidence = {"check": "commit", "commit": sha}
    _run_issue(ident, ["close", ref])
    after = _show_item(ident, ref)
    if after.get("status") != "closed":
        raise TwError("conflict", "read-back mismatch: status expected 'closed', got %r"
                      % after.get("status"))
    result = _item_envelope(ident, ref, evidence=evidence)
    if reason is not None:
        result["reason"], _ = _redact(reason, cfg.get("redaction") or {}, ident["root"])
    return result


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
