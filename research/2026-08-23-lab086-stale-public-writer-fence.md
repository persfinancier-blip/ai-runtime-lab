# LAB-086 — stale public-custody writer fence

## Problem

After the authenticated LAB-086 cutoff, the underlying LAB-085 `AsymmetricRecoveryCustody.rotate()` API could still create a new public recovery authority using only old-public + new-public Ed25519 quorum. LAB-086 requires an additional current normal/root quorum. The later LAB-086 verifier detected the missing root proof, but only after the stale writer had already committed authority/transition/head state, turning a rejected authority change into persistent fail-closed DoS.

## Correction

The branch now has `experiments/asymmetric_break_glass_history/final_supported.py` as the final fenced LAB-086 surface.

It installs cutoff-conditional SQLite triggers on:

- `provider_recovery_public_authorities` insert/update;
- `provider_recovery_public_transitions` insert/update;
- `provider_recovery_public_head` update.

After the cutoff, those mutations are accepted only when `provider_asymmetric_recovery_public_root_proofs` already contains an exact proof binding:

- the proposed new public authority;
- the currently active old public authority;
- the currently active normal/root authority ID, version and generation.

The supported rotation path is intentionally reordered inside one `BEGIN IMMEDIATE` transaction:

1. re-verify the migration boundary and reject pending work;
2. validate old-public and new-public Ed25519 thresholds;
3. validate the current normal/root threshold;
4. insert/check the exact root-proof row;
5. call the existing LAB-085 `rotate_locked()` primitive;
6. re-verify public-recovery history;
7. commit.

Any failure rolls back proof + authority + transition + head together.

## Executed deterministic SQLite probe

A local SQLite probe using the same trigger predicates was actually executed in this run.

Observed stale-writer path:

- transaction began with boundary present, public head `old`, root head `root@7`;
- stale writer attempted `INSERT provider_recovery_public_authorities('new')` without a root proof;
- SQLite raised `IntegrityError: proof first`;
- rollback left public head `old` and authority count `1`.

Observed supported path:

- inserted exact proof `new <- old`, root `root@7` first;
- inserted successor authority;
- inserted `new <- old` public transition;
- updated public head to `new@2`;
- commit succeeded with exactly one proof row.

This is evidence for the SQL serialization/fencing shape, not a substitute for the repository-wide exact-source regression gate.

## New regression surface

`tests/test_stale_public_writer_regression.py` now uses the final fenced surface and checks both:

- direct stale LAB-085 custody rotation after cutoff commits zero authority/transition/head/root-proof changes;
- the final supported rotation commits the exact root proof and successor and survives durable verification.

## Boundary / remaining gate

The original `suffix.SupportedAsymmetricBreakGlassLedger` remains the underlying implementation primitive; the new `final_supported.SupportedFencedAsymmetricBreakGlassLedger` is the final LAB-086 supported authority boundary. Callers that deliberately bypass the final surface and also have arbitrary SQL write access are outside this stale-API threat model; durable history verification still detects proof corruption/substitution.

Full LAB-086 plus LAB-085/084/083/082/080 exact-source regressions, unsafe seed, compileall and a fresh complete patch audit remain mandatory before merge/DONE.
