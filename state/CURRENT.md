# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-085 — finish recovery-authority lifecycle and asymmetric custody with an authenticated immutable public-custody enablement boundary and robust Ed25519 quorum handling.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-084.
- Active: Issue #161 / LAB-085 — IN_PROGRESS.
- Active branch: `lab/085-recovery-authority-lifecycle`.
- Active PR: #162 — draft, currently mergeable at HEAD `09edfb81b7041a5a9fcfcacab9d4fa7930ed0d6e`.
- Follow-up after LAB-085: Issue #163 / LAB-086 — migrate historical LAB-084 HMAC recovery proofs to asymmetric/public-verification history.

## Last completed step

The prior lower-layer regression gate was clean from connector-reconstructed exact Git blobs: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17 — 87/87 total, plus compileall.

After the authenticated cutoff fix, a fresh audit found another real LAB-085 defect in Ed25519 quorum filtering. `accepted_public_signatures()` marked a signer identity as consumed before cryptographic verification. A structurally valid but forged signature using a legitimate signer ID could therefore precede the real signature and suppress that signer from the quorum, causing a denial-of-service.

The branch now consumes a signer ID only after successful Ed25519 verification. A regression places an invalid signature for a known signer before the legitimate signature on both old and new recovery quorums and requires rotation/restart to succeed.

## Evidence produced

- Current quorum-fix implementation commit: `f15f908b8c756e5ab1e1f463576e0333e0dc8e7a`.
- Current PR HEAD after regression: `09edfb81b7041a5a9fcfcacab9d4fa7930ed0d6e`.
- Exact published `asymmetric_custody.py` blob: `771e2ae8cde15ce06297a9cf4a94c4b3f0d81dd4`.
- Exact published `test_asymmetric_custody.py` blob: `cf8ec19252c44a6d448d4907e6d8c6659f8fb076`.
- Both blobs were connector-reconstructed and matched locally with `git hash-object`.
- Exact current asymmetric-custody focused suite: 8/8 passed.
- The four cutoff-authentication delta files from the prior audited HEAD were also connector-reconstructed and matched their Git blobs; changed implementation files compile.
- Issue #161 and PR #162 record the new counterexample, fix, and evidence.

## Known blockers / constraints

- PR #162 remains draft because the quorum robustness fix changed current HEAD after the earlier full LAB-085 38/38 and lower-layer 87/87 runs. A fresh complete exact-current-head regression/audit gate is still required before integration.
- Direct shell `git` access to GitHub remains DNS-unavailable in this runtime; GitHub connector reconstruction is the safe supported exact-source path.
- The branch is diverged from main but its PR paths are 14 LAB-085 files added under `experiments/provider_recovery_authority_lifecycle/`; no overlapping main paths were observed in the latest compare. If normal merge later fails after all validation, file-scoped Contents API integration remains an allowed audited fallback.
- Historical LAB-084 break-glass proofs before the authenticated custody cutoff remain compatibility history. Issue #163 / LAB-086 owns their later asymmetric migration.
- Whole-store rollback freshness remains a separate external-anchor responsibility.

## Exact next action

Reconstruct the remaining exact executable/test bytes for PR #162 HEAD `09edfb81b7041a5a9fcfcacab9d4fa7930ed0d6e` and the exact merged dependencies through the GitHub connector, verifying each Git blob identity. Execute the full current LAB-085 corrected suite including the authenticated-cutoff regression and the invalid-first-known-signer quorum regression, the LAB-085 unsafe self-swap seed, compileall, and the exact LAB-080/082/083/084 regression stack. If any failure occurs, fix and repeat. Then perform one fresh full PR patch audit focused on cutoff immutability, public-proof restart semantics, quorum robustness, recovery/custody rotation races, and historical compatibility. Only if HEAD remains unchanged and all gates are clean may PR #162 be marked ready, integrated, Issue #161 closed DONE, and LAB-086 selected next.

## Backlog

- #161 / LAB-085 — IN_PROGRESS; quorum DoS fix published and focused exact 8/8 passed; full exact-current-head regression/audit gate remains.
- #163 / LAB-086 — READY after LAB-085; historical LAB-084 HMAC proof migration to asymmetric/public-verification history.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
