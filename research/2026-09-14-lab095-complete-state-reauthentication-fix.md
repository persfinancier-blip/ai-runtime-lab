# LAB-095 COMPLETE-state reauthentication fix

Date: 2026-09-14

## Finding

`migrate_database_identity()` had a trust-boundary bypass after the confirmed-finalize TOCTOU fix.

`SharedAnchorLedger.execute()` is the production mechanism that reauthenticates an already-CONFIRMED shared-anchor entry against the external provider. `_finalize_confirmed()` was already prepared to accept an authenticated CONFIRMED snapshot even when local custody classified as `COMPLETE`.

However, `migrate_database_identity()` returned `logical_database_identity_digest` immediately when `prepare_database_identity()` reported `COMPLETE`. That branch never called `ledger.execute()`. Consequently a repeated migration/startup verification could trust only locally self-consistent SQLite custody/intent state without reauthenticating the external receipt.

This matters because LAB-095's logical database identity is explicitly required to be externally authenticated rather than a same-DB self-assertion.

## Regression-first change

PR #187 commit `86766045eceddc754bc495a345d371a0edbee227` adds `red_intent_lab095_complete_reauthentication.py`.

The regression installs a valid identity on the first execution, then makes every later `ledger.execute()` fail with `simulated external reauthentication failure`. A second `migrate_database_identity()` must surface that failure rather than returning the locally stored digest.

The pre-fix control flow demonstrably bypassed `execute()` for `COMPLETE`; a focused executable semantic probe confirmed zero execute calls on that branch.

## Production fix

PR #187 commit `473185a0278a3ff3777dfe578be018c33018e415` removes the COMPLETE early return from `migrate_database_identity()`.

All non-corrupt installed states now follow one path:

1. run `prepare_database_identity()` including under-lock provider-history verification;
2. reload custody and reconstruct the exact identity intent;
3. call `ledger.execute()` so CONFIRMED state is externally reauthenticated;
4. pass the returned authenticated entry into `_finalize_confirmed()`;
5. under a final `BEGIN IMMEDIATE`, require exact durable-row equality with that authenticated snapshot before returning/finalizing the logical database identity.

Published production blob after update: `c4d1db46b8b64fec116dcfef8bb05e1e7a7b875e`.

## Validation actually executed

- Focused semantic control-flow probe: pre-fix COMPLETE path made zero `execute()` calls; corrected flow makes one — PASS.
- Re-fetched the published production tail from PR #187 and verified the COMPLETE early return is absent and `ledger.execute()` is unconditional after custody reconstruction — PASS.
- The new committed repository regression has **not** been executed against a complete byte-exact repository closure in this runtime. Do not count full LAB-095 as GREEN.

## Runtime/materialization observation

The GitHub connector can read exact files at pinned refs, but no supported bridge from connector response bytes into the executable filesystem was observed. Shell/Python network access to `raw.githubusercontent.com`/`github.com` still fails DNS resolution. The raw-download helper also requires a web-opened URL, while web access to the raw GitHub URL is disabled. Therefore the retained exact-gate requirement is unchanged.

## Remaining gates

Keep PR #187 draft until:

- committed confirmed-finalize, COMPLETE-reauthentication, recovery, concurrent-installer, legacy-prefix and locked-custody-tamper regressions execute on a byte-exact closure;
- DB-A -> DB-B lifetime-binding regression executes;
- LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates execute;
- a fresh conflict/security audit passes, preserving `CanonicalDatabaseBinding` through LAB-090/LAB-095 `supported.py` conflict resolution.
