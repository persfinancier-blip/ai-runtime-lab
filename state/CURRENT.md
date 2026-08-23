# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-086 — migrate historical break-glass verification from durable symmetric/HMAC material to an explicit authenticated legacy cutoff plus Ed25519 public-only proof history, without auto-promoting legacy rows or weakening LAB-084/LAB-085 authority semantics.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Active branch: `lab/086-asymmetric-break-glass-history`.
- Active draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current PR #165 HEAD: `a7d403439a31a3ddc8894f9839b0456b7251684b` at last inspection.
- PR #165 is open, mergeable and intentionally draft.

## Last completed step

LAB-086 now has the intended real-schema migration shape published on PR #165.

`migration_guard.py` derives the exact legacy HMAC/custody prefix from the actual LAB-084/LAB-085 tables, threshold-signs the cutoff with the historically-bound current Ed25519 recovery authority, and installs a persistent SQL trigger blocking any new `provider_rotation_recovery_transitions` row after migration.

`experiments/asymmetric_break_glass_history/suffix.py` now adds post-cutoff Ed25519-only break-glass edges directly to the existing `provider_rotation_authorities` / `provider_rotation_authority_head`. The successor root, public proof and root-head CAS are committed in one `BEGIN IMMEDIATE` transaction. The verifier requires exactly one proof type per root-history edge: normal threshold rotation, legacy HMAC recovery, or post-cutoff asymmetric recovery.

Historical recovery-generation authorization reuses LAB-085 lifecycle windows. Old public keys remain usable to verify old proof rows, but a recovery generation cannot authorize a new break-glass edge outside its activation window.

New real-schema suffix regressions cover restart, explicit blocking of both HMAC recovery entry points, insufficient Ed25519 quorum, proof tamper, duplicate proof type and stale old Ed25519 signers after recovery-authority rotation.

## Audit findings corrected in the latest run

1. The first LAB-086 supported surface could establish the cutoff without rerunning the full pre-migration LAB-085 mixed-root verifier. `payload()` / `establish()` now route the exact LAB-086 surface through its pre-boundary branch, which delegates to the authoritative LAB-085 mixed-history verifier under the same write fence.
2. Recovery-generation activation did not need a second event-clock subsystem. LAB-085 already derives activation/deactivation cutoffs from the root version that co-authorized each recovery-authority transition. Since every break-glass advances root version, this gives an unambiguous historical authorization window.
3. The post-cutoff verifier now rejects stale recovery generations, requires exact recovery/public custody binding, re-verifies Ed25519 quorum bytes, and counts exactly one root-edge proof type.

## Evidence produced

- Earlier standalone LAB-086 reference evidence remains: corrected 12/12, unsafe legacy auto-promotion seed failed as expected, compileall passed.
- Current real-schema draft files include:
  - `migration_guard.py` — hardened cutoff and SQL legacy-HMAC fence;
  - `suffix.py` — Ed25519-only real root-history suffix;
  - `tests/test_migration_guard.py`;
  - `tests/test_suffix.py` including recovery-generation rotation regression.
- PR #165 currently has nine new LAB-086 paths and no path overlap with newer `main` changes; last compare showed the branch diverged only because `main` advanced separately.
- Direct shell `git ls-remote` / checkout was probed again in this runtime and fails before execution with `Could not resolve host: github.com`; GitHub connector access remains healthy.
- No exact-source test run is claimed for the current real-schema suffix/head.

## Known blockers / constraints

- The intended code is published, but the current PR head has **not** yet passed exact-source execution of the new migration guard + suffix against the merged dependency stack. Earlier 12/12 standalone evidence must not be reused for these bytes.
- Direct shell GitHub networking remains unavailable due DNS; this is a runtime capability constraint, not an owner blocker.
- The current PR is intentionally draft until LAB-086 plus LAB-085/084/083/082/080 regressions, unsafe seed and compileall are actually executed from exact published bytes.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.
- No live HSM/KMS was exercised; Ed25519 signer objects remain a reference interface.

## Exact next action

Re-fetch PR #165 and confirm the head has not moved from the last audited state. Reconstruct exact published bytes through the GitHub connector (or use direct checkout only if networking is newly available), verify Git blob identities, and execute:

1. LAB-086 standalone reference tests;
2. LAB-086 real migration-guard tests;
3. LAB-086 asymmetric suffix tests;
4. LAB-085, LAB-084, LAB-083, LAB-082 and LAB-080 regression suites;
5. unsafe legacy auto-promotion seed;
6. `compileall` for the affected experiment tree.

If any test fails, fix and repeat. If the exact-source gate is clean, perform a fresh full remote patch audit. Only then mark PR #165 ready, merge it, close Issue #163 DONE, and select the next highest-value unblocked correctness bottleneck.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; intended real-schema implementation published, exact-source regression/audit gate remains.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
