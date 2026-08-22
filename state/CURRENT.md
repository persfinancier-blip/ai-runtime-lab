# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-081 — preserve verification of historical shared-anchor receipts across authenticated provider-generation rotation while keeping new-effect authority restricted to the current provider generation.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-080.
- Active: Issue #153 / LAB-081 — IN_PROGRESS.
- Active branch: `lab/081-provider-generation-history`.
- Active draft PR: #154 `[LAB-081] Historical provider generation continuity`.
- Current published PR HEAD: `6043706553a69c8aa410e2c0b889e507fa717d60`.

## Last completed step

A fresh audit found the low-level `DurableProviderHistory` still had the durable receipt-binding bug already fixed in the integrated supported surface: standalone `load_receipt()` ignored the persisted `stable_binding`, and standalone `verify_durable()` did not walk historical receipts. The branch now has transaction-local receipt verification in `protocol.py`; restart verifies all stored historical receipt signatures and stored-vs-recomputed stable bindings, and direct receipt load performs the same exact binding check.

A new standalone corruption regression was added. Exact published `protocol.py` and `test_standalone_audit.py` were reconstructed locally and matched their Git blob IDs. The standalone audit regression executed successfully.

Direct shell checkout was re-probed and still fails before checkout because `github.com` DNS resolution is unavailable. GitHub connector reconstruction remains the supported route.

## Evidence produced

- PR #154 remains open, mergeable, and draft.
- Current HEAD `6043706553a69c8aa410e2c0b889e507fa717d60`.
- Standalone durability fix commit `cc1bb7071cb92d2ed5a80d3a1b1c7cd0461e7411`.
- Standalone regression commit / current HEAD `6043706553a69c8aa410e2c0b889e507fa717d60`.
- Published hardened protocol blob `c2077635aa2ecebf9a3072d97efeacb37cb0d478`; local `git hash-object` matched exactly.
- Published standalone regression blob `024cbb2e0926ea096b91e23d2027c25ef9eb66cd`; local `git hash-object` matched exactly.
- Exact `test_standalone_audit`: 1/1 passed.
- Hardened protocol compile check passed.
- Earlier integrated durable-binding regression remains present.
- Full current PR HEAD is deliberately not yet claimed exact-source regression-tested.

## Known blockers / constraints

- No owner/product blocker.
- PR #154 must remain draft until the full exact-source regression gate for the current HEAD passes.
- Direct shell checkout is unavailable in the observed runtime because GitHub DNS resolution fails; reconstruct exact bytes through the GitHub connector.
- Historical generations are verification-only and must never regain new-effect authority.
- The reference uses HMAC historical material because LAB-036 is HMAC-based; production should retain public-only verification material / protected signing custody.
- Provider-generation lifecycle is not provider consensus, cross-provider failover, HSM custody, or general PKI.

## Exact next action

Resume Issue #153 / PR #154 at HEAD `6043706553a69c8aa410e2c0b889e507fa717d60`. Reconstruct the remaining exact current PR executable files (`integration.py`, `supported.py`, protocol/integration/audit tests) plus exact merged LAB-080 and LAB-036 dependencies/tests through the GitHub connector and verify Git blob identities. Execute LAB-081 isolated + integration + both audit-regression suites, LAB-080 regressions, LAB-036 regressions, unsafe baseline, and compileall. Fix any failure and republish. Then perform a fresh complete remote patch audit of every PR file. If clean and HEAD is unchanged, mark PR #154 ready, squash-merge, close Issue #153 DONE, and choose the next highest-value correctness bottleneck.

## Backlog

- #153 / LAB-081 — historical anchor-provider generation continuity and receipt verification — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
