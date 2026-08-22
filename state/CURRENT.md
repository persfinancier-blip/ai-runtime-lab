# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-081 — preserve verification of historical shared-anchor receipts across authenticated provider-generation rotation while keeping new-effect authority restricted to the current provider generation.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-080.
- Active: Issue #153 / LAB-081 — IN_PROGRESS.
- Active branch: `lab/081-provider-generation-history`.
- Active draft PR: #154 `[LAB-081] Historical provider generation continuity`.
- Current published PR HEAD: `d4e23da423273b4e0bbd6e38bd094d7a6ee49816`.

## Last completed step

The real LAB-080 integration is published: provider generation history and the shared-anchor ledger use the same SQLite database; reservation and provider rotation serialize through the same write boundary; historical signed observations are retained for old CONFIRMED entries; direct standalone integrated provider-history rotation is blocked; and mixed-generation/restart/race tests are present.

A fresh audit in the current run found another durable-integrity defect: `IntegratedProviderHistory._load_receipt_locked()` recomputed the authenticated receipt's stable binding but ignored the separately persisted `historical_provider_receipts.stable_binding` column. Corrupting only that durable column therefore survived restart verification. The branch now reads the persisted binding and requires exact equality with the recomputed authenticated binding. A dedicated `test_audit_regressions.py` corrupts only that column and requires restart failure.

Direct `git clone` was re-probed in this run and failed before checkout because `github.com` DNS resolution remains unavailable. GitHub connector is the durable read/write route.

## Evidence produced

- Draft PR #154 remains open, mergeable, and draft.
- Current branch HEAD `d4e23da423273b4e0bbd6e38bd094d7a6ee49816`.
- Durable-binding fix commit `5ef0f1ad0119bd6045e78c690e3de34dfa542500`.
- Audit regression commit `d4e23da423273b4e0bbd6e38bd094d7a6ee49816`.
- Original isolated corrected suite: 12/12 passed; compileall passed before later integration changes.
- Current integrated/audit-fix HEAD is deliberately **not** claimed exact-source tested yet.
- Fresh remote code audit identified and fixed the persisted stable-binding omission.
- Primary donor remains TUF root-update continuity: explicit persisted trust-generation continuity rather than caller-supplied historical keys.

## Known blockers / constraints

- No owner/product blocker.
- PR #154 must remain draft until exact-source regression execution of the current HEAD passes.
- Direct shell checkout is unavailable in the observed runtime because GitHub DNS resolution fails; connector reconstruction is the supported fallback.
- Historical generations are verification-only and must never regain new-effect authority.
- The reference uses HMAC historical material because LAB-036 is HMAC-based; verification-only is an audited execution-policy property, not cryptographic key-custody separation. Production should retain public-only verification material / protected signing custody.
- Provider-generation lifecycle is not provider consensus, cross-provider failover, HSM custody, or general PKI.

## Exact next action

Resume Issue #153 / PR #154. Reconstruct exact current PR-head executable bytes plus exact merged LAB-080 and LAB-036 dependencies through the GitHub connector and verify their Git blob identities. Execute LAB-081 protocol + integration + audit-regression suites, LAB-080 protocol/supported regressions, LAB-036 regressions, the unsafe baseline, and compileall. If failures occur, fix and republish rather than weakening the gate. Then perform a fresh complete remote patch audit of every PR file. If the exact-source gate and audit are clean and HEAD has not moved, mark PR #154 ready, squash-merge, close Issue #153 DONE, and choose the next highest-value correctness bottleneck.

## Backlog

- #153 / LAB-081 — historical anchor-provider generation continuity and receipt verification — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
