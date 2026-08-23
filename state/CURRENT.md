# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `bde0aa90a8e0180cb9f8f3237bdb7c88a8bfb0e6`.
- Latest compare against `main` (`2c539953c56610eb39bf1548f74d1a67a07defb2`): branch `ahead 38 / behind 6`, all 11 LAB-086 paths are new files. GitHub currently reports mergeability false after the main-state commits; treat this as divergence to re-check after the test gate, not as an owner blocker.

## Last completed step

Fresh authority audit showed the prior LAB-086 draft was not honestly public-only: deleting MAC strings still left actual recovery HMAC key maps durable, and lifecycle/window verification still reconstructed symmetric recovery authorities.

The draft branch now implements a stronger candidate boundary:

1. fully verify LAB-085 compatibility history immediately before cutoff;
2. construct a canonical non-secret projection of verified recovery/lifecycle identities, legacy recovery edges, custody evidence and verified recovery windows;
3. threshold-sign the exact projection/cutoff with the current Ed25519 recovery quorum;
4. persist projection + cutoff and atomically scrub recovery HMAC key maps/proof fields in one `BEGIN IMMEDIATE`;
5. post-cutoff restart does not construct LAB-084/LAB-085 symmetric recovery controllers and accepts `recovery_authority=None`;
6. legacy root edges verify from the signed projection; new root edges use Ed25519 threshold proofs;
7. post-cutoff recovery-authority rotation is old-public + new-public Ed25519 thresholds plus current normal/root threshold co-authorization over one canonical transition;
8. SQL guards block old LAB-085 writers from extending symmetric recovery history after cutoff.

Logical scrub targets:
- `provider_rotation_recovery_authorities.keys_json -> {}`;
- `provider_recovery_lifecycle_authorities.keys_json -> {}`;
- legacy break-glass `signatures_json -> []`;
- recovery-lifecycle old/new/root HMAC signature fields -> `[]`.

A focused local model passed the core invariant: `verify HMAC prefix -> sign non-secret projection -> scrub keys/proofs -> verify without HMAC -> semantic tamper detected`. This is design evidence only, not exact repository regression evidence.

## Evidence / constraints

- Earlier exact standalone LAB-086 reference suite: 12/12 passed; unsafe auto-promotion seed failed as expected; compileall passed. Those unchanged standalone blobs predate the current real-schema rewrite.
- New/updated branch tests cover restart without recovery HMAC authority, symmetric-material reintroduction, scrubbed legacy prefix + Ed25519 suffix, public-only recovery rotation/root co-authorization and stale-public-signer rejection. They have not yet been executed as exact current-head source.
- Direct shell GitHub access remains unavailable (`Could not resolve host: github.com`; direct-IP probe also failed). GitHub connector is healthy, so exact source must be reconstructed file-scoped unless network capability changes.
- Logical SQLite-state scrubbing is not forensic erasure; WAL/filesystem remnants are outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Re-fetch PR #165 and require a stable HEAD; restart the gate if it moved.
2. Reconstruct exact current-head LAB-086 executable/test files plus merged LAB-085/084/083/082/080 dependencies through the GitHub connector; verify local bytes with `git hash-object`.
3. Execute exact LAB-086 migration/suffix tests, including atomic key/proof scrub, `recovery_authority=None` restart, reintroduced symmetric-material rejection, scrubbed legacy prefix + Ed25519 suffix, public-only recovery-authority rotation with root co-authorization, stale signer and proof-tamper cases, and pre-cutoff public-custody corruption rejection.
4. Run LAB-085/084/083/082/080 regressions, unsafe legacy-promotion seed and compileall.
5. Fix every failure and repeat; then perform a fresh full remote patch audit.
6. Re-check branch/main divergence. If normal merge is unavailable but the gate is clean and the 11 paths remain new/conflict-free, the documented small/file-scoped Contents API fallback is allowed; do not use refs/trees/force or bypass any safety gate.
7. Only after a clean gate: update evidence, integrate, close Issue #163 DONE and choose the next highest-value unblocked bottleneck.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; public-only candidate published, exact current-head regression/audit gate remains.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
