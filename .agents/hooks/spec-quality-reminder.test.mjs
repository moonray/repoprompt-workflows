// Unit tests for the spec/plan/skill artifact reminder hook (#47).
// Layer: payload -> stdout contract of the python script, via real child processes
// (the matcher itself is settings.json config and is verified by the e2e probe, not here).
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";

const SCRIPT = new URL("./spec-quality-reminder.py", import.meta.url).pathname;

function run(payload) {
  const r = spawnSync("python3", [SCRIPT], { input: JSON.stringify(payload), encoding: "utf8" });
  assert.equal(r.status, 0, `script exited ${r.status}: ${r.stderr}`);
  const out = r.stdout.trim();
  return out ? JSON.parse(out).hookSpecificOutput.additionalContext : "";
}

function runRaw(input) {
  const r = spawnSync("python3", [SCRIPT], { input, encoding: "utf8" });
  assert.equal(r.status, 0, `script exited ${r.status}: ${r.stderr}`);
  return r.stdout.trim();
}

const edit = (tool_input, tool_response) => ({
  hook_event_name: "PostToolUse",
  tool_name: "mcp__RepoPromptCE__apply_edits",
  tool_input,
  ...(tool_response !== undefined ? { tool_response } : {}),
});

test("spec edit (relative apply_patch body) -> SPEC QUALITY reminder", () => {
  const c = edit({ command: "*** Begin Patch\n*** Add File: docs/spec/foo.md\n+x" });
  assert.match(run(c), /SPEC QUALITY/);
});

test("absolute path under docs/spec via path field -> SPEC QUALITY reminder", () => {
  assert.match(run(edit({ path: "/Users/agent/work/project/docs/spec/foo.md" })), /SPEC QUALITY/);
});

test("plan edit -> PLAN READINESS reminder (and only that class)", () => {
  const c = run(edit({ path: "docs/plans/foo.md" }));
  assert.match(c, /PLAN READINESS/);
  assert.ok(!c.includes("SPEC QUALITY"));
});

test("nested SKILL.md (group/audit depth) -> SKILL STANDARDS reminder", () => {
  // Defect this guards: a one-level .agents/skills/*/SKILL.md glob misses real nested skills.
  assert.match(run(edit({ path: ".agents/skills/group-a/audit/SKILL.md" })), /SKILL STANDARDS/);
});

test("file_actions move: new_path AND old_path are both inspected", () => {
  // Defect this guards: a move INTO docs/spec whose destination lives in new_path only.
  assert.match(run(edit({ action: "move", path: "docs/old.md", new_path: "docs/spec/moved.md" })), /SPEC QUALITY/);
});

test("batched edits: every file in the edits array is classified, one bad entry is not fatal", () => {
  // Defect this guards: a malformed sibling suppressing the reminder for the real spec path.
  const c = run(edit({ edits: [{ path: 7 }, { path: "docs/spec/batch.md" }, { path: "docs/plain.md" }] }));
  assert.match(c, /SPEC QUALITY/);
  assert.ok(!c.includes("PLAN READINESS"));
});

test("multi-class batch aggregates BOTH reminders in one output", () => {
  const c = run(edit({ edits: [{ path: "docs/spec/a.md" }, { path: ".agents/skills/x/SKILL.md" }] }));
  assert.match(c, /SPEC QUALITY/);
  assert.match(c, /SKILL STANDARDS/);
});

test("negative: unrelated markdown and spec README are silent", () => {
  assert.equal(run(edit({ path: "docs/README.md" })), "");
  assert.equal(run(edit({ path: "docs/spec/README.md" })), "");
  assert.equal(run(edit({ path: "docs/business/overview.md" })), "");
  assert.equal(run(edit({ path: ".agents/skills/foo/OTHER.md" })), "");
});

test("negative: failed tool call makes no reminder (every failure shape)", () => {
  // Defect this guards: nagging on edits that did not change anything — across
  // EVERY failure shape the suppressor recognizes; the positive control guards
  // the opposite regression (a success-dict wrongly treated as failure would
  // silently suppress all reminders).
  for (const tr of [{ is_error: true }, { error: true }, { status: "error" }, { status: "ERROR" }]) {
    assert.equal(run(edit({ path: "docs/spec/failed.md" }, tr)), "", JSON.stringify(tr));
  }
  assert.match(run(edit({ path: "docs/spec/ok.md" }, { status: 200 })), /SPEC QUALITY/);
});

test("negative: valid-but-non-object JSON exits 0 with no output", () => {
  // Defect this guards: a JSON array/null/string parses successfully and then
  // crashes on payload.get() — exit 1 + traceback in the hook log.
  for (const raw of ["[]", "null", '"x"', "42"]) {
    assert.equal(runRaw(raw), "", raw);
  }
});

test("negative: non-PostToolUse events are ignored", () => {
  assert.equal(run({ hook_event_name: "PreToolUse", tool_input: { path: "docs/spec/x.md" } }), "");
});

// ---- Cross-runtime compatibility (#47 follow-up): the shared script must serve
// Claude Code (MCP + native), Codex, and opencode without breaking any of them.

test("codex shape: apply_patch command body + tool_name apply_patch -> SPEC QUALITY", () => {
  // Codex delivers edits as a patch command; payload is otherwise Claude-compatible.
  const c = run({
    hook_event_name: "PostToolUse",
    tool_name: "apply_patch",
    tool_input: {
      command: "*** Begin Patch\n*** Update File: docs/spec/codex.md\n@@\n-x\n+y",
    },
  });
  assert.match(c, /SPEC QUALITY/);
});

test("opencode shape: write tool, spread args + extracted file_path -> SPEC QUALITY", () => {
  // the opencode plugin builds {tool_input: {...args, file_path}} — extra arg keys must be ignored.
  const c = run({
    hook_event_name: "PostToolUse",
    tool_name: "write",
    tool_input: { content: "x", filePath: "docs/spec/oc.md", file_path: "docs/spec/oc.md" },
  });
  assert.match(c, /SPEC QUALITY/);
});

test("opencode shape: edit tool with a paths array of strings -> classified per entry", () => {
  // Defect this guards: a runtime sending paths as a list bypassing scalar keys.
  const c = run({
    hook_event_name: "PostToolUse",
    tool_name: "edit",
    tool_input: { paths: ["docs/other.md", "docs/plans/oc-plan.md"] },
  });
  assert.match(c, /PLAN READINESS/);
  assert.ok(!c.includes("SPEC QUALITY"));
});

test("cross-runtime negative: bash-shaped payload with no matching path is silent", () => {
  assert.equal(run({
    hook_event_name: "PostToolUse",
    tool_name: "bash",
    tool_input: { command: "echo hi" },
  }), "");
});
