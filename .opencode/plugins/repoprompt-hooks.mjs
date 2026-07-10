// opencode plugin bridging the .agents/hooks/*.py guarantees.
// Auto-loaded when this repo is opened in opencode (project plugin dir).
//
// Mapping (honest — opencode's plugin model differs from Claude/Codex):
//   spec-conformance-gate  -> tool.execute.after (write/edit): BLOCK via throw. [enforced]
//   spec-quality-reminder  -> tool.execute.after (write/edit): log only.       [best-effort]
//   test-quality-reminder  -> tool.execute.after (bash)        : log only.       [best-effort]
//                             event(session.idle) ≈ Stop       : log only.       [reactive]
// opencode tool hooks have no model-visible "additionalContext" injection, so the two
// reminder hooks surface as structured warn logs; the nudges also ride global rules + the
// skills, which opencode reads. The hard guarantee (conformance gate) IS enforced.
//
// Repo-scoped: this plugin calls .agents/hooks/*.py relative to the project root, so it
// is active when working IN this repo (or any repo that ships .agents/hooks/).
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
