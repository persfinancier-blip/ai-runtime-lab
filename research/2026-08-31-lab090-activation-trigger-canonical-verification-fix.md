# LAB-090 activation trigger canonical verification fix

Date: 2026-08-31
Issue: #169
Draft PR: #175
Branch: `lab-090-provider-activation-fencing`

## Problem

The persisted `block_intent_during_provider_activation` trigger is part of the durable writer-safety boundary: while any provider activation remains `SQL_COMMITTED`, new rows in `shared_anchor_intents` must be rejected.

The previous initializer used `CREATE TRIGGER IF NOT EXISTS`. SQLite intentionally leaves an already-existing same-name trigger untouched. A persisted same-name trigger could therefore be replaced with a no-op definition (for example `WHEN 0`), survive restart, and silently remove the cross-process activation fence. `_verify_activation_records()` authenticated activation rows but not the enforcement trigger definition.

A deterministic RED regression was already published as commit `23087e48fbc99229e194e15620fa35d13f8a1e86`, file `experiments/provider_generation_history/tests/test_activation_trigger_tamper_restart.py`, blob `3b6efe53d3cef505ef78a4fadf9d283aa88deac7`.

## Fix

PR #175 commit `5101eba17df411d194ef1194d23d2c3ec130d923` changes only `experiments/provider_generation_history/supported.py`; resulting blob `d80a6015df8b39a43a1d3674ff7fc65263f1de7b`.

The implementation now:

1. stores one canonical trigger definition in `_ACTIVATION_TRIGGER_SQL`;
2. derives the idempotent install statement from that exact definition by adding `IF NOT EXISTS`;
3. reads the persisted trigger SQL from `sqlite_master` immediately after initialization;
4. compares normalized-whitespace SQL against the canonical definition;
5. raises `HistoricalVerificationError("activation intent fence trigger definition mismatch")` on absence or mismatch;
6. does not drop/recreate an existing trigger, avoiding a concurrency window in which the durable fence could temporarily disappear.

Whitespace normalization is deliberately narrow. It tolerates SQLite/source formatting differences but does not normalize tokens, expressions, names, predicates, or trigger body semantics. A semantically altered same-name trigger therefore fails closed.

## Validation actually executed

GitHub commit inspection confirmed a one-file patch: 38 additions / 9 deletions in `supported.py`, plus the pre-existing missing-newline-at-EOF marker.

A separate file-backed SQLite mechanism test executed successfully:

- fresh canonical install -> persisted `sqlite_master.sql` normalizes equal to `_ACTIVATION_TRIGGER_SQL`;
- replace trigger with same-name `WHEN 0` no-op;
- rerun the same `CREATE TRIGGER IF NOT EXISTS` initialization;
- SQLite preserves the tampered trigger, as expected;
- canonical verification returns mismatch and therefore the production initializer will fail closed.

Result: `canonical trigger install/verification mechanism: PASS`.

## Validation not claimed

Exact published-branch behavioral execution of `test_activation_trigger_tamper_restart.py`, the activation restart/integration suite, and downstream tests is not claimed in this run because direct repository execution transport remains unavailable. The PR must remain draft until those gates execute on exact published bytes.

## Audit notes

- No drop/recreate repair is attempted; startup rejects tamper rather than opening a fence gap.
- The trigger name is also canonicalized to avoid duplicated literals in install and verification.
- Table-schema authentication remains a separate concern; this change intentionally closes only the already-reproduced trigger-definition hole.
- LAB-086 remains priority #1 and was not mutated because its retained security patch still requires a byte-preserving composition/write bridge.
