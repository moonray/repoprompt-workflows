---
title: Live Dry-Run Skill
issue: none
status: implemented
---

# Live Dry-Run Skill

## Problem

Mocked tests assert the response shape a client *assumed* the API returns — so they pass while the client is broken against the real API. Response-shape mismatches, auth/header issues, and pagination quirks are invisible until the real service is called. The `live-dryrun` skill is the contract for exercising a backend/API/provider client against the live service read-only, before the feature is declared done. It is distinct from `user-testing` (which drives a rendered UI) and from unit-tested pure logic.

## Goals

1. Fire on the right triggers — a dry-run/live-verification request about an API client, or the close of a feature wrapping an external HTTP service — and never accept "mocked tests pass" as verification. (S-001, S-002)
2. Exercise every live assumption the change introduces — response shape, auth, pagination, error paths — read-only by default. (S-005, S-006, S-008)
3. Diff real responses against the client's assumptions on **values, not just shape**, without normalizing both sides to make the check pass. (S-007, S-009)
4. Size transport timeouts from measured live latency, not defaults. (S-010)
5. Land the findings: fix the client extraction, update mocked tests to the **real** shapes, re-verify both sides. (S-011)
6. Report status honestly — mutating ops consented-and-restored, deferred ops as pending (never evidence), unconfirmable shapes as unverified — with credentials handled safely across workspaces. (S-003, S-012, S-013, S-014, S-015, S-016)

## Non-Goals

- Rendered-UI verification — the `user-testing` skill's contract.
- Pure-logic/stdlib code with no external service — unit tests suffice.
- Side-effectful provider operations folded into the read-only run — they are deferred with exact safe instructions, or consented to individually under the mutating-op rule; handing a command to the user does not verify it.
- Repo-specific procedure or script templates — each target repo owns its own; this skill stays repo-independent and points at them.
- Load/performance testing — only representative latency is measured, to size timeouts.

## Constraints

- **Read-only by default.** Mutating operations need explicit user consent, and the consent covers one known-reversible operation on one named target: capture before-state, exercise, restore, verify restoration, disclose residual effects.
- **Credentials.** Loaded from the repo `.env` **by absolute path** (a script in `/tmp` will not find it via working-directory discovery); never committed, never printed (presence/length/redacted previews only); any password captured in a transcript is rotated afterward.
- **The dry-run script is throwaway** — `/tmp` or gitignored, never committed.
- **Preflight before any batch run**: the cheapest authenticated read-only call is classified as `ready` / `service_unreachable` / `authentication_rejected` / `unexpected_contract` before proceeding; the preflight itself never enables auth methods or alters provider settings.
- **No destructive git operations with uncommitted fixes present** — commit or stash first.
- Scenario IDs `S-NNN` are stable and never renumbered.

## Scenarios

### Scenario S-001: The skill fires on dry-run triggers
- **Given** the user asks for "automated user testing", a "dry run", "live verification", or "does it actually work?" about a backend/API/provider client, or such a feature is about to be declared done
- **When** skills are considered
- **Then** this skill runs — and does not run for rendered-UI work (`user-testing`) or pure-logic code (unit tests)

### Scenario S-002: Done means live-verified
- **Given** an API-client feature whose mocked suite is green
- **When** the feature is declared done
- **Then** the claim rests on a successful read-only dry-run against the real service — "mocked tests pass" alone is never reported as verification

### Scenario S-003: Missing credentials are reconciled, then asked — never silently skipped
- **Given** the repo `.env` lacks an expected credential
- **When** the dry-run is prepared
- **Then** the skill first reconciles whether the key is actually required (code, contract, safe current probe — the repo's own scripts may seed it); if genuinely required and absent, it asks the user rather than skipping, and never reports "verified" without it

### Scenario S-004: The dry-run script is throwaway and loads `.env` by absolute path
- **Given** the dry-run script is written
- **When** it runs
- **Then** it lives in `/tmp` or a gitignored path (never committed), loads the repo `.env` by absolute path, sets observed non-secret config, disables the transport cache, and resets any settings singleton so creds take effect

### Scenario S-005: Coverage is minimal but sufficient
- **Given** the client operations the change introduced
- **When** the operation set is chosen
- **Then** every live assumption — auth plus every read op, each with a real response checked — is exercised; cheapness is subordinate to coverage, and operations that exercise no changed assumption are marked not-applicable with a reason

### Scenario S-006: Preflight classifies before a batch run
- **Given** a batch or long-running verification about to start
- **When** the cheapest authenticated read-only preflight call completes
- **Then** its result is classified before proceeding: `ready` → proceed; `service_unreachable` → stop (environment, not a client bug); `authentication_rejected` → inspect provider policy/admin state before touching client code, leaving the cause unresolved if policy cannot be inspected; `unexpected_contract` → contract investigation

### Scenario S-007: The real response is printed before any mapping
- **Given** an operation exercised live
- **When** its response arrives
- **Then** the raw shape — top-level type, keys, lengths, one sample item — is printed **before** the client's extraction runs, and every mismatch between real shape and client extraction is listed

### Scenario S-008: Pagination is probed with naturally available data
- **Given** a paginated operation with more than one page of real items
- **When** pagination is verified
- **Then** a small page size is requested and the documented page parameters are observed as honored, clamped, or ignored; staging or creating remote records to force pagination is a mutating op requiring consent

### Scenario S-009: Semantic values are checked, not just shape
- **Given** the live-vs-mock diff
- **When** representative caller-visible values are compared
- **Then** entity escaping, timestamp basis and timezone representation, locale-sensitive numbers/dates, enum spelling/casing, and nullable-vs-empty distinctions are checked against the client's promised canonical value — both sides are never normalized to make the check pass; decoding/normalization enters the client only where its public contract calls for it

### Scenario S-010: Timeouts are sized from measured tails
- **Given** real auth/slow-endpoint latency measured live
- **When** transport budgets are set
- **Then** explicit provider-specific timeout and retry budgets are sized to the measured tail (e.g. a 2–6 s auth tail breaks a 5 s default), not left at library defaults

### Scenario S-011: Fixes land on both sides and are re-verified
- **Given** the mismatch list
- **When** fixes are applied
- **Then** each client extraction/mapping is fixed, the mocked tests are updated to the **real** shapes (exact-outcome, vetted with `test-quality`), and both the dry-run and the full mocked suite are re-run green

### Scenario S-012: A consented mutating op is reversible, restored, and disclosed
- **Given** the user explicitly consents to verifying one mutating operation
- **When** it is exercised
- **Then** a known-reversible operation on one named target is used: before-state captured, op exercised, state restored, restoration verified, and any residual effect (audit trail, history entry, notification) disclosed — "zero net state" is claimed only when exact restoration is demonstrated

### Scenario S-013: Deferred operations are pending requirements, not evidence
- **Given** an operation deferred by explicit constraint (prohibited, side-effectful, too costly, or operator-only)
- **When** status is reported
- **Then** the exact safe command, prerequisites, expected output shape, and acceptance criteria are recorded (credentials redacted), and the feature is reported as partially live-verified — blocked/pending-operator-verification when the operation is required for acceptance — until its result is returned and evaluated

### Scenario S-014: An unconfirmable shape is marked unverified
- **Given** a shape that cannot be confirmed without a mutating operation the user did not consent to
- **When** the report is written
- **Then** that shape is marked unverified and stated as such — never guessed

### Scenario S-015: Cross-workspace invocation resolves the target repo by absolute path
- **Given** a dry-run on repo A requested from a session rooted in workspace B
- **When** the verification runs
- **Then** A's root, memory file, and procedure docs are read by absolute path (B's loaded memory does not carry A's pointer), and root-scoped tool limitations are worked around with absolute-path shell access — or the run happens from a session rooted in A

### Scenario S-016: Secrets stay secret
- **Given** credentials in play through the whole run
- **When** output is produced
- **Then** token values and passwords are never printed or committed (only presence/length/redacted previews), and any password captured in the session transcript is rotated

## Proposed Surface

### Inputs

| Input | Required | Source | Description |
|---|---|---|---|
| Target client + operation list | yes | request / code | the HTTP integration, REST wrapper, or API-client class, with its ops |
| Real credentials | yes | repo `.env` | loaded by absolute path; reconciled-then-asked when absent (S-003) |
| Consent (mutating ops only) | per-op | user | one known-reversible op on one named target (S-012) |
| Target-repo procedure | no | target repo | the repo's own dry-run docs/script template, read by absolute path (S-015) |

### Outputs

| Output | Description |
|---|---|
| Real-response prints | raw shape per op, before any mapping (S-007) |
| Mismatch list | every real-vs-assumed divergence, shape and semantic values |
| Fixed client | extraction/mapping corrected; timeouts sized from measured tails |
| Updated mocked tests | asserting the **real** shapes, exact-outcome, `test-quality`-vetted |
| Verification status | per-op: executed + verified / deferred (pending, with safe instructions) / not applicable (with reason) |

## Open Questions

None. The trigger boundary (vs `user-testing` and unit tests), the read-only default with per-op consent, the deferred-op status semantics, and the repo-independence of procedure docs are resolved as design decisions encoded above.
