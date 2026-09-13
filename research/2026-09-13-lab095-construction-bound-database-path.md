# LAB-095 — construction-bound supported database path

Date: 2026-09-13
Issue: #180
Draft PR: #187

## Objective

Close the original LAB-095 runtime rebinding finding for the supported ledger/provider-history surface: after successful construction against DB A, ordinary retained path state must not be assignable to DB B and then consumed by supported reserve/execute/rotate/verify operations.

This physical binding is intentionally separate from LAB-095 logical database/history identity. A canonical filesystem path is a runtime routing reference, not authenticated durable identity authority.

## Priority / capability observation

LAB-086 was re-probed first as required. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with:

`Could not resolve host: github.com`

exit 128.

No LAB-086 executable/security PASS is claimed and no byte-exact gate was weakened.

## Source finding reconfirmed

On the LAB-095 branch before this slice:

- `SharedAnchorLedger.__init__()` assigned public mutable `self.path = str(path)` and inherited `_con()` opened that path;
- `DurableProviderHistory.__init__()` independently assigned public mutable `self.path = str(path)` and its `_con()` opened that path;
- `SupportedHistoricalSharedAnchorLedger` constructed a `CoordinatorOnlyProviderHistory` and then the supported shared ledger, so both supported objects retained independently assignable path references;
- transaction-internal history helpers consume the ledger's already-open connection, meaning rebinding the ledger path can redirect the serialization/authority database without reconstructing the object and rerunning full provider-history verification on the new target.

## Implemented slice

PR #187 now contains `experiments/database_binding.py` with `CanonicalDatabaseBinding`.

Contract:

1. the first `path` assignment performed by an existing base constructor is canonicalized with `Path(...).expanduser().resolve(strict=False)`;
2. the canonical value is retained in private `_canonical_database_path`;
3. public `path` stays readable for compatibility/diagnostics;
4. any later assignment to `path` raises `AttributeError("database path is construction-bound")`;
5. direct later assignment to `_canonical_database_path` also raises;
6. all other object attributes remain assignable, so this does not freeze unrelated runtime state.

The mixin is applied only at the audited supported boundary:

- `SupportedSharedAnchorLedger(CanonicalDatabaseBinding, SharedAnchorLedger)`;
- `CoordinatorOnlyProviderHistory(CanonicalDatabaseBinding, IntegratedProviderHistory)`.

This keeps lower-level protocol experiments unchanged while making every inherited `_con()` on the supported objects resolve through the same construction-bound property.

Published blobs after the slice:

- `experiments/database_binding.py`: `c6bf05b3a5579e076142300aefbc9d785cc6354a`;
- `experiments/shared_anchor_intent_ledger/supported.py`: `b16fda1fd1f47ab3f333af6ac94190d6135dcf64`;
- `experiments/provider_generation_history/supported.py`: `7808753d7fb27c979e93f342eaf05d1e9f3f7c41`;
- `experiments/provider_generation_history/tests/test_database_path_binding.py`: `a7671276b4c8f6b7b3b1de507fe1ed405ee3be97`.

Current PR head after the regression commit: `fd6d75ea35decdb719632802a538427cf51d71c7`.

## Regression contract

The new `test_database_path_binding.py` creates a supported historical ledger on DB A, executes one intent, rotates to provider generation 2, then copies A to DB B.

DB B is deliberately corrupted by replacing the authenticated transition `old_mac` while retaining the same generation-2 `provider_generation_head`. This is the important adversarial shape from #180: a superficial current-head comparison can still match even though full provider-history continuity is invalid.

The regression then requires:

- `ledger.path = db_b` fails;
- `ledger.provider_history.path = db_b` fails;
- direct private canonical-slot rebinding fails for both objects;
- both objects still report canonical DB A;
- `ledger.verify_durable()` continues to validate A;
- a subsequent supported `execute()` succeeds on A;
- DB B's reserved tail does not move and it receives no new intent.

## Validation actually executed

The exact published `CanonicalDatabaseBinding` source was independently executed in the current runtime against a small inherited base that assigns `self.path` in its constructor and later consumes `self.path`.

Observed PASS:

- first assignment canonicalizes to DB A;
- public `path` reassignment to DB B is rejected;
- direct `_canonical_database_path` reassignment is rejected;
- subsequent base behavior continues selecting DB A.

The full new DB-A/DB-B repository regression was **not** executed because the exact dependency closure could not be safely materialized in this runtime. It is committed regression evidence, not a claimed GREEN gate.

PR #187 remained draft and was re-fetched after the changes as `mergeable=true`.

## Audit notes

The mixin is intentionally placed in supported classes rather than changing the lower-level experimental protocol classes. This minimizes compatibility risk while closing the supported authority surface named by #180.

The MRO is coherent with existing constructors:

- `SupportedSharedAnchorLedger` reaches `SharedAnchorLedger.__init__()` through the mixin, so the legacy first `self.path = ...` assignment initializes the canonical slot;
- `CoordinatorOnlyProviderHistory` reaches `DurableProviderHistory.__init__()` through the mixin in the same manner;
- later `self.attested` and other runtime assignments are unaffected.

This slice does **not** claim to close LAB-094 mutable bootstrap authority or LAB-096 mutable `provider_history` strategy authority. Those remain separate retained-authority findings.

## Remaining gate

Before LAB-095 integration:

1. execute `test_database_path_binding.py` on the exact repository closure;
2. inspect LAB-090/LAB-092 supported subclasses for repeated path initialization or a bypass that replaces the supported binding surface;
3. run the remaining migration crash/partial/concurrent/legacy regressions;
4. run LAB-080/LAB-081/LAB-090/LAB-092 downstream suites;
5. perform final conflict/security audit against current main.

LAB-099 PREPARED authority remains blocked until LAB-095 completes its authenticated logical identity and physical lifetime-binding gates.
