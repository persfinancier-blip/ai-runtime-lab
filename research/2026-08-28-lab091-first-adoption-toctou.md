# LAB-091 first-adoption verification/guard-install TOCTOU

Date: 2026-08-28

## Finding

The current final LAB-091 constructor does not make first-adoption durable verification and persistent guard installation one atomic state transition.

The inherited LAB-082 constructor performs a full `verify_durable()` before returning to `SupportedMutableAsymmetricSharedAnchorLedger.__init__()`. LAB-091 then installs its persistent guards in a separate `BEGIN IMMEDIATE` transaction and commits them. Only after that commit does `SupportedMutableAsymmetricSharedAnchorLedger.__init__()` call `self.verify_durable()` again.

This leaves an interleaving on first adoption:

1. inherited full LAB-082 durable verification succeeds;
2. another still-writable lower/legacy connection mutates authenticated LAB-082 history;
3. LAB-091 `_install_guards()` validates only the mutable state-machine projection and commits LAB-091 triggers;
4. the final full durable verification detects the lower-history corruption and the constructor raises;
5. LAB-091 guards remain persisted even though adoption failed.

The existing `test_failed_adoption_no_guard_persistence.py` corrupts history before step 1, so it correctly proves early failure but does not cover this race.

## Source evidence

`history_bound_operation_scoped._install_guards()` installs the v2/v3/v4 guards and calls `validate_existing_mutable_state_locked(q)` under one `BEGIN IMMEDIATE` transaction, then commits.

`adoption_validation.validate_existing_mutable_state_locked()` intentionally validates retroactive LAB-091 state-machine invariants only. Its contract delegates receipt signatures/provider-generation binding to LAB-082. It does not cryptographically verify the historical receipt rows inside the guard-install transaction.

LAB-082 `AsymmetricHistoricalSharedAnchorLedger.verify_durable()` is broader than `provider_history._verify_durable_locked(q)`: in the same read transaction it verifies provider generations/transitions/receipt signatures, shared-anchor tail continuity, PREPARED/CONFIRMED receipt binding, and component watermark consistency.

Therefore adding only `provider_history._verify_durable_locked(q)` to LAB-091 adoption would not close the complete TOCTOU boundary.

## Regression

Added `experiments/mutable_shared_anchor_writer/tests/test_adoption_toctou_guard_persistence_regression.py`.

The regression deterministically models the race by subclassing the final supported LAB-091 surface. After the first inherited full `verify_durable()` succeeds, it corrupts the persisted LAB-082 receipt signature before control reaches LAB-091 guard installation. Construction must then fail, and the acceptance condition is that no `lab091_%` triggers survive the failed adoption.

Published regression blob: `262834c34b6b7be182427e86f78963fc5caafa42`.

No test PASS is claimed in this runtime. The expected current behavior is RED: the second durable verification should reject the corrupted receipt only after `_install_guards()` has committed, leaving persisted LAB-091 triggers.

## Required fix shape

Refactor the complete LAB-082 durable verification into a locked helper that accepts the already-open SQLite connection/transaction, preserving all current checks. Then LAB-091 first adoption should, under the same `BEGIN IMMEDIATE` transaction used to install/validate guards:

1. install candidate guards;
2. run LAB-091 retroactive state-machine validation;
3. run the complete lower LAB-082 durable locked verifier against the same snapshot while the write lock excludes competing lower writers;
4. commit only after all validation succeeds.

A validation failure must roll back both the guard DDL and adoption validation. The normal post-construction verifier may remain as defense in depth, but it must not be the first full lower-history verification after guard commit.

Do not duplicate only a subset of LAB-082 checks in LAB-091; that would create two drifting definitions of durable validity.

## Boundary

LAB-087 is intended to own the sole writable process/filesystem boundary in deployment, but LAB-091 is explicitly being audited for legacy/alternate supported write surfaces and first adoption. The upgrade/adoption transition must either be atomic against those surfaces or explicitly require a verified exclusive-owner precondition. The current code expresses neither as an atomic constructor guarantee, so the regression is retained as a merge blocker for PR #173.
