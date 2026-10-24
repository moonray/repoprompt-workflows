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



# ---------------------------------------------------------------- T4: file backend

class FileBackendFixture(unittest.TestCase):
    """Shared throwaway git fixtures for the file-backend commands (T4)."""

    def make_repo(self, config_yaml=None):
        import shutil
        import tempfile
        root = tempfile.mkdtemp(prefix="tw-t4-")
        self.addCleanup(shutil.rmtree, root, True)
        subprocess.run(["git", "init", "-q", root], check=True, capture_output=True)
        subprocess.run(["git", "-C", root, "config", "user.email", "t@example.com"],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", root, "config", "user.name", "T"],
                       check=True, capture_output=True)
        if config_yaml is not None:
            os.makedirs(os.path.join(root, ".agents"), exist_ok=True)
            with open(os.path.join(root, ".agents", "track-work.config.md"), "w") as f:
                f.write("```yaml\n%s```\n" % config_yaml)
        return root

    def commit(self, root, message):
        subprocess.run(["git", "-C", root, "commit", "-qm", message, "--allow-empty"],
                       check=True, capture_output=True)

    def item_text(self, root, item_id, issues_dir=".agents/issues"):
        with open(os.path.join(root, issues_dir, item_id + ".md"), encoding="utf-8") as f:
            return f.read()

    def body_of(self, root, item_id, issues_dir=".agents/issues"):
        lines = self.item_text(root, item_id, issues_dir).splitlines()
        end = lines.index("---", 1)
        return "\n".join(lines[end + 1:])


class TestFileCreate(FileBackendFixture):
    """T4 create over issue.sh: envelope, redaction (S-036), labels (S-037 file half)."""

    def create(self, cwd, title="A bug", type_="bug", priority="p1",
               extra=(), body_file=None, env_extra=None):
        args = ["create", "--title", title, "--type", type_, "--priority", priority]
        for label in extra:
            args += ["--label", label]
        if body_file:
            args += ["--body-file", body_file]
        return run_tw(*args, cwd=cwd, env_extra=env_extra)

    def test_create_envelope_and_item(self):
        # Defect this guards: the wrapper mis-wiring engine args would file an
        # item whose stored fields disagree with the requested ones.
        root = self.make_repo(config_yaml=(
            "labels:\n"
            "  dimensions:\n"
            "    - { prefix: type, count: exactly1 }\n"
            "    - { prefix: priority, count: exactly1 }\n"
            "    - { prefix: area, count: at_least1 }\n"))
        code, env, out, _ = self.create(root, title="Fix the flux", extra=["area:core"])
        self.assertEqual(code, 0, out)
        self.assertTrue(env["ok"])
        self.assertEqual(env["backend"], "file")
        self.assertEqual(env["issues_dir"], ".agents/issues")
        self.assertEqual(env["item"]["id"], "ISSUE-001")
        self.assertTrue(os.path.isfile(os.path.join(root, env["item"]["path"])))
        text = self.item_text(root, "ISSUE-001")
        self.assertIn('title: "Fix the flux"', text)
        self.assertIn("status: draft", text)          # birth state is draft (S-026)
        self.assertIn("labels: [type:bug,priority:p1,area:core]", text)

    def test_create_redacts_before_staging_and_cleans_up(self):
        # S-036: secret values and absolute paths are gone before the item exists;
        # the envelope reports the classes; no unredacted copy survives the run.
        import tempfile
        root = self.make_repo(config_yaml="redaction:\n  secrets: [EXAMPLE_API_KEY]\n")
        staged = tempfile.mkdtemp(prefix="tw-t4-tmp-")
        self.addCleanup(__import__("shutil").rmtree, staged, True)
        body = os.path.join(root, "body.md")
        canonical_root = subprocess.run(
            ["git", "-C", root, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True).stdout.strip()
        with open(body, "w") as f:
            f.write("key hunter2 here\nsee %s/docs/spec/x.md and /Users/bala/elsewhere.yml\n"
                    % canonical_root)
        code, env, out, _ = self.create(root, body_file=body, env_extra={
            "EXAMPLE_API_KEY": "hunter2", "TMPDIR": staged})
        self.assertEqual(code, 0, out)
        self.assertEqual(env["redaction"]["classes"], ["secrets", "absolute-paths"])
        self.assertEqual(env["redaction"]["secrets_redacted"], ["EXAMPLE_API_KEY"])
        self.assertNotIn("hunter2", out)              # the value never reaches stdout
        body_out = self.body_of(root, "ISSUE-001")
        self.assertIn("[redacted:EXAMPLE_API_KEY]", body_out)
        self.assertIn("see docs/spec/x.md", body_out)  # repo root -> repo-relative
        self.assertIn("[redacted:absolute-path]", body_out)
        self.assertNotIn("hunter2", body_out)
        self.assertNotIn(canonical_root, body_out)
        for name in os.listdir(staged):                # staged temp bodies are gone
            with open(os.path.join(staged, name)) as f:
                self.assertNotIn("hunter2", f.read())

    def test_redaction_is_deterministic(self):
        # S-036: identical inputs -> identical redacted output, byte for byte.
        root = self.make_repo(config_yaml="redaction:\n  secrets: [K]\n")
        body = os.path.join(root, "body.md")
        with open(body, "w") as f:
            f.write("secret s3cr3t and /Users/bala/x.md\n")
        for _ in range(2):
            code, env, out, _ = self.create(root, body_file=body, env_extra={"K": "s3cr3t"})
            self.assertEqual(code, 0, out)
        first = self.body_of(root, "ISSUE-001")
        second = self.body_of(root, "ISSUE-002")
        self.assertEqual(first, second)

    def test_public_visibility_tightens_path_redaction(self):
        # S-011: public repos do not keep repo-relative meaning — placeholder only.
        root = self.make_repo(config_yaml="redaction:\n  repo_visibility: public\n")
        canonical_root = subprocess.run(
            ["git", "-C", root, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True).stdout.strip()
        body = os.path.join(root, "body.md")
        with open(body, "w") as f:
            f.write("see %s/docs/spec/x.md\n" % canonical_root)
        code, env, out, _ = self.create(root, body_file=body)
        self.assertEqual(code, 0, out)
        self.assertIn("[redacted:absolute-path]", self.body_of(root, "ISSUE-001"))
        self.assertNotIn("docs/spec/x.md", self.body_of(root, "ISSUE-001"))

    def test_unknown_label_rejected_with_proposal_and_no_item(self):
        # S-037: a label outside the repo's set fails unknown-label naming the
        # valid values, and nothing is created.
        root = self.make_repo()
        code, env, _, _ = self.create(root, extra=["priority:p9"])
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "unknown-label")
        self.assertIn("p0", env["error"]["message"])
        self.assertIn("p3", env["error"]["message"])
        self.assertFalse(os.path.exists(os.path.join(root, ".agents/issues")))

    def test_unknown_prefix_rejected(self):
        root = self.make_repo()
        code, env, _, _ = self.create(root, extra=["color:red"])
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "unknown-label")
        self.assertIn("prefix", env["error"]["message"])

    def test_cardinality_violation_rejected(self):
        # S-007 via S-037: two type:* labels violate exactly1 — no silent mutation.
        root = self.make_repo()
        code, env, _, _ = self.create(root, extra=["type:feature"])
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "cardinality")
        self.assertIn("exactly1", env["error"]["message"])

    def test_config_dimensions_override_defaults(self):
        root = self.make_repo(config_yaml=(
            "labels:\n"
            "  dimensions:\n"
            "    - { prefix: type, count: exactly1 }\n"
            "    - { prefix: area, count: at_least1 }\n"))
        code, env, _, _ = self.create(root, extra=["area:core"])
        self.assertEqual(code, 0)
        self.assertIn("area:core", env["labels"])
        code, env, _, _ = self.create(root, title="Second", extra=["area:core", "area:ui"])
        self.assertEqual(code, 0)  # at_least1 permits two
        code, env, _, _ = self.create(root, title="Third")  # area missing -> cardinality
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "cardinality")
        self.assertIn("at_least1", env["error"]["message"])

    def test_exempt_label_accepted_from_config(self):
        root = self.make_repo(config_yaml="close_gate:\n  exempt_labels: [k wontfix]\n")
        code, env, _, _ = self.create(root, extra=["k wontfix"])
        self.assertEqual(code, 0)
        self.assertIn("k wontfix", env["labels"])

    def test_missing_body_file_is_usage(self):
        root = self.make_repo()
        code, env, _, _ = self.create(root, body_file=os.path.join(root, "nope.md"))
        self.assertEqual(code, 2)
        self.assertEqual(env["error"]["code"], "usage")

    def test_create_on_github_backend_blocks_until_t5(self):
        # File commands refuse a GitHub identity instead of creating a second ledger.
        root = self.make_repo()
        subprocess.run(["git", "-C", root, "remote", "add", "origin",
                        "https://github.com/acme/widgets"],
                       check=True, capture_output=True)
        code, env, _, _ = self.create(root)
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "blocked")
        code, env, _, _ = self.create(root, env_extra={"TRACK_WORK_BACKEND": "file"})
        self.assertEqual(code, 0)  # explicit override unlocks the file backend


class TestFileList(FileBackendFixture):

    def test_list_reports_items_with_labels_and_repo(self):
        # Defect this guards: losing per-item labels or repo attribution in the
        # aggregate (S-024's per-repo labeling) at the single-repo layer.
        root = self.make_repo()
        run_tw("create", "--title", "One", "--type", "bug", "--priority", "p1", cwd=root)
        run_tw("create", "--title", "Two", "--type", "feature", "--priority", "p2",
               "--label", "wontfix", cwd=root)
        code, env, out, _ = run_tw("list", cwd=root)
        self.assertEqual(code, 0, out)
        self.assertEqual(env["backend"], "file")
        self.assertEqual([i["id"] for i in env["items"]], ["ISSUE-001", "ISSUE-002"])
        self.assertEqual(env["items"][0]["title"], "One")
        self.assertEqual(env["items"][0]["status"], "draft")
        self.assertEqual(env["items"][0]["labels"], ["type:bug", "priority:p1"])
        self.assertEqual(env["items"][0]["repo"], os.path.basename(root))
        self.assertIn("wontfix", env["items"][1]["labels"])

    def test_list_filters_status_and_label(self):
        root = self.make_repo()
        run_tw("create", "--title", "One", "--type", "bug", "--priority", "p1", cwd=root)
        run_tw("create", "--title", "Two", "--type", "bug", "--priority", "p1",
               "--label", "wontfix", cwd=root)
        run_tw("status", "ISSUE-001", "in-progress", cwd=root)
        _, env, _, _ = run_tw("list", "--status", "in-progress", cwd=root)
        self.assertEqual([i["id"] for i in env["items"]], ["ISSUE-001"])
        _, env, _, _ = run_tw("list", "--status", "closed", cwd=root)
        self.assertEqual(env["items"], [])
        _, env, _, _ = run_tw("list", "--label", "wontfix", cwd=root)
        self.assertEqual([i["id"] for i in env["items"]], ["ISSUE-002"])
        _, env, _, _ = run_tw("list", "--status", "open", cwd=root)
        self.assertEqual(len(env["items"]), 2)  # open = every non-closed state

    def test_list_bad_status_value_is_usage(self):
        root = self.make_repo()
        code, env, _, _ = run_tw("list", "--status", "bogus", cwd=root)
        self.assertEqual(code, 2)
        self.assertEqual(env["error"]["code"], "usage")

    def test_list_bad_scope_is_not_found(self):
        # Defect this guards: a configured issues dir pointing at a non-directory
        # would otherwise look like an empty ledger instead of a broken scope.
        root = self.make_repo()
        with open(os.path.join(root, "not-a-dir"), "w") as f:
            f.write("x")
        code, env, _, _ = run_tw("list", cwd=root, env_extra={"TW_ISSUES_DIR": "not-a-dir"})
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "not-found")

    def test_list_empty_ledger_is_success(self):
        root = self.make_repo()
        code, env, _, _ = run_tw("list", cwd=root)
        self.assertEqual(code, 0)
        self.assertEqual(env["items"], [])


class TestFileStatus(FileBackendFixture):

    def test_status_transition_recorded_and_read_back(self):
        # Defect this guards: reporting from→to without the file actually holding
        # the new state (a stale or dropped engine call).
        root = self.make_repo()
        run_tw("create", "--title", "One", "--type", "bug", "--priority", "p1", cwd=root)
        run_tw("status", "ISSUE-001", "backlog", cwd=root)
        code, env, out, _ = run_tw("status", "ISSUE-001", "in-progress", cwd=root)
        self.assertEqual(code, 0, out)
        self.assertEqual(env["from"], "backlog")
        self.assertEqual(env["to"], "in-progress")
        self.assertIn("status: in-progress", self.item_text(root, "ISSUE-001"))
        self.assertEqual(env["labels"], ["type:bug", "priority:p1"])

    def test_status_cannot_close(self):
        # S-017/S-038: close requires landed evidence — status must not bypass it.
        root = self.make_repo()
        run_tw("create", "--title", "One", "--type", "bug", "--priority", "p1", cwd=root)
        code, env, _, _ = run_tw("status", "ISSUE-001", "closed", cwd=root)
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "invalid-transition")
        self.assertIn("close", env["error"]["message"])
        self.assertIn("status: draft", self.item_text(root, "ISSUE-001"))  # untouched

    def test_status_unknown_state_and_malformed_ref_are_usage(self):
        root = self.make_repo()
        run_tw("create", "--title", "One", "--type", "bug", "--priority", "p1", cwd=root)
        code, env, _, _ = run_tw("status", "ISSUE-001", "done", cwd=root)
        self.assertEqual(code, 2)
        self.assertEqual(env["error"]["code"], "usage")
        code, env, _, _ = run_tw("status", "../../etc/passwd", "backlog", cwd=root)
        self.assertEqual(code, 2)
        self.assertEqual(env["error"]["code"], "usage")

    def test_status_missing_item_is_not_found(self):
        root = self.make_repo()
        code, env, _, _ = run_tw("status", "ISSUE-999", "backlog", cwd=root)
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "not-found")


class TestFileClose(FileBackendFixture):
    """S-038 (file half): close only with landed evidence or an exempt label."""

    def test_close_without_evidence_refuses_and_does_not_mutate(self):
        root = self.make_repo()
        run_tw("create", "--title", "One", "--type", "bug", "--priority", "p1", cwd=root)
        code, env, _, _ = run_tw("close", "ISSUE-001", cwd=root)
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "landed-evidence")
        self.assertIn("ISSUE-001", env["error"]["message"])
        self.assertIn("status: draft", self.item_text(root, "ISSUE-001"))  # no mutation

    def test_close_with_padded_and_unpadded_commit_reference(self):
        # Real convention: commits cite ISSUE-57 for ISSUE-057 — both must verify.
        root = self.make_repo()
        run_tw("create", "--title", "One", "--type", "bug", "--priority", "p1", cwd=root)
        run_tw("create", "--title", "Two", "--type", "bug", "--priority", "p1", cwd=root)
        self.commit(root, "Fixes ISSUE-001: padded ref")  # canonical padded form
        self.commit(root, "Fixes ISSUE-2: unpadded ref")  # historical unpadded form
        for item_id in ("ISSUE-001", "ISSUE-002"):
            code, env, out, _ = run_tw("close", item_id, cwd=root)
            self.assertEqual(code, 0, "%s: %s" % (item_id, out))
            self.assertEqual(env["evidence"]["check"], "commit")
            self.assertRegex(env["evidence"]["commit"], r"^[0-9a-f]{40}$")
            self.assertIn("status: closed", self.item_text(root, item_id))

    def test_close_digit_boundary_not_fooled_by_longer_ids(self):
        # Defect this guards: ISSUE-001 closed by an ISSUE-0010-only history.
        root = self.make_repo()
        run_tw("create", "--title", "One", "--type", "bug", "--priority", "p1", cwd=root)
        self.commit(root, "work on ISSUE-0010 unrelated")
        code, env, _, _ = run_tw("close", "ISSUE-001", cwd=root)
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "landed-evidence")

    def test_close_via_exempt_label(self):
        root = self.make_repo()
        run_tw("create", "--title", "One", "--type", "bug", "--priority", "p1",
               "--label", "wontfix", cwd=root)
        code, env, out, _ = run_tw("close", "ISSUE-001", cwd=root)
        self.assertEqual(code, 0, out)
        self.assertEqual(env["evidence"], {"check": "exempt-label", "label": "wontfix"})

    def test_close_config_exempt_labels_override_defaults(self):
        root = self.make_repo(config_yaml="close_gate:\n  exempt_labels: [k wontfix]\n")
        run_tw("create", "--title", "One", "--type", "bug", "--priority", "p1",
               "--label", "k wontfix", cwd=root)
        code, env, _, _ = run_tw("close", "ISSUE-001", cwd=root)
        self.assertEqual(code, 0)
        self.assertEqual(env["evidence"]["label"], "k wontfix")

    def test_close_missing_item_is_not_found(self):
        root = self.make_repo()
        code, env, _, _ = run_tw("close", "ISSUE-999", cwd=root)
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "not-found")


class TestFileConfinement(FileBackendFixture):
    """S-016 through the CLI: traversal, symlinks, configured issues_dir."""

    def test_traversal_issues_dir_rejected_and_nothing_escapes(self):
        # Defect this guards: TW_ISSUES_DIR carrying the ledger outside the repo.
        root = self.make_repo()
        parent = os.path.dirname(root)
        code, env, _, _ = run_tw("list", cwd=root, env_extra={"TW_ISSUES_DIR": "../escape"})
        self.assertEqual(code, 2)
        self.assertEqual(env["error"]["code"], "usage")
        code, env, _, _ = run_tw("list", cwd=root, env_extra={"TW_ISSUES_DIR": "/tmp/abs"})
        self.assertEqual(code, 2)
        self.assertEqual(env["error"]["code"], "usage")
        code, env, _, _ = run_tw("create", "--title", "X", "--type", "bug",
                                 "--priority", "p1", cwd=root,
                                 env_extra={"TW_ISSUES_DIR": "../escape"})
        self.assertEqual(code, 2)
        self.assertFalse(os.path.exists(os.path.join(parent, "escape")))

    def test_symlinked_issues_dir_refused(self):
        # Defect this guards: a symlinked ledger silently writing elsewhere.
        import tempfile
        root = self.make_repo()
        target = tempfile.mkdtemp(prefix="tw-t4-evil-")
        self.addCleanup(__import__("shutil").rmtree, target, True)
        os.makedirs(os.path.join(root, ".agents"))
        os.symlink(target, os.path.join(root, ".agents", "issues"))
        for args in (["list"], ["create", "--title", "X", "--type", "bug", "--priority", "p1"]):
            code, env, _, _ = run_tw(*args, cwd=root)
            self.assertEqual(code, 1, args)
            self.assertEqual(env["error"]["code"], "conflict", args)
        self.assertEqual(os.listdir(target), [])      # nothing reached the target

    def test_symlinked_item_refused(self):
        root = self.make_repo()
        run_tw("create", "--title", "One", "--type", "bug", "--priority", "p1", cwd=root)
        outside = os.path.join(root, "outside.md")
        with open(outside, "w") as f:
            f.write("decoy")
        os.symlink(outside, os.path.join(root, ".agents", "issues", "ISSUE-002.md"))
        code, env, _, _ = run_tw("status", "ISSUE-002", "backlog", cwd=root)
        self.assertEqual(code, 1)
        self.assertEqual(env["error"]["code"], "conflict")

    def test_config_issues_dir_honored(self):
        root = self.make_repo(config_yaml="issues_dir: docs/backlog\n")
        code, env, out, _ = run_tw("create", "--title", "One", "--type", "bug",
                                   "--priority", "p1", cwd=root)
        self.assertEqual(code, 0, out)
        self.assertEqual(env["issues_dir"], "docs/backlog")
        self.assertTrue(os.path.isfile(os.path.join(root, "docs/backlog/ISSUE-001.md")))


class TestFileConcurrency(FileBackendFixture):
    """S-016/S-018: parallel creates serialize to unique IDs with isolated bodies."""

    def test_parallel_creates_unique_ids_intact_index_isolated_bodies(self):
        # Defect this guards: lock-contention failures surfacing as create errors,
        # duplicate IDs, a torn index, or one agent filing another's body.
        root = self.make_repo()
        marker_dir = __import__("tempfile").mkdtemp(prefix="tw-t4-par-")
        self.addCleanup(__import__("shutil").rmtree, marker_dir, True)
        procs = []
        for n in range(4):
            body = os.path.join(marker_dir, "body-%d.md" % n)
            with open(body, "w") as f:
                f.write("parallel body MARKER-%d\n" % n)
            env = dict(os.environ)
            for ambient in ("TW_NONINTERACTIVE", "TRACK_WORK_BACKEND", "GH_REPO"):
                env.pop(ambient, None)
            procs.append((n, subprocess.Popen(
                [sys.executable, SCRIPT, "create", "--title", "Parallel %d" % n,
                 "--type", "bug", "--priority", "p2", "--body-file", body],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                env=env, cwd=root)))
        marker_to_id = {}
        for n, proc in procs:
            stdout, _ = proc.communicate(timeout=60)
            self.assertEqual(proc.returncode, 0, stdout)
            envelope = json.loads(stdout)
            self.assertTrue(envelope["ok"], envelope)
            marker_to_id[n] = envelope["item"]["id"]
        self.assertEqual(len(set(marker_to_id.values())), 4, marker_to_id)
        with open(os.path.join(root, ".agents/issues/README.md")) as f:
            self.assertEqual(sum(1 for line in f if line.startswith("| [ISSUE-")), 4)
        self.assertFalse(os.path.exists(os.path.join(root, ".agents/issues/.track-work.lock")))
        for n in range(4):  # each item carries its own process's body — never another's
            text = self.item_text(root, marker_to_id[n])
            self.assertIn("MARKER-%d" % n, text)
            for other in range(4):
                if other != n:
                    self.assertNotIn("MARKER-%d" % other, text)
