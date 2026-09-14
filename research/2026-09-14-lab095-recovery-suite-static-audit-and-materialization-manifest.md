# LAB-095 recovery/tamper suite static audit and exact materialization manifest

Date: 2026-09-14

## Context

LAB-086 remained the mandatory first probe. Direct Git materialization from the executable runtime failed before repository execution with:

`Could not resolve host: github.com` (exit 128)

No LAB-086 gate was weakened and no new LAB-086 PASS is claimed.

The permitted fallback was therefore the next LAB-095 gate recorded in `state/CURRENT.md`: confirmed-finalize / locked-custody tamper plus migration recovery.

## Static audit performed

The current LAB-095 PR branch `lab-095-database-identity-red-intent` was inspected directly through the GitHub control plane.

Recovery test `test_database_identity_migration_recovery.py` covers four retained recovery properties:

1. crash before the reservation commit rolls back custody DDL, identity intent, reserved tail and generated nonce state;
2. an orphan CONFIRMED identity intent is rejected as corrupt before any new nonce can be generated;
3. two concurrent installers converge on one nonce/request and one PREPARED intent;
4. a pre-existing legacy CONFIRMED anchor tail causes the identity reservation to use exactly the next shared-anchor position without rewriting the legacy entry.

The confirmed-finalize regression `red_intent_lab095_confirmed_finalize_reauthentication.py` models the post-external-reauthentication / pre-local-finalize race and requires exact comparison of the authenticated 11-field ledger snapshot under the final SQLite writer lock. The implementation in `database_identity_migration._finalize_confirmed()` performs this comparison before mutating custody.

The locked classifier in `database_identity_migration._classify_locked()` recomputes the canonical LAB-095 payload digest from `nonce_hex + bootstrap_generation_id` and rejects mismatches before PREPARED/CONFIRMED classification. This retains the previously added nonce/bootstrap tamper fail-closed property.

No new production defect was identified by this static pass. This is not a behavioral PASS: the retained tests still need byte-exact execution.

## Exact files already identified for the focused closure

The following branch blobs are authoritative inputs for the next executable reconstruction:

- `experiments/provider_generation_history/database_identity.py` — `bac58a48c576001370144cc10cfab8e0cfd129e3`
- `experiments/provider_generation_history/database_identity_migration.py` — `c4d1db46b8b64fec116dcfef8bb05e1e7a7b875e`
- `experiments/provider_generation_history/tests/test_database_identity_migration.py` — `cde9d16c5fb257a8b9ad7110f9badb79bede8f3f`
- `experiments/provider_generation_history/tests/test_database_identity_migration_recovery.py` — `363ab95f1aad425fc89f146ae8fba35d9169950d`
- `experiments/provider_generation_history/tests/red_intent_lab095_confirmed_finalize_reauthentication.py` — `7dcd20dfd24a9439583595bf433f9f696bd870e7`
- `experiments/provider_generation_history/tests/red_intent_lab095_locked_custody_payload_tamper.py` — `443e84f65e1d7f58c9b0ae284d700d4ec0f77cc6`
- `experiments/shared_anchor_intent_ledger/protocol.py` — `68834409363c93eee4e9a9a7b9ec076098af0acf`
- `experiments/anchor_attestation/protocol.py` — `15d8b7cf8ff093490ccb75679030d3a0fe41e401`

The first eight-file reconstruction target is intentionally narrow: it is sufficient to remove ambiguity around the immediate recovery/tamper gate before expanding to DB-A -> DB-B and downstream LAB-080/081/090/092 gates. Every reconstructed file must be checked with `git hash-object` against the blob above before execution. SQLite tests must continue to use `TMPDIR=/dev/shm` in this runtime because that filesystem is the observed journal-capable path.

## Decision

Keep PR #187 draft. The next run should again probe LAB-086 first. If direct materialization remains blocked, reconstruct the eight-file LAB-095 closure above through connector exact content, verify all 8/8 blob hashes, run `compileall`, then execute:

- `test_database_identity_migration_recovery.py`
- `red_intent_lab095_confirmed_finalize_reauthentication.py`
- `red_intent_lab095_locked_custody_payload_tamper.py`

Only observed executions count as GREEN. After that, proceed to the DB-A -> DB-B lifetime-binding regression and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates.
