// opencode plugin bridging the .agents/hooks/*.py guarantees.
// Auto-loaded when this repo is opened in opencode (project plugin dir).
//
// Mapping (honest — opencode's plugin model differs from Claude/Codex):
//   spec-conformance-gate  -> tool.execute.after (write/edit): BLOCK via throw.  [enforced]
//   chrome-gate            -> tool.execute.before (chrome-devtools MCP): BLOCK via throw. [enforced, pre-call]
//   spec-quality-reminder  -> tool.execute.after (write/edit): log only.       [best-effort]
//   test-quality-reminder  -> tool.execute.after (bash)        : log only.       [best-effort]
//                             event(session.idle) ≈ Stop       : log only.       [reactive]
// Model-visible injection: re-verified 2026-10-11 against live opencode docs (#9) —
// tool hooks still have none: `hookSpecificOutput.additionalContext` is a Claude-Code
// shape opencode lacks, after-hook output mutations are ignored (opencode issue, Feb 2026),
// and the one documented channel (`experimental.session.compacting` → output.context.push)
// fires at compaction time, not tool time. So the reminder hooks surface as structured
// warn logs; the nudges also ride global rules + the skills, which opencode reads.
// The hard guarantee (conformance gate) IS enforced. The chrome gate runs PRE-call via
// `tool.execute.before` (throwing blocks the call itself; opencode plugin docs, re-verified
// 2026-10-11) — wired in #9, harness-validated against the real chrome-gate.py.
//
// Repo-scoped: this plugin calls .agents/hooks/*.py relative to the project root, so it
// is active when working IN this repo (or any repo that ships .agents/hooks/).
// LOADING (verified live on opencode 1.18.35, 2026-10-11, #9): plugins are NOT auto-scanned
// from .opencode/plugins/ — the repo's opencode.json must declare this file in its "plugin"
// array (it does). Session identity arrives as input.sessionID on tool hooks.
import { execFileSync } from "node:child_process";
import path from "node:path";

const HOOKS_DIR = ".agents/hooks";

// Pull a file path out of opencode tool args without guessing the exact key name.
function extractPath(args) {
  if (!args || typeof args !== "object") return "";
  for (const k of ["filePath", "file_path", "path", "notebook_path", "filename"]) {
    if (typeof args[k] === "string" && args[k]) return args[k];
  }
  for (const v of Object.values(args)) {
    if (typeof v === "string" && /[\\/].+\.[a-z0-9]{1,5}$/i.test(v)) return v;
  }
  return "";
}

const CHROME_TOOL_RE = /chrome[-_.]devtools/i;

function extractSession(input, output) {
  const cand = input?.sessionID || input?.session_id || input?.session?.id
    || output?.sessionID || output?.session_id
    || (typeof input?.session === "string" ? input.session : "");
  return typeof cand === "string" ? cand : "";
}

function runHook(script, payload, root) {
  try {
    const out = execFileSync("python3", [path.join(root, HOOKS_DIR, script)], {
      input: JSON.stringify(payload),
      encoding: "utf8",
      timeout: 20000,
    }).trim();
    return out ? JSON.parse(out) : null;
  } catch (e) {
    // A crashed hook must never trap the agent.
    console.error(`[repoprompt-hooks] ${script} failed: ${e.message}`);
    return null;
  }
}

async function note(client, result) {
  const ctx = result?.hookSpecificOutput?.additionalContext;
  if (!ctx) return;
  await client?.app?.log?.({
    body: { service: "repoprompt-hooks", level: "warn", message: ctx },
  });
}

export const RepromptHooks = async ({ worktree, directory, client }) => {
  const root = () => worktree || directory || process.cwd();
  return {
    "tool.execute.before": async (input, output) => {
      const tool = String(input?.tool || "");
      if (!CHROME_TOOL_RE.test(tool)) return;
      // Normalize to the naming chrome-gate.py matches (Claude keeps the hyphen,
      // Codex underscores it; other opencode shapes get the prefix synthesized).
      let name = tool;
      if (!/^mcp__chrome[-_]devtools__/.test(name)) name = `mcp__chrome-devtools__${name}`;
      const gate = runHook("chrome-gate.py", {
        hook_event_name: "PreToolUse",
        tool_name: name,
        tool_input: input?.args || {},
        session_id: extractSession(input, output),
        cwd: root(),
      }, root());
      if (gate && gate.decision === "block") {
        // Throwing in tool.execute.before blocks the call itself: the model sees
        // the reason and must load the chrome skill before retrying (#9).
        throw new Error(gate.reason);
      }
    },

    "tool.execute.after": async (input, output) => {
      const tool = input?.tool;
      const args = output?.args || input?.args || {};
      const rootDir = root();

      if (tool === "bash") {
        const r = runHook("test-quality-reminder.py", {
          hook_event_name: "PostToolUse",
          tool_name: "Bash",
          tool_input: { command: args.command || "" },
          cwd: rootDir,
        }, rootDir);
        await note(client, r);
      } else if (tool === "write" || tool === "edit") {
        const fp = extractPath(args);
        const payload = {
          hook_event_name: "PostToolUse",
          tool_name: tool,
          tool_input: { ...(args || {}), ...(fp ? { file_path: fp } : {}) },
        };
        await note(client, runHook("spec-quality-reminder.py", payload, rootDir));
        const gate = runHook("spec-conformance-gate.py", payload, rootDir);
        if (gate && gate.decision === "block") {
          // Errors the edit result; the model sees the reason and must reconcile
          // (add a conformance matrix / drop the terminal status) before closing.
          throw new Error(gate.reason);
        }
      }
    },

    event: async ({ event }) => {
      if (event?.type === "session.idle") {
        // ≈ Stop, but reactive: the turn already ended, so we can only warn.
        const r = runHook("test-quality-reminder.py", {
          hook_event_name: "Stop",
          cwd: root(),
        }, root());
        if (r && r.decision === "block") {
          await client?.app?.log?.({
            body: { service: "repoprompt-hooks", level: "warn", message: r.reason },
          });
        }
      }
    },
  };
};
