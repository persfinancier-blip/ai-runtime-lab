# LAB-086 — hidden rowid REPLACE exact RED→GREEN verification

Date: 2026-08-28

## Scope

This note records execution evidence for the hidden SQLite `rowid` REPLACE blocker already documented in `research/2026-08-28-lab086-hidden-rowid-replace.md` and covered by `test_thaw_rowid_collision_regression.py`.

The runtime patch is **not published by this note**. PR #165 must remain draft until the candidate is published byte-exact and the repinned strict/thaw + full real-ledger gates are clean.

## Exact predecessor

- executable pin: `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`
- exact predecessor `strict_fence.py` blob: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`
- exact regression blob: `9773536e5c1627f2a01f13d45fcdcb7016aa7d08`

The predecessor runtime was reconstructed locally and accepted only after `git hash-object` matched `d4a6a40f...`. The regression was reconstructed and accepted only after `git hash-object` matched `9773536e...`.

## Exact RED result

The exact predecessor runtime was executed against the exact regression. Result: **3/3 FAILED as intended**. Each failure was `AssertionError: IntegrityError not raised`, confirming the bypass on all three covered surfaces:

1. INSERT-thawed authenticated public history;
2. transaction-thawed post-cutoff proof history;
3. append-only provider receipt history.

In each case `INSERT OR REPLACE` could target an existing hidden SQLite `rowid` while supplying a fresh declared identity.

## Candidate construction

The durable patch `research/2026-08-28-lab086-hidden-rowid-replace.patch` was applied programmatically to the exact predecessor bytes. The resulting local candidate has Git blob:

`b78e7c98e35138719f77c482c7f1aab36b702de7`

`py_compile` / focused package compileall completed successfully.

## Exact GREEN result

The exact regression blob `9773536e...` was executed unchanged against candidate `b78e7c98...`.

Result: **3/3 PASS**.

The tests also preserve the positive side of the contract: a legitimate new declared history/proof/receipt identity remains insertable where the supported final writer requires append capability.

## Publication gate

The available GitHub write primitive for the existing security-critical file is whole-file Contents API replacement and does not accept a local file reference. In this runtime there is no byte-preserving local-file → connector-file transfer. The ~40 KB candidate was therefore **not manually reserialized into the write call**.

Safe next action:

1. publish `strict_fence.py` only through a byte-safe transfer path from exact predecessor + durable patch;
2. require GitHub to return exactly blob `b78e7c98e35138719f77c482c7f1aab36b702de7`;
3. re-fetch/hash-verify the published file;
4. run `test_thaw_rowid_collision_regression.py` plus the complete strict/thaw conflict subgate and compileall;
5. repin only after that exact published-source gate is green, then resume the complete branch-local LAB-080→086 gate.
