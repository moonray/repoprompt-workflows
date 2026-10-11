import { execFileSync } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { test } from "node:test";
import assert from "node:assert/strict";

const HOOK = path.join(import.meta.dirname, "model-roster-reminder.py");

const SKILL_MD = `# Model Routing

## Recommended RepoPrompt Architecture

Canonical as of 2026-10-10.

| Role | Consultations | Model | Effort | Why |
|---|---|---|---|---|
| Context & Discovery | drafting | GPT-6.1 Sol | high | cache economics |
| Review & Refine | verdicts | Claude Opus 5.5 | medium | cross-family |
| Escalation | stuck | GPT-6 Astra, or Claude Fable 5.1 | low–medium, or high | capability |

## Applying the routing

(no table here — parser must not stray into other sections)
`;

function fixtures({ codexSlugs, ccIds }) {
  const dir = mkdtempSync(path.join(tmpdir(), "roster-hook-"));
  const skill = path.join(dir, "SKILL.md");
  writeFileSync(skill, SKILL_MD);
  const codex = path.join(dir, "codex-cache.json");
  writeFileSync(codex, JSON.stringify({ models: codexSlugs.map((slug) => ({ slug })) }));
  const cc = path.join(dir, "cc-catalog.json");
  writeFileSync(cc, JSON.stringify({ catalog: { config: { models: ccIds.map((id) => ({ id })) } } }));
  return { dir, skill, codex, cc };
}

function runHook(payload, env) {
  const out = execFileSync("python3", [HOOK], {
    input: JSON.stringify(payload),
    encoding: "utf8",
    env: { ...process.env, ...env },
  });
  return out.trim() ? JSON.parse(out) : null;
}

const PAYLOAD = (tool_name = "mcp__RepoPromptCE__app_settings") => ({
  hook_event_name: "PostToolUse",
  tool_name,
  tool_input: {},
  cwd: "/tmp",
});

test("non-matching tool is silent", () => {
  const f = fixtures({
    codexSlugs: ["gpt-6.1-sol", "gpt-6-astra"],
    ccIds: ["claude-opus-5-5", "claude-fable-5-1"],
  });
  assert.equal(runHook(PAYLOAD("mcp__RepoPromptCE__file_actions"), env(f)), null);
});

test("current picks are silent (the zero-token common case)", () => {
  const f = fixtures({
    codexSlugs: ["gpt-6.1-sol", "gpt-6-astra", "gpt-5.6-terra"],
    ccIds: ["claude-opus-5-5", "claude-fable-5-1", "claude-code"],
  });
  assert.equal(runHook(PAYLOAD(), env(f)), null);
});

test("newer generation flags with a suggestion", () => {
  const f = fixtures({
    codexSlugs: ["gpt-6.1-sol", "gpt-6-astra", "gpt-6.6-sol"],
    ccIds: ["claude-opus-5-5", "claude-fable-5-1"],
  });
  const r = runHook(PAYLOAD(), env(f));
  const ctx = r?.hookSpecificOutput?.additionalContext ?? "";
  assert.match(ctx, /MODEL ROUTING DRIFT/);
  assert.match(ctx, /gpt-6\.6-sol/);
  assert.match(ctx, /model-routing/);
});

test("missing pick flags roster drift", () => {
  const f = fixtures({
    codexSlugs: ["gpt-6.1-sol", "gpt-6-astra"],
    ccIds: ["claude-fable-5-1"], // claude-opus-5-5 gone
  });
  const r = runHook(PAYLOAD("mcp__RepoPromptCE__ask_oracle"), env(f));
  const ctx = r?.hookSpecificOutput?.additionalContext ?? "";
  assert.match(ctx, /claude-opus-5-5.*not found/);
});

test("fails open when the skill is absent", () => {
  const f = fixtures({
    codexSlugs: ["gpt-6.1-sol"],
    ccIds: ["claude-opus-5-5"],
  });
  assert.equal(runHook(PAYLOAD(), { ...env(f), MODEL_ROUTING_SKILL: "/nonexistent/SKILL.md" }), null);
});

function env(f) {
  return {
    MODEL_ROUTING_SKILL: f.skill,
    MODEL_ROSTER_CODEX_CACHE: f.codex,
    MODEL_ROSTER_CC_CACHE: f.cc,
  };
}
