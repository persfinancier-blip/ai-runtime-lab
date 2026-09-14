# LAB-095 cross-generation COMPLETE reauthentication regression

Date: 2026-09-14

## Context

LAB-095 now requires every repeated `migrate_database_identity()` call, including a local COMPLETE custody state, to pass the reconstructed identity intent through `ledger.execute()` and then bind finalization to the exact authenticated `LedgerEntry`. The previous audit established that this remains compatible with legitimate provider-generation rotation only through the supported historical ledger, where a persisted signed `HistoricalReceipt` authenticates an older confirmed ledger entry.

## This run

LAB-086 was probed first as required. Direct GitHub materialization through shell Git remains blocked before repository execution with `Could not resolve host: github.com` (exit 128). GitHub connector reads/writes remain available, but no supported byte-preserving connector-to-executable-filesystem bridge was established for the complete executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`. No LAB-086 requirement was weakened and no new PASS is claimed.

On draft PR #187, added:

`experiments/provider_generation_history/tests/test_database_identity_rotation_reauthentication.py`

PR branch commit: `835a81914c5234e68ef436e30c9837331d262432`.
Published test blob: `c46914e435a1edbcf234265718976a89eb7a7108`.

The regression uses the real `SupportedHistoricalSharedAnchorLedger`, real signed providers, real generation descriptors and real `rotate_provider()` path. It requires all of the following:

1. Install/confirm LAB-095 logical database identity while provider generation 1 is current.
2. Prove that the identity request has a persisted historical receipt bound to provider `anchor-A`, generation 1, position 1 and the exact request id.
3. Legitimately rotate the provider to generation 2 through `rotate_provider()` using the real transition proof and generation-2 attested provider.
4. Make generation 1 unavailable and re-run `migrate_database_identity()`.
5. Require the same logical database identity digest to be returned, proving COMPLETE reauthentication uses retained historical signed evidence rather than live access to the obsolete provider generation.
6. Delete the exact historical receipt and re-run migration.
7. Require fail-closed `HistoricalVerificationError`; local COMPLETE custody alone must not be enough authority.

The committed test source was re-read from GitHub after the write and passed local Python syntax compilation. Full behavioral GREEN is intentionally not claimed because the complete byte-exact dependency closure is not executable in this run.

## Security conclusion

The retained contract is now explicit in code: provider rotation must not strand an already-confirmed LAB-095 identity when historical signed receipt evidence is intact, but loss/corruption of that historical external evidence must prevent repeated COMPLETE-state authentication. This preserves both availability across legitimate key/provider-generation rollover and fail-closed authority semantics.

## Next action

After the mandatory LAB-086 materialization probe, execute this new regression together with the committed LAB-095 COMPLETE-reauthentication, confirmed-finalize, recovery, concurrency, legacy-prefix and tamper regressions on the smallest safe byte-exact closure that can be materialized. Then execute DB-A -> DB-B lifetime-binding and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates before considering PR #187 integration.
