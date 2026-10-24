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

Status: T2 skeleton — dispatch + envelope contract only; the six commands return
blocked/not-implemented until T3–T6 land (docs/plans/track-work-cli.md).
"""
import json
import os
import sys

COMMANDS = ("resolve", "list", "create", "status", "close", "migrate")

ERROR_CODES = (
    "usage", "origin-rejected", "capability", "blocked", "unknown-label",
    "cardinality", "invalid-transition", "not-found", "wrong-repository",
    "landed-evidence", "conflict",
)


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
    """Pull global flags (--noninteractive, --gh PATH, -h/--help) from anywhere;
    everything left keeps its order as command + command args."""
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


def dispatch(ctx):
    """Execute one command; return its payload dict (success) or raise TwError.

    T2 skeleton: every command reports blocked until its task lands.
    """
    raise TwError("blocked", f"{ctx.command} is not implemented yet (T2 skeleton)")


def main(argv):
    try:
        noninteractive, gh, rest = split_global_flags(argv)
        if rest and rest[0] in ("-h", "--help"):
            print(__doc__)
            return 0
        if not rest:
            raise UsageError(f"missing command; one of: {', '.join(COMMANDS)}")
        command = rest[0]
        if command not in COMMANDS:
            raise UsageError(f"unknown command: {command} (one of: {', '.join(COMMANDS)})")
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
