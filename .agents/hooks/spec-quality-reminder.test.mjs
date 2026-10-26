// Unit tests for the spec/plan/skill artifact reminder hook (#47).
// Layer: payload -> stdout contract of the python script, via real child processes
// (the matcher itself is settings.json config and is verified by the e2e probe, not here).
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";

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

test("absolute path under docs/spec via path field -> SPEC QUALITY reminder", () => {
  assert.match(run(edit({ path: "/Users/agent/work/project/docs/spec/foo.md" })), /SPEC QUALITY/);
});

test("backslash-separated paths are normalized before classification", () => {
  // Defect this guards: deleting the '\'->'/' normalization (as seemingly dead code)
  // would silently drop Windows-shaped payload paths from every rule.
  assert.match(run(edit({ path: "docs\\spec\\win.md" })), /SPEC QUALITY/);
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

test("file_actions move: destination in scalar new_path is inspected", () => {
  // Defect this guards: a move INTO docs/spec whose destination lives in new_path only.
  assert.match(run(edit({ action: "move", path: "docs/old.md", new_path: "docs/spec/moved.md" })), /SPEC QUALITY/);
});

test("file_actions move: source in scalar old_path is inspected", () => {
  // Defect this guards: dropping old_path from the scalar key tuple would let a move
  // OUT of docs/spec (removing the spec file) escape the reminder.
  assert.match(run(edit({ action: "move", old_path: "docs/spec/original.md", new_path: "docs/elsewhere.md" })), /SPEC QUALITY/);
});

test("batched edits: move pairs inside list entries carry new_path/old_path sub-keys", () => {
  // Defect this guards: the sub-key tuple inside list entries losing new_path or
  // old_path (e.g. reduced back to path/file_path) would let batched moves into or
  // out of docs/spec escape the reminder — each sub-key gets its own payload so one
  // cannot mask the other's omission.
  assert.match(run(edit({ edits: [{ old_path: "docs/spec/source-of-move.md", new_path: "docs/dest.md" }] })), /SPEC QUALITY/);
  assert.match(run(edit({ edits: [{ old_path: "docs/from.md", new_path: "docs/spec/via-subkey.md" }] })), /SPEC QUALITY/);
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
  // EVERY failure shape the suppressor recognizes, including MCP/JSON-RPC errors
  // that arrive as strings or {code,message} objects; the positive control guards
  // the opposite regression (a success-dict wrongly treated as failure would
  // silently suppress all reminders).
  const failed = [
    { is_error: true }, { isError: true },
    { error: true }, { error: "Error: [-32602] Invalid params" }, { error: { code: -32602, message: "bad params" } },
    { status: "error" }, { status: "ERROR" },
    { ok: false }, { success: false },
  ];
  for (const tr of failed) {
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

test("same-class dedup: two docs/spec paths in one batch emit the rule exactly once", () => {
  // Defect this guards: removing the `text not in reminders` dedup would duplicate
  // the nag text in every multi-file spec batch while match-based assertions still pass.
  const c = run(edit({ edits: [{ path: "docs/spec/a.md" }, { path: "docs/spec/b.md" }] }));
  assert.equal((c.match(/SPEC QUALITY/g) || []).length, 1);
});

test("output envelope: hookSpecificOutput carries hookEventName PostToolUse", () => {
  // Defect this guards: a renamed/wrong envelope field would make Claude Code drop
  // the context while property-access assertions stay green.
  const r = spawnSync("python3", [SCRIPT], {
    input: JSON.stringify(edit({ path: "docs/spec/env.md" })), encoding: "utf8",
  });
  assert.equal(r.status, 0);
  const parsed = JSON.parse(r.stdout.trim());
  assert.equal(parsed.hookSpecificOutput.hookEventName, "PostToolUse");
  assert.match(parsed.hookSpecificOutput.additionalContext, /SPEC QUALITY/);
});

test("negative: non-PostToolUse events are ignored", () => {
  assert.equal(run({ hook_event_name: "PreToolUse", tool_input: { path: "docs/spec/x.md" } }), "");
});

// ---- Cross-runtime compatibility (#47 follow-up): the shared script must serve
// Claude Code (MCP + native), Codex, and opencode without breaking any of them.

test("codex shape: apply_patch command body + tool_name apply_patch -> SPEC QUALITY", () => {
  // The single patch-command extractor test (Codex/opencode deliver edits as a patch
  // command with no path field); Add and Update alternatives are each asserted in
  // their own payload so neither can mask the other's omission — Delete and Move-to
  // keep their own tests below, and per-runtime duplicates belong to the e2e probe,
  // not here.
  for (const op of ["Add", "Update"]) {
    const c = run({
      hook_event_name: "PostToolUse",
      tool_name: "apply_patch",
      tool_input: { command: `*** Begin Patch\n*** ${op} File: docs/spec/codex.md\n+x` },
    });
    assert.match(c, /SPEC QUALITY/, op);
  }
});

test("apply_patch Delete File lines are inspected", () => {
  // Defect this guards: a spec REMOVAL is as decision-relevant as an edit; the
  // Delete alternative of the patch regex must keep matching.
  assert.match(run(edit({ command: "*** Begin Patch\n*** Delete File: docs/spec/gone.md" })), /SPEC QUALITY/);
});

test("apply_patch Move-to destinations are inspected (source AND destination)", () => {
  // Defect this guards: a Codex move whose destination lands under docs/spec/ —
  // Update carries the source, Move to: carries the destination; missing the
  // Move-to half let moves escape the reminder.
  const c = run(edit({ command: "*** Begin Patch\n*** Update File: docs/old.md\n-x\n*** Move to: docs/spec/moved.md" }));
  assert.match(c, /SPEC QUALITY/);
});

test("plans rule is direct-children only (documented docs/plans/*.md)", () => {
  // Defect this guards: the recursive regex matched docs/plans/archive/old.md,
  // over-firing PLAN READINESS beyond the documented contract; spec files stay
  // recursive by contrast.
  assert.equal(run(edit({ path: "docs/plans/archive/old.md" })), "");
  assert.match(run(edit({ path: "docs/plans/active.md" })), /PLAN READINESS/);
  assert.match(run(edit({ path: "docs/spec/sub/deep.md" })), /SPEC QUALITY/);
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

// --- hook-script spec-debt rule (#12) ---

function hookTree({ spec, index }) {
  const dir = mkdtempSync(path.join(tmpdir(), "sqr-hook-"));
  mkdirSync(path.join(dir, ".agents", "hooks"), { recursive: true });
  mkdirSync(path.join(dir, "docs", "spec"), { recursive: true });
  writeFileSync(path.join(dir, ".agents", "hooks", "new-reminder.py"), "#!/usr/bin/env python3\n");
  if (spec) writeFileSync(path.join(dir, "docs", "spec", "new-reminder.md"), "---\ntitle: t\n---\n");
  if (index) writeFileSync(path.join(dir, "docs", "spec", "README.md"), index);
  return { dir, script: path.join(dir, ".agents", "hooks", "new-reminder.py") };
}

const editAt = (file_path, extra = {}) => ({
  hook_event_name: "PostToolUse",
  tool_name: "Edit",
  tool_input: { file_path },
  ...extra,
});

test("hook script with no spec and no index mention nudges HOOK SPEC", () => {
  // Defect this guards: a new hook ships unspecced and nothing at creation time
  // flags it — the gap that left doc-freshness-reminder specless until closeout.
  const t = hookTree({ spec: false, index: "# Spec Index\n| Spec |\n" });
  try {
    assert.match(run(editAt(t.script)), /HOOK SPEC/);
  } finally {
    rmSync(t.dir, { recursive: true, force: true });
  }
});

test("hook script with its own spec stays silent", () => {
  const t = hookTree({ spec: true, index: "# Spec Index\n" });
  try {
    assert.equal(run(editAt(t.script)), "");
  } finally {
    rmSync(t.dir, { recursive: true, force: true });
  }
});

test("hook covered by an index mention stays silent (chrome-gate pattern)", () => {
  // A hook whose spec lives inside another spec is named in the index — that
  // mention is the coverage signal, not a same-named spec file.
  const t = hookTree({ spec: false, index: "# Spec Index\n… `chrome-gate` under the chrome spec …\n" });
  try {
    const script = path.join(t.dir, ".agents", "hooks", "chrome-gate.py");
    writeFileSync(script, "#!/usr/bin/env python3\n");
    assert.equal(run(editAt(script)), "");
  } finally {
    rmSync(t.dir, { recursive: true, force: true });
  }
});

test("unresolvable coverage (relative path, no cwd) nudges — remind, don't guess", () => {
  // RPCE multi-root deliveries carry workspace-relative paths the hook cannot
  // map to a filesystem tree; unverifiable coverage nudges rather than staying
  // silent on a guess.
  assert.match(
    run(editAt("someworkspace/.agents/hooks/new-reminder.py")),
    /HOOK SPEC/
  );
});

test("cwd candidate resolves a relative workspace root", () => {
  const t = hookTree({ spec: true, index: "# Spec Index\n" });
  const wsRoot = path.join(t.dir, "repoprompt-workflows");
  mkdirSync(path.join(wsRoot, ".agents", "hooks"), { recursive: true });
  mkdirSync(path.join(wsRoot, "docs", "spec"), { recursive: true });
  writeFileSync(path.join(wsRoot, ".agents", "hooks", "new-reminder.py"), "#!/usr/bin/env python3\n");
  writeFileSync(path.join(wsRoot, "docs", "spec", "new-reminder.md"), "---\ntitle: t\n---\n");
  try {
    assert.equal(
      run(editAt("repoprompt-workflows/.agents/hooks/new-reminder.py", { cwd: t.dir })),
      ""
    );
  } finally {
    rmSync(t.dir, { recursive: true, force: true });
  }
});

test("non-hook python scripts are out of scope for the spec-debt rule", () => {
  assert.equal(run(editAt("scripts/install-helper.py")), "");
});

test("uncovered hook aggregates with other rule classes in one reminder", () => {
  const t = hookTree({ spec: false, index: "# Spec Index\n" });
  try {
    const c = run({
      hook_event_name: "PostToolUse",
      tool_name: "Edit",
      tool_input: { edits: [{ path: t.script }, { path: "docs/spec/x.md" }] },
    });
    assert.match(c, /HOOK SPEC/);
    assert.match(c, /SPEC QUALITY/);
  } finally {
    rmSync(t.dir, { recursive: true, force: true });
  }
});
