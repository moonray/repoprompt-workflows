// Unit tests for the spec-accuracy reminder hook (#13).
// Layer: payload -> stdout contract of the python script, via real child processes
// (the matcher itself is settings.json config and is verified by the e2e probe, not here).
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";

const SCRIPT = new URL("./spec-accuracy-reminder.py", import.meta.url).pathname;

function run(payload) {
  const r = spawnSync("python3", [SCRIPT], { input: JSON.stringify(payload), encoding: "utf8" });
  assert.equal(r.status, 0, `script exited ${r.status}: ${r.stderr}`);
  const out = r.stdout.trim();
  return out ? JSON.parse(out).hookSpecificOutput.additionalContext : "";
}

const edit = (file_path, tool_response, cwd) => ({
  hook_event_name: "PostToolUse",
  tool_name: "mcp__RepoPromptCE__apply_edits",
  tool_input: { path: file_path },
  ...(cwd !== undefined ? { cwd } : {}),
  ...(tool_response !== undefined ? { tool_response } : {}),
});

// A fake repo root: exists on disk, with or without a docs/spec/ directory.
function fakeRepo(withSpec) {
  const dir = mkdtempSync(path.join(tmpdir(), "sar-test-"));
  if (withSpec) mkdirSync(path.join(dir, "docs", "spec"), { recursive: true });
  return dir;
}

test("runbook edit (.agents/slash/*.md, spec dir present) fires the nudge", () => {
  // Defect this guards: the observed 2026-10-30 incident — a rewritten runbook left its
  // spec describing the old behavior for days because nothing prompted a check.
  const repo = fakeRepo(true);
  try {
    assert.match(run(edit(`${repo}/.agents/slash/add-location.md`)), /SPEC ACCURACY/);
  } finally {
    rmSync(repo, { recursive: true, force: true });
  }
});

test("procedure and operations-doc edits fire the nudge", () => {
  const repo = fakeRepo(true);
  try {
    assert.match(run(edit(`${repo}/docs/procedures/deployment.md`)), /SPEC ACCURACY/);
    assert.match(run(edit(`${repo}/docs/operations/server-environment.md`)), /SPEC ACCURACY/);
  } finally {
    rmSync(repo, { recursive: true, force: true });
  }
});

test("repo without docs/spec/ stays silent (positive absence)", () => {
  // Negative control for the spec-dir gate: a repo whose operational docs have no specs
  // has nothing to drift against — nudging there is pure noise.
  const repo = fakeRepo(false);
  try {
    assert.equal(run(edit(`${repo}/.agents/slash/deploy.md`)), "");
    assert.equal(run(edit(`${repo}/docs/procedures/deployment.md`)), "");
  } finally {
    rmSync(repo, { recursive: true, force: true });
  }
});

test("unresolvable root nudges (remind rather than stay silent on a guess)", () => {
  // Defect this guards: a path whose repo root cannot be verified (e.g. cwd pointing
  // nowhere on disk) must not silently skip the check — verification failure is not
  // evidence of absence.
  assert.match(run(edit(".agents/slash/deploy.md", undefined, "/nonexistent/sar-root")), /SPEC ACCURACY/);
});

test("relative path resolves against payload cwd", () => {
  const withSpec = fakeRepo(true);
  const withoutSpec = fakeRepo(false);
  try {
    assert.match(run(edit(".agents/slash/deploy.md", undefined, withSpec)), /SPEC ACCURACY/);
    assert.equal(run(edit("docs/procedures/deployment.md", undefined, withoutSpec)), "");
  } finally {
    rmSync(withSpec, { recursive: true, force: true });
    rmSync(withoutSpec, { recursive: true, force: true });
  }
});

test("README.md under a watched dir stays silent", () => {
  // House convention: index READMEs are not behavioral docs.
  const repo = fakeRepo(true);
  try {
    assert.equal(run(edit(`${repo}/.agents/slash/README.md`)), "");
    assert.equal(run(edit(`${repo}/docs/procedures/README.md`)), "");
  } finally {
    rmSync(repo, { recursive: true, force: true });
  }
});

test("non-watched paths stay silent", () => {
  // Negative control: specs themselves, plans, and source files are not operational
  // docs (spec edits already have their own quality nudge).
  const repo = fakeRepo(true);
  try {
    assert.equal(run(edit(`${repo}/docs/spec/add-location.md`)), "");
    assert.equal(run(edit(`${repo}/docs/plans/plan-2026.md`)), "");
    assert.equal(run(edit(`${repo}/src/main.py`)), "");
  } finally {
    rmSync(repo, { recursive: true, force: true });
  }
});

test("failed edit is suppressed; unknown response shape still nudges", () => {
  // Defect this guards: nudging after an edit the runtime reported as errored (the doc
  // did not change) trains the model to ignore the nudge.
  const repo = fakeRepo(true);
  try {
    const p = `${repo}/.agents/slash/deploy.md`;
    assert.equal(run(edit(p, { is_error: true })), "");
    assert.equal(run(edit(p, { ok: false })), "");
    assert.match(run(edit(p, {})), /SPEC ACCURACY/);
  } finally {
    rmSync(repo, { recursive: true, force: true });
  }
});

test("batch inputs surface watched paths from arrays and moves", () => {
  // Defect this guards: apply_edits batches (edits[]), file_actions moves
  // (old_path/new_path), and multi-file writes (files[]) carry their paths in
  // nested/array keys — missing them leaves whole tool families unguarded.
  const repo = fakeRepo(true);
  try {
    const batch = {
      hook_event_name: "PostToolUse",
      tool_name: "MultiEdit",
      tool_input: { file_path: `${repo}/docs/notes.md`, edits: [{ path: `${repo}/.agents/slash/x.md` }] },
    };
    assert.match(run(batch), /SPEC ACCURACY/);
    const move = {
      hook_event_name: "PostToolUse",
      tool_name: "file_actions",
      tool_input: { path: `${repo}/.agents/slash/old-name.md`, new_path: `${repo}/docs/procedures/new-name.md` },
    };
    assert.match(run(move), /SPEC ACCURACY/);
  } finally {
    rmSync(repo, { recursive: true, force: true });
  }
});

test("apply_patch command forms are parsed for paths", () => {
  // Codex/opencode deliver edits as an apply_patch command with *** Update File headers.
  const repo = fakeRepo(true);
  try {
    const payload = {
      hook_event_name: "PostToolUse",
      tool_name: "Bash",
      tool_input: { command: `*** Begin Patch\n*** Update File: ${repo}/.agents/slash/run-tests.md\n@@\n-x\n+y\n*** End Patch\n` },
    };
    assert.match(run(payload), /SPEC ACCURACY/);
  } finally {
    rmSync(repo, { recursive: true, force: true });
  }
});

test("exactly one nudge per event with multiple watched paths", () => {
  const repo = fakeRepo(true);
  try {
    const payload = {
      hook_event_name: "PostToolUse",
      tool_name: "file_actions",
      tool_input: { paths: [`${repo}/.agents/slash/a.md`, `${repo}/docs/procedures/b.md`] },
    };
    const nudge = run(payload);
    assert.equal(nudge.match(/SPEC ACCURACY/g)?.length, 1);
  } finally {
    rmSync(repo, { recursive: true, force: true });
  }
});

test("foreign events are ignored", () => {
  const repo = fakeRepo(true);
  try {
    const payload = { hook_event_name: "Stop", tool_input: { path: `${repo}/.agents/slash/x.md` } };
    assert.equal(run(payload), "");
  } finally {
    rmSync(repo, { recursive: true, force: true });
  }
});

test("malformed input exits cleanly with no output", () => {
  for (const bad of ["not json", "null", "[1,2]", '"str"']) {
    const r = spawnSync("python3", [SCRIPT], { input: bad, encoding: "utf8" });
    assert.equal(r.status, 0, `input ${bad}: exited ${r.status}`);
    assert.equal(r.stdout.trim(), "");
  }
});

test("nudge content names the same-session check, old behavior, matrices, and the no-op", () => {
  const repo = fakeRepo(true);
  try {
    const nudge = run(edit(`${repo}/.agents/slash/deploy.md`));
    assert.match(nudge, /same session|NOW/i);
    assert.match(nudge, /OLD behavior/);
    assert.match(nudge, /conformance matrix/);
    assert.match(nudge, /no-op/);
  } finally {
    rmSync(repo, { recursive: true, force: true });
  }
});
