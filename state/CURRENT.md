# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an explicit authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Active branch: `lab/086-asymmetric-break-glass-history`.
- Active draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `bde0aa90a8e0180cb9f8f3237bdb7c88a8bfb0e6`; re-fetch before any test/merge gate.
- PR #165 is open, mergeable and intentionally draft.

## Last completed step

A fresh authority audit found that the prior LAB-086 design was still not honestly public-only: it removed historical MAC proof strings but LAB-084/LAB-085 still persisted the actual HMAC recovery key maps and post-cutoff lifecycle/window verification still reconstructed those symmetric authorities.

The draft branch was substantially hardened rather than masking that gap. The current candidate now:

1. fully verifies the LAB-085 compatibility history immediately before cutoff;
2. builds a canonical non-secret projection of the verified recovery/lifecycle identities, legacy recovery edges, custody evidence and already-verified recovery windows;
3. threshold-signs that exact projection/cutoff with the current Ed25519 recovery quorum;
4. persists projection + cutoff and atomically scrubs recovery HMAC key maps/proof fields in the same `BEGIN IMMEDIATE` transaction;
5. restarts post-cutoff without constructing LAB-084/LAB-085 symmetric recovery controllers (`recovery_authority=None` is the acceptance path);
6. verifies legacy root edges from the signed cutoff projection and verifies new root edges with Ed25519 threshold proofs;
7. replaces post-cutoff dual symmetric/public recovery-authority rotation with old-public + new-public Ed25519 thresholds plus current normal/root threshold co-authorization over one canonical transition;
8. installs SQL guards preventing old LAB-085 writers from extending symmetric recovery history after cutoff.

The logical scrub targets:
- `provider_rotation_recovery_authorities.keys_json -> {}`;
- `provider_recovery_lifecycle_authorities.keys_json -> {}`;
- legacy break-glass `signatures_json -> []`;
- recovery-lifecycle old/new/root HMAC signature fields -> `[]`.

A focused local model executed successfully for the core migration invariant: `verify HMAC prefix -> sign non-secret projection -> scrub keys/proofs -> verify projection without HMAC -> semantic tamper detected`. This was a design/protocol model only; it is not exact repository regression evidence.

New/updated branch tests now require restart without recovery HMAC authority, rejection of reintroduced symmetric material, a scrubbed legacy prefix followed by an Ed25519 suffix, public-only recovery-authority rotation with root co-authorization, and stale-public-signer rejection.

## Evidence produced

- Earlier exact standalone LAB-086 reference suite: 12/12 passed; unsafe auto-promotion seed failed as expected; compileall passed. These blobs are unchanged historical evidence only and predate the current real-schema rewrite.
- Focused local projection/scrub model in this run: passed.
- Current candidate implementation commits in PR #165 include the public projection / HMAC scrub, public-only suffix and updated regressions; current observed branch HEAD is `bde0aa90a8e0180cb9f8f3237bdb7c88a8bfb0e6`.
- Current branch docs explicitly state logical DB scrubbing is not forensic erasure.
- Direct shell GitHub access was probed again and remains unavailable (`Could not resolve host: github.com` / direct IP connection also unavailable). GitHub connector remains healthy; this is a runtime capability constraint, not an owner blocker.

## Known blockers / constraints

- The current public-only real-schema rewrite has **not** yet been executed as exact published source against the full dependency stack. Do not merge or mark DONE based on the earlier standalone 12/12.
- The connector can retrieve exact source but cannot directly materialize a repository checkout in the shell runtime; exact reconstruction/execution must continue file-scoped unless network capability changes.
- The new branch changed constructor/restart semantics after cutoff and introduced a new public-only recovery-authority rotation path; both require runtime regression coverage before merge.
- Logical SQLite state scrubbing is not secure/forensic deletion. WAL/filesystem remnants are outside LAB-086.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.
- No live HSM/KMS is claimed.

## Exact next action

1. Re-fetch PR #165 and require a stable current HEAD; restart the gate if it moved.
2. Reconstruct the exact executable current-head LAB-086 files plus the merged LAB-085/084/083/082/080 dependency stack through the GitHub connector and verify each local file with `git hash-object`.
3. Execute exact-source LAB-086 tests, especially:
   - migration cutoff after real LAB-085 compatibility recovery;
   - atomic scrub of both recovery HMAC key maps and all recovery-HMAC proof fields;
   - restart with `recovery_authority=None`;
   - reintroduced symmetric material rejection;
   - scrubbed legacy prefix + Ed25519 break-glass suffix + restart;
   - public-only recovery-authority rotation requiring old/new Ed25519 thresholds + current root threshold;
   - stale public signer rejection and root-proof/asymmetric-proof tamper rejection;
   - public-custody corruption before cutoff rejection.
4. Run LAB-085, LAB-084, LAB-083, LAB-082 and LAB-080 regressions, unsafe legacy-promotion seed and compileall.
5. Fix every failure and repeat; then perform a fresh full remote patch audit.
6. Only after a clean exact-source gate: update evidence/docs, mark PR #165 ready, squash-merge, close Issue #163 DONE and select the next highest-value unblocked correctness bottleneck.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; public-only candidate published, exact current-head regression/audit gate remains.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
