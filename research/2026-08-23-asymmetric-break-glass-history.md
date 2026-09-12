# LAB-086 — asymmetric historical break-glass proof migration

## Current candidate result

LAB-086 now has a full public-only post-cutoff recovery design on the real LAB-084/LAB-085 SQLite authority. This is newer than the previous exact-source evidence and remains a candidate until the current PR head passes the full regression gate.

Immediately before migration, the implementation runs the complete LAB-085 compatibility verifier. It then builds a canonical non-secret projection of the verified recovery history: recovery/lifecycle identities and metadata, lifecycle transition identities, legacy break-glass edges, public-custody proofs/bindings and the already-verified recovery activation windows. The current Ed25519 recovery quorum signs the digest of that projection together with the exact root/public cutoff identity.

Within the same `BEGIN IMMEDIATE` transaction the implementation:

1. persists the canonical projection;
2. persists the threshold-signed cutoff;
3. replaces historical LAB-084 break-glass `signatures_json` with canonical `[]`;
4. replaces durable LAB-084 and LAB-085 recovery `keys_json` with canonical `{}`;
5. replaces old/new/root HMAC signature sets in the symmetric recovery-lifecycle transition table with canonical `[]`.

After commit, the supported LAB-086 restart path deliberately does **not** construct the LAB-084 recovery controller or LAB-085 symmetric recovery lifecycle. It loads only the LAB-083 root/provider authority, the Ed25519 public recovery history and the LAB-086 cutoff/projection. A required regression passes `recovery_authority=None` on restart and requires durable verification to succeed.

This is logical durable-state scrubbing, not forensic erasure. SQLite/WAL/filesystem remnants are explicitly outside the claim.

## Legacy prefix verification

Post-cutoff legacy root edges are not HMAC-verified again. Their exact semantic rows are compared against the signed projection that was created only after full pre-cutoff verification. Reintroduced HMAC key/proof material is rejected. SQL triggers also prevent old LAB-085 writers from inserting new HMAC break-glass or symmetric recovery-lifecycle rows after the boundary.

The projection preserves the historical activation/deactivation windows that were derived and verified before scrubbing, so the old symmetric recovery authorities no longer need to be reconstructed from key maps after migration.

## Public-only recovery-authority rotation

The previous draft still used LAB-085 dual symmetric/public rotation after the cutoff. That would have kept HMAC recovery keys operational even if historical break-glass proofs were asymmetric.

The current candidate replaces that path with a public-only recovery-authority rotation:

- old public recovery threshold signs the exact successor;
- new public recovery threshold signs the same transition;
- the current normal/root threshold co-authorizes that same canonical transition;
- Ed25519 public transition and root co-authorization proof commit in one SQL transaction;
- the symmetric recovery heads are frozen at the cutoff and are not advanced.

Historical public keys remain verification-only. A root-version activation window for post-cutoff public generations is reconstructed from the cutoff plus these root-coauthorized public transitions, so a stale public generation cannot authorize a later asymmetric break-glass edge.

## Post-cutoff break-glass suffix

Each new break-glass root edge is Ed25519-threshold authorized by the public recovery generation that is active for the predecessor root version. The proof binds the migration boundary and exact predecessor/successor root. Root-head advancement and proof persistence occur in one `BEGIN IMMEDIATE` transaction.

Exactly one root-history proof type is permitted per edge: normal root rotation, legacy pre-cutoff recovery committed by the signed projection, or post-cutoff asymmetric recovery.

## Audit fixes accumulated during integration

- migration-vs-legacy-recovery TOCTOU moved into SQL;
- nested write/self-lock paths removed;
- inherited public-custody history is cryptographically rechecked under a writer-excluding interval;
- pre-cutoff LAB-086 delegates to the full LAB-085 mixed-root verifier;
- stale public recovery generations cannot sign a cutoff or later break-glass edge;
- cutoff projection excludes symmetric secret/proof bytes;
- HMAC recovery key maps and proof bytes are scrubbed atomically with the cutoff;
- post-cutoff constructor no longer instantiates symmetric recovery controllers;
- inherited symmetric recovery-authority rotation is blocked after cutoff and replaced by Ed25519 old+new threshold plus normal-root co-authorization.

## Evidence status

The earlier standalone reference suite passed 12/12 and its unsafe legacy auto-promotion baseline failed as expected. Those results predate this real-schema public-only rewrite. A small local model in the current engineering pass separately confirmed the core projection property (`verify HMAC prefix -> sign non-secret projection -> scrub keys/proofs -> verify projection without HMAC -> semantic tamper detected`), but that is not a substitute for exact repository tests.

The required gate remains: exact current LAB-086 migration/suffix tests, LAB-085/084/083/082/080 regressions, unsafe seed, compileall and a fresh remote patch audit.

## Boundary

No live HSM/KMS is claimed. Whole-store rollback freshness remains delegated to the external monotonic-anchor work. Filesystem-level secure deletion is not claimed.
