#!/usr/bin/env node
// Sync the maintainability-review (thermo-nuclear) lens from upstream into:
//   .agents/skills/maintainability-review/SKILL.md            (canonical, between markers)
//   .agents/workflows/Deep-Review.md                           (inline lens block, between markers)
//
// Usage:
//   node scripts/sync-maintainability-review.mjs             # check: compare upstream digest to recorded
//   node scripts/sync-maintainability-review.mjs --update    # re-sync both files from upstream
//
// Exit codes: 0 up-to-date, 1 drift detected (check only), 2 error (e.g. fetch failed).
import { createHash } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const UPSTREAM_URL =
  "https://raw.githubusercontent.com/cursor/plugins/main/cursor-team-kit/skills/thermo-nuclear-code-quality-review/SKILL.md";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const SKILL = path.join(ROOT, ".agents/skills/maintainability-review/SKILL.md");
const WORKFLOW = path.join(ROOT, ".agents/workflows/Deep-Review.md");

// Marker pairs must match the strings embedded in the two files exactly.
const SKILL_BEGIN = "<!-- BEGIN upstream rubric (synced; do not edit between markers) -->";
const SKILL_END = "<!-- END upstream rubric -->";
const WF_BEGIN =
  "<!-- BEGIN maintainability-review lens (synced from .agents/skills/maintainability-review; do not edit between markers) -->";
const WF_END = "<!-- END maintainability-review lens -->";

const DIGEST_RE = /(?:^|\n)upstream_sha256:\s*([0-9a-f]{64})/; // read the recorded value
const DIGEST_LINE = /(^|\n)upstream_sha256:[^\n]*/g;            // rewrite the whole line (robust to malformed values)
const DATE_LINE = /(^|\n)retrieved:[^\n]*/g;                    // rewrite the whole line

const sha256 = (s) => createHash("sha256").update(s, "utf8").digest("hex");
const today = () => new Date().toISOString().slice(0, 10);

function stripFrontmatter(md) {
  if (md.startsWith("---")) {
    const end = md.indexOf("\n---", 3);
    if (end !== -1) return md.slice(end + 4).replace(/^\n+/, "");
  }
  return md;
}

async function fetchUpstream() {
  const res = await fetch(UPSTREAM_URL, { redirect: "follow" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.text();
}

function replaceBetween(text, begin, end, replacement) {
  const b = text.indexOf(begin);
  const e = text.indexOf(end);
  if (b === -1 || e === -1 || e < b) {
    throw new Error(`markers not found\n  begin: ${begin}\n  end:   ${end}`);
  }
  return text.slice(0, b + begin.length) + "\n" + replacement + "\n" + text.slice(e);
}

async function main() {
  const doUpdate = process.argv.includes("--update");

  let upstream;
  try {
    upstream = await fetchUpstream();
  } catch (e) {
    console.error(`error: could not fetch upstream (${e.message})\n  ${UPSTREAM_URL}`);
    process.exit(2);
  }
  const digest = sha256(upstream);
  const body = stripFrontmatter(upstream).trimEnd();

  const skillTxt = await readFile(SKILL, "utf8");
  const m = skillTxt.match(DIGEST_RE);
  const recorded = m ? m[1] : null;

  if (!doUpdate) {
    if (recorded === digest) {
      console.log(`up to date (sha256 ${digest.slice(0, 12)}…)`);
      process.exit(0);
    }
    console.log("DRIFT detected.");
    console.log(`  recorded: ${recorded || "(none)"}`);
    console.log(`  upstream: ${digest}`);
    console.log(`  url:      ${UPSTREAM_URL}`);
    console.log("Re-sync with: node scripts/sync-maintainability-review.mjs --update");
    process.exit(1);
  }

  // --update: rewrite both marker regions, refresh provenance.
  const date = today();
  let nextSkill = replaceBetween(skillTxt, SKILL_BEGIN, SKILL_END, body);
  // Unconditionally rewrite the provenance lines so a malformed value is repaired.
  nextSkill = nextSkill.replace(DIGEST_LINE, `$1upstream_sha256: ${digest}`);
  nextSkill = nextSkill.replace(DATE_LINE, `$1retrieved: ${date}`);
  await writeFile(SKILL, nextSkill, "utf8");

  const wfTxt = await readFile(WORKFLOW, "utf8");
  await writeFile(WORKFLOW, replaceBetween(wfTxt, WF_BEGIN, WF_END, body), "utf8");

  console.log(`synced maintainability-review lens (sha256 ${digest.slice(0, 12)}…, retrieved ${date})`);
  console.log(`  ${path.relative(ROOT, SKILL)}`);
  console.log(`  ${path.relative(ROOT, WORKFLOW)}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(2);
});
