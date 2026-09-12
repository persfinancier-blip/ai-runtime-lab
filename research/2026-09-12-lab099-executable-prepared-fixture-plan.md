# LAB-099 executable PREPARED fixture plan

Date: 2026-09-12
Status: test-owned fixture slice published; repository RED/GREEN still unexecuted
Related: #184, PR #186, PR #177

## Result

PR #186 now contains an executable test-only `atomic_prepared_plan()` path for the already-frozen LAB-099 precursor cutover contract.

No production LAB-099 behavior was added.

## Capability observation

LAB-086 was probed first as required. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with:

`Could not resolve host: github.com`

Exit status: 128.

The GitHub connector remained available for audited source reads and Contents API writes, but this run still exposed no byte-exact whole-repository materialization primitive suitable for the pending LAB-086 execution gate. Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security, or conflict PASS is claimed.

## Published test-owned changes

Branch: `lab-099-precursor-cutover-red-intent`

Current PR #186 head after this slice:

`3ce932e1e20813644b14c0916b5802e5f96cfa85`

New file:

`experiments/provider_generation_history/tests/lab099_precursor_fixture_vectors.py`

Published blob:

`8ca5f2fb508500758a5129d75a29c2406169b361`

The module composes only already-frozen test/reference authorities:

- precursor literal V1 DDL;
- cutover materialization literal V1 DDL;
- byte-exact PREPARED canonical bytes/digest;
- confirmation nonce;
- deterministic shared-anchor intent identity and payload digest;
- existing shared-anchor request-id semantics.

It does not import production LAB-099 code and performs no external provider call.

The existing fixture adapter was updated so `SqlMutation` may carry an `expected_rowcount`. `_apply_plan()` now checks that rowcount inside the same `BEGIN IMMEDIATE` transaction and rolls back the entire fixture transaction on mismatch.

Updated adapter blob:

`671ace9ed879a0a1d0c06786b11d2e46fb746de3`

## Atomic PREPARED plan

The plan mechanically performs:

1. exact precursor relation DDL;
2. exact cutover materialization DDL;
3. exact `provider_activation_reservation_cutovers` row containing the frozen PREPARED bytes/digest, confirmation nonce and deterministic anchor intent ID;
4. exact matching shared-anchor PREPARED insertion;
5. exact `shared_anchor_meta.reserved_position` compare-and-swap.

The PREPARED digest remains:

`77ffdf5f657510a285d75e866d3418a85d1aeb0ca0f2c830617c850a5277b53e`

The deterministic anchor payload digest remains:

`8aee140ac30142fac83fe03f95f36e56be94583b4ef100060610bb9ec59089e9`

## Audit finding and fix

The first authored version protected the shared-anchor tail with CAS but used provider/generation values obtained during preflight directly in a later `INSERT VALUES`.

That left a race: provider-generation head could change after preflight but before the fixture transaction while the shared-anchor tail remained unchanged.

The published version fixes this without adding a new subsystem. The shared-anchor PREPARED row is inserted with `INSERT ... SELECT` from the current `provider_generation_head` joined to `provider_generations`, constrained to the preflight provider/generation, and the adapter requires rowcount exactly 1.

Therefore two independent stale-snapshot axes now fail closed inside the fixture transaction:

- provider-generation head mismatch => PREPARED insert rowcount 0 => rollback;
- shared-anchor predecessor mismatch => meta CAS rowcount 0 => rollback.

Any DDL/materialization/anchor row inserted earlier in that transaction is rolled back with the mismatch.

## Validation actually executed

Because exact repository materialization is still unavailable, these are scratch/mechanical validations, not repository RED/GREEN evidence.

Executed locally:

- initial authored fixture-vector module: `py_compile` PASS;
- initial static fixture-vector self-check: PASS;
- semantically equivalent SQLite success path: materialization row inserted, PREPARED shared-anchor row inserted at predecessor 1 / position 2, and reserved position advanced to 2;
- stale shared-anchor CAS simulation: expected rowcount mismatch observed and the transaction rolled back; precursor DDL, cutover DDL and PREPARED row were absent afterward;
- stale provider-generation-head simulation: `INSERT ... SELECT` returned rowcount 0 and no PREPARED row survived rollback.

No claim is made that the final published PR closure, `red_intent_lab099_precursor_cutover.py`, or any production LAB-099 module was executed in this run.

## PR topology

Compared with pinned PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`:

- ahead: 14;
- behind: 0;
- changed files: 8;
- all changed files remain under `experiments/provider_generation_history/tests/`.

PR #186 remains open, draft, and mergeable. It must remain draft until exact repository materialization is available and the RED-intent scenarios are actually observed RED before any production LAB-099 implementation is introduced.

## Next action

After the mandatory LAB-086 materialization probe, if exact execution is still unavailable, continue only test-owned PR #186 work.

The next smallest safe slice is to audit and implement the PREPARED recovery-side fixture assertions without inventing production behavior: add a side-effect-free verifier for the exact materialization row + shared-anchor PREPARED cross-binding and use it to make the crash-after-commit fixture self-check mechanically prove that only the exact frozen PREPARED digest/nonce/anchor row is resumable. Do not implement production `activation_reservation_provenance` until an executable repository RED has actually been observed.
