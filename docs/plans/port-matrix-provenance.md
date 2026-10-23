# Plan — Ported-matrix provenance labeling (#8, provenance slice)

Derived from `docs/spec/port-matrix-provenance.md` (blob recorded at commit time). Implementation branch: `backlog/8-port-matrix-provenance`. **Route note (Backlog 2026-10-22):** no worktree — this repo's dispatch runs serialized branch-in-checkout from the primary-root session per the wizard-authorized route change.

## Ordered tasks

- **T1 — chat-mining.md (3 refs).** L3 Tracking header: `#46 (cycle updates)` → `keryxsolutions#46 (cycle updates)`, `#42 (original landing)` → `keryxsolutions#42 (original landing)`; L7 overview: `(#46)` → `(keryxsolutions#46)`.
- **T2 — chat-mining.conformance.md (6 refs).** L3 `post-#46 implementation` → `post-keryxsolutions#46 implementation` and `the #46 commits` → `the keryxsolutions#46 commits`; L9 `2026-10-07 #42 validation probe` → `2026-10-07 keryxsolutions#42 validation probe`; L16 `#42's landing decisions` → `keryxsolutions#42's landing decisions`; L17 `#42/#44/#45 filings` → `keryxsolutions#42/keryxsolutions#44/keryxsolutions#45 filings` (full prefix per member — S-001 requires every reference in keryxsolutions#NN form); L26 `(created #42, updated #46)` → `(created keryxsolutions#42, updated keryxsolutions#46)`. Re-grep the whole file — any keryx-origin bare `#NN` beyond these also gets labeled (same rule).
- **T3 — the two single-line fixes.** `live-dryrun.conformance.md` L58: `` (`2506c45`) `` → `` (`keryxsolutions@2506c45`) ``. `rpce-tool-gotchas.conformance.md` L22 (Constraints/runtime-generic row): `SKILL.md:9` → `SKILL.md:8`; verify with `sed -n '8p'` that the provenance sentence lives there.
- **T4 — verify + closeout artifacts.** Run all three grep oracles from the spec's Constraints (capture output as evidence). Write `docs/spec/port-matrix-provenance.conformance.md` (S-001–S-003, grep-captured evidence) and confirm the spec README row (added at contract commit). Commit.

## Risks / rollback

- Over-labeling: only originating-workspace refs get the prefix — any reference to THIS repo's issues stays bare. Verify no `keryxsolutions` prefix lands on an rpw-origin ref.
- Rollback: revert the single implementation commit.

## Toolchain

- Verification is read-only: `grep`/`sed` oracles (spec Constraints). No test suite applies (doc-only slice); `git diff --stat` stays inside `docs/spec/` (+ index/conformance artifacts).
