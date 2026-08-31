# LAB-090 activation trigger tamper restart audit

Date: 2026-08-31

## Scope

Narrow fail-closed audit of the durable provider-activation fence in draft PR #175 while LAB-086 exact-byte publication remains blocked by the absence of a supported byte-preserving server-side patch-composition operation.

## Finding

`SupportedHistoricalSharedAnchorLedger._init_activation_schema()` installs `block_intent_during_provider_activation` with `CREATE TRIGGER IF NOT EXISTS`.

That is sufficient when the trigger is missing, but it does not authenticate an already-persisted same-name trigger. A database containing a same-name no-op/tampered trigger therefore survives restart unchanged. `_verify_activation_records()` verifies activation rows but does not verify the persisted enforcement trigger definition.

This matters because the trigger is the durable SQLite boundary that prevents new `shared_anchor_intents` while any activation remains `SQL_COMMITTED`. If the trigger is replaced by a no-op, restart can accept the database and later intents are no longer fenced by unresolved activation state.

## Reproduction evidence

Published deterministic regression on `lab-090-provider-activation-fencing`:

- commit `23087e48fbc99229e194e15620fa35d13f8a1e86`;
- `experiments/provider_generation_history/tests/test_activation_trigger_tamper_restart.py`;
- independently calculated and remotely re-fetched blob `3b6efe53d3cef505ef78a4fadf9d283aa88deac7`;
- local `py_compile` PASS.

The regression creates a valid ledger, replaces `block_intent_during_provider_activation` with a same-name `WHEN 0` no-op, and requires restart to raise `HistoricalVerificationError`.

A separate file-backed SQLite mechanism check confirmed:

1. a same-name tampered `WHEN 0` trigger survives the production-shaped `CREATE TRIGGER IF NOT EXISTS` statement;
2. with a persisted `SQL_COMMITTED` activation row, an intent insert is admitted through that no-op trigger.

This mechanism check passed. Exact branch behavioral RED/GREEN is not claimed because direct repository execution transport remains unavailable in this run.

## Fix direction

Fail closed before accepting restart. The minimal production change should authenticate the persisted enforcement trigger semantics after schema initialization, or safely reinstall the canonical trigger while holding an appropriate serialization boundary. Blind drop/recreate without serialization is not acceptable because it can temporarily remove the fence for concurrent writers.

Prefer a single canonical trigger SQL definition used both for creation and verification so the installation and audit paths cannot drift independently.

## LAB-086 capability observation

The GitHub connector in this run can fetch exact blobs by SHA. It successfully retrieved predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` and retained patch `61841b58be42b01b97ca223567cbf9f428f7f0ce`, and the LAB-086 branch was conflict-checked: `strict_fence.py` still has exactly the predecessor blob.

However, no supported high-level server-side apply-patch/composition action is exposed. The normal Contents API requires complete replacement UTF-8 content, which would require manually/model-reserializing the 949-line security-critical file and violates the retained exact-byte publication contract. Therefore LAB-086 was not mutated.

## Next action

LAB-086 remains first priority if a supported byte-preserving composition bridge appears. Otherwise, for LAB-090 implement canonical trigger-definition verification/reinstallation under a safe serialization boundary, run the new regression plus activation restart/integration/downstream gates when exact execution is available, then retain only evidence actually observed.
