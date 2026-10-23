# Conformance — Ported-matrix provenance labeling

**Spec:** `docs/spec/port-matrix-provenance.md` (blob `8ae4a627`) · **Audited:** 2026-10-22 · **Audited at:** commit `4c85903` (branch `backlog/8-port-matrix-provenance`; contract tuple `rpw8:0f97cd2`) · **Scope:** moonray/repoprompt-workflows#8 provenance slice only

## Matrix

| Section | Item | Status | Evidence | Note |
|---|---|---|---|---|
| Proposed Surface | `docs/spec/chat-mining.md` + `docs/spec/chat-mining.conformance.md` — every keryx-origin `#NN` labeled | Conformed | `docs/spec/chat-mining.md:3` (`keryxsolutions#46`, `keryxsolutions#42`), `:7` (`keryxsolutions#46`); `docs/spec/chat-mining.conformance.md:3` ×2, `:9`, `:16`, `:17` ×3 (`keryxsolutions#42/keryxsolutions#44/keryxsolutions#45` — each member prefixed), `:26` ×2. Token enumeration `grep -noE '[a-zA-Z0-9]+#[0-9]+'` → 12/12 tokens `keryxsolutions#NN` | commit `4c85903` |
| Proposed Surface | `docs/spec/live-dryrun.conformance.md` — authoring commit labeled | Conformed | `docs/spec/live-dryrun.conformance.md:58` `` (`keryxsolutions@2506c45`) `` | label-only hunk; rest of sentence verbatim |
| Proposed Surface | `docs/spec/rpce-tool-gotchas.conformance.md` — cite corrected to real line | Conformed | `docs/spec/rpce-tool-gotchas.conformance.md:22` cites `SKILL.md:8`; `.agents/skills/rpce-tool-gotchas/SKILL.md:8` verifiably carries the provenance sentence (line 9 empty); no stale `SKILL.md:9` remains in the file | |
| Scenarios | S-001 chat-mining references unambiguous | Conformed | Pinned oracle (a) over both files → empty (exit 1); supplementary `(^|[^a-zA-Z0-9])#[0-9]+` → empty (covers `/`-shielded members); token enum 12/12 prefixed — no bare keryx-origin `#NN` in either file | DR-1-A form: full prefix per series member |
| Scenarios | S-002 live-dryrun commit cite labeled | Conformed | Oracle (b): L58 labeled form captured | sentence meaning unchanged |
| Scenarios | S-003 gotchas cite points at the real line | Conformed | Oracle (c): `sed -n '8p'` output contains "provenance"; row cites `:8` | |
| Constraints | Oracle (a) passes | Conformed | `grep -nE '(^|[^/a-zA-Z0-9])#[0-9]+' docs/spec/chat-mining.md docs/spec/chat-mining.conformance.md` → empty, exit 1 (loop run + independent delegated re-run) | zero hits ⇒ "every hit is `keryxsolutions#NN`" holds; token enum supplies the positive proof of the labeled form |
| Constraints | Oracle (b) passes | Conformed | labeled output captured at L58 | |
| Constraints | Oracle (c) passes | Conformed | both halves captured | |
| Non-goals | numbers preserved (not genericized); no verdict re-audit; other #8 slices untouched | Conformed | `4c85903` diff = 9 insertions / 9 deletions, label-only hunks across the 4 surface files (delegated review: label-only drift confirmed; no scenario/surface/constraint/verdict/table text altered) | |

## Coverage proof

- **audited:** Overview (purpose + doc-only scope), Proposed Surface (3/3 elements), Scenarios (S-001, S-002, S-003), Constraints ((a), (b), (c)), Non-goals (3 clauses), Open Questions (none open).
- **unreconciled:** `[]` — no Diverged, no Not-built.

Verification basis: pinned oracles green at `4c85903` (outputs captured in `docs/progress/backlog-8-loop.md`, epoch L8-E2); delegated independent review (read-only explore session `820455E7`, 2026-10-22) verdict `clean`, `findings: []`.
