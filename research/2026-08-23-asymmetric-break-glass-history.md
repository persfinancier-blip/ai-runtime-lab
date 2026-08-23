# LAB-086 — asymmetric historical break-glass proof migration

## Result so far

LAB-086 now has both sides of the migration boundary on the real LAB-084/LAB-085 SQLite authority.

The authenticated cutoff commits the exact legacy HMAC break-glass prefix plus the corresponding LAB-085 public-custody proofs. A persistent SQL trigger prevents even an old LAB-085 writer from appending another HMAC break-glass row after migration. Legacy rows remain legacy verification history; they are never copied or auto-promoted into the asymmetric proof table.

The post-cutoff suffix uses Ed25519 threshold signatures only. Every asymmetric proof binds:

- the exact migration boundary digest;
- predecessor root ID/version/generation;
- full successor root descriptor;
- exact symmetric recovery lifecycle authority;
- exact historically-bound public recovery authority/version/generation.

The successor root row, asymmetric proof and root-head CAS commit in one `BEGIN IMMEDIATE` transaction. Exactly one proof type is permitted per root-history edge: normal threshold rotation, legacy HMAC recovery, or post-cutoff asymmetric recovery.

## Historical authority window

LAB-085 already gives each recovery generation an activation/deactivation window derived from the root that co-authorized the recovery-authority transition. LAB-086 reuses that existing authority boundary rather than inventing another clock or sequence system. Because each break-glass recovery itself advances root version, the relative order of recovery-authority rotation and break-glass use is reconstructable from the root-version boundary.

Consequently, an old Ed25519 public key remains valid for verification of a historical proof inside its activation window, while signatures from that old generation cannot authorize a new break-glass edge after the recovery authority rotates.

## Audit fixes during integration

- migration-vs-legacy-recovery TOCTOU was moved into SQL with the persistent post-cutoff trigger;
- nested write/self-lock paths were removed;
- inherited public-custody verification was restored under one writer-excluding interval;
- the LAB-086 supported surface preserves the full LAB-085 mixed-root verifier before the cutoff instead of weakening pre-migration authority checks;
- post-cutoff verification counts exactly one proof type per root edge and re-verifies historical Ed25519 quorum material rather than trusting persisted labels.

## Evidence status

The earlier standalone reference suite passed 12/12 and its unsafe legacy auto-promotion baseline failed as expected. Those results do **not** cover the current real-schema migration guard and asymmetric suffix bytes. The current PR must still pass exact-source LAB-086 plus LAB-085/084/083/082/080 regressions and compileall before merge.

## Boundary

This removes durable symmetric signing material from *new* break-glass history. Legacy HMAC proof rows remain verification-only compatibility history behind the authenticated cutoff. Private Ed25519 signing capability is runtime-only; durable state contains public verification material and signed proof bytes. No live HSM/KMS or whole-store rollback protection is claimed here; whole-store freshness remains delegated to the external monotonic-anchor work.
