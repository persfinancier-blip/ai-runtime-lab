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

That violates the post-install provenance deletion boundary: a live object could continue durable mutation after the evidence whose absence would make restart fail closed had already disappeared.

This is not a whole-call linearizability requirement and does not depend on a concurrent writer racing a validation window; the marker is deleted before the public mutation call begins.

Regression-first branch commit:

- `60c71feb21a88ddac1530fd102913305f8de890f` — added the execute-after-marker-deletion regression.

First fix:

- `3f183bd539ff8547f5d8bd05b4be2d02b35bf995` — added `_require_complete_activation_schema_provenance()` and guarded provenanced `reserve()`.

Because inherited `execute()` calls `self.reserve(intent)`, ordinary execute/reserve mutation now fails before any new durable intent reservation when marker/DDL provenance is incomplete.

## Finding 2 — provider rotation bypassed reserve guard

The first fix did not cover inherited LAB-090 `rotate_provider()`. That mutation path does not call `reserve()`: it can prepare an external activation ticket, insert a `provider_generation_activations` row, rotate durable provider generation history, durably acknowledge/release the provider fence, and replace runtime attestation.

Therefore the same deterministic post-construction marker deletion left a second reachable mutation path:

1. obtain a legitimately migrated provenanced ledger;
2. delete the confirmed migration marker;
3. call `rotate_provider()` with a valid next generation and activation-capable provider;
4. pre-second-fix LAB-092 has no provenance check on this path, so LAB-090 rotation can proceed despite local provenance already being `DDL_INSTALLED_UNMARKED`.

Again, no concurrent race is required.

Second regression-first branch commit:

- `78f36768ac8d6b3489d4eb7cf3795f31bd7647ea`
- exact test blob `e83515e7b5d1b6886064072ca31d02e026349705`
- adds `test_rotate_provider_fails_closed_after_confirmed_marker_is_deleted` and retains the execute regression.

Second fix/current PR #177 head:

- `9debde700f17ed2d4fe6abe70e45edc2bc7d7a95`
- production blob `experiments/provider_generation_history/activation_schema_provenance.py` = `2f797fcac39d7e65ab4889b405b547b197c1fb35`
- provenanced `rotate_provider()` now invokes the same local COMPLETE-provenance guard before delegating to LAB-090.

The regression requires rotation to fail with `HistoricalVerificationError`, leave durable generation at 1, and leave no activation row for generation 2.

## Migration-path compatibility

The explicit migration confirmation path is unaffected by the subclass mutation guards because it deliberately uses the non-initializing inherited `_reservation_surface`, not `ProvenancedHistoricalSharedAnchorLedger`. Constructor marker authentication likewise uses that confirmation surface before `super().__init__()`.

## Validation status

Exact behavioral RED/GREEN execution was not available in this run because fresh local GitHub transport failed before repository execution with `Could not resolve host: github.com`. Source/branch bytes were re-fetched through the connector, but no behavioral PASS is claimed. PR #177 remains draft.

## Remaining audit boundary

The two known direct durable mutation surfaces are now guarded after post-construction provenance deletion: shared-anchor reservation/execute and provider rotation. Future LAB-092 fallback auditing should inspect other methods only when they can demonstrably write provider receipts, activation status, migration marker state, provider history, or another durable authority surface after provenance becomes incomplete. Do not invent a whole-call linearizability contract without a concrete mutation-before-validation path.
