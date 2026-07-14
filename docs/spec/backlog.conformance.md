# Spec Conformance — Backlog Workflow

- **Spec:** `docs/spec/backlog.md` (Backlog Workflow)
- **Implementation:** `.agents/workflows/Backlog.md`
- **Audited:** 2026-07-14
- **Method:** one row per scenario and atomic Proposed Surface field/enum/constraint; evidence uses workflow line ranges.

## Matrix

| Item | Status | Evidence |
|---|---|---|
| S-001 Discovery is backend-agnostic via track-work | Conformed | `.agents/workflows/Backlog.md:31-43` |
| S-002 Triage order is bugs, then priority, then ease | Conformed | `.agents/workflows/Backlog.md:31-43` |
| S-003 Exempt items form a confirmed close batch | Conformed | `.agents/workflows/Backlog.md:31-43,62-72,154-170` |
| S-004 The wizard is the only solicited ask | Conformed | `.agents/workflows/Backlog.md:18-30,45-74,205-213` |
| S-005 Authorization is a ceiling, not responsibility | Conformed | `.agents/workflows/Backlog.md:18-30,62-74,185-193` |
| S-006 Capability gaps surface before dispatch | Conformed | `.agents/workflows/Backlog.md:45-59,104-120` |
| S-007 Contract generation requires clear committed outputs | Conformed | `.agents/workflows/Backlog.md:80-93` |
| S-008 Oracle-down degrades only preauthorized existing-contract work | Conformed | `.agents/workflows/Backlog.md:86-88,205-213` |
| S-009 One unique worktree and branch per issue | Conformed | `.agents/workflows/Backlog.md:18-30,94-120` |
| S-010 Predecessor reconciliation preserves work | Conformed | `.agents/workflows/Backlog.md:99-108,185-191` |
| S-011 Dispatch calls are isolated | Conformed | `.agents/workflows/Backlog.md:18-30,108-121` |
| S-012 Provisioning attempts and replacement epochs are distinct | Conformed | `.agents/workflows/Backlog.md:108-138` |
| S-013 Concurrent issues are sibling-aware | Conformed | `.agents/workflows/Backlog.md:135-137` |
| S-014 At most three issues are in flight | Conformed | `.agents/workflows/Backlog.md:76-79` |
| S-015 Contended issues serialize | Conformed | `.agents/workflows/Backlog.md:95-102` |
| S-016 Independent closeout verifies both ranges | Conformed | `.agents/workflows/Backlog.md:139-150` |
| S-017 Verification may overlap dispatch but precedes close | Conformed | `.agents/workflows/Backlog.md:139-150,172-183` |
| S-018 CI failure parks without asking | Conformed | `.agents/workflows/Backlog.md:154-170` |
| S-019 Merge conflicts regenerate only derived outputs | Conformed | `.agents/workflows/Backlog.md:154-170` |
| S-020 Decision items are never auto-resolved | Conformed | `.agents/workflows/Backlog.md:31-43,205-213` |
| S-021 Ledger captures authority and lineage | Conformed | `.agents/workflows/Backlog.md:172-183` |
| S-022 Resume restores authority without replay | Conformed | `.agents/workflows/Backlog.md:215-223` |
| S-023 Escalation cannot invent conformance acceptance | Conformed | `.agents/workflows/Backlog.md:205-213` |
| S-024 Rollup includes contract and recovery disposition | Conformed | `.agents/workflows/Backlog.md:225-241` |
| S-025 Browser testing is concurrency-safe | Conformed | `.agents/workflows/Backlog.md:45-59` |
| S-026 Resume syncs default before retroactive verify | Conformed | `.agents/workflows/Backlog.md:215-223` |
| S-027 Retroactive UI testing uses synced merged tree | Conformed | `.agents/workflows/Backlog.md:145-150` |
| S-028 Track-work status is authoritative | Conformed | `.agents/workflows/Backlog.md:31-43` |
| S-029 Backlog finishes only verified mechanical git flow | Conformed | `.agents/workflows/Backlog.md:139-170` |
| S-030 Close metadata follows landing ownership | Conformed | `.agents/workflows/Backlog.md:154-170` |
| S-031 Browser isolation is detected | Conformed | `.agents/workflows/Backlog.md:45-59` |
| S-032 Brief carries immutable authority and lineage | Conformed | `.agents/workflows/Backlog.md:114-121` |
| S-033 Documentation permission is not contract permission | Conformed | `.agents/workflows/Backlog.md:185-193,225-233` |
| S-034 Cleanup follows lifecycle and ownership | Conformed | `.agents/workflows/Backlog.md:172-193,234-241` |
| S-035 Independent issues fly by default | Conformed | `.agents/workflows/Backlog.md:18-30,76-102` |
| S-036 Concurrent branches land serially | Conformed | `.agents/workflows/Backlog.md:154-170` |
| S-037 Harness rejection text is not user intent | Conformed | `.agents/workflows/Backlog.md:18-30,108-138` |
| S-038 Cross-window risk is captured | Conformed | `.agents/workflows/Backlog.md:18-30,45-74` |
| S-039 Provisioning wedge requires restart recovery | Conformed | `.agents/workflows/Backlog.md:122-136,215-223` |
| S-040 Cleanup skip quarantines clean dead-session branch bindings | Conformed | `.agents/workflows/Backlog.md:99-138,172-191` |
| S-041 Diagnosis separates evidence from hypotheses | Conformed | `.agents/workflows/Backlog.md:122-136,282-315` |
| S-042 Backlog owns external contract preparation | Conformed | `.agents/workflows/Backlog.md:80-93` |
| S-043 Failure never authorizes Backlog implementation | Conformed | `.agents/workflows/Backlog.md:185-191` |
| S-044 Oracle ownership and accounting are durable | Conformed | `.agents/workflows/Backlog.md:57-59,90-93` |
| S-045 Authorization and responsibility are independent | Conformed | `.agents/workflows/Backlog.md:18-30,114-121,154-170` |
| S-046 Explicit amendments revise authority without another wizard | Conformed | `.agents/workflows/Backlog.md:62-74,191-193` |
| S-047 Issue branches start from refreshed default | Conformed | `.agents/workflows/Backlog.md:94-96,185-193` |
| S-048 Contract inputs have immutable provenance | Conformed | `.agents/workflows/Backlog.md:90-93,114-121` |
| S-049 Only post-initialization evidence is accepted | Conformed | `.agents/workflows/Backlog.md:139-150` |
| S-050 Dirty predecessor work is preserved and audited | Conformed | `.agents/workflows/Backlog.md:99-138,185-191` |
| S-051 Mechanical publication requires verified-complete work | Conformed | `.agents/workflows/Backlog.md:139-170,191-193` |
| S-052 Delegation capability is proven before dispatch | Conformed | `.agents/workflows/Backlog.md:45-59,108-120` |
| S-053 Conformance generation and acceptance are separate | Conformed | `.agents/workflows/Backlog.md:139-150` |
| S-054 Contract-only commits remain visible | Conformed | `.agents/workflows/Backlog.md:185-193,225-241` |
| S-055 Lifecycle controls resume/replacement/cleanup | Conformed | `.agents/workflows/Backlog.md:172-191` |

## Proposed Surface and Constraints

| Item | Status | Evidence | Note |
|---|---|---|---|
| Wizard.contract_maintenance enum deny|workflow-only; default workflow-only | Conformed | `.agents/workflows/Backlog.md:45-74` | — |
| Wizard.contract_publication_scope enum with-issue-only|branch+pr|branch+pr+merge; default with-issue-only | Conformed | `.agents/workflows/Backlog.md:45-74` | — |
| Wizard.conformance_acceptances item-specific; default none | Conformed | `.agents/workflows/Backlog.md:45-74` | — |
| Wizard.delegation capability summary | Conformed | `.agents/workflows/Backlog.md:45-59` | — |
| Wizard.degraded_ok explicit per issue; default false | Conformed | `.agents/workflows/Backlog.md:57-74` | — |
| Wizard.concurrent_orchestration none|yes|unknown; default unknown | Conformed | `.agents/workflows/Backlog.md:45-74` | — |
| Authorization revision/issuer/timestamps | Conformed | `.agents/workflows/Backlog.md:62-74,187-195` | — |
| Authorization git/contract/doc/issue scopes | Conformed | `.agents/workflows/Backlog.md:62-74,187-195` | — |
| Authorization conformance acceptances/stop/granted_at | Conformed | `.agents/workflows/Backlog.md:62-74,187-195` | — |
| Responsibility Backlog-owned actions | Conformed | `.agents/workflows/Backlog.md:18-30,116-123,154-195` | — |
| Responsibility Loop-owned independent readiness + implementation evidence | Conformed | `.agents/workflows/Backlog.md:116-123` | — |
| Contract identity reachable contract_commit + Spec/Plan blobs | Conformed | `.agents/workflows/Backlog.md:80-95,116-123` | — |
| Contract identity refreshed base + implementation_base_sha | Conformed | `.agents/workflows/Backlog.md:92-99,116-123` | — |
| Maintenance request workflow/operation/paths/branch/start/counterpart | Conformed | `.agents/workflows/Backlog.md:80-95` | — |
| Maintenance outcomes complete|partial|dirty + range/identity/dirty/reason | Conformed | `.agents/workflows/Backlog.md:80-95,174-195` | — |
| Delegation roles test|implementation|review|refactor | Conformed | `.agents/workflows/Backlog.md:45-59,110-122` | — |
| Delegation states available|unavailable|unproven + evidence/topology/time/reason | Conformed | `.agents/workflows/Backlog.md:45-59,110-122` | — |
| Oracle readiness budget 1 verdict/2 attempts | Conformed | `.agents/workflows/Backlog.md:57-59,92-95` | — |
| Oracle lineage ceilings standalone 3/6; orchestrated 2/4 | Conformed | `.agents/workflows/Backlog.md:57-59,174-195` | — |
| Oracle clarity/conflict separate; deterministic consumes none; counters persist | Conformed | `.agents/workflows/Backlog.md:57-59,92-95,174-195` | — |
| Lifecycle states paused|terminated|handed_off_outside_loop|replacement_required|blocked|completed | Conformed | `.agents/workflows/Backlog.md:174-195` | — |
| Ledger lineage/epoch/phase/authority/capability/identity/manifest/outcome/counters/handoff/validation/conformance/ranges | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Gate: tracking capability | Conformed | `.agents/workflows/Backlog.md:18-43` | — |
| Gate: single wizard | Conformed | `.agents/workflows/Backlog.md:45-74,207-215` | — |
| Gate: authority+responsibility | Conformed | `.agents/workflows/Backlog.md:18-30,62-74,187-195` | — |
| Gate: provenance/default-parent branch | Conformed | `.agents/workflows/Backlog.md:80-99` | — |
| Gate: dispatch+liveness/progress/delegation/oracle | Conformed | `.agents/workflows/Backlog.md:100-140` | — |
| Gate: independent verify/conformance/landing/conflict | Conformed | `.agents/workflows/Backlog.md:141-172` | — |
| Gate: lifecycle-safe cleanup | Conformed | `.agents/workflows/Backlog.md:174-195` | — |
| Artifact: run and Loop progress | Conformed | `.agents/workflows/Backlog.md:174-195,227-243` | — |
| Artifact: immutable inputs and maintenance report | Conformed | `.agents/workflows/Backlog.md:80-95` | — |
| Artifact: dirty handoff and delegated evidence | Conformed | `.agents/workflows/Backlog.md:100-151,174-195` | — |
| Artifact: conformance status/acceptance and rollup | Conformed | `.agents/workflows/Backlog.md:141-151,227-243` | — |
| Constraint: Discovery/status/close use track-work; unavailable capability blocks | Conformed | `.agents/workflows/Backlog.md:18-43` | — |
| Constraint: At most three in flight; lower ceiling for shared orchestration risk | Conformed | `.agents/workflows/Backlog.md:18-30,45-79` | — |
| Constraint: Unique issue branch/worktree rooted on refreshed default | Conformed | `.agents/workflows/Backlog.md:80-102` | — |
| Constraint: Backlog owns publication/landing/status/close/replacement/cleanup | Conformed | `.agents/workflows/Backlog.md:18-30,154-195` | — |
| Constraint: External Spec/Deep Plan preparation; no inline contract authoring | Conformed | `.agents/workflows/Backlog.md:80-95` | — |
| Constraint: Readiness uses committed blob tuple, not implementation HEAD | Conformed | `.agents/workflows/Backlog.md:92-95` | — |
| Constraint: Dirty predecessor retains original identity; no suffix fallback | Conformed | `.agents/workflows/Backlog.md:100-140,187-193` | — |
| Constraint: Authorization revisions ordered/prospective/rechecked | Conformed | `.agents/workflows/Backlog.md:62-74,187-195` | — |
| Authorization field: `revision` | Conformed | `.agents/workflows/Backlog.md:62-74,187-195` | — |
| Authorization field: `issuer` | Conformed | `.agents/workflows/Backlog.md:62-74,187-195` | — |
| Authorization field: `issued_at` | Conformed | `.agents/workflows/Backlog.md:62-74,187-195` | — |
| Authorization field: `effective_at` | Conformed | `.agents/workflows/Backlog.md:62-74,187-195` | — |
| Authorization field: `git_scope` | Conformed | `.agents/workflows/Backlog.md:62-74,187-195` | — |
| Authorization field: `contract_maintenance` | Conformed | `.agents/workflows/Backlog.md:62-74,187-195` | — |
| Authorization field: `contract_publication_scope` | Conformed | `.agents/workflows/Backlog.md:62-74,187-195` | — |
| Authorization field: `doc_edits` | Conformed | `.agents/workflows/Backlog.md:62-74,187-195` | — |
| Authorization field: `issue_scope` | Conformed | `.agents/workflows/Backlog.md:62-74,187-195` | — |
| Authorization field: `conformance_acceptances` | Conformed | `.agents/workflows/Backlog.md:62-74,187-195` | — |
| Authorization field: `stop` | Conformed | `.agents/workflows/Backlog.md:62-74,187-195` | — |
| Authorization field: `granted_at` | Conformed | `.agents/workflows/Backlog.md:62-74,187-195` | — |
| Contract identity field: `contract_commit` | Conformed | `.agents/workflows/Backlog.md:80-99,116-123` | — |
| Contract identity field: `spec_path` | Conformed | `.agents/workflows/Backlog.md:80-99,116-123` | — |
| Contract identity field: `spec_blob_sha` | Conformed | `.agents/workflows/Backlog.md:80-99,116-123` | — |
| Contract identity field: `plan_path` | Conformed | `.agents/workflows/Backlog.md:80-99,116-123` | — |
| Contract identity field: `plan_blob_sha` | Conformed | `.agents/workflows/Backlog.md:80-99,116-123` | — |
| Contract identity field: `tuple_key` | Conformed | `.agents/workflows/Backlog.md:80-99,116-123` | — |
| Contract identity field: `base_branch` | Conformed | `.agents/workflows/Backlog.md:80-99,116-123` | — |
| Contract identity field: `base_sha` | Conformed | `.agents/workflows/Backlog.md:80-99,116-123` | — |
| Contract identity field: `implementation_base_sha` | Conformed | `.agents/workflows/Backlog.md:80-99,116-123` | — |
| Maintenance request field: `workflow` | Conformed | `.agents/workflows/Backlog.md:80-95` | — |
| Maintenance request field: `operation` | Conformed | `.agents/workflows/Backlog.md:80-95` | — |
| Maintenance request field: `paths` | Conformed | `.agents/workflows/Backlog.md:80-95` | — |
| Maintenance request field: `branch` | Conformed | `.agents/workflows/Backlog.md:80-95` | — |
| Maintenance request field: `starting_commit` | Conformed | `.agents/workflows/Backlog.md:80-95` | — |
| Maintenance request field: `counterpart` | Conformed | `.agents/workflows/Backlog.md:80-95` | — |
| Maintenance report field: `outcome` | Conformed | `.agents/workflows/Backlog.md:80-95,174-195` | — |
| Maintenance report field: `commit_range` | Conformed | `.agents/workflows/Backlog.md:80-95,174-195` | — |
| Maintenance report field: `final_identity` | Conformed | `.agents/workflows/Backlog.md:80-95,174-195` | — |
| Maintenance report field: `dirty_paths` | Conformed | `.agents/workflows/Backlog.md:80-95,174-195` | — |
| Maintenance report field: `reason` | Conformed | `.agents/workflows/Backlog.md:80-95,174-195` | — |
| Lifecycle value: `paused` | Conformed | `.agents/workflows/Backlog.md:174-195` | — |
| Lifecycle value: `terminated` | Conformed | `.agents/workflows/Backlog.md:174-195` | — |
| Lifecycle value: `handed_off_outside_loop` | Conformed | `.agents/workflows/Backlog.md:174-195` | — |
| Lifecycle value: `replacement_required` | Conformed | `.agents/workflows/Backlog.md:174-195` | — |
| Lifecycle value: `blocked` | Conformed | `.agents/workflows/Backlog.md:174-195` | — |
| Lifecycle value: `completed` | Conformed | `.agents/workflows/Backlog.md:174-195` | — |
| Ledger field: `lineage` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Ledger field: `epoch` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Ledger field: `phase` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Ledger field: `authority` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Ledger field: `responsibility` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Ledger field: `capabilities` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Ledger field: `contract_identity` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Ledger field: `dirty_snapshot` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Ledger field: `manifest` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Ledger field: `maintenance_outcome` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Ledger field: `oracle_counters` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Ledger field: `handoff` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Ledger field: `validation` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Ledger field: `conformance` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Ledger field: `acceptance` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Ledger field: `contract_range` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |
| Ledger field: `implementation_range` | Conformed | `.agents/workflows/Backlog.md:174-195,217-243` | — |

## Coverage Proof

- **audited:** S-001…S-055, 88 atomic Proposed Surface/field/enum items, and all 8 constraints.
- **unreconciled:** none.
- **status:** `passed`.
