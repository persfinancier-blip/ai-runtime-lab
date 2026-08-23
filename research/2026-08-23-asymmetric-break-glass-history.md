# LAB-086 — asymmetric historical break-glass proof migration

## Current result

LAB-086 has both sides of the migration boundary on the real LAB-084/LAB-085 SQLite authority, but the latest audit shows that one more migration step is required before the phrase **public-only historical recovery** is accurate.

The authenticated cutoff is now a v2 boundary. Immediately before signing it, the implementation runs the complete pre-migration LAB-085 verifier. It then commits a canonical semantic projection of the legacy recovery edges and their public-custody evidence **without including the HMAC proof bytes**. Boundary insertion and replacement of the legacy `provider_rotation_recovery_transitions.signatures_json` values with canonical `[]` occur in the same `BEGIN IMMEDIATE` transaction.

Post-cutoff verification therefore no longer calls the LAB-084 HMAC verifier for those legacy root edges. It requires the proof bytes to remain scrubbed, checks the exact legacy semantic projection against the threshold-signed cutoff, and continues to verify Ed25519 public-custody evidence. A persistent SQL trigger prevents any new legacy HMAC break-glass row from being inserted after cutoff.

A new mixed-history regression creates a real LAB-085 compatibility recovery, migrates/scrubs it, reopens through the LAB-086 surface, adds an Ed25519-only break-glass successor and checks restart convergence.

## Why MAC scrubbing alone is not the finish line

A fresh authority audit found a deeper residual dependency. LAB-084/LAB-085 still persist symmetric recovery key maps in:

- `provider_rotation_recovery_authorities.keys_json`;
- `provider_recovery_lifecycle_authorities.keys_json`.

The current LAB-085 lifecycle/window helpers reconstruct those authorities and HMAC-verify lifecycle transitions. Those keys are actual symmetric signing material; merely deleting old MAC signature strings does not make historical verification public-only.

Therefore LAB-086 remains IN_PROGRESS. The next supported post-cutoff surface must derive historical recovery identity/activation windows from an authenticated cutoff/public projection rather than loading HMAC key maps. Once that verifier exists, obsolete recovery HMAC key maps and HMAC lifecycle proof bytes can be scrubbed atomically with the cutoff. A required acceptance regression is:

`verified legacy history -> authenticated cutoff -> scrub recovery symmetric material -> restart -> verify legacy prefix + Ed25519 suffix successfully`

and a companion negative test must show that reintroducing or depending on symmetric recovery material is rejected.

## Post-cutoff Ed25519 suffix

The current suffix uses Ed25519 threshold signatures for new break-glass root edges. Each asymmetric proof binds the migration boundary, exact predecessor/successor root and the public recovery authority. Root-head advancement and proof persistence occur in one SQL transaction. Historical recovery-generation windows are currently still obtained through LAB-085's symmetric lifecycle; this is the dependency that the next slice must remove.

## Audit fixes accumulated during integration

- migration-vs-legacy-recovery TOCTOU moved into SQL with a persistent post-cutoff trigger;
- nested write/self-lock paths were removed;
- inherited public-custody verification restored under one writer-excluding interval;
- pre-cutoff LAB-086 surface delegates to the full LAB-085 mixed-root verifier;
- stale recovery generations cannot sign the cutoff or a new asymmetric edge;
- the cutoff verifier re-runs historical Ed25519 public-custody transition verification;
- v2 cutoff excludes HMAC proof bytes from its canonical projection and atomically scrubs those bytes after successful threshold authorization;
- post-cutoff legacy edge verification no longer invokes the HMAC break-glass verifier.

## Evidence status

The earlier standalone reference suite passed 12/12 and its unsafe legacy auto-promotion baseline failed as expected. Those results predate the v2 proof-scrubbing changes and are not evidence for the current PR head. The new real-schema files and tests still require exact-source execution together with LAB-085/084/083/082/080 regressions.

## Boundary

No live HSM/KMS is claimed. Whole-store rollback freshness remains delegated to the external monotonic-anchor work. LAB-086 must not be marked DONE until historical recovery verification succeeds without durable symmetric recovery signing material.
