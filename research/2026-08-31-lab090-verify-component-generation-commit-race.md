# LAB-090 — `verify_component` generation commit-boundary race

Date: 2026-08-31

## Scope

Audit target from `state/CURRENT.md`: determine whether provider generation can change after `verify_component()` authenticates the current provider but before the component watermark is durably advanced.

## Source finding

On PR #175 head lineage, inherited LAB-080 `SharedAnchorLedger.verify_component()` does the following:

1. authenticated external read through `self.attested`;
2. checks `(observed.provider_id, observed.generation)` against `self._provider()`;
3. verifies the ledger slice / historical receipt bindings;
4. opens `BEGIN IMMEDIATE`;
5. re-reads the exact ledger slice and existing component watermark;
6. advances `component_anchor_watermarks`.

LAB-090's `_provider()` now rejects a runtime provider that is already stale relative to the durable provider-generation head. That closes the stable stale-runtime case, but the check occurs before the final watermark transaction.

`rotate_provider()` also commits provider-generation history/head under `BEGIN IMMEDIATE`. Therefore this schedule remains possible:

- G1 is durable current and runtime current;
- `verify_component()` authenticates a G1 read and passes `_provider()`;
- before the final watermark `BEGIN IMMEDIATE`, another actor completes G1 -> G2 rotation;
- verification continues using the already-authenticated G1 evidence / immutable historical receipt binding;
- the final watermark transaction re-checks ledger rows but does not re-check provider-generation head;
- stale-generation evidence can durably advance the component watermark after G2 became current.

This is a linearizability/correctness defect in the current-generation freshness claim. It is not an authority escalation: the G1 evidence remains authenticated and the ledger rows remain immutable/confirmed. The problem is that a watermark committed after the generation cutover can be justified by a read that is no longer from the durable current generation.

## Regression published

PR #175 commit `27b059fb1da8cd7f790daaa3e5603f0172c427c4` adds:

`experiments/provider_generation_history/tests/test_activation_verify_component_rotation_race.py`

The test uses a narrow deterministic subclass that performs G1 -> G2 rotation after one ledger entry has been reauthenticated but before the inherited final watermark transaction. Required behavior:

- `verify_component("component-A")` raises `CurrentGenerationRequired`;
- durable provider head is G2;
- component watermark remains 0 (no stale-generation DML).

Published test blob: `359288e32e7df0ffd60bd359e326398b0bec276a`.

The exact published bytes were independently reconstructed and Git-blob hashed to the same SHA. `py_compile` PASS. Behavioral unittest PASS is not claimed because the production guard is not yet published; the regression is intentionally a RED candidate against the current implementation.

## Minimal fix design

The safe fix must validate the observed generation **inside the same `BEGIN IMMEDIATE` transaction that may write the watermark, before any watermark DML**. A post-write check is insufficient.

Preferred minimal structure:

1. add a no-op commit-boundary verification hook in LAB-080 `SharedAnchorLedger.verify_component(q, observed)` immediately after `BEGIN IMMEDIATE` and before row/watermark mutation checks;
2. override that hook in the provider-history integration layer to use the same SQLite connection `q` and `IntegratedProviderHistory._current_locked(q)`;
3. require `(observed.provider_id, observed.generation)` to equal the durable current descriptor in that locked transaction, otherwise raise `CurrentGenerationRequired`;
4. only then continue the existing exact-row and watermark CAS checks.

Because rotation uses the same SQLite write serialization boundary, either rotation commits first and the stale verification aborts before DML, or verification acquires the lock first and its watermark commit linearizes before the later rotation. This closes the window without process-local locks and works across processes.

## Tool / publication constraint

The GitHub connector exposes normal Contents API writes but only complete-file replacement, not a server-side patch operation. The two production files involved are nontrivial shared protocol files; this run did not model-reserialize them merely to add a few lines. The regression is safely published as a new file. Production mutation should be applied when an exact byte-preserving patch/composition path is available, or after reconstructing and independently verifying the complete replacement bytes and exact diff.

## Current decision

Keep PR #175 draft. The race is now reproduced at source/schedule level with an exact-byte regression candidate. Next action is to publish the commit-boundary generation guard through a byte-exact path, then run this regression plus the activation integration/restart/downstream gate.
