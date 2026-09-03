# LAB-092 post-construction provenance check is TOCTOU

Date: 2026-09-03

## Scope

Source audit of draft PR #177 (`experiments/provider_generation_history/activation_schema_provenance.py`) against inherited `SharedAnchorLedger.execute()` / `verify_component()` behavior.

This note does not claim exact branch execution. It records a source-proved race that should be turned into a deterministic regression when exact source execution is available.

## Finding

`ProvenancedHistoricalSharedAnchorLedger` checks `_classify(self.path) == "COMPLETE"` at the entry to `reserve()`, `rotate_provider()`, and `verify_component()`. That protects simple post-construction marker deletion before those methods begin.

However, the provenance condition is not held or revalidated at the later mutation/authority boundaries of the inherited multi-step operations.

For `execute(intent)` the inherited sequence is:

1. `entry = self.reserve(intent)` — LAB-092 provenance is checked here;
2. external `attested.catch_up_one(...)` may advance the monotonic provider;
3. `_reauthenticate(entry)` obtains provider evidence;
4. a new `BEGIN IMMEDIATE` transaction confirms the SQLite intent row.

A concurrent actor that deletes the confirmed migration marker after step 1 but before step 2/4 can therefore invalidate activation-schema provenance after the only check has passed. The same `execute()` invocation can still advance the external anchor and then durably mark its intent CONFIRMED while `_classify(path)` would now be `DDL_INSTALLED_UNMARKED` rather than `COMPLETE`.

The existing post-construction deletion test covers deletion before `execute()` starts; it does not close this check/use window.

The same structural class exists in `verify_component()`: LAB-092 checks provenance only before the inherited external read/history verification; the later watermark write transaction does not re-check the marker/DDL provenance at the commit boundary. `rotate_provider()` similarly checks before provider prepare and the later SQL/provider-commit sequence.

## Why this matters

LAB-092 treats the authenticated migration completion marker as the evidence that LAB-090 activation DDL is an installed, provenance-bound authority surface. If a supported operation may cross from COMPLETE to non-COMPLETE after its initial check yet still perform external or durable authority changes, post-install deletion is not fail-closed for already-running operations.

SQLite `BEGIN IMMEDIATE` in the later operation does not serialize the earlier standalone `_classify()` read with a concurrent deletion that happens between those phases.

## Regression-first contract

Add deterministic interleaving tests, starting with `execute()`:

1. construct a valid migrated LAB-092 ledger;
2. start a non-migration `execute(intent)`;
3. pause immediately after the LAB-092 provenance check / successful `reserve()` and before `catch_up_one()`;
4. from a second connection delete the confirmed migration completion marker (or delete/mismatch one activation DDL object where the race is feasible);
5. resume the operation;
6. pre-fix: demonstrate the external anchor and/or intent confirmation can still advance after provenance became non-COMPLETE;
7. post-fix: fail closed before any further external or durable authority mutation, or prove the provenance evidence is locked/bound across the full operation so the invalidation cannot interleave.

Also cover `verify_component()` before watermark commit and `rotate_provider()` before provider/SQL activation mutation.

## Design constraint

Do not merely add another unsynchronized `_classify()` call immediately before each mutation; that creates another check/use window. The fix must bind provenance to the same serialization/authority boundary as the consequential mutation, or use an authenticated/versioned invariant that the mutation transaction can verify atomically. External provider changes that occur before the final SQLite transaction need an explicit recovery/ownership contract if provenance can be invalidated concurrently.

This strengthens LAB-092/#176 and should not create a duplicate issue.