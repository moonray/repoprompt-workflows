---
name: live-dryrun
description: Use when the user asks for "automated user testing", a "dry run", or "live verification" of a backend/API/provider client (a new HTTP integration, REST wrapper, or API-client class), or before declaring such a feature done. Exercises the real client against the live service READ-ONLY to catch response-shape defects that mocked tests cannot (mocks assert the ASSUMED shape, so they pass while the client is broken against the real API). Distinct from the user-testing skill (which drives a rendered UI). Loads creds from the repo .env by ABSOLUTE path, prints real response shapes, diffs against assumptions, fixes the client + updates mocked tests to the REAL shapes, re-verifies. Never skip just because mocked tests pass.
---

# Live dry-run — backend / API client verification

## Why
Mocked tests assert the shape you *assumed* the API returns. They pass while the client is **broken against the real API**. A read-only dry-run against the live service is the only thing that catches response-shape mismatches, auth/header issues, and pagination quirks. "Done" for a provider/client = it works against the real API, not just mocks.

## When to run
- The user says "automated user testing" / "dry run" / "live verification" / "does it actually work?" about a backend/API/provider client.
- Before closing a feature that wraps an external HTTP/API service (new client, provider, integration).
- **Not** for: pure-logic/stdlib code (unit tests suffice) or rendered UI (use the `user-testing` skill).

## Preconditions
- Real credentials in the repo `.env` (gitignored). If absent, **ask the user** — never skip silently, and never claim "verified" without them. If a key *seems* missing, first determine from code, contract, and — where safe — a current probe whether it is actually required: the repo's own scripts may already seed it (e.g. `os.environ.setdefault` recon constants), and the service may tolerate its absence. Prior successful runs are investigative leads, not proof; reconcile before asking the user.
- **Read-only by default.** Mutating ops (downloads, writes, deletes) need explicit user consent — real side effects. When the user consents to verifying one mutating op, choose a known-reversible operation on one named target: capture the before-state, exercise, restore, verify restoration, and disclose any residual effect (audit trail, history entry, notification). Claim "zero net state" only when exact restoration is demonstrated — never as a blanket promise.
- Rotate any password that was captured in a session transcript (security / leaked-creds hygiene).

## Live verification coverage and partial status

The in-session operation set is **minimal but sufficient**: it must exercise every live assumption the change introduces — response shape, auth, pagination, error paths. Cheap is subordinate to coverage. Classify each operation:

1. **Executed + verified** — read-only, allowed by repo policy, run in-session with actual output checked against assumptions.
2. **Deferred by explicit constraint** — prohibited by a repo long-run rule, side-effectful/unsafe, too costly, or operator-only. Record the exact safe command, prerequisites, expected output shape, and acceptance criteria (redact credentials; never hand over commands that side-effect by default). This is a **pending verification requirement, not evidence**: until its result is returned and evaluated, report the feature as partially live-verified only — and blocked/pending-operator-verification if the operation is required for acceptance.
3. **Not applicable** — explain why the operation exercises no changed assumption.

Side-effectful provider operations are never folded into this read-only dry-run merely by handing their commands to the user.

## Preflight (before any batch or long-running run)

Make the cheapest authenticated read-only call that exercises the same base URL, transport, credentials, and auth mechanism as the intended run, and classify the result before starting:

- `ready` → proceed;
- `service_unreachable` (DNS/TLS/transport) → stop: environment/provider availability, not a client bug;
- `authentication_rejected` → inspect the provider's policy/admin state (a security plugin or admin setting can disable the auth path) before changing client code; if policy cannot be inspected, leave the cause unresolved — do not label it a client bug;
- `unexpected_contract` → proceed to contract investigation.

The preflight stays read-only: it never enables auth methods or alters provider settings.

## Semantic value checks (diff values, not just shape)

The live-vs-mock diff covers representative caller-visible values: entity escaping/encoding (`&amp;` vs `&`), timestamp basis and timezone representation, locale-sensitive numbers/dates, enum spelling and casing, nullable/empty distinctions. Preserve the raw provider value while determining the canonical value the client promises; do not normalize both sides to make the check pass — decoding/normalization belongs in the client only when its public contract calls for it.

## Timing, not just shape

Measure representative latency of the real auth/slow endpoints before trusting defaults, and set explicit provider-specific timeout and retry budgets sized to the measured tail — an auth endpoint with a 2–6s tail will intermittently break a 5s default timeout.

## Procedure
1. List the client ops; pick the read-only ones to exercise (auth + every GET/read op).
2. Write a throwaway dry-run script (in `/tmp` or gitignored — NOT committed). **Load `.env` by ABSOLUTE path** — `find_dotenv()` searches from the calling *script* directory, not the cwd, so a script in `/tmp` will NOT find the repo `.env` and creds silently come up empty. Use `load_dotenv("/abs/repo/.env")`.
3. Set any non-secret config observed during recon (e.g. a fixed `app_id`), and **disable the transport cache** so calls hit the live service fresh.
4. Reset the settings singleton after loading env (so it picks up the creds).
5. Exercise: `login`/auth → confirm a token is stored. Then each read op. For any paginated op, probe pagination with naturally available data: if more than one page of real items exists, request a small page size and observe whether documented page params are honored, clamped, or ignored (one live run found `page` silently ignored — the full snapshot returned). Creating or staging remote records to test pagination is a mutating op: it needs consent under the preconditions rule. Print the REAL response — top-level type, keys, lengths, one sample item — **before** any mapping.
6. Diff: for each op, does the real shape match the client extraction? (Wrong key? pagination ignored? metadata field absent? list under a different name?) List every mismatch.
7. Fix the client extraction/mapping for each mismatch.
8. Update/add mocked tests to the **REAL** shapes (the old mocks asserted the wrong shapes — that is why they passed). Keep them exact-outcome; run `test-quality` on them.
9. Re-run the dry-run → confirm every op returns sensible real data. Re-run the full mocked suite → green.

## Hard rules
- Never claim "live-verified" / "works" without a successful dry-run against the real service. "Mocked tests pass" is **not** verification.
- Never `git reset --hard` / `git stash drop` with uncommitted fixes present — commit or stash FIRST, then sync main. (Reset --hard destroys uncommitted work — a real mistake made once.)
- Never commit credentials or print secrets (token values, passwords). Print only presence / lengths / redacted previews.
- If a shape can't be confirmed without a mutating op, mark it unverified and say so; don't guess.

## Reference
Repo-specific procedure and reusable dry-run script template: check the TARGET repo's own docs/config first — a repo with an established dry-run script pattern points at it from its AGENTS.md/CLAUDE.md or a docs path of its choosing (e.g. `docs/research/live-dryrun-procedure.md`). This skill stays repo-independent: no repo's paths, class names, or clients belong here; per-repo specifics live in the repo that owns them.

**Cross-workspace invocation** (running on repo A from a session rooted in workspace B): resolve the TARGET repo's root from the request, then read its memory file and procedure docs BY ABSOLUTE PATH — the session's loaded AGENTS.md/CLAUDE.md is workspace B's and will not carry A's pointer. Expect root-scoped tooling (MCP file tools) to refuse paths outside the loaded roots: use shell reads for discovery, and prefer editing through absolute-path shell/Python when the target is not a loaded root — or simply run the verification from a session rooted in the target repo, which restores full tooling.
