# LAB-086 — stale public-custody writer fence

## Problem

After the authenticated LAB-086 cutoff, the underlying LAB-085 `AsymmetricRecoveryCustody.rotate()` API could still create a new public recovery authority using only old-public + new-public Ed25519 quorum. LAB-086 requires an additional current normal/root quorum. The later LAB-086 verifier detected the missing root proof, but only after the stale writer had already committed authority/transition/head state, turning a rejected authority change into persistent fail-closed DoS.

A later audit found the same class of bypass one layer higher: `suffix.SupportedAsymmetricBreakGlassLedger` was still directly constructible and its `rotate_public_recovery_authority()` implementation was mutation-first. Fencing only `final_supported.SupportedFencedAsymmetricBreakGlassLedger` therefore protected callers that chose the final wrapper but did not make the authenticated cutoff itself authoritative.

## Correction

The proof-first public recovery fence is now installed by `AuthenticatedBreakGlassMigrationGuard._ensure_schema_locked()`, so the SQLite boundary exists independently of which Python surface a stale caller still holds.

It creates the exact root-proof table and installs cutoff-conditional triggers on:

- `provider_recovery_public_authorities` insert/update;
- `provider_recovery_public_transitions` insert/update;
- `provider_recovery_public_head` update.

Before the authenticated cutoff these triggers are dormant. After the boundary row exists, mutations are accepted only when `provider_asymmetric_recovery_public_root_proofs` already contains an exact proof binding:

- the proposed new public authority;
- the currently active old public authority;
- the currently active normal/root authority ID, version and generation.

This means both stale LAB-085 custody writers and the directly constructible mutation-first LAB-086 suffix surface are rejected before durable public authority state changes.

The legitimate final path remains `experiments/asymmetric_break_glass_history/final_supported.py`. Its supported rotation ordering is, inside one `BEGIN IMMEDIATE` transaction:

1. re-verify migration boundary and reject pending work;
2. validate old-public and new-public Ed25519 thresholds;
3. validate the current normal/root threshold;
4. insert/check the exact root-proof row;
5. call the existing LAB-085 `rotate_locked()` primitive;
6. re-verify public-recovery history;
7. commit.

Any failure rolls back proof + authority + transition + head together. Because the migration guard and final wrapper use the same idempotent trigger/table names and predicates, wrapper installation is now defense-in-depth rather than the sole authority fence.

## Executed focused SQLite evidence

The exact updated `_ensure_schema_locked()` method was extracted from the modified branch source and executed against a deterministic SQLite schema.

Observed mutation-first path:

- transaction began with authenticated boundary present, public head `old`, root head `root@7`;
- writer attempted to insert successor public authority `new` without a root proof;
- SQLite raised `IntegrityError: LAB-086 public recovery successor requires current-root proof first`;
- rollback left public head/state unchanged.

Observed proof-first path:

- inserted exact proof `new <- old`, root `root@7` first;
- inserted successor authority;
- inserted `new <- old` public transition;
- updated public head to `new@2`;
- commit succeeded with exactly one proof row.

Post-cutoff UPDATE attempts against public authority and transition rows were also rejected by the immutability triggers.

This is actual evidence for the SQL serialization/fencing shape, not a substitute for the repository-wide exact-source regression gate.

## Regression surfaces

`tests/test_stale_public_writer_regression.py` checks:

- direct stale LAB-085 custody rotation after cutoff commits zero authority/transition/head/root-proof changes;
- the final supported rotation commits the exact root proof and successor and survives durable verification.

`tests/test_unfenced_supported_surface_regression.py` now checks the independently discovered direct-suffix bypass. It constructs `SupportedAsymmetricBreakGlassLedger` directly, migrates, attempts its older mutation-first public rotation, and requires both an exception and no change to public head, authority count, transition count or root-proof count.

The one legacy suffix test that intentionally exercises a successful post-cutoff public recovery rotation now routes that consequential operation through `SupportedFencedAsymmetricBreakGlassLedger.from_existing()`.

## Boundary / remaining gate

The database fence is now part of the migration authority boundary, not merely a convention of one wrapper. Arbitrary SQL writers that can manufacture a proof row remain outside this stale-library-API prevention claim; durable cryptographic verification is still responsible for rejecting forged/substituted proof contents.

Full current-head LAB-086 plus LAB-085/084/083/082/080 exact-source regressions, unsafe seed, compileall and a fresh complete patch audit remain mandatory before merge/DONE.
