# LAB-095 authenticated finalize binding fix

Date: 2026-09-14

## Finding
`SharedAnchorLedger.execute()` returns the CONFIRMED `LedgerEntry` whose provider result was externally reauthenticated, but LAB-095 previously discarded that return value and later finalized from a fresh SQLite read. A same-host writer could therefore replace authority-bearing fields after reauthentication and before local custody finalization.

## Fix
Draft PR #187 now retains the exact CONFIRMED entry returned by `ledger.execute()` and passes it into `_finalize_confirmed()`.

Under the final `BEGIN IMMEDIATE`, LAB-095 rereads the complete durable identity-intent tuple and requires exact equality with the authenticated snapshot before any custody mutation. Compared fields are:

- intent id;
- component id;
- intent type;
- payload digest;
- provider id;
- provider generation;
- predecessor position;
- position;
- request id;
- status;
- receipt binding.

The row is also rechecked against the LAB-095 identity/custody binding. Any drift raises `DatabaseIdentityMigrationError("confirmed identity intent changed after authentication")` and leaves custody unfinalized. The same comparison is required even when another process has already moved custody to COMPLETE, so COMPLETE cannot bypass authenticated-snapshot binding.

Production commit: `f958719e9108b9d2011fcebfd5500edead854494`.
Test-helper API alignment commit: `d022656ceac70700009d302de9d26ad47190b0f6`.
Published production blob after re-fetch: `3292c0aacaf564416cb336a95ccf9229963dd738`.

## Validation actually executed
A focused file-backed SQLite semantic regression was executed in this runtime. It first accepted an unchanged authenticated 11-field tuple, then replaced provider id/generation/position/receipt after authentication and verified the finalization guard rejected the replacement with the required error. Result: PASS.

A GitHub compare from prior PR head `e3d4821f...` to `d022656c...` shows only two touched files: production migration code and its migration-test helper.

Full exact-repository LAB-095/downstream GREEN is not claimed yet.

## LAB-086 capability observation
The GitHub connector can now read the exact recursive tree for executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, which is useful control-plane evidence. The shell execution environment still cannot resolve `github.com`, so it cannot materialize the complete exact dependency closure into the executable filesystem; the mandatory full LAB-086 gate therefore remains unexecuted and its byte-exact requirements were not weakened.
