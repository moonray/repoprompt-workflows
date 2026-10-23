// Regression tests for the test-quality reminder hook (issue #2).
// Layer: payload -> marker/stdout contract of the python script, via real child
// processes and real temp git repos (markers keyed by resolved repo root, mtimes
// controlled with utimes). Wiring is config verified separately (README/installer).
import { test, after } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdtempSync, existsSync, utimesSync, writeFileSync, mkdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { homedir } from "node:os";

const SCRIPT = new URL("./test-quality-reminder.py", import.meta.url).pathname;
const CACHE_DIR = join(homedir(), ".cache", "tq-hook");
const repos = [];

function mkrepo() {
  const dir = mkdtempSync(join(tmpdir(), "tqhook-"));
  spawnSync("git", ["-C", dir, "init", "-q"]);
  // The hook keys markers by `git rev-parse --show-toplevel` of the payload cwd —
  // on macOS that canonicalizes (/var -> /private/var), so resolve it the same way.
  const root = spawnSync("git", ["-C", dir, "rev-parse", "--show-toplevel"],
    { encoding: "utf8" }).stdout.trim();
  repos.push({ dir, root });
  return { dir, root };
}

function marker(root, kind) { // kind: "lastrun" | "tqskill"
  const key = createHash("sha1").update(root).digest("hex").slice(0, 12);
  return join(CACHE_DIR, `${kind}-${key}`);
}

function run(payload, env) {
  const r = spawnSync("python3", [SCRIPT], {
    input: JSON.stringify(payload), encoding: "utf8",
    ...(env ? { env: { ...process.env, ...env } } : {}),
  });
  assert.equal(r.status, 0, `script exited ${r.status}: ${r.stderr}`);
  return r.stdout.trim();
}

function runRaw(input) {
  const r = spawnSync("python3", [SCRIPT], { input, encoding: "utf8" });
  assert.equal(r.status, 0, `script exited ${r.status}: ${r.stderr}`);
  return r.stdout.trim();
}

const bash = (command, root) => ({
  hook_event_name: "PostToolUse", tool_name: "Bash", cwd: root, tool_input: { command },
});

const stop = (root) => ({ hook_event_name: "Stop", cwd: root });

const ATTEST = `python3 "$(git rev-parse --show-toplevel)/.agents/hooks/test-quality-reminder.py" --attest-vetted`;

after(() => {
  for (const { dir, root } of repos) {
    rmSync(dir, { recursive: true, force: true });
    for (const kind of ["lastrun", "tqskill"]) {
      try { rmSync(marker(root, kind), { force: true }); } catch {}
    }
  }
});

// ---- PostToolUse: run detection (SP-1..SP-3) --------------------------------

test("real runner invocation writes the run marker and the vet reminder", () => {
  // Defect: broken run detection would kill the run half of the Stop gate.
  const { root } = mkrepo();
  const out = run(bash("pytest -q", root));
  const parsed = JSON.parse(out);
  assert.equal(parsed.hookSpecificOutput.hookEventName, "PostToolUse");
  assert.match(parsed.hookSpecificOutput.additionalContext, /TEST QUALITY/);
  assert.ok(existsSync(marker(root, "lastrun")), "lastrun marker written");
  assert.ok(!existsSync(marker(root, "tqskill")), "a run never stamps the vet marker");
});

test("runner words outside command position do nothing (heredoc/comment/string)", () => {
  // Defect: a bare 'pytest' in prose/comment/heredoc registering a phantom run.
  const { root } = mkrepo();
  for (const cmd of [
    "cat <<'EOF'\npytest\nEOF",
    "# run pytest now",
    'echo "please run pytest before stopping"',
  ]) {
    assert.equal(run(bash(cmd, root)), "", cmd);
  }
  assert.ok(!existsSync(marker(root, "lastrun")));
});

test("help/version and install invocations are not runs", () => {
  // Defect: 'pytest --help' / 'npm install jest' counting as vetted runs.
  const { root } = mkrepo();
  for (const cmd of ["pytest --help", "npm install jest"]) {
    assert.equal(run(bash(cmd, root)), "", cmd);
  }
  assert.ok(!existsSync(marker(root, "lastrun")));
});

test("malformed payloads exit 0 silently (invalid JSON and non-object JSON)", () => {
  // Defect: a traceback (exit 1) on '[]'/null/noise would spam every hook log.
  for (const raw of ["not json{", "[]", "null", "42"]) {
    assert.equal(runRaw(raw), "", raw);
  }
});

// ---- PostToolUse: vet-marker paths (skill + attestation) ---------------------

test("Skill invocation of test-quality stamps the vet marker only", () => {
  // Defect: the vet half dead -> Claude Code gate could never clear.
  const { root } = mkrepo();
  const out = run({
    hook_event_name: "PostToolUse", tool_name: "Skill", cwd: root,
    tool_input: { skill: "test-quality" },
  });
  assert.equal(out, "");
  assert.ok(existsSync(marker(root, "tqskill")));
  assert.ok(!existsSync(marker(root, "lastrun")));
});

test("a different skill stamps nothing", () => {
  // Defect: any skill invocation clearing the vet gate without vetting.
  const { root } = mkrepo();
  run({ hook_event_name: "PostToolUse", tool_name: "Skill", cwd: root, tool_input: { skill: "spec-quality" } });
  assert.ok(!existsSync(marker(root, "tqskill")));
});

test("attestation command stamps the vet marker under TQ_HOOK_RUNTIME (Codex rung)", () => {
  // Defect this whole issue exists for: Codex routes Stop but cannot observe skill
  // invocations, so the vet half could NEVER clear -> Stop gate unfixable until commit.
  const { root } = mkrepo();
  const out = run(bash(ATTEST, root), { TQ_HOOK_RUNTIME: "codex" });
  assert.equal(out, "");
  assert.ok(existsSync(marker(root, "tqskill")), "attestation stamps vet marker");
  assert.ok(!existsSync(marker(root, "lastrun")), "attestation is not a run");
});

test("attestation is inert without TQ_HOOK_RUNTIME (Claude Code pin)", () => {
  // Defect: an ungated attest command would let Claude Code agents bypass the
  // real Skill-tool invocation — weakening the pinned runtime.
  const { root } = mkrepo();
  assert.equal(run(bash(ATTEST, root)), "");
  assert.ok(!existsSync(marker(root, "tqskill")));
  assert.ok(!existsSync(marker(root, "lastrun")));
});

test("attestation detection survives shell substitution paths and quoted-string mentions", () => {
  // Defect: the documented command embeds $(git rev-parse …) — naive token
  // matching must still find the flag; and an echo of the words (flag not a
  // standalone argv token) must NOT count as a deliberate attestation.
  const { root } = mkrepo();
  run(bash(ATTEST, root), { TQ_HOOK_RUNTIME: "codex" });
  assert.ok(existsSync(marker(root, "tqskill")), "unexpanded $() form still attests");
  const { root: root2 } = mkrepo();
  run(bash('echo "python3 test-quality-reminder.py --attest-vetted"', root2), { TQ_HOOK_RUNTIME: "codex" });
  assert.ok(!existsSync(marker(root2, "tqskill")), "echoing the words is not attesting");
});

// ---- Stop gate (SP-4..SP-7 + per-runtime) ------------------------------------

function dirtyRepo(testPath) {
  const { dir, root } = mkrepo();
  const f = join(dir, testPath);
  mkdirSync(join(f, ".."), { recursive: true });
  writeFileSync(f, "content\n");
  return { root, file: f };
}

const T0 = Date.now() / 1000;
function aged(path, secondsAgo) { utimesSync(path, T0 - secondsAgo, T0 - secondsAgo); }

test("dirty test file with no markers is blocked with the Skill-tool reason", () => {
  // Defect: gate silently passing unvetted test edits.
  const { root, file } = dirtyRepo("tests/x_test.py");
  aged(file, 50);
  const out = run(stop(root));
  const parsed = JSON.parse(out);
  assert.equal(parsed.decision, "block");
  assert.match(parsed.reason, /TEST QUALITY GATE/);
  assert.match(parsed.reason, /Skill tool/);
});

test("edit→run→vet→stop is allowed (both markers newer than the edit)", () => {
  // Defect: a gate that traps even after BOTH owed acts were performed.
  const { root, file } = dirtyRepo("tests/x_test.py");
  aged(file, 100);
  for (const kind of ["lastrun", "tqskill"]) {
    writeFileSync(marker(root, kind), "");
    aged(marker(root, kind), 10);
  }
  assert.equal(run(stop(root)), "");
});

test("edit→run→stop WITHOUT vetting is blocked (run alone never clears)", () => {
  // Defect: the silent run-only clear the binding policy prohibits.
  const { root, file } = dirtyRepo("tests/x_test.py");
  aged(file, 100);
  writeFileSync(marker(root, "lastrun"), "");
  aged(marker(root, "lastrun"), 10);
  assert.equal(JSON.parse(run(stop(root))).decision, "block");
});

test("vetting without a run is blocked", () => {
  // Defect: attesting/skilling around an un-run suite.
  const { root, file } = dirtyRepo("tests/x_test.py");
  aged(file, 100);
  writeFileSync(marker(root, "tqskill"), "");
  aged(marker(root, "tqskill"), 10);
  assert.equal(JSON.parse(run(stop(root))).decision, "block");
});

test("markers older than the edit are stale (block)", () => {
  // Defect: post-edit test tweaks riding pre-edit markers.
  const { root, file } = dirtyRepo("tests/x_test.py");
  for (const kind of ["lastrun", "tqskill"]) {
    writeFileSync(marker(root, kind), "");
    aged(marker(root, kind), 100);
  }
  aged(file, 10);
  assert.equal(JSON.parse(run(stop(root))).decision, "block");
});

test("clean repo stops freely; docs/spec dirt is not test dirt", () => {
  // Defects: gating clean trees; or a docs/spec markdown home read as tests/.
  const clean = mkrepo();
  assert.equal(run(stop(clean.root)), "");
  const docs = dirtyRepo("docs/spec/foo.md");
  aged(docs.file, 10);
  assert.equal(run(stop(docs.root)), "");
});

test("under TQ_HOOK_RUNTIME the block reason names the attestation command, not the Skill tool", () => {
  // Defect: a Codex agent told to use a Skill tool it does not have = an
  // unactionable stop loop (the exact pain reported in issue #2).
  const { root, file } = dirtyRepo("tests/x_test.py");
  aged(file, 50);
  const parsed = JSON.parse(run(stop(root), { TQ_HOOK_RUNTIME: "codex" }));
  assert.equal(parsed.decision, "block");
  assert.match(parsed.reason, /--attest-vetted/);
  assert.ok(!parsed.reason.includes("Skill tool"));
});

test("edit→run→attest→stop clears under TQ_HOOK_RUNTIME (the Codex path)", () => {
  // Defect: the rung-2 path this issue exists to build — full clear via attestation.
  const { root, file } = dirtyRepo("tests/x_test.py");
  aged(file, 100);
  for (const kind of ["lastrun", "tqskill"]) {
    writeFileSync(marker(root, kind), "");
    aged(marker(root, kind), 10);
  }
  assert.equal(run(stop(root), { TQ_HOOK_RUNTIME: "codex" }), "");
});
