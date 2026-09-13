# LAB-095 confirmed-finalize reauthentication race

Date: 2026-09-14

## Finding

`migrate_database_identity()` calls `ledger.execute(intent)`, which for a real `SharedAnchorLedger` reauthenticates a CONFIRMED entry against the external provider. LAB-095 then discards the returned authenticated `LedgerEntry`, opens a new SQLite transaction in `_finalize_confirmed()`, rereads the row, and derives the logical database identity from that later row.

That creates a TOCTOU window between external reauthentication and local custody finalization. A same-host SQLite writer can replace authority-bearing CONFIRMED fields after `ledger.execute()` returns and before `_finalize_confirmed()` reads them. The current LAB-095 locked classifier checks custody payload/request coherence, but it does not bind finalization to the exact externally authenticated CONFIRMED snapshot returned by `ledger.execute()`.

A narrow file-backed SQLite semantic probe reproduced the consequence: after an authenticated tuple `(provider-alpha, generation 1, position 1, receipt d...)` was captured, changing the durable row to `(attacker-provider, generation 99, position 99, receipt e...)` while retaining the same request/payload allowed the current finalization shape to persist the attacker tuple into CONFIRMED custody and derive a logical identity from it.

## Regression-first artifact

Draft PR #187 now contains `experiments/provider_generation_history/tests/red_intent_lab095_confirmed_finalize_reauthentication.py`, commit `e3d4821f4c53349eff8f96614ef0c36b4c5e8230`.

The regression models `SharedAnchorLedger.execute()` returning the authenticated CONFIRMED snapshot, mutates the SQLite row before LAB-095 finalization, and requires `DatabaseIdentityMigrationError("confirmed identity intent changed after authentication")` while custody remains PREPARED/unfinalized.

## Required production fix

Do not perform another external increment. Preserve same-request reconciliation. Instead:

1. retain the exact CONFIRMED `LedgerEntry` returned by `ledger.execute()`;
2. pass that authenticated snapshot into `_finalize_confirmed()`;
3. inside the final `BEGIN IMMEDIATE`, compare the complete current identity-intent authority tuple with the authenticated snapshot before deriving or persisting the logical identity;
4. any difference must fail closed and leave custody PREPARED;
5. idempotent COMPLETE restart remains verify/read-only.

The comparison should cover at least component/type/payload, provider id/generation, predecessor/position, request id, status, and receipt binding, not merely request/payload.

## Validation status

- Current behavior reproduced by a local file-backed SQLite semantic probe: vulnerable tampered tuple was accepted by the current finalization shape.
- RED regression is committed to PR #187.
- Full exact-closure execution is not claimed: shell GitHub/raw GitHub DNS remains unavailable in this runtime, and no large closure was manually reconstructed.

## LAB-086 observation

Priority LAB-086 materialization was re-probed first. Both `git ls-remote https://github.com/...` and raw GitHub `curl` failed on DNS resolution before repository execution. No LAB-086 gate was weakened and no new PASS is claimed.
