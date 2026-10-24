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

Status: T3 — resolve implemented (identity ladder + capability probes, S-034);
list/create/status/close/migrate return blocked until T4–T6 land
(docs/plans/track-work-cli.md).
"""
import json
import os
import re
import subprocess
import sys

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


def _read_config(root):
    """Trusted-base config subset the CLI needs: backend, github.repo, issues_dir —
    taken from the first ```yaml fence of .agents/track-work.config.md."""
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
    section = None
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, _, value = line.strip().partition(":")
        value = value.strip()
        if line[:1] in (" ", "\t"):  # nested (github: block)
            if section == "github" and key == "repo" and value:
                cfg["github_repo"] = value
            continue
        section = "github" if (key == "github" and not value) else None
        if key in ("backend", "issues_dir") and value:
            cfg[key] = value
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
    raise TwError("blocked", "%s is not implemented yet (T3: resolve only)" % ctx.command)


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


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
