# LAB-092 — full provider-history verification before marker receipt recovery

Date: 2026-09-01

## Context

LAB-092 ordinary startup classifies activation-schema provenance before constructing the LAB-090 surface. For `COMPLETE` state it then re-authenticates the deterministic migration marker through a non-constructor historical-ledger bridge so provider-activation recovery cannot run first.

## Audit finding

The bridge's `execute()` path is not purely read-only when the marker's historical receipt is missing. For a current-generation confirmed marker it can reconcile against the external anchor and persist a replacement `historical_provider_receipts` row.

Before this change, that happened before the later LAB-090 constructor performed full provider-history verification. Receipt verification only needs the generation that signed the receipt; therefore corruption elsewhere in provider history can remain invisible long enough for the replacement receipt write to occur.

Concrete regression construction:

1. complete a legitimate LAB-092 migration;
2. delete only the migration marker's historical receipt;
3. insert a valid-looking orphan successor descriptor into `provider_generations` without its required transition/head continuity;
4. restart LAB-092.

Receipt-only reauthentication can still validate generation 1 and recreate the receipt, while complete provider-history verification must reject the orphan successor. Startup must fail before that write.

## Regression-first evidence

Branch `lab-092-activation-schema-provenance` commit:

- `e243511fb4001d049f3948227d727d486a3691f4`
- adds `experiments/provider_generation_history/tests/test_activation_schema_pre_auth_history_verification.py`;
- requires corrupt history to raise `HistoricalVerificationError` and leave the deleted marker receipt absent.

Exact branch execution is not claimed because fresh git transport failed before repository execution with `Could not resolve host: github.com`.

## Fix

Commit:

- `7b14fc29217bdf987704d61bfcbc80fba43db1a4`
- `activation_schema_provenance.py` blob `35e1adef996640578bf7ade76972680189211bd4`.

Added `_verify_confirmation_authority()` using the already-audited non-mutating reservation objects. It opens a read transaction, runs complete `_verify_durable_locked()` provider-history verification, derives the runtime descriptor from the exact `AttestedCatchup`, and requires runtime generation == durable head. Only after that read-only gate may marker `execute()` perform external reauthentication/recovery.

The same gate is used on both COMPLETE startup and the post-DDL explicit-migration confirmation handoff.

## Additional audit conclusions

- Direct local `receipt_binding` substitution is already fail-closed: confirmed `execute()` recomputes/loads a cryptographically verified historical receipt binding and compares it with the ledger row.
- A stored historical receipt means repeated startup reauthentication is local verification, not a repeated external reconcile call.
- Missing-receipt recovery can perform an authenticated external reconcile and one durable receipt write by inherited design; after this change it cannot do so before complete provider-history/runtime verification.
- No LAB-090 provider-activation recovery is introduced by the new helper; it uses `object.__new__` reservation surfaces and read-only history verification.

## Remaining validation

Keep PR #177 draft. Execute the new regression and the full LAB-092 suite on exact published head once source execution transport is available. Then audit the remaining boundary between successful external marker reauthentication and LAB-090 constructor recovery for concurrent authority changes; inherited current-generation checks appear to fail stale runtime before activation recovery, but this still needs exact branch execution and concurrency validation.
