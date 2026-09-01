# LAB-092 marker-recovery runtime verification hardening

Date: 2026-09-01

## Finding

`_install_and_reserve_prepared()` classified the activation DDL and provenance marker under `BEGIN IMMEDIATE`, but its `PREPARED` and `CONFIRMED` branches returned before the newly added full inherited provider-history verification and runtime-current check. That created an inconsistent authorization boundary: first installation rejected stale runtime/history before publishing DDL+marker, while recovery of an already-present marker could return from the same helper without first proving that inherited provider authority remained valid/current.

The externally reachable risk is the PREPARED recovery path: `migrate_activation_schema_v1()` classifies `DDL_INSTALLED_PREPARED`, calls `_install_and_reserve_prepared()`, then proceeds toward confirmation. A stale runtime therefore had to be rejected before that helper can return the existing PREPARED marker.

## Regression-first change

Published regression commit `978613365271090cb18a624fbcfc9ae3e61f70e2` on `lab-092-activation-schema-provenance`.

Added `test_stale_runtime_cannot_recover_existing_prepared_marker`:

1. create a legitimate generation-1 inherited ledger;
2. durably rotate provider history to generation 2;
3. model the legitimate pre-LAB-090 activation-schema state;
4. use the current generation-2 runtime to create the atomic exact-DDL + PREPARED migration boundary;
5. retry explicit migration with a generation-1 runtime;
6. require `CurrentGenerationRequired` and require the marker to remain PREPARED.

## Implementation

Published fix/current PR #177 head `aaf13678b0d9d84f42e709a2d9cd051c83e06787`; provenance blob `b529e93879659dfe857795e632985b9d06938f71`.

Inside the same `BEGIN IMMEDIATE` transaction, immediately after reading schema/marker state and before either marker early return, the helper now:

- runs `ledger.provider_history._verify_durable_locked(q)` over the complete inherited provider history;
- derives the exact runtime descriptor through the existing LAB-081 helper;
- requires runtime generation identity to equal the verified durable head;
- only then permits PREPARED/CONFIRMED marker recovery or first-install continuation.

DDL tamper behavior is unchanged: existing PREPARED/CONFIRMED provenance with missing or mismatched activation table/trigger still fails closed and is not repaired.

## Validation actually performed

- GitHub Contents writes succeeded for regression and implementation.
- PR #177 re-fetch shows open, draft, mergeable, head `aaf13678...`.
- GitHub patch re-fetch confirms the full-history/runtime verification is before both marker early-return branches.
- Fresh exact branch checkout/test execution was attempted with `git clone --depth 1 --branch lab-092-activation-schema-provenance ...`; transport failed before repository code execution with `Could not resolve host: github.com`.

No branch-level RED/GREEN is claimed for this slice because exact source execution did not occur.

## Security interpretation

Marker recovery is authority-sensitive, not merely idempotent schema bookkeeping. An existing authenticated provenance row cannot itself prove that the runtime attempting recovery is the durable current provider, nor can it excuse re-verifying the inherited provider history. The migration writer lock is the correct place to make those checks because it binds the recovered marker state to the same durable authority snapshot used by first installation.

## Next action

LAB-086 remains priority #1. If its byte-preserving publication bridge remains unavailable and exact execution is still blocked, continue LAB-092 audit around the transition from `_install_and_reserve_prepared()` to constructing `SupportedHistoricalSharedAnchorLedger` for external marker confirmation: verify that constructor initialization cannot mutate/recover provider activation state in a way that should be prohibited during schema migration, especially when exact DDL+PREPARED exists and provider activation records are unresolved.
