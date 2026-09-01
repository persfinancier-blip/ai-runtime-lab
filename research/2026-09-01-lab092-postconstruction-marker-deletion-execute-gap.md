# LAB-092 post-construction provenance-marker deletion / mutation gaps

Date: 2026-09-01

## Question

Can a live `ProvenancedHistoricalSharedAnchorLedger` continue to make durable mutations after the already-confirmed LAB-092 migration provenance marker is deleted post-construction?

## Finding 1 — shared-anchor execute/reserve

Yes. The pre-fix LAB-092 class validated provenance during construction and in `verify_activation_schema_provenance()`, but inherited `SharedAnchorLedger.execute()` dynamically called inherited `reserve()` without re-checking LAB-092 provenance. Therefore this deterministic sequence was reachable without any timing assumption:

1. perform a legitimate explicit LAB-092 migration and obtain a live provenanced ledger;
2. delete the confirmed migration marker row from `shared_anchor_intents`;
3. local `_classify()` is now `DDL_INSTALLED_UNMARKED`;
4. call `ledger.execute()` for a new ordinary intent;
5. pre-fix `reserve()` can append a new PREPARED row and advance `shared_anchor_meta.reserved_position`, after which `execute()` can advance/reconcile the external anchor and confirm the new row.

This is not a whole-call linearizability requirement; marker deletion happens before the mutation call begins.

Regression-first commit `60c71feb21a88ddac1530fd102913305f8de890f` added the execute-after-marker-deletion regression. Fix `3f183bd539ff8547f5d8bd05b4be2d02b35bf995` added `_require_complete_activation_schema_provenance()` and guarded provenanced `reserve()`. Because inherited `execute()` calls `self.reserve(intent)`, execute/reserve now fails before new durable reservation when provenance is incomplete.

## Finding 2 — provider rotation bypassed reserve guard

Inherited LAB-090 `rotate_provider()` does not call `reserve()`. With the marker already deleted, it could still prepare an external activation ticket, insert a `provider_generation_activations` row, rotate durable provider history, durably acknowledge/release the provider fence, and replace runtime attestation.

Regression-first commit `78f36768ac8d6b3489d4eb7cf3795f31bd7647ea` added a valid generation-2 rotation case requiring failure after marker deletion. Fix `9debde700f17ed2d4fe6abe70e45edc2bc7d7a95` guarded provenanced `rotate_provider()` with the same COMPLETE-provenance check.

## Finding 3 — component watermark mutation also bypassed reserve guard

Inherited `verify_component()` is read-mostly but can durably advance `component_anchor_watermarks`. A concrete no-race sequence exists:

1. migrate successfully; migration marker occupies position 1;
2. call `verify_component(component-A)` while provenance is intact, advancing component-A watermark to 1;
3. execute and confirm an ordinary position-2 intent while provenance is intact;
4. delete the migration marker at position 1;
5. call `verify_component(component-A)` again.

Because the local watermark already starts at 1, inherited verification reads only position 2, sees a contiguous one-row suffix, and can advance the durable watermark to 2 without revisiting the now-missing provenance row at position 1. Thus marker deletion does not automatically force an `IntentGap` on this path.

Regression-first commit:

- `dd17e19c227e29b3262b031d0a1676a7a305fa8f`
- exact current test blob `4f1409672786ba23e1c258075f03f3c98dbcba9d`
- test requires `HistoricalVerificationError` and watermark to remain at 1 after marker deletion.

Fix/current PR #177 head:

- `ba71515f99060216d7c4698d5566bbc7be207e54`
- production blob `experiments/provider_generation_history/activation_schema_provenance.py` = `62a35b0fbbbb1c26d155df65d71e2009e01235aa`
- provenanced `verify_component()` now invokes the same local COMPLETE-provenance guard before inherited verification/watermark mutation.

## Current guarded public mutation surfaces

The provenanced class now performs the local COMPLETE check before:

- `reserve()` (therefore inherited `execute()` reservation/confirmation paths);
- `rotate_provider()` (provider activation/history mutation);
- `verify_component()` (component watermark mutation).

Explicit migration confirmation and constructor marker authentication remain on the deliberately non-initializing inherited `_reservation_surface`, so the new subclass guards do not block migration confirmation.

## Validation status

Exact behavioral RED/GREEN execution was not available in this run because fresh local GitHub transport failed before repository execution with `Could not resolve host: github.com`. Branch/source blobs were re-fetched through the connector, but no behavioral PASS is claimed. PR #177 remains draft.

At the final PR metadata read in this run GitHub reported `mergeable=false`; no integration action was attempted and this signal must be re-checked because exact execution/base reconciliation is still pending.

## Remaining audit boundary

Future LAB-092 fallback auditing should enumerate remaining public/reachable methods and only add further guards when a method can demonstrably write provider receipts, activation status, migration marker state, provider history, watermarks, or another durable authority surface after provenance becomes incomplete. Do not invent a whole-call linearizability contract without a concrete mutation-before-validation path.
