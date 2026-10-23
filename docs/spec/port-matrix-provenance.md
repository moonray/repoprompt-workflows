# Ported-matrix provenance labeling

**Status:** Active · **Created:** 2026-10-22 · **Tracking:** [#8](https://github.com/moonray/repoprompt-workflows/issues/8) (provenance slice) · **Implements:** `docs/spec` edits only

## Overview

Spec and conformance files ported from the originating keryxsolutions workspace carry bare issue numbers and one commit SHA that do not resolve in this repo — a bare `#42` here reads as a moonray/repoprompt-workflows issue, but it is a keryxsolutions one. Label originating-repo identifiers as originating-repo provenance so every reference stays unambiguous and traceable. Doc-only; no code, skill, or hook changes.

## Proposed Surface

- `docs/spec/chat-mining.md` + `docs/spec/chat-mining.conformance.md` — every bare `#NN` referring to an originating-workspace (keryxsolutions) issue is labeled `keryxsolutions#NN` (Tracking header, overview prose, evidence rows).
- `docs/spec/live-dryrun.conformance.md` — the authoring-commit reference `2506c45` (~L58) is labeled `keryxsolutions@2506c45`.
- `docs/spec/rpce-tool-gotchas.conformance.md` — the provenance cite `SKILL.md:9` (~L22) is corrected to `SKILL.md:8`, the line the provenance sentence verifiably occupies.

## Scenarios

- **S-001 chat-mining references are unambiguous.** Reading any issue-number reference in the two chat-mining files, a contributor can tell which repo's issue it names: every originating-workspace reference appears as `keryxsolutions#NN`; no bare keryxsolutions-origin `#NN` remains in either file.
- **S-002 live-dryrun commit cite is labeled provenance.** The governance row cites the authoring commit as `keryxsolutions@2506c45`; the sentence's meaning is unchanged.
- **S-003 gotchas cite points at the real line.** The runtime-generic/provenance-free row cites `SKILL.md:8`, and line 8 of `.agents/skills/rpce-tool-gotchas/SKILL.md` verifiably contains the provenance sentence.

## Constraints

- Grep oracles (all must pass at closeout): (a) `grep -nE '(^|[^/a-zA-Z0-9])#[0-9]+' docs/spec/chat-mining.md docs/spec/chat-mining.conformance.md` → every hit is `keryxsolutions#NN`; (b) `grep -n '2506c45' docs/spec/live-dryrun.conformance.md` → labeled form; (c) `sed -n '8p' .agents/skills/rpce-tool-gotchas/SKILL.md` contains "provenance" and the conformance row cites `:8`.

## Non-goals

- Not genericizing the numbers away (labeling preserves traceability).
- No re-audit of any matrix's verdicts — labeling only.
- The other #8 slices (test-fixture hardening, `manage()` consolidation) are out of scope for this slice.

## Open questions

None.
