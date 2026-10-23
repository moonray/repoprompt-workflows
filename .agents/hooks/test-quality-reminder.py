#!/usr/bin/env python3
"""Keep test work run AND vetted with the test-quality skill, per runtime.

Wired per runtime (see .agents/hooks/README.md):
  Claude Code — ~/.claude/settings.json PostToolUse matcher "Bash|Skill" + Stop.
    A real Skill-tool invocation of test-quality stamps the vet marker (the
    matcher MUST keep "Skill" — without it the vet half can never clear).
  Codex — repo .codex/hooks.json PostToolUse(Bash) + Stop, both invoked with
    TQ_HOOK_RUNTIME=codex in the environment. Codex routes Stop but emits no
    event for skill invocations, so the deliberate vetting act there is the
    attestation command (this script invoked with --attest-vetted over Bash),
    honored ONLY when that env is set — on runtimes that can observe skills
    (Claude Code, no env) attestation is inert and only a real Skill-tool
    invocation stamps the vet marker.
  opencode — repo plugin: session.idle ≈ Stop is post-turn and log-only; the
    gate is documented-unsupported there (it warns, it cannot block).

  PostToolUse (Bash test-run, Skill "test-quality", or runtime-gated
    attestation): record a last-run marker (a test run) or a vet marker (an
    actual Skill-tool invocation or attestation) for the repo. A test run also
    emits a reminder to vet added/modified tests with the skill.
  Stop: block if any uncommitted test file was edited since the LATER of {last
    test run, last vetting}. edit->run->vet->stop is allowed; edit->run->stop
    (vetting skipped or "applied from context") is NOT. This closes the loophole
    where an agent runs the suite and rationales the checklist from memory.
    Committing/cleaning the tests is always an escape, so it never traps.

Source of truth: `.agents/hooks/test-quality-reminder.py` in this repo; symlink it into your runtime's hooks directory (e.g. `~/.claude/hooks/`).
"""
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys

CACHE_DIR = os.path.expanduser("~/.cache/tq-hook")

VET_REMINDER = (
    "TEST QUALITY: you just ran a test suite. Before declaring test work done, run the "
    "test-quality skill (Skill tool) and apply its checklist to any tests you added or "
    "modified this session: (1) name a plausible defect each test catches; (2) assert "
    "exact observable outcomes (no not-nil / field-presence-only); (3) lowest faithful "
    "layer; (4) consolidate equivalent branch cases."
)
STOP_REASON = (
    "TEST QUALITY GATE: uncommitted test files changed since the last test run AND the last "
    "test-quality skill invocation. After editing tests you must BOTH (1) run the affected "
    "suite AND (2) invoke the test-quality skill (Skill tool) to vet the changes — each after "
    "the last edit. Applying the checklist 'from context' does not count; the skill must be "
    "actually invoked. (Committing/cleaning test changes also clears this gate.)"
)

# Stop reason for runtimes whose wiring cannot observe skill invocations (Codex):
# the vetting act there is the explicit attestation command below, so the reason
# must name an act that runtime can actually perform.
ATTEST_COMMAND = (
    'python3 "$(git rev-parse --show-toplevel)/.agents/hooks/test-quality-reminder.py"'
    " --attest-vetted"
)
STOP_REASON_ATTEST = (
    "TEST QUALITY GATE: uncommitted test files changed since the last test run AND the last "
    "test-quality vetting attestation. After editing tests you must BOTH (1) run the affected "
    "suite AND (2) apply the test-quality checklist (.agents/skills/test-quality/SKILL.md), then "
    f"attest with: {ATTEST_COMMAND} — each after the last edit. (Committing/cleaning test "
    "changes also clears this gate.)"
)

# The skill name whose actual Skill-tool invocation clears the second half of the Stop gate.
_TEST_QUALITY_SKILL = "test-quality"

# --- Test-run command detection ------------------------------------------------
# Match only real command-position invocations, not the bare words "pytest"/"jest"/"test"
# appearing in comments, heredoc bodies, echo strings, or commit messages. We split the
# command on shell operators, strip comments + heredoc bodies + env assignments + path and
# wrapper prefixes, then match the leading program against known test runners.

# Programs that run tests directly (any arguments).
_DIRECT_RUNNERS = {
    "pytest", "py.test", "jest", "vitest", "mocha", "rspec", "ctest", "tox", "nox",
    "ava", "karma", "playwright", "cypress",
}

# Wrapper words that precede the real command and should be skipped (by basename).
_WRAPPER_WORDS = {"sudo", "env", "time", "nice", "nohup", "command", "npx", "bunx", "bundle", "exec"}

# Package-manager subcommands that do NOT run tests (so `npm install jest` is not a test run).
_PM_NO_RUN = {
    "install", "i", "ci", "add", "remove", "rm", "uninstall", "update", "upgrade", "up",
    "why", "list", "ls", "outdated", "audit", "info", "view", "show", "docs", "explain",
    "pack", "publish", "init", "create", "link", "unlink", "dedupe", "fetch",
}

# Flags that mean "show help/version" — such invocations never run tests.
_HELP_FLAGS = {"--help", "-h", "--version"}

_HEREDOC_START = re.compile(r"<<-?['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?")
_LEADING_ENV = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def _subcommand_is_test(prog, toks):
    """True if `prog` with remaining tokens `toks` is a test run."""
    if prog == "node":
        if any(a == "--test" or a.startswith("--test=") for a in toks):
            return True
        return _script_arg_is_test(toks)  # node tests/test_foo.js (standalone-script convention)
    if prog in {"swift", "go", "cargo", "deno", "dotnet", "rake", "xcodebuild"}:
        return any(a == "test" for a in toks)
    if prog == "make":
        return any(a == "test" or a.startswith("test") for a in toks)
    if prog in {"mvn", "mvnw", "gradle", "gradlew"}:
        return any("test" in a for a in toks)
    if prog in {"npm", "pnpm", "yarn", "bun"}:
        if any(a in _PM_NO_RUN for a in toks):
            return False
        return any(a == "test" or a.startswith("test") or a in _DIRECT_RUNNERS for a in toks)
    if prog in {"python", "python2", "python3"} or prog.startswith("python3."):
        for i, a in enumerate(toks):
            if a == "-m" and i + 1 < len(toks) and toks[i + 1] in {
                "pytest", "unittest", "nose", "nose2", "tox", "nox",
            }:
                return True
        return _script_arg_is_test(toks)  # python tests/test_foo.py (standalone-script convention)
    return False


def _strip_heredocs(cmd):
    """Remove heredoc bodies so words inside them (e.g. 'pytest') aren't seen as commands."""
    out, skip = [], None
    for line in cmd.split("\n"):
        if skip is not None:
            if line.strip() == skip:
                skip = None
            continue
        m = _HEREDOC_START.search(line)
        if m:
            skip = m.group(1)
            line = _HEREDOC_START.sub("", line)
        out.append(line)
    return "\n".join(out)


def _segment_tokens(cmd):
    """Yield the token list for each simple command in `cmd`, after stripping wrappers."""
    for part in re.split(r"&&|\|\||;|\||\n", cmd):
        try:
            toks = shlex.split(part, comments=True, posix=True)
        except ValueError:
            toks = [w for w in part.split() if w and not w.startswith("#")]
        i = 0
        while i < len(toks) and _LEADING_ENV.match(toks[i]):  # drop leading NAME=value
            i += 1
        toks = toks[i:]
        while toks and toks[0].split("/")[-1] in _WRAPPER_WORDS:  # drop sudo/npx/bundle exec/...
            toks = toks[1:]
        if toks:
            yield toks


def is_test_run_command(cmd):
    """True if any simple command in `cmd` invokes a known test runner at command position."""
    if not isinstance(cmd, str) or not cmd.strip():
        return False
    for toks in _segment_tokens(_strip_heredocs(cmd)):
        if any(t in _HELP_FLAGS for t in toks):
            continue
        prog = toks[0].split("/")[-1]
        if prog in _DIRECT_RUNNERS or _subcommand_is_test(prog, toks[1:]):
            return True
    return False

def runtime_attest_enabled():
    """True when the runtime's wiring declared skill invocations unobservable.

    Codex's hooks.json sets TQ_HOOK_RUNTIME=codex on both invocations of this
    script. Claude Code's wiring sets nothing, so attestation stays inert there
    and a real Skill-tool invocation remains the only vetting act (pinned).
    """
    return bool(os.environ.get("TQ_HOOK_RUNTIME"))


def is_attestation_command(cmd):
    """True if a simple command in `cmd` deliberately attests test-quality vetting.

    The attestation is a Bash command invoking this script with a standalone
    ``--attest-vetted`` token — e.g.
    ``python3 "$(git rev-parse --show-toplevel)/.agents/hooks/test-quality-reminder.py" --attest-vetted``.
    Token-level matching keeps it a real argv act: the unexpanded ``$(...)`` path
    still matches by substring, while the flag appearing only inside a quoted
    string, comment, or heredoc body does not count.
    """
    if not isinstance(cmd, str) or not cmd.strip():
        return False
    for toks in _segment_tokens(_strip_heredocs(cmd)):
        if any(t == "--attest-vetted" for t in toks) and any(
            "test-quality-reminder.py" in t for t in toks
        ):
            return True
    return False


# Multi-language test-file path detection (directories + filename conventions).
TEST_FILE_RE = re.compile(
    r"(/(tests?|__tests__|specs?)/)"
    r"|(_test\.(go|rs|py|rb|ts|js|tsx|jsx)$)"
    r"|(_spec\.(rb|py|ts|js|tsx|jsx)$)"
    r"|(test_[^/]+\.(py|rb|ts|js|sh|go)$)"
    r"|(\.(test|spec)\.(ts|tsx|js|jsx)$)"
    r"|((Test|Tests|Spec|Specs)\.(swift|kt|java|cs|php)$)"
)

# Documentation is never an executable test for any framework detected above; exclude it
# so a docs/spec/ directory (this repo's spec-doc home) isn't misread as a test directory.
# Does not weaken the gate: every real code-extension test file still matches TEST_FILE_RE.
DOC_FILE_RE = re.compile(r"\.(md|markdown|rst|adoc|txt|tex)$", re.IGNORECASE)


def _script_arg_is_test(toks):
    """True if a positional script argument matches the test-file pattern.

    For interpreters run without a named test runner — ``python tests/x.py``,
    ``node tests/x.js`` (common in repos with no pytest/aggregate runner) — treat a
    direct script invocation as a test run when the script path matches TEST_FILE_RE.
    This keeps 'is a test run' consistent with the dirty-test-file detector (the other
    half of the gate), since both sides use the same regex. Flags are skipped, and the
    literal after ``-c`` (python) / ``-e`` (node) is skipped too, so inline code that
    merely mentions a 'tests' path can't register a fake run.
    """
    skip_next = False
    for a in toks:
        if skip_next:
            skip_next = False
            continue
        if a == "--":
            break
        if a in {"-c", "-e", "--eval"}:   # inline code string — next token is code, not a path
            skip_next = True
            continue
        if a.startswith("-"):
            continue
        if TEST_FILE_RE.search(a):
            return True
    return False


def repo_root(cwd):
    try:
        return subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except Exception:
        return cwd


def lastrun_path(root):
    key = hashlib.sha1(root.encode()).hexdigest()[:12]
    return os.path.join(CACHE_DIR, f"lastrun-{key}")


def skill_path(root):
    """Marker touched when the test-quality Skill is actually invoked (not 'applied from context')."""
    key = hashlib.sha1(root.encode()).hexdigest()[:12]
    return os.path.join(CACHE_DIR, f"tqskill-{key}")


def dirty_test_files(root):
    try:
        out = subprocess.run(
            ["git", "-C", root, "status", "--short", "--untracked-files=all"],
            capture_output=True, text=True, timeout=5,
        ).stdout
    except Exception:
        return []
    files = []
    for line in out.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip().split(" -> ")[-1]
        if DOC_FILE_RE.search(path):
            continue
        if TEST_FILE_RE.search(path):
            files.append(os.path.join(root, path))
    return files


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if not isinstance(payload, dict):  # valid-but-non-object JSON (e.g. `[]`) never raises
        sys.exit(0)
    event = payload.get("hook_event_name", "")
    cwd = payload.get("cwd") or os.getcwd()
    root = repo_root(cwd)
    os.makedirs(CACHE_DIR, exist_ok=True)

    if event == "PostToolUse":
        tool_name = payload.get("tool_name", "")
        ti = payload.get("tool_input") or {}
        cmd = ti.get("command", "") or ""
        if runtime_attest_enabled() and is_attestation_command(cmd):
            # Rung 2 (Codex): the runtime cannot observe skill invocations, so the
            # deliberate vetting act is the attestation command itself. Inert on
            # runtimes without TQ_HOOK_RUNTIME (Claude Code) — see docstring.
            try:
                open(skill_path(root), "w").close()
            except Exception:
                pass
        elif is_test_run_command(cmd):
            # Touch the last-run marker (its mtime = last run time for this repo).
            try:
                open(lastrun_path(root), "w").close()
            except Exception:
                pass
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": VET_REMINDER,
                }
            }))
        elif tool_name == "Skill" and ti.get("skill") == _TEST_QUALITY_SKILL:
            # The test-quality skill was actually invoked (not 'applied from context'):
            # stamp the skill marker so the Stop gate's second half can clear.
            try:
                open(skill_path(root), "w").close()
            except Exception:
                pass
    elif event == "Stop":
        tests = dirty_test_files(root)
        if not tests:
            sys.exit(0)
        newest_edit = max(
            (os.path.getmtime(t) for t in tests if os.path.exists(t)),
            default=0.0,
        )
        lr = lastrun_path(root)
        lastrun_ts = os.path.getmtime(lr) if os.path.exists(lr) else 0.0
        sk = skill_path(root)
        skill_ts = os.path.getmtime(sk) if os.path.exists(sk) else 0.0
        # Two gates must both clear after the last test edit: the suite was run AND the
        # test-quality skill was invoked. newest_edit newer than either marker means that
        # step is still owed (closes the 'applied from context' loophole).
        if newest_edit > lastrun_ts or newest_edit > skill_ts:
            reason = STOP_REASON_ATTEST if runtime_attest_enabled() else STOP_REASON
            print(json.dumps({"decision": "block", "reason": reason}))

    sys.exit(0)


if __name__ == "__main__":
    main()
