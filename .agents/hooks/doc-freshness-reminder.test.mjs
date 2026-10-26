// Unit tests for the doc-freshness close reminder hook (#12).
// Layer: payload -> stdout contract of the python script, via real child processes
// (the matcher itself is settings.json config and is verified by the e2e probe, not here).
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";

const SCRIPT = new URL("./doc-freshness-reminder.py", import.meta.url).pathname;

function run(payload) {
  const r = spawnSync("python3", [SCRIPT], { input: JSON.stringify(payload), encoding: "utf8" });
  assert.equal(r.status, 0, `script exited ${r.status}: ${r.stderr}`);
  const out = r.stdout.trim();
  return out ? JSON.parse(out).hookSpecificOutput.additionalContext : "";
}

const bash = (command, tool_response) => ({
  hook_event_name: "PostToolUse",
  tool_name: "Bash",
  tool_input: { command },
  ...(tool_response !== undefined ? { tool_response } : {}),
});

const edit = (file_path) => ({
  hook_event_name: "PostToolUse",
  tool_name: "mcp__RepoPromptCE__apply_edits",
  tool_input: { path: file_path },
});

test("canonical $TW variable invocation (no tw.py literal) fires the nudge", () => {
  // Defect this guards: matching only the literal `tw.py` misses the skill's own
  // documented close invocation `python3 "$TW" close <ref>`, where the script path
  // lives in a shell variable.
  assert.match(run(bash('python3 "$TW" close ISSUE-001 --reason "landed"')), /DOC FRESHNESS/);
});

test("tw.py close with assignment in the same command fires", () => {
  assert.match(
    run(bash("TW=$PWD/.agents/skills/track-work/scripts/tw.py; python3 \"$TW\" close owner/repo#5")),
    /DOC FRESHNESS/
  );
});

test("bare `tw close` alias shape fires", () => {
  assert.match(run(bash("tw close ISSUE-002")), /DOC FRESHNESS/);
});

test("issue.sh close fires", () => {
  assert.match(
    run(bash("sh .agents/skills/track-work/scripts/issue.sh close ISSUE-003")),
    /DOC FRESHNESS/
  );
});

test("close.sh (obligation projection closer) fires", () => {
  assert.match(run(bash("bash ~/skills/track-work/scripts/close.sh ISSUE-007")), /DOC FRESHNESS/);
});

test("gh issue close fires", () => {
  assert.match(run(bash("gh issue close 12 -R owner/repo")), /DOC FRESHNESS/);
});

test("the word 'close' alone does not fire", () => {
  // Negative control: guards against a loose \bclose\b matcher nudging on prose,
  // commit messages ("close the loop"), or unrelated commands.
  assert.equal(run(bash('git commit -m "close the loop on the refactor"')), "");
  assert.equal(run(bash("ls -la && echo close")), "");
});

test("gh pr close is NOT an item close", () => {
  assert.equal(run(bash("gh pr close 7 -R owner/repo")), "");
});

test("failed close command is suppressed", () => {
  // Defect this guards: nudging after a close the runtime reported as errored
  // (item still open) trains the model to ignore the nudge.
  assert.equal(run(bash("tw close ISSUE-001", { is_error: true })), "");
});

function issueFile(name, frontmatter) {
  const dir = mkdtempSync(path.join(tmpdir(), "dfr-test-"));
  const issues = path.join(dir, ".agents", "issues");
  mkdirSync(issues, { recursive: true });
  const f = path.join(issues, name);
  writeFileSync(f, frontmatter);
  return { dir, f };
}

test("file-backend frontmatter flip to closed fires", () => {
  // Defect this guards: the close edit is a frontmatter status flip on the ledger
  // file — missing it leaves the file backend (no shell close command) unguarded.
  const { dir, f } = issueFile("ISSUE-004.md", "---\nid: ISSUE-004\nstatus: closed\n---\nbody\n");
  try {
    assert.match(run(edit(f)), /DOC FRESHNESS/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("file-backend issue still open stays silent", () => {
  const { dir, f } = issueFile("ISSUE-005.md", "---\nid: ISSUE-005\nstatus: in-progress\n---\nbody\n");
  try {
    assert.equal(run(edit(f)), "");
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("issues-dir README (index, no frontmatter) stays silent", () => {
  const dir = mkdtempSync(path.join(tmpdir(), "dfr-test-"));
  try {
    const inner = path.join(dir, ".agents", "issues");
    mkdirSync(inner, { recursive: true });
    const f = path.join(inner, "README.md");
    writeFileSync(f, "# index\n| id | status |\n");
    assert.equal(run(edit(f)), "");
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("non-issue doc edit stays silent", () => {
  assert.equal(run(edit("docs/spec/some-spec.md")), "");
});
