// reprompt-hooks — opencode ≥2.x plugin bridging the .agents/hooks/*.py guarantees.
//
// V2 Promise plugin API (opencode 2.x): `export default Plugin.define({ id, setup })`.
// The 1.x named-export plugin (same guarantees) remains in git history; 2.x loaders
// reject it ("must export a default definition"). The host resolves the
// `@opencode/plugin` import to its own runtime instance — no node_modules needed.
//
// Mapping (parity with the Claude/Codex wiring; opencode has no model-visible
// additionalContext injection, so reminder hooks surface as structured warn logs):
//   spec-conformance-gate -> tool execute.after (write/edit): BLOCK via throw. [enforced]
//   chrome-gate           -> tool execute.before (chrome-devtools tools): BLOCK via throw. [enforced, pre-call]
//   spec-quality/spec-accuracy/doc-freshness/test-quality reminders
//                         -> tool execute.after (bash + write/edit): log only. [best-effort]
//   test-quality Stop gate -> session "experimental.idle": reactive warn only — opencode
//                             still has no blocking session-end channel (documented-
//                             unsupported, as in 1.x).
//
// Repo-scoped with global fallback: resolves .agents/hooks/*.py relative to the
// project root when present, else the global ~/.claude/hooks symlinks — active in
// this repo AND, via the ~/.config/opencode plugin entry install.sh maintains, in
// every repo opencode opens.
import { Plugin } from "@opencode/plugin"
import { execFileSync } from "node:child_process"
import { existsSync } from "node:fs"
import os from "node:os"
import path from "node:path"

const HOOKS_DIR = ".agents/hooks"

function resolveScript(script, root) {
  const local = path.join(root, HOOKS_DIR, script)
  if (existsSync(local)) return local
  return path.join(process.env.HOME ?? os.homedir(), ".claude", "hooks", script)
}

// Pull a file path out of tool input without guessing the exact key name.
function extractPath(input) {
  if (!input || typeof input !== "object") return ""
  for (const k of ["filePath", "file_path", "path", "notebook_path", "filename"]) {
    if (typeof input[k] === "string" && input[k]) return input[k]
  }
  for (const v of Object.values(input)) {
    if (typeof v === "string" && /[\\/].+\.[a-z0-9]{1,5}$/i.test(v)) return v
  }
  return ""
}

function runHook(script, payload, root) {
  try {
    const out = execFileSync("python3", [resolveScript(script, root)], {
      input: JSON.stringify(payload),
      encoding: "utf8",
      timeout: 20000,
    }).trim()
    return out ? JSON.parse(out) : null
  } catch (e) {
    // A crashed hook must never trap the agent.
    console.error(`[repoprompt-hooks] ${script} failed: ${e.message}`)
    return null
  }
}

function nudge(ctx) {
  if (ctx) console.warn(`[repoprompt-hooks] ${ctx}`)
}

const CHROME_TOOL_RE = /chrome[-_.]devtools/i

export default Plugin.define({
  id: "repoprompt-hooks",
  setup: async (ctx) => {
    // v2 ctx.directory/worktree are domain objects, not plain strings — coerce to a
    // usable path before falling back to the server cwd.
    const root = () => {
      const d = ctx.directory ?? ctx.worktree
      if (typeof d === "string" && d) return d
      if (d && typeof d === "object") {
        for (const k of ["path", "directory", "root", "worktree"]) {
          if (typeof d[k] === "string" && d[k]) return d[k]
        }
        const s = String(d)
        if (s.startsWith("/")) return s
      }
      return process.cwd()
    }

    await ctx.tool.hook("execute.before", async (event) => {
      const tool = String(event.tool ?? "")
      if (!CHROME_TOOL_RE.test(tool)) return
      let name = tool
      if (!/^mcp__chrome[-_]devtools__/.test(name)) name = `mcp__chrome-devtools__${name}`
      const gate = runHook("chrome-gate.py", {
        hook_event_name: "PreToolUse",
        tool_name: name,
        tool_input: event.input ?? {},
        cwd: root(),
      }, root())
      if (gate && gate.decision === "block") {
        // Throwing in execute.before blocks the call itself; the model sees the reason.
        throw new Error(gate.reason)
      }
    })

    await ctx.tool.hook("execute.after", async (event) => {
      const tool = String(event.tool ?? "")
      const input = event.input ?? {}
      const rootDir = root()
      if (event.status === "error") return // no change was made; reminders would train ignoring
      const isBash = tool === "bash" || tool === "shell"
      const isEdit = tool === "write" || tool === "edit" || /patch/i.test(tool)
      const toolName = isBash ? "Bash" : tool

      if (isBash) {
        const payload = {
          hook_event_name: "PostToolUse",
          tool_name: "Bash",
          tool_input: { command: input.command ?? "" },
          cwd: rootDir,
        }
        nudge(runHook("test-quality-reminder.py", payload, rootDir)?.hookSpecificOutput?.additionalContext)
        nudge(runHook("doc-freshness-reminder.py", payload, rootDir)?.hookSpecificOutput?.additionalContext)
      } else if (isEdit) {
        const fp = extractPath(input)
        const payload = {
          hook_event_name: "PostToolUse",
          tool_name: toolName,
          tool_input: { ...(input ?? {}), ...(fp ? { file_path: fp } : {}) },
          cwd: rootDir,
        }
        nudge(runHook("spec-quality-reminder.py", payload, rootDir)?.hookSpecificOutput?.additionalContext)
        nudge(runHook("spec-accuracy-reminder.py", payload, rootDir)?.hookSpecificOutput?.additionalContext)
        nudge(runHook("doc-freshness-reminder.py", payload, rootDir)?.hookSpecificOutput?.additionalContext)
        const gate = runHook("spec-conformance-gate.py", payload, rootDir)
        if (gate && gate.decision === "block") {
          // Errors the edit result; the model sees the reason and must reconcile.
          throw new Error(gate.reason)
        }
      } else if (/RepoPromptCE/i.test(tool) && /(app_settings|agent_manage|ask_oracle)/.test(tool)) {
        const name = (tool.match(/(app_settings|agent_manage|ask_oracle)/) || [])[1] || "app_settings"
        nudge(runHook("model-roster-reminder.py", {
          hook_event_name: "PostToolUse",
          tool_name: `mcp__RepoPromptCE__${name}`,
          tool_input: input,
          cwd: rootDir,
        }, rootDir)?.hookSpecificOutput?.additionalContext)
      }
    })

    // ≈ Stop, but reactive: the session already went idle, so we can only warn.
    await ctx.session.hook("experimental.idle", async () => {
      const r = runHook("test-quality-reminder.py", {
        hook_event_name: "Stop",
        cwd: root(),
      }, root())
      if (r && r.decision === "block") {
        console.warn(`[repoprompt-hooks] ${r.reason}`)
      }
    })

    return () => {} // cleanup — nothing held
  },
})
