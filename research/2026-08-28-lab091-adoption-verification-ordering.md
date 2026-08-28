# LAB-091 adoption verification ordering audit — 2026-08-28

## Finding

The final `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` inherits the constructor from `SupportedMutableAsymmetricSharedAnchorLedger`.

That constructor currently performs:

1. lower LAB-080/LAB-082 construction;
2. `self._install_guards()`;
3. `self.verify_durable()`.

Because `_install_guards()` dynamically dispatches to the final LAB-091 implementation, it installs and commits persistent v2/v3/v4 triggers plus adoption-state validation before the complete lower LAB-082 durable verifier runs.

This means an existing database that passes the LAB-091 state-shape validator but fails lower cryptographic/history verification can fail adoption **after persistent LAB-091 triggers have already been committed**. Adoption is fail-closed, but not side-effect-free/atomic on invalid preexisting state.

## Why the current adoption validator does not subsume lower verification

`validate_existing_mutable_state_locked()` intentionally checks state-machine invariants only. It does not reverify asymmetric receipt signatures/provider-generation history. Lower LAB-082 `verify_durable()` owns that cryptographic/history verification and cross-binds confirmed/PREPARED intents to authenticated receipts.

Therefore the ordering matters: successful state-shape validation is not equivalent to successful durable verification.

## Executable mechanism reproduction

A focused file-backed SQLite experiment modeled the current ordering:

- transaction A installs and commits a persistent guard trigger;
- durable verification then rejects invalid state;
- reopening `sqlite_master` still shows the guard trigger.

Result: `current_order -> [('lab091_guard',)]`.

A pre-verification-first ordering rejected the same invalid state before installing the trigger.

Result: `safer_order -> []`.

This is mechanism evidence, not an exact real-stack regression.

## Candidate correction

Before changing runtime, add an exact real-stack regression proving that failed first adoption leaves no LAB-091 trigger/schema side effects.

If reproduced through the final supported surface, the minimal constructor ordering candidate is:

1. lower construction;
2. `verify_durable()` before guard installation;
3. `_install_guards()`;
4. `verify_durable()` again after installation.

The second verification preserves the existing post-install check and catches any installation/adoption bug; the first prevents persistent guard installation on a database that is already invalid under the lower durable contract.

Do not publish the runtime reorder until the exact LAB-080/LAB-082 regression is executable and green.
