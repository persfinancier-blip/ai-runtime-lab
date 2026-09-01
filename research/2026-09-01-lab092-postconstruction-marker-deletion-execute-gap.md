# LAB-092 post-construction provenance-marker deletion / execute gap

Date: 2026-09-01

## Question

Can a live `ProvenancedHistoricalSharedAnchorLedger` continue to make durable shared-anchor mutations after the already-confirmed LAB-092 migration provenance marker is deleted post-construction?

## Finding

Yes. The pre-fix LAB-092 class validated provenance during construction and in `verify_activation_schema_provenance()`, but inherited `SharedAnchorLedger.execute()` dynamically called inherited `reserve()` without re-checking LAB-092 provenance. Therefore this deterministic sequence was reachable without any timing assumption:

1. perform a legitimate explicit LAB-092 migration and obtain a live provenanced ledger;
2. delete the confirmed migration marker row from `shared_anchor_intents`;
3. local `_classify()` is now `DDL_INSTALLED_UNMARKED`;
4. call `ledger.execute()` for a new ordinary intent;
5. pre-fix `reserve()` can append a new PREPARED row and advance `shared_anchor_meta.reserved_position`, after which `execute()` can advance/reconcile the external anchor and confirm the new row.

That violates the post-install provenance deletion boundary: a live object could continue durable mutation after the evidence whose absence would make restart fail closed had already disappeared.

This is not a whole-call linearizability requirement and does not depend on a concurrent writer racing a validation window; the marker is deleted before the public mutation call begins.

## Regression-first change

Regression commit on `lab-092-activation-schema-provenance`:

- `60c71feb21a88ddac1530fd102913305f8de890f`
- new test `experiments/provider_generation_history/tests/test_activation_schema_postconstruction_marker_deletion.py`
- exact published test blob `f2757e7de37f4d1402fb4b1da0e7c33513b4c432`

The regression requires `ledger.execute()` to raise `HistoricalVerificationError` after marker deletion and verifies that the requested new intent row was not inserted.

Exact behavioral RED execution was not available in this run because local GitHub transport failed before repository execution (`Could not resolve host: github.com`). The RED claim is therefore source-level/deterministic reasoning only, not reported as an executed test result.

## Fix

Fix commit on the same branch:

- `3f183bd539ff8547f5d8bd05b4be2d02b35bf995`
- production blob `experiments/provider_generation_history/activation_schema_provenance.py` = `df99fa6bd9c0d9952008c4671f1f233ed1baaadd`

The provenanced class now has a local fail-closed guard:

- `_require_complete_activation_schema_provenance()` requires `_classify(self.path) == "COMPLETE"`;
- overridden `reserve()` invokes that guard before delegating to LAB-090/LAB-080 reservation logic.

Because inherited `execute()` calls `self.reserve(intent)`, ordinary execute/reserve mutation now fails before any new durable intent reservation when the marker or exact activation DDL provenance is missing/mismatched.

The explicit migration confirmation path is unaffected because it deliberately uses the non-initializing inherited `_reservation_surface`, not the provenanced subclass override. Constructor marker authentication also uses that confirmation surface before `super().__init__()`.

## Audit / remaining boundary

This fix is intentionally scoped to shared-anchor reservation/execute mutation. `rotate_provider()` is a separate LAB-090 mutation path that does not call `reserve()` and must be audited separately for the same post-construction marker-deletion condition before claiming the live-object provenance boundary is complete.

No exact branch behavioral/full-suite PASS is claimed. PR #177 remains draft.
