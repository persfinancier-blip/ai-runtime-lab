# Current Lab State

Last updated: 2026-08-23

## Active objective

Verify the merged LAB-085 recovery-authority lifecycle/asymmetric-custody implementation against one fresh exact-source full regression stack before declaring the issue DONE and starting LAB-086.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-084.
- Active verification: Issue #161 / LAB-085 — VERIFY.
- Integrated PR: #162 — squash-merged normally as `9aa67f3aae9a3cb25aadd50e62c85c29af533980` from audited HEAD `773a6071de9cd9f8689feabd0a389dd503deb16d`.
- Follow-up after LAB-085 verification: Issue #163 / LAB-086 — migrate historical LAB-084 HMAC recovery proofs to asymmetric/public-verification history.

## Last completed step

The current PR #162 patch was re-audited at immutable HEAD `773a6071de9cd9f8689feabd0a389dd503deb16d`. The audit confirmed the latest two security fixes are present:

1. Ed25519 quorum handling marks a signer identity as seen only after successful cryptographic verification, so an invalid known-signer signature cannot suppress a later valid signature.
2. HMAC-only new break-glass recovery is blocked not only on the final `SupportedRecoveryCustodyLedger`, but also on the intermediate `SupportedPublicRecoveryAuthorityLifecycleLedger` supported surface.

`main` had advanced from the PR merge-base only by updates to `state/CURRENT.md`; lower-layer executable dependencies were unchanged. PR #162 was marked ready and then squash-merged through the normal GitHub merge endpoint.

## Evidence produced

- LAB-085 integration commit: `9aa67f3aae9a3cb25aadd50e62c85c29af533980`.
- Prior exact LAB-085 corrected suite: 38/38 passed.
- Prior exact lower-layer regressions: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17 — 87/87 total.
- Exact asymmetric-custody focused suite after quorum robustness fix: 8/8 passed.
- LAB-085 unsafe self-swap seed previously failed as expected.
- Prior compileall passed.
- Fresh integration audit inspected the current `public_custody_supported.py`, `final_supported.py`, `asymmetric_custody.py`, and the new intermediate-surface regression.

## Known blockers / constraints

- No content/integration blocker remains; LAB-085 code is merged.
- This invocation did not execute a new full exact-source current-head regression after the latest supported-surface fix. Do not rewrite prior evidence as if it were a fresh run.
- Direct shell `git` access to GitHub remains DNS-unavailable in this runtime; GitHub connector reconstruction is the supported exact-source path.
- Historical LAB-084 break-glass proofs before the authenticated custody cutoff remain HMAC-verifiable compatibility history. Issue #163 / LAB-086 owns their asymmetric migration.
- Whole-store rollback freshness remains a separate external-anchor responsibility.

## Exact next action

Reconstruct the merged LAB-085 executable/test bytes and unchanged merged LAB-080/082/083/084 dependencies through the GitHub connector, verify Git blob identities, and execute the full LAB-085 corrected suite + LAB-080/082/083/084 regressions + LAB-085 unsafe seed + compileall. Perform one post-merge audit focused on cutoff immutability, intermediate/final supported-surface method inheritance, Ed25519 quorum robustness, mixed public/HMAC historical verification, and recovery/custody races. If clean, close Issue #161 DONE and begin Issue #163 / LAB-086. If a defect is found, patch `main` through a normal branch/PR and repeat the gate.

## Backlog

- #161 / LAB-085 — VERIFY; integrated, post-merge exact-source regression gate remains.
- #163 / LAB-086 — READY after LAB-085 verification; historical LAB-084 HMAC proof migration to asymmetric/public-verification history.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
