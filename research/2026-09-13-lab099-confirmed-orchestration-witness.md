# LAB-099 frozen CONFIRMED orchestration witness

Date: 2026-09-13

## Objective

Compose the already-frozen LAB-099 test-only mechanisms into one end-to-end witness without creating any new semantic authority:

`legitimate shared-anchor prefix 1..41 -> frozen PREPARED at 42 -> existing provider increment/RECONCILE -> frozen CONFIRMED plan -> persisted CONFIRMED verification`.

Production LAB-099 behavior remains forbidden until an actual repository RED is observed.

## LAB-086 priority probe

LAB-086 remained priority #1. The pinned executable commit `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` is readable through the GitHub connector, but this runtime still exposes no supported byte-preserving path that materializes the complete manifest-listed repository closure into the local filesystem for execution. No LAB-086 behavioral/security/compile/conflict PASS is claimed in this run.

## Added test-only helper

PR #186 now contains:

`experiments/provider_generation_history/tests/lab099_confirmed_orchestration_witness.py`

The helper deliberately imports and composes only existing frozen/reference mechanisms. It does not derive alternative request IDs, receipts, confirmed heads, epochs, or PREPARED/CONFIRMED protocol bytes.

It performs these checks/mechanics:

1. builds the legitimate shared-anchor prefix 1..41 using `lab099_shared_anchor_prefix_witness.build_legitimate_prefix()`;
2. requires durable verification of that prefix;
3. installs the exact atomic PREPARED cutover through `lab099_precursor_fixture_adapter.install_atomic_prepared_cutover()`;
4. reads the persisted PREPARED row and requires exact predecessor=41, position=42, frozen request ID, and PREPARED status;
5. advances the same existing generation-8 provider from 41 to 42 using the frozen request ID;
6. reauthenticates the result through the existing `RECONCILE` path;
7. requires the stable binding to equal frozen receipt `ead923c6b9bcd68bc6e4276284fd72211544fcede9f06297b8bc074d898130b4`;
8. persists that existing-provider receipt through the normal `provider_history.store_receipt()` mechanism;
9. applies the already-frozen `confirmed_event_plan()`;
10. runs the persisted CONFIRMED verifier against frozen position/head authority;
11. requires confirmed head `45c53da7909f826f6c8107fef542ba17bed551df8637f8a3185fe66a04410dda`;
12. finally requires full historical-ledger durable verification.

## Audit correction

The first authored helper verified the RECONCILE receipt but did not persist it into `historical_provider_receipts`. Source audit of `HistoricalSharedAnchorLedger.verify_durable()` showed that every CONFIRMED row must have a matching authenticated historical receipt; the first helper would therefore have failed the final durable gate.

The published helper was immediately corrected to call the existing `witness.ledger.provider_history.store_receipt(receipt)` before CONFIRMED installation, require the exact frozen binding, and run final `witness.ledger.verify_durable()`.

This correction is important because the orchestration must exercise existing receipt durability rather than only the separate LAB-099 persisted-row verifier.

## Observed validation

Executed locally on the authored helper:

- `python -m py_compile`: PASS;
- local Git blob after the audit correction: `71a50df5b5d8c3cece33274d5263f1c4fe0ec27a`;
- GitHub Contents update returned the same content blob `71a50df5b5d8c3cece33274d5263f1c4fe0ec27a`.

Full import/end-to-end execution is not claimed because the exact repository dependency closure was not materialized in this runtime.

## Branch state

PR #186 remains open/draft/mergeable and test-only. Current head after the audit correction: `766434563a5ad82a88156687c84de9c9e17b14c6`. Compared with pinned PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`: ahead 26 / behind 0. There are 17 changed files, all under `experiments/provider_generation_history/tests/`.

## Next action

LAB-086 must still be probed first next run. If no exact executable materialization path exists, the next LAB-099 step is not production code: attempt exact materialization of the minimal orchestration dependency closure with byte-identity verification. Only if the complete closure is available should `execute_frozen_confirmed_orchestration()` be run against a fresh file-backed SQLite database and its result compared to the frozen request/receipt/head identities. If closure materialization remains unavailable, source-audit the minimal closure manifest and persist it so a later executable runtime can reproduce the gate exactly.
