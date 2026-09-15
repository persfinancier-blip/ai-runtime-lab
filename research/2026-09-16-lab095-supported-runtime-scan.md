# LAB-095 supported-runtime composition scan — 2026-09-16

## Runtime probe
LAB-086 was probed first with a direct `git clone --no-checkout` of the repository. The operation failed before repository code execution with `Could not resolve host: github.com`, exit 128. No LAB-086 executable PASS is claimed.

## Scope
Continued PR #187 scan requested by `state/CURRENT.md`, prioritizing actual supported-runtime construction/restart sites rather than lower-level migration/classifier fixtures.

Inspected:
- `experiments/provider_generation_history/tests/test_provider_history_capability_surface.py`
- `experiments/provider_generation_history/tests/test_store_receipt_guard_hook.py`
- `experiments/provider_generation_history/tests/test_audit_regressions.py`

## Findings and changes
Two stale supported-runtime composition sites were found and adapted on branch `lab-095-database-identity-red-intent`.

1. `test_provider_history_capability_surface.py` directly constructed `SupportedHistoricalSharedAnchorLedger` on a fresh DB with `SignedAnchorProvider`. It now uses the explicit LAB-101 `migrate_activation_schema_v1()` entrypoint and `FencedActivationProvider`. The authenticated activation migration consumes provider position 1; the test asserts that fact before exercising the original capability-surface boundary. No rotation is performed in this test.

2. `test_audit_regressions.py` likewise directly constructed the supported ledger on a fresh DB. It now bootstraps through `migrate_activation_schema_v1()` with `FencedActivationProvider`, asserts migration position 1, executes the original ordinary intent, corrupts the persisted historical receipt binding, and retains the original restart fail-closed assertion through the ordinary supported constructor.

`test_store_receipt_guard_hook.py` was intentionally not rewritten. It uses `object.__new__` plus fake connection/history objects to isolate `_store_receipt()` transaction ordering and the provenance guard hook. It does not claim supported startup or provider rotation; routing it through LAB-101 would destroy the unit boundary under test.

## Branch commits
- `41f559c3daf0b9c670943fd2ff1855d418f6ba9c` — bootstrap capability-surface regression.
- `efaa96eeade6e3e6bebc8ad0fd66c3c8af098ecc` — bootstrap audit restart regression.

## Validation discipline
Changes were source-audited against the already-adapted LAB-101/LAB-090 composition pattern. Exact repository pytest/compileall was not executed because byte-exact repository materialization remains unavailable in this runtime. These commits are not an executable GREEN claim.

## Next action
After the mandatory LAB-086 probe, continue scanning remaining PR #187 supported integration call sites for direct fresh/pre-LAB-092 `SupportedHistoricalSharedAnchorLedger` construction or non-fenced `rotate_provider()` usage. Preserve lower-level `object.__new__`, fake, migration, and classifier fixtures when they intentionally test below the supported startup boundary. If no stale supported call sites remain, continue LAB-095/LAB-096 authority audit.
