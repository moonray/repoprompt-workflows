import { execFileSync } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { test } from "node:test";
import assert from "node:assert/strict";

const HOOK = path.join(import.meta.dirname, "oracle-review-reminder.py");

// Each test gets its own state dir + session id, so accumulation is isolated.
function fresh() {
  const dir = mkdtempSync(path.join(tmpdir(), "oracle-hook-"));
  return { dir, sid: `sess-${Math.random().toString(36).slice(2)}` };
}

function runHook(payload, f) {
  const out = execFileSync("python3", [HOOK], {
    input: JSON.stringify(payload),
    encoding: "utf8",
    env: { ...process.env, ORACLE_REVIEW_STATE_DIR: f.dir },
  });
  return out.trim() ? JSON.parse(out) : null;
}

const EDIT = (f, file_path, tool_response) => ({
  hook_event_name: "PostToolUse",
  session_id: f.sid,
  tool_name: "mcp__RepoPromptCE__apply_edits",
  tool_input: { path: file_path },
  ...(tool_response !== undefined ? { tool_response } : {}),
});

const COMMIT = (f, command = 'git commit -m "x"', tool_response) => ({
  hook_event_name: "PostToolUse",
  session_id: f.sid,
  tool_name: "Bash",
  tool_input: { command },
  ...(tool_response !== undefined ? { tool_response } : {}),
});

const ORACLE = (f) => ({
  hook_event_name: "PostToolUse",
  session_id: f.sid,
  tool_name: "mcp__RepoPromptCE__ask_oracle",
  tool_input: { message: "review the diff" },
});

test("below threshold (2 files) stays silent at commit", () => {
  const f = fresh();
  runHook(EDIT(f, "src/a.py"), f);
  runHook(EDIT(f, "src/b.py"), f);
  assert.equal(runHook(COMMIT(f), f), null);
});

test("threshold (3 non-doc files) with no consultation nudges once", () => {
  const f = fresh();
  for (const p of ["src/a.py", "src/b.py", "src/c.ts"]) runHook(EDIT(f, p), f);
  const r = runHook(COMMIT(f), f);
  const ctx = r?.hookSpecificOutput?.additionalContext ?? "";
  assert.match(ctx, /ORACLE REVIEW/);
  assert.match(ctx, /ask_oracle/);
  assert.match(ctx, /model-routing/);
  // one-shot: a second qualifying commit stays silent
  assert.equal(runHook(COMMIT(f), f), null);
});

test("consulted session stays silent at commit", () => {
  const f = fresh();
  for (const p of ["src/a.py", "src/b.py", "src/c.ts"]) runHook(EDIT(f, p), f);
  runHook(ORACLE(f), f);
  assert.equal(runHook(COMMIT(f), f), null);
});

test("spec/plan write alone crosses the threshold", () => {
  const f = fresh();
  runHook(EDIT(f, "docs/spec/thing.md"), f);
  const r = runHook(COMMIT(f), f);
  assert.match(r?.hookSpecificOutput?.additionalContext ?? "", /ORACLE REVIEW/);
});

test("doc-only change sets stay silent", () => {
  const f = fresh();
  for (const p of ["README.md", "docs/guide.md", "notes.txt"]) runHook(EDIT(f, p), f);
  assert.equal(runHook(COMMIT(f), f), null);
});

test("failed edits do not count toward the threshold", () => {
  const f = fresh();
  runHook(EDIT(f, "src/a.py"), f);
  runHook(EDIT(f, "src/b.py"), f);
  runHook(EDIT(f, "src/c.py", { is_error: true }), f);
  assert.equal(runHook(COMMIT(f), f), null);
});

test("non-commit shell commands never nudge regardless of state", () => {
  const f = fresh();
  for (const p of ["src/a.py", "src/b.py", "src/c.ts"]) runHook(EDIT(f, p), f);
  assert.equal(runHook(COMMIT(f, "git status"), f), null);
  assert.equal(runHook(COMMIT(f, "git add -A"), f), null);
  assert.equal(runHook(COMMIT(f, "git push"), f), null);
  assert.equal(runHook(COMMIT(f, "gh pr close 12"), f), null);
});

test("a failed commit stays silent and does not consume the one-shot", () => {
  const f = fresh();
  for (const p of ["src/a.py", "src/b.py", "src/c.ts"]) runHook(EDIT(f, p), f);
  assert.equal(runHook(COMMIT(f, 'git commit -m "x"', { is_error: true }), f), null);
  assert.match(
    runHook(COMMIT(f), f)?.hookSpecificOutput?.additionalContext ?? "",
    /ORACLE REVIEW/,
  );
});

test("chained and flagged commit forms are detected", () => {
  const f1 = fresh();
  for (const p of ["src/a.py", "src/b.py", "src/c.ts"]) runHook(EDIT(f1, p), f1);
  assert.match(
    runHook(COMMIT(f1, 'git add -A && git commit -m "land"'), f1)
      ?.hookSpecificOutput?.additionalContext ?? "",
    /ORACLE REVIEW/,
  );
  const f2 = fresh();
  for (const p of ["src/a.py", "src/b.py", "src/c.ts"]) runHook(EDIT(f2, p), f2);
  assert.match(
    runHook(COMMIT(f2, 'git -C /some/repo commit -m "land"'), f2)
      ?.hookSpecificOutput?.additionalContext ?? "",
    /ORACLE REVIEW/,
  );
});

test("apply_patch command paths are accumulated (Codex shape)", () => {
  const f = fresh();
  const patch = "*** Begin Patch\n*** Update File: src/a.py\n@@\n-x\n+y\n*** Update File: src/b.py\n@@\n-x\n+y\n*** Update File: src/c.py\n@@\n-x\n+y\n*** End Patch";
  runHook({
    hook_event_name: "PostToolUse",
    session_id: f.sid,
    tool_name: "apply_patch",
    tool_input: { command: patch },
  }, f);
  assert.match(
    runHook(COMMIT(f), f)?.hookSpecificOutput?.additionalContext ?? "",
    /ORACLE REVIEW/,
  );
});

test("foreign events are ignored", () => {
  const f = fresh();
  for (const p of ["src/a.py", "src/b.py", "src/c.ts"]) runHook(EDIT(f, p), f);
  assert.equal(runHook({
    hook_event_name: "Stop",
    session_id: f.sid,
  }, f), null);
});

test("steering markdown (.agents skills/workflows/rules) counts as non-doc", () => {
  const f = fresh();
  runHook(EDIT(f, ".agents/skills/model-routing/SKILL.md"), f);
  runHook(EDIT(f, ".agents/workflows/Deep-Review.md"), f);
  runHook(EDIT(f, ".agents/rules/global.md"), f);
  assert.match(
    runHook(COMMIT(f), f)?.hookSpecificOutput?.additionalContext ?? "",
    /ORACLE REVIEW/,
  );
});

test("docs/plans writes also set the spec/plan flag", () => {
  const f = fresh();
  runHook(EDIT(f, "docs/plans/thing-2026.md"), f);
  assert.match(
    runHook(COMMIT(f), f)?.hookSpecificOutput?.additionalContext ?? "",
    /ORACLE REVIEW/,
  );
});

test("commit look-alikes and dry-runs do not trigger", () => {
  const f = fresh();
  for (const p of ["src/a.py", "src/b.py", "src/c.ts"]) runHook(EDIT(f, p), f);
  assert.equal(runHook(COMMIT(f, "git commit-tree HEAD^{tree} -m x"), f), null);
  assert.equal(runHook(COMMIT(f, "git commit-graph write"), f), null);
  assert.equal(runHook(COMMIT(f, 'git commit --dry-run -m "x"'), f), null);
  // ...and none of those consumed the one-shot:
  assert.match(
    runHook(COMMIT(f), f)?.hookSpecificOutput?.additionalContext ?? "",
    /ORACLE REVIEW/,
  );
});

test("long-flag and =value commit forms are detected", () => {
  const f = fresh();
  for (const p of ["src/a.py", "src/b.py", "src/c.ts"]) runHook(EDIT(f, p), f);
  assert.match(
    runHook(COMMIT(f, "git --no-pager commit -m x"), f)
      ?.hookSpecificOutput?.additionalContext ?? "",
    /ORACLE REVIEW/,
  );
  const f2 = fresh();
  for (const p of ["src/a.py", "src/b.py", "src/c.ts"]) runHook(EDIT(f2, p), f2);
  assert.match(
    runHook(COMMIT(f2, 'git --git-dir=/x/.git --work-tree=/x commit -m y'), f2)
      ?.hookSpecificOutput?.additionalContext ?? "",
    /ORACLE REVIEW/,
  );
});

test("absent session_id keys state by cwd (fallback shares state)", () => {
  const dir = mkdtempSync(path.join(tmpdir(), "oracle-hook-"));
  const shared = { dir, sid: undefined };
  const NO_SID = (file_path) => ({
    hook_event_name: "PostToolUse",
    cwd: "/fallback/cwd",
    tool_name: "mcp__RepoPromptCE__apply_edits",
    tool_input: { path: file_path },
  });
  const env = { ...process.env, ORACLE_REVIEW_STATE_DIR: dir };
  for (const p of ["src/a.py", "src/b.py", "src/c.py"]) {
    execFileSync("python3", [HOOK], { input: JSON.stringify(NO_SID(p)), encoding: "utf8", env });
  }
  const r = execFileSync("python3", [HOOK], {
    input: JSON.stringify({
      hook_event_name: "PostToolUse",
      cwd: "/fallback/cwd",
      tool_name: "Bash",
      tool_input: { command: 'git commit -m "x"' },
    }),
    encoding: "utf8",
    env,
  });
  assert.match(JSON.parse(r).hookSpecificOutput.additionalContext, /ORACLE REVIEW/);
  void shared;
});

test("path aliasing collapses (./ and // prefixes normalize)", () => {
  const f = fresh();
  runHook(EDIT(f, "src/a.py"), f);
  runHook(EDIT(f, "./src/a.py"), f);
  runHook(EDIT(f, "src//a.py"), f);
  assert.equal(runHook(COMMIT(f), f), null); // one distinct file, not three
});

test("malformed input exits cleanly", () => {
  const f = fresh();
  const out = execFileSync("python3", [HOOK], {
    input: "not json at all",
    encoding: "utf8",
    env: { ...process.env, ORACLE_REVIEW_STATE_DIR: f.dir },
  });
  assert.equal(out.trim(), "");
});
