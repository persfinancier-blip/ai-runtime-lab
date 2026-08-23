# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-085 — finish recovery-authority lifecycle by proving the newly integrated public-only custody binding on exact PR-head bytes and then performing the final merge audit.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-084.
- Active: Issue #161 / LAB-085 — IN_PROGRESS.
- Branch: `lab/085-recovery-authority-lifecycle`.
- Draft PR: #162 — open, mergeable.
- Current PR HEAD: `140481c9252614ef3bf2ddac546930fc60bfc18d`.
- Follow-up: Issue #163 / LAB-086 — asymmetric migration of historical LAB-084 break-glass proofs after LAB-085.

## Last completed step

Closed the remaining LAB-085 implementation gap instead of treating the earlier standalone Ed25519 custody slice as authoritative. Added `public_custody_supported.py`, which binds the symmetric LAB-085 lifecycle, LAB-084 recovery head, Ed25519 public custody head, and exact `(symmetric authority ID, public authority ID, version, generation)` record in one `BEGIN IMMEDIATE` transaction. A supported rotation now requires both the existing symmetric old+new+current-root authorization and the public old+new Ed25519 quorum; a symmetric-only lifecycle rotation is rejected once this surface is used.

Added restart/corruption and race regressions for metadata mismatch, public-head rollback, binding substitution, and root-recovery versus custody-rotation serialization.

A fresh remote audit then found a mixed-SQL-snapshot defect in restart verification: symmetric history, public history, and binding checks were performed in separate transactions. Added `final_supported.py`, whose `SupportedRecoveryCustodyLedger.verify_durable()` holds a write-excluding transaction across all inherited verification passes and the final binding check. Added a concurrency regression that asserts a competing writer cannot commit during this verification barrier.

README/PR/Issue #161 now explicitly distinguish public-only lifecycle custody from still-HMAC-based historical LAB-084 break-glass proofs; Issue #163 remains the later migration task for those proofs.

## Evidence produced

- PR #162 current HEAD: `140481c9252614ef3bf2ddac546930fc60bfc18d`; GitHub reports mergeable/draft.
- New files:
  - `experiments/provider_recovery_authority_lifecycle/public_custody_supported.py`
  - `experiments/provider_recovery_authority_lifecycle/final_supported.py`
  - `experiments/provider_recovery_authority_lifecycle/tests/test_public_custody_supported.py`
  - `experiments/provider_recovery_authority_lifecycle/tests/test_final_supported.py`
- Remote patch audit found and fixed the mixed-snapshot verifier weakness before handoff.
- Previous exact-source asymmetric-custody evidence remains valid only for earlier blobs: protocol `920a2586e665aa5187a1a1e97e5fc6401cb49e29`, tests `80f3ade5042ea2872b6395ca8fa4f1802d329d68`, focused suite 7/7.
- Do **not** reuse that 7/7 result as evidence for the new HEAD.
- Direct `git ls-remote`/clone and direct HTTPS access from the execution container were probed in this run and failed before execution (DNS/connectivity). GitHub connector read/write operations remain available.
- Branch comparison versus main: LAB-085 paths are additive/new; branch is diverged because main contains newer durable-state commits, not because these LAB-085 code paths overlap.

## Known blockers / constraints

- No owner/product blocker.
- PR #162 must remain draft until current HEAD exact-source execution is observed.
- The newly integrated public-custody/final-verifier code has been remote patch-audited but has not yet passed the required exact-source LAB-085 + LAB-084/083/082/080 regression stack.
- Existing LAB-084 break-glass proofs remain HMAC-based and still require historical symmetric verification material. LAB-085 must not claim they are already public-only; Issue #163 tracks that migration.
- If both normal/root authorization and recovery-lifecycle authorization are unavailable/compromised, fail closed and require external bootstrap ceremony.

## Exact next action

Reconstruct exact executable bytes for PR #162 HEAD `140481c9252614ef3bf2ddac546930fc60bfc18d` plus merged LAB-084/083/082/080 dependencies through the GitHub connector or another supported exact-byte path, and verify Git blob identities. Execute all LAB-085 suites (`test_protocol`, `test_supported_integration`, `test_asymmetric_custody`, `test_public_custody_supported`, `test_final_supported`), then LAB-084/083/082/080 regressions, unsafe seed, and compileall. If any failure appears, fix and rerun. Then perform a fresh full PR patch audit. Only after a clean exact-source run and audit: mark PR #162 ready, squash-merge, close Issue #161 DONE, and move to Issue #163 / LAB-086.

## Backlog

- #161 / LAB-085 — recovery-authority lifecycle + asymmetric custody — IN_PROGRESS; implementation gap closed, exact-source regression/audit gate remains.
- #163 / LAB-086 — asymmetric break-glass proof migration/public-only historical recovery — READY after LAB-085.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
