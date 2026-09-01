# LAB-092 — non-mutating completion-marker confirmation bridge

Date: 2026-09-01
Issue: #176
Draft PR: #177

## Finding

The LAB-092 migration path correctly made exact activation DDL plus the deterministic PREPARED migration marker visible in one SQLite writer commit. However, immediately after that commit it instantiated `SupportedHistoricalSharedAnchorLedger` solely to call `execute()` on the already-reserved migration intent.

That constructor is not side-effect-free. LAB-090 `SupportedHistoricalSharedAnchorLedger.__init__()` initializes/validates the activation schema, checks runtime provider history, then calls `_recover_pending_activation()` and `_verify_activation_records()` before control reaches migration-marker confirmation.

Therefore a provider activation that became unresolved after the atomic DDL+PREPARED commit could be reconciled/committed/released as an incidental side effect of schema migration before the schema provenance marker itself was externally confirmed. The migration helper should not own provider-activation recovery.

## Regression first

Published branch commit `6f5c564f37b05f199af49fa392d6169097679b54` adds `test_activation_schema_migration_confirmation_bridge.py`.

The regression patches LAB-090 activation recovery so that any call before the migration marker is CONFIRMED raises. Recovery remains permitted after confirmation, when the final supported LAB-092 surface is constructed. This distinguishes the forbidden pre-confirmation constructor side effect from legitimate post-confirmation startup/recovery behavior.

## Fix

Published branch commit `adc02cd7696e0fbd72c1e20a7161b95458241343`; exact provenance source blob `437d94e5d173f45056bc9c52fa7428ab8e3519f3`.

`migrate_activation_schema_v1()` now confirms the already-reserved PREPARED marker through `_reservation_surface(path, attested, bootstrap)` instead of constructing `SupportedHistoricalSharedAnchorLedger`.

`_reservation_surface` is the existing LAB-092 non-mutating authenticated/history-aware object built with `object.__new__`: it carries the exact attested runtime and read/verify-only `CoordinatorOnlyProviderHistory` without running provider-history or activation constructors. Calling inherited `execute()` on that surface preserves LAB-080 semantics:

1. `reserve()` sees the existing exact PREPARED intent rather than inserting a second intent;
2. external catch-up and authenticated reconciliation bind the exact request/position;
3. confirmation updates the exact PREPARED row to CONFIRMED under `BEGIN IMMEDIATE`;
4. historical LAB-090 `_reauthenticate()` still checks the durable current provider generation, so a provider-generation change between reservation and confirmation fails closed rather than confirming stale authority.

Only after the marker is CONFIRMED does migration construct the final `ProvenancedHistoricalSharedAnchorLedger`, at which point normal LAB-090 activation recovery is appropriate.

## Validation actually performed

- Re-fetched the published source from GitHub and confirmed the migration handoff is `_reservation_surface(...).execute(_completion_intent())`; source blob is exactly `437d94e5d173f45056bc9c52fa7428ab8e3519f3`.
- Audited LAB-080 `execute()` and LAB-090 constructor ordering from repository source.
- Fresh branch `git clone` was attempted in this run and failed before repository code execution with `Could not resolve host: github.com`.

No branch-level RED/GREEN is claimed because exact source execution remains unavailable in this runtime.

## Security boundary

This change deliberately does not bypass LAB-080 authenticated confirmation semantics and does not auto-repair activation state. It only removes an unrelated constructor/recovery side effect from the interval between atomic PREPARED provenance publication and external provenance confirmation.

PR #177 must remain draft until the exact regression suite executes.
