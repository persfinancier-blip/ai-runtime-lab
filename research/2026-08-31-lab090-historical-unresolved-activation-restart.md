# LAB-090 historical unresolved activation restart audit

Date: 2026-08-31

## Context

PR #175 now blocks a new provider rotation whenever any activation row remains `SQL_COMMITTED`. That closes the overlap prospectively. This audit asked whether a database produced by an older/pre-fix implementation can already contain the forbidden state and how the current constructor handles it.

## Finding

A pre-fix database can contain:

- provider-generation history/head already advanced through G3;
- an older G2 activation row still `SQL_COMMITTED`;
- current G3 activation resolved/`COMMITTED`.

The current constructor calls `_recover_pending_activation()` only for the durable current generation. Therefore the historical unresolved G2 row is ignored. `_verify_activation_records()` validates ticket shape and status but does not reject `SQL_COMMITTED` on a non-current generation. Construction can therefore succeed.

The persisted `block_intent_during_provider_activation` trigger is global: any `SQL_COMMITTED` row blocks every new shared-anchor intent. The newer overlapping-rotation guard likewise sees that unresolved row. Because the runtime provider is G3, the ordinary current-generation recovery path cannot reconcile the historical G2 provider reservation. The upgraded ledger can therefore construct successfully but remain permanently unavailable.

This is fail-closed availability/correctness, not an authority escalation. The defect is that an unrecoverable legacy state is silently accepted instead of being diagnosed at restart.

## Required invariant

After current-generation recovery, no activation row belonging to a historical generation may remain `SQL_COMMITTED`.

Minimal safe behavior: fail constructor verification with `HistoricalVerificationError` if any non-current generation has `status='SQL_COMMITTED'`. Automatic historical reconciliation is not justified because the current runtime does not possess that historical provider's activation state and silently clearing the row would weaken the provider-side fencing contract.

## Regression published

Branch `lab-090-provider-activation-fencing`, commit `0cbbfd2477db1774b0cadc5294cd85c2b5495d17` adds:

`experiments/provider_generation_history/tests/test_activation_historical_unresolved_restart.py`

The regression creates valid G1→G2→G3 history, then seeds the durable shape that models the older vulnerable scheduler by changing the G2 activation back to `SQL_COMMITTED`. Restart with the valid current G3 runtime must raise `HistoricalVerificationError` rather than construct an indefinitely blocked ledger.

The regression is expected RED on the current PR head. It was not executed in this run because direct filesystem network transport still cannot resolve GitHub. The GitHub connector was able to read exact head/tree metadata, but there is no current connector-to-local byte transfer primitive that materializes the repository for Python execution without manual source reserialization.

## Next implementation

Add a minimal check in activation-record verification after current-generation recovery: resolve the durable current generation once, and reject every `SQL_COMMITTED` activation whose `new_generation_id` differs from that current generation. Then run the new regression plus all LAB-090 activation/integration/downstream gates from exact published bytes before considering PR #175 ready.
