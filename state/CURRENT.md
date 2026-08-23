# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-085 — finish recovery-authority lifecycle and asymmetric custody with authenticated cutoff, robust Ed25519 quorum handling, and no HMAC-only break-glass bypass on any supported public-custody surface.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-084.
- Active: Issue #161 / LAB-085 — IN_PROGRESS.
- Active branch: `lab/085-recovery-authority-lifecycle`.
- Active PR: #162 — draft, mergeable at HEAD `773a6071de9cd9f8689feabd0a389dd503deb16d`.
- Follow-up after LAB-085: Issue #163 / LAB-086 — migrate historical LAB-084 HMAC recovery proofs to asymmetric/public-verification history.

## Last completed step

A fresh current-head supported-surface audit found a real bypass after the prior authenticated-cutoff and quorum fixes. `SupportedPublicRecoveryAuthorityLifecycleLedger` is itself an explicitly supported intermediate boundary but inherited LAB-084 `recover_rotation_authority()` unchanged. A caller could instantiate that intermediate supported class directly and create a new HMAC-only break-glass root recovery, bypassing the final `SupportedRecoveryCustodyLedger` Ed25519+compatibility dual-proof boundary.

The branch now overrides `recover_rotation_authority()` on the intermediate public-custody supported class and fails closed. A new regression calls the inherited entry point through that intermediate surface and requires `CustodyBindingError`.

## Evidence produced

- Prior exact lower-layer regression gate remains recorded: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17 — 87/87 total, plus compileall.
- Prior exact LAB-085 suite at pre-cutoff-fix HEAD: 38/38 passed.
- Exact current asymmetric-custody focused suite before this latest surface fix: 8/8 passed.
- New intermediate-surface implementation commit: `4120c42a55053955988ef1456e5644f7a1bb5bd6`.
- New regression commit / current PR HEAD: `773a6071de9cd9f8689feabd0a389dd503deb16d`.
- Current `public_custody_supported.py` blob after fix: `e15a251e5951278df5fcc24f28ac9a766d75f06e`.
- Current `test_public_custody_supported.py` blob after regression: `859c0438732f70a7be4324971b99402928e03e21`.
- Issue #161 records the bypass, fix, and current gate.

## Known blockers / constraints

- PR #162 remains draft because current HEAD changed after all prior full exact-source gates. The latest two files have not yet received a fresh full-stack exact-current-head execution.
- Direct shell `git` access to GitHub is DNS-unavailable in this runtime; GitHub connector reconstruction is the safe supported exact-source path.
- The branch remains limited to LAB-085 paths under `experiments/provider_recovery_authority_lifecycle/`; if normal integration later fails after validation, audited file-scoped Contents API fallback remains allowed.
- Historical LAB-084 break-glass proofs before the authenticated custody cutoff remain compatibility history. Issue #163 / LAB-086 owns their asymmetric migration.
- Whole-store rollback freshness remains a separate external-anchor responsibility.

## Exact next action

Connector-reconstruct the exact executable/test bytes for PR #162 HEAD `773a6071de9cd9f8689feabd0a389dd503deb16d` and the exact merged dependencies, verifying Git blob identities. Execute the full LAB-085 corrected suite including authenticated-cutoff downgrade, invalid-known-signer-first quorum robustness, and the new intermediate-supported-surface HMAC-only break-glass rejection; run the LAB-085 unsafe seed, compileall, and the exact LAB-080/082/083/084 regression stack. If any failure occurs, fix and repeat. Then perform one fresh full PR patch audit focused on inherited-method bypasses, cutoff immutability, public-proof restart semantics, quorum robustness, recovery/custody races, and historical compatibility. Only if HEAD remains unchanged and all gates are clean may PR #162 be marked ready, integrated, Issue #161 closed DONE, and LAB-086 selected next.

## Backlog

- #161 / LAB-085 — IN_PROGRESS; latest supported-surface bypass fixed; full exact-current-head regression/audit gate remains.
- #163 / LAB-086 — READY after LAB-085; historical LAB-084 HMAC proof migration to asymmetric/public-verification history.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
