"""Adversarial + contract tests for tw.py (issue #1; plan T2+).

Layer: provider/adapter/entrypoint — every case runs the real CLI as a subprocess
and asserts the observable contract (stdout envelope, exit codes, S-033/S-039).
Grows per task: T3 adds resolve/identity, T4 file backend, T5 GitHub, T6 migration.

Run: python3 -m unittest discover -s .agents/skills/track-work/scripts -p 'test_tw.py'
"""
import json
import os
import subprocess
import sys
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tw.py")


def run_tw(*args, env_extra=None, stdin=None):
    """Run the CLI exactly as a caller would; return (exit, envelope-or-None, stdout, stderr)."""
    env = dict(os.environ)
    env.pop("TW_NONINTERACTIVE", None)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        [sys.executable, SCRIPT, *args],
        input=stdin, capture_output=True, text=True, env=env, timeout=30,
    )
    parsed = None
    try:
        parsed = json.loads(r.stdout)
    except (json.JSONDecodeError, ValueError):
        parsed = None
    return r.returncode, parsed, r.stdout, r.stderr


class TestEnvelopeContract(unittest.TestCase):
    """S-033: one JSON envelope per invocation; exit 0/2/1 mapping.

    (Success-side envelope assertions land with T3's first succeeding command;
    the skeleton exercises the failure + usage halves.)
    """

    def test_unknown_command_is_usage_exit_2(self):
        code, env, out, _ = run_tw("frobnicate")
        self.assertEqual(code, 2)
        self.assertIsNotNone(env, f"stdout is not one JSON object: {out!r}")
        self.assertFalse(env["ok"])
        self.assertEqual(env["command"], "frobnicate")
        self.assertEqual(env["error"]["code"], "usage")

    def test_missing_command_is_usage_exit_2(self):
        code, env, out, _ = run_tw()
        self.assertEqual(code, 2)
        self.assertIsNotNone(env, f"stdout is not one JSON object: {out!r}")
        self.assertFalse(env["ok"])
        self.assertEqual(env["error"]["code"], "usage")

    def test_stdout_is_exactly_one_json_object(self):
        # Defect this guards: extra prints (diagnostics, banners) before/after the
        # envelope break machine consumption — json.loads must see exactly one doc.
        for args in (["frobnicate"], ["resolve"], ["create", "--title", "x"]):
            with self.subTest(args=args):
                _, _, out, _ = run_tw(*args)
                self.assertEqual(out.count("\n"), 1, repr(out))
                self.assertIsInstance(json.loads(out), dict)

    def test_unknown_flag_is_usage(self):
        code, env, _, _ = run_tw("--bogus", "resolve")
        self.assertEqual(code, 2)
        self.assertEqual(env["error"]["code"], "usage")

    def test_help_is_human_text_exit_0(self):
        # Documented exception to the envelope: --help is not a command execution —
        # its output must not parse as one JSON envelope.
        code, _, out, _ = run_tw("--help")
        self.assertEqual(code, 0)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(out)


class TestSkeletonStubs(unittest.TestCase):
    """T2: the six commands dispatch and report blocked (not-implemented)."""

    def test_every_command_blocked_exit_1(self):
        for command in ("resolve", "list", "create", "status", "close", "migrate"):
            with self.subTest(command=command):
                code, env, _, _ = run_tw(command)
                self.assertEqual(code, 1)
                self.assertFalse(env["ok"])
                self.assertEqual(env["command"], command)
                self.assertEqual(env["error"]["code"], "blocked")

    def test_global_flags_accepted_without_changing_stub_contract(self):
        code, env, _, _ = run_tw("--gh", "/nonexistent/gh", "--noninteractive", "resolve")
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "blocked")
        self.assertTrue(env["noninteractive"])

    def test_flags_accepted_after_command_too(self):
        # The surface lists --noninteractive among per-command args; it is global.
        code, env, _, _ = run_tw("close", "--noninteractive")
        self.assertEqual(code, 1)
        self.assertTrue(env["noninteractive"])


class TestNoninteractiveMode(unittest.TestCase):
    """S-039 (skeleton half): flag and env both engage; no invocation waits on stdin."""

    def test_env_var_engages_noninteractive(self):
        code, env, _, _ = run_tw("list", env_extra={"TW_NONINTERACTIVE": "1"})
        self.assertEqual(code, 1)
        self.assertTrue(env["noninteractive"])

    def test_no_invocation_hangs_without_a_tty(self):
        # stdin closed: a prompt would either hang (timeout) or die on EOF; the
        # stub contract must return blocked immediately.
        code, env, _, _ = run_tw("create", stdin="")
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "blocked")


if __name__ == "__main__":
    unittest.main()
