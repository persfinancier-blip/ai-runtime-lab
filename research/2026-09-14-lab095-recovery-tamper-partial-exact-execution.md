# LAB-095 recovery/tamper partial exact execution

Date: 2026-09-14

## Context

LAB-086 remained first priority. A fresh direct Git materialization probe failed before repository execution with `Could not resolve host: github.com` (exit 128). No LAB-086 requirement was weakened and no complete LAB-086 PASS is claimed.

The permitted fallback was the LAB-095 recovery/tamper execution recorded in `state/CURRENT.md`.

## Exact materialized files

The following PR #187 head `835a81914c5234e68ef436e30c9837331d262432` files were reconstructed from GitHub connector content and verified locally with `git hash-object` against the recorded branch blobs:

- `experiments/provider_generation_history/database_identity.py` -> `bac58a48c576001370144cc10cfab8e0cfd129e3`
- `experiments/provider_generation_history/database_identity_migration.py` -> `c4d1db46b8b64fec116dcfef8bb05e1e7a7b875e`
- `experiments/provider_generation_history/tests/test_database_identity_migration.py` -> `cde9d16c5fb257a8b9ad7110f9badb79bede8f3f`
- `experiments/provider_generation_history/tests/test_database_identity_migration_recovery.py` -> `363ab95f1aad425fc89f146ae8fba35d9169950d`
- `experiments/provider_generation_history/tests/red_intent_lab095_confirmed_finalize_reauthentication.py` -> `7dcd20dfd24a9439583595bf433f9f696bd870e7`
- `experiments/provider_generation_history/tests/red_intent_lab095_locked_custody_payload_tamper.py` -> `443e84f65e1d7f58c9b0ae284d700d4ec0f77cc6`

Thus 6/8 files from the previously recorded focused manifest were byte-exact.

## Controlled dependency substitution

The executable runtime still had no byte-preserving bulk mount for the two remaining protocol dependencies:

- `experiments/shared_anchor_intent_ledger/protocol.py` (`68834409363c93eee4e9a9a7b9ec076098af0acf`)
- `experiments/anchor_attestation/protocol.py` (`15d8b7cf8ff093490ccb75679030d3a0fe41e401`)

For this focused run, a minimal local `shared_anchor_intent_ledger.protocol` stub supplied only the exact semantics consumed by the target migration tests: `Intent.payload_digest`, `LedgerEntry`, and `SharedAnchorLedger._request_id`. No external-provider behavior was exercised by these tests. `anchor_attestation.protocol` was therefore not needed by the stubbed import path.

Because these two dependencies were not byte-exact repository files, this run is **not** counted as the complete 8/8 exact closure gate.

## Execution

Filesystem: `/dev/shm` via `TMPDIR=/dev/shm`, because this runtime previously showed SQLite journaling failures on ordinary temporary paths.

`compileall` passed for the exact LAB-095 production files and the three focused target test files.

Executed:

- `test_database_identity_migration_recovery.py`
- `red_intent_lab095_confirmed_finalize_reauthentication.py`
- `red_intent_lab095_locked_custody_payload_tamper.py`

Observed result: **6/6 PASS**.

Covered behaviors:

1. crash before reservation commit rolls back custody schema/intent/tail/nonce effects;
2. orphan CONFIRMED identity intent is rejected before replacement nonce generation;
3. two concurrent installers converge on one nonce/request/PREPARED intent;
4. legacy CONFIRMED tail causes exact next-position reservation without rewriting legacy evidence;
5. post-reauthentication mutation of the authenticated 11-field CONFIRMED tuple fails closed before custody finalization;
6. PREPARED custody nonce tamper is detected under the migration writer lock and no replacement request is generated.

## Audit / decision

No new production defect was observed in this focused execution.

The evidence materially upgrades the previous static-only status, but it is deliberately scoped: six target behaviors passed with byte-exact LAB-095 production/test blobs while two protocol dependencies were substituted with a minimal local semantic stub. Therefore PR #187 remains draft and the complete 8/8 closure plus DB-A -> DB-B and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates remain required.

## Next action

On the next run, probe LAB-086 first. If still blocked, complete the remaining two protocol files through a byte-preserving reconstruction, verify 8/8 manifest hashes, rerun the same six tests without stubs, then proceed to the full DB-A -> DB-B lifetime-binding regression and downstream gates.
