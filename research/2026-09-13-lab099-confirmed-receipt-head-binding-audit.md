# LAB-099 confirmed receipt/head binding audit

Date: 2026-09-13

## Scope

Follow-up to issue #184 and draft PR #186. This slice audited the already-frozen LAB-099 CONFIRMED vector against the existing shared-anchor confirmation/re-authentication semantics on the pinned LAB-092 base. No production LAB-099 behavior was changed and no repository RED/GREEN claim is made.

## Existing authority that must be reused

`experiments/shared_anchor_intent_ledger/protocol.py` already defines the durable CONFIRMED semantics:

- a PREPARED row has `receipt_binding IS NULL`;
- a CONFIRMED row must carry a 64-hex receipt binding;
- `_reauthenticate()` obtains a fresh challenge, calls provider `reconcile_increment(request_id=entry.request_id)`, verifies an exact RECONCILE observation, requires the same `position` and `request_id`, then derives the stable receipt as SHA-256 over provider id, generation, position and request id;
- `execute()` refuses to accept a previously CONFIRMED row unless that receipt reauthenticates identically;
- `verify_component()` repeats the same receipt reauthentication before advancing the durable component watermark.

Decision: LAB-099 must reuse this receipt authority. It must not add a second signature/MAC/receipt mechanism for cutover confirmation.

## New test-owned verifier

Draft PR #186 now contains `experiments/provider_generation_history/tests/lab099_confirmed_fixture_row_verifier.py`.

The verifier is intentionally test-only. It:

1. resolves exactly one cutover materialization by the externally expected PREPARED digest;
2. resolves exactly one matching shared-anchor row;
3. requires status `CONFIRMED` and a well-formed receipt binding;
4. converts only the status/receipt projection back to PREPARED shape and reuses the already-published exact PREPARED cross-binding oracle, so CONFIRMED cannot silently rebind its ancestry;
5. requires an externally supplied confirmed position rather than trusting the mutable recovery row as its own authority;
6. performs the existing provider RECONCILE reauthentication and requires the stable receipt to equal the stored receipt binding;
7. requires the confirmed shared-anchor entry digest to equal an externally supplied expected confirmed-head digest.

The module also exposes narrow test-only mutations for receipt binding, position/predecessor and PREPARED digest ancestry. These are fixture hooks only.

## Important audit finding: exact frozen CONFIRMED vector is not yet mechanically connected to a concrete confirmed ledger entry

The frozen `lab099_precursor_reference_vectors.py` CONFIRMED event contains `RESULTING_PROVENANCE_HEAD_DIGEST = c0..df` and epoch `8` as independent reference values. Separately, `lab099_cutover_storage_reference.confirmed_head_digest(entry)` deterministically hashes an exact CONFIRMED shared-anchor ledger entry, including `receipt_binding`.

However, no frozen reference CONFIRMED ledger entry / receipt-binding vector currently exists whose `confirmed_head_digest(entry)` is proven to equal the frozen `RESULTING_PROVENANCE_HEAD_DIGEST`, and `lab099_precursor_fixture_vectors.py` currently implements only PREPARED installation; the adapter's `install_confirmed_event()` is intentionally still unavailable because `confirmed_event_plan()` does not yet exist.

Therefore it would be fabricated evidence to claim that the existing fixed CONFIRMED canonical bytes already bind a mechanically reproducible shared-anchor CONFIRMED row. The test-owned verifier can validate a real confirmed row against externally supplied head authority, but the reference-vector bridge still has to be frozen before a CONFIRMED fixture RED case can honestly execute.

## Decision

Freeze the next boundary as `LAB099_CONFIRMED_LEDGER_REFERENCE_BRIDGE_REQUIRED_V1`:

- choose one exact reference shared-anchor CONFIRMED entry, including a real stable `receipt_binding` vector derived under the existing RECONCILE receipt formula;
- freeze its exact `confirmed_head_digest(entry)`;
- either update the LAB-099 CONFIRMED reference event so field 7 equals that digest, or explicitly freeze a separate deterministic provenance-head transform if field 7 is not intended to be the shared-anchor confirmed-entry digest;
- freeze the epoch mapping independently;
- only then implement `confirmed_event_plan()` and the non-discoverable persisted CONFIRMED tamper RED-intent cases.

Do not guess a receipt, head digest or epoch mapping merely to make the fixture executable.

## Validation actually observed in this run

- direct `git clone --no-checkout` again failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector source inspection and Contents API writes succeeded;
- PR #186 remains draft and test-only;
- topology after the new verifier: ahead 19 / behind 0 relative to pinned PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`;
- no local import, py_compile, repository test, RED or GREEN execution is claimed for the new verifier because an exact connector-to-local materialization path is still unavailable.
