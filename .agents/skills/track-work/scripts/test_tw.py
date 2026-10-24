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


def run_tw(*args, env_extra=None, stdin=None, cwd=None):
    """Run the CLI exactly as a caller would; return (exit, envelope-or-None, stdout, stderr)."""
    env = dict(os.environ)
    for ambient in ("TW_NONINTERACTIVE", "TRACK_WORK_BACKEND", "GH_REPO"):
        env.pop(ambient, None)  # ambient ledger context never leaks into a test
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        [sys.executable, SCRIPT, *args],
        input=stdin, capture_output=True, text=True, env=env, cwd=cwd, timeout=30,
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
    """T2/T3: the not-yet-implemented commands dispatch and report blocked."""

    def test_unimplemented_commands_blocked_exit_1(self):
        # resolve landed in T3; the remaining commands report blocked until T4-T6.
        for command in ("list", "create", "status", "close", "migrate"):
            with self.subTest(command=command):
                code, env, _, _ = run_tw(command)
                self.assertEqual(code, 1)
                self.assertFalse(env["ok"])
                self.assertEqual(env["command"], command)
                self.assertEqual(env["error"]["code"], "blocked")

    def test_global_flags_accepted_without_changing_stub_contract(self):
        code, env, _, _ = run_tw("--gh", "/nonexistent/gh", "--noninteractive", "list")
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


# ---------------------------------------------------------------- T3: resolve

_SHIM_TEMPLATE = """#!/usr/bin/env python3
import json, sys
args = sys.argv[1:]
if args[:1] == ["--version"]:
    sys.exit(0)
if args[:2] == ["auth", "status"]:
    sys.exit(AUTH_RC)
if args[:2] == ["repo", "view"]:
    repo = args[2] if len(args) > 2 else ""
    if WRONG_REPO:
        repo = "evil/other-repo"
    print(json.dumps({"nameWithOwner": repo, "hasIssuesEnabled": ISSUES}))
    sys.exit(0)
sys.exit(1)
"""


def write_gh_shim(directory, auth_rc=0, issues=True, wrong_repo=False):
    """A fake gh for capability tests: --version/auth/repo-view with knobs."""
    path = os.path.join(directory, "gh-shim")
    with open(path, "w", encoding="utf-8") as f:
        f.write(_SHIM_TEMPLATE
                .replace("AUTH_RC", str(auth_rc))
                .replace("ISSUES", "True" if issues else "False")
                .replace("WRONG_REPO", "True" if wrong_repo else "False"))
    os.chmod(path, 0o755)
    return path


class TestResolve(unittest.TestCase):
    """S-034: identity ladder + capability separation; S-001–S-003 adversarially.
    Every case runs in a throwaway git fixture; --gh never touches the network."""

    def make_repo(self, origin=None, push_urls=None, config_yaml=None):
        import shutil
        import tempfile
        root = tempfile.mkdtemp(prefix="tw-t3-")
        self.addCleanup(shutil.rmtree, root, True)
        subprocess.run(["git", "init", "-q", root], check=True, capture_output=True)
        if origin:
            subprocess.run(["git", "remote", "add", "origin", origin],
                           cwd=root, check=True, capture_output=True)
        for u in (push_urls or []):
            subprocess.run(["git", "remote", "set-url", "--add", "--push", "origin", u],
                           cwd=root, check=True, capture_output=True)
        if config_yaml is not None:
            os.makedirs(os.path.join(root, ".agents"), exist_ok=True)
            with open(os.path.join(root, ".agents", "track-work.config.md"), "w") as f:
                f.write("```yaml\n%s```\n" % config_yaml)
        return root

    def resolve(self, cwd, gh="/nonexistent/gh", env_extra=None):
        return run_tw("--gh", gh, "resolve", cwd=cwd, env_extra=env_extra)

    def test_https_origin_selects_github(self):
        # Defect this guards: mis-parsing the canonical https form would misfile the ledger.
        root = self.make_repo(origin="https://github.com/acme/widgets.git")
        code, env, _, _ = self.resolve(root)
        self.assertEqual(code, 0)
        self.assertTrue(env["ok"])
        self.assertEqual(env["backend"], "github")
        self.assertEqual(env["selected_by"], "origin")
        self.assertEqual(env["repo"], "acme/widgets")

    def test_scp_form_selects_github(self):
        root = self.make_repo(origin="git@github.com:acme/widgets")
        _, env, _, _ = self.resolve(root)
        self.assertEqual((env["backend"], env["repo"]), ("github", "acme/widgets"))

    def test_no_git_suffix_and_trailing_slash_normalize_identically(self):
        root = self.make_repo(origin="https://github.com/acme/widgets/")
        _, env, _, _ = self.resolve(root)
        self.assertEqual(env["repo"], "acme/widgets")

    def test_userinfo_origin_rejected_with_remediation(self):
        # Defect this guards: a token-bearing URL silently selecting a backend (or leaking).
        root = self.make_repo(origin="https://user:tok@github.com/acme/widgets")
        code, env, _, _ = self.resolve(root)
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "origin-rejected")
        self.assertIn("github.repo", env["error"]["message"])  # remediation is named

    def test_lookalike_host_rejected_not_file(self):
        # Defect this guards: github.com.evil.com being classified "non-GitHub" -> file ledger.
        root = self.make_repo(origin="https://github.com.evil.com/acme/widgets")
        code, env, _, _ = self.resolve(root)
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "origin-rejected")

    def test_ssh_scheme_form_rejected(self):
        # Not one of the two accepted forms -> stop, with the pin-override remediation.
        root = self.make_repo(origin="ssh://git@github.com/acme/widgets.git")
        code, env, _, _ = self.resolve(root)
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "origin-rejected")

    def test_multiple_push_urls_rejected(self):
        root = self.make_repo(origin="https://github.com/acme/widgets",
                              push_urls=["https://github.com/acme/widgets",
                                         "https://github.com/acme/widgets-mirror"])
        code, env, _, _ = self.resolve(root)
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "origin-rejected")
        self.assertIn("push URL", env["error"]["message"])

    def test_non_github_origin_selects_file(self):
        root = self.make_repo(origin="https://gitlab.com/acme/widgets")
        code, env, _, _ = self.resolve(root)
        self.assertEqual(code, 0)
        self.assertEqual(env["backend"], "file")
        self.assertEqual(env["selected_by"], "non-github-origin")
        self.assertEqual(env["issues_dir"], ".agents/issues")
        self.assertIsNone(env["capability"])  # no GitHub probes for a file identity

    def test_no_origin_selects_file(self):
        root = self.make_repo()
        _, env, _, _ = self.resolve(root)
        self.assertEqual((env["backend"], env["selected_by"]), ("file", "no-origin"))

    def test_env_file_override_beats_github_origin(self):
        # S-001: a confirmed override wins over origin identity.
        root = self.make_repo(origin="https://github.com/acme/widgets")
        _, env, _, _ = self.resolve(root, env_extra={"TRACK_WORK_BACKEND": "file"})
        self.assertEqual((env["backend"], env["selected_by"]), ("file", "env-override"))

    def test_env_github_without_repo_stops(self):
        # "github" override without origin and without github.repo must not guess.
        root = self.make_repo()
        code, env, _, _ = self.resolve(root, env_extra={"TRACK_WORK_BACKEND": "github"})
        self.assertEqual(code, 2)
        self.assertEqual(env["error"]["code"], "usage")
        self.assertIn("github.repo", env["error"]["message"])

    def test_env_github_takes_repo_from_config(self):
        root = self.make_repo(config_yaml="github:\n  repo: acme/widgets\n")
        _, env, _, _ = self.resolve(root, env_extra={"TRACK_WORK_BACKEND": "github"})
        self.assertEqual((env["backend"], env["repo"]), ("github", "acme/widgets"))

    def test_invalid_env_backend_stops(self):
        root = self.make_repo()
        code, env, _, _ = self.resolve(root, env_extra={"TRACK_WORK_BACKEND": "bogus"})
        self.assertEqual(code, 2)
        self.assertEqual(env["error"]["code"], "usage")

    def test_config_backend_override(self):
        root = self.make_repo(origin="https://github.com/acme/widgets",
                              config_yaml="backend: file\n")
        _, env, _, _ = self.resolve(root)
        self.assertEqual((env["backend"], env["selected_by"]), ("file", "config-override"))

    def test_capability_probes_reported_separately_from_identity(self):
        # S-002/S-034: gh missing entirely -> capability fails, identity unchanged.
        root = self.make_repo(origin="https://github.com/acme/widgets")
        code, env, _, _ = self.resolve(root, gh="/nonexistent/gh")
        self.assertEqual(code, 0)
        self.assertEqual(env["repo"], "acme/widgets")
        self.assertFalse(env["capability"]["ok"])
        self.assertEqual(env["capability"]["error_class"], "gh-missing")

    def test_capability_ok_shim(self):
        import tempfile
        root = self.make_repo(origin="https://github.com/acme/widgets")
        with tempfile.TemporaryDirectory() as d:
            shim = write_gh_shim(d)
            code, env, _, _ = self.resolve(root, gh=shim)
        self.assertEqual(code, 0)
        self.assertTrue(env["capability"]["ok"])
        self.assertEqual(env["capability"]["checked"], ["gh-present", "gh-auth", "gh-repo-view"])

    def test_capability_auth_failure_preserves_identity(self):
        import tempfile
        root = self.make_repo(origin="https://github.com/acme/widgets")
        with tempfile.TemporaryDirectory() as d:
            shim = write_gh_shim(d, auth_rc=1)
            code, env, _, _ = self.resolve(root, gh=shim)
        self.assertEqual(code, 0)  # resolve succeeds; capability carries the failure
        self.assertEqual(env["capability"]["error_class"], "gh-auth")

    def test_capability_issues_disabled(self):
        # S-003: disabled Issues is a capability stop, not a different backend.
        import tempfile
        root = self.make_repo(origin="https://github.com/acme/widgets")
        with tempfile.TemporaryDirectory() as d:
            shim = write_gh_shim(d, issues=False)
            code, env, _, _ = self.resolve(root, gh=shim)
        self.assertEqual(code, 0)
        self.assertEqual(env["capability"]["error_class"], "issues-disabled")

    def test_capability_wrong_repo_readback(self):
        # S-035 seed: the shim claims a different repository -> wrong-repository, not ok.
        import tempfile
        root = self.make_repo(origin="https://github.com/acme/widgets")
        with tempfile.TemporaryDirectory() as d:
            shim = write_gh_shim(d, wrong_repo=True)
            code, env, _, _ = self.resolve(root, gh=shim)
        self.assertEqual(code, 0)
        self.assertFalse(env["capability"]["ok"])
        self.assertEqual(env["capability"]["error_class"], "wrong-repository")

    def test_ambient_gh_repo_cannot_redirect(self):
        # S-015: hostile ambient GH_REPO must not change the resolved identity.
        root = self.make_repo(origin="https://github.com/acme/widgets")
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            shim = write_gh_shim(d)
            _, clean, _, _ = self.resolve(root, gh=shim)
            _, hostile, _, _ = self.resolve(root, gh=shim, env_extra={"GH_REPO": "evil/hijack"})
        self.assertEqual(clean["repo"], "acme/widgets")
        self.assertEqual(hostile["repo"], "acme/widgets")
        self.assertEqual(clean, hostile)

    def test_resolve_output_is_deterministic(self):
        # S-034: identical inputs -> byte-identical envelope (no timestamps, no ordering wobble).
        root = self.make_repo(origin="https://github.com/acme/widgets")
        _, _, out1, _ = self.resolve(root)
        _, _, out2, _ = self.resolve(root)
        self.assertEqual(out1, out2)

    def test_outside_git_repo_is_usage(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            code, env, _, _ = self.resolve(d)
        self.assertEqual(code, 2)
        self.assertEqual(env["error"]["code"], "usage")

