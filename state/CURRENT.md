# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-085 — finish recovery-authority lifecycle and asymmetric custody without allowing post-custody break-glass effects to be downgraded into HMAC-only compatibility history.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-084.
- Active: Issue #161 / LAB-085 — IN_PROGRESS.
- Active branch: `lab/085-recovery-authority-lifecycle`.
- Active PR: #162 — draft, mergeable at audited HEAD `aacb4af1855f8afadac57b1564fd4cb452cf490b`.
- Follow-up after LAB-085: Issue #163 / LAB-086 — migrate historical LAB-084 HMAC recovery proofs to asymmetric/public-verification history.

## Last completed step

The remaining lower-layer regression gate was executed from connector-reconstructed exact Git blobs because direct shell GitHub access remains DNS-unavailable in this runtime. Results were clean:

- LAB-080 / shared anchor intent ledger: 18/18 passed.
- LAB-082 / asymmetric provider history: 28/28 passed.
- LAB-083 / threshold-authorized provider rotation: 24/24 passed.
- LAB-084 / provider rotation recovery: 17/17 passed.
- Total lower-layer regressions: 87/87 passed.
- `python -m compileall -q experiments`: passed.

PR #162 HEAD was re-fetched and remained unchanged at `aacb4af1855f8afadac57b1564fd4cb452cf490b`. A fresh full patch audit then found a new merge-blocking downgrade path in the public-custody enablement cutoff.

## New audit blocker

`provider_recovery_custody_enablement` is currently mutable SQL state without its own authenticated transition/proof. `SupportedRecoveryCustodyLedger._verify_break_glass_custody_locked()` uses the stored `start_rotation_version` to decide whether a recovery edge must have a public-custody proof or may remain HMAC-only compatibility history.

Counterexample to fix and encode as a regression:

1. enable public custody at root R1;
2. perform a valid custody-bound break-glass recovery R1 -> R2, creating both the LAB-084 compatibility proof and the public-custody proof;
3. tamper the enablement row so its cutoff points to valid historical root R2 while keeping valid symmetric/public custody IDs;
4. delete the public-custody proof for R2;
5. restart/verify must fail closed, but the current design can reclassify the R1 -> R2 edge as pre-custody because `old_version < substituted_start_version`.

This is a correctness/security blocker because a mutable cutoff must not be able to weaken historical proof requirements after the fact.

## Evidence produced

- Connector reconstruction and Git blob verification for the exact LAB-080/082/083/084 executable stack.
- Observed test results: 18/18 + 28/28 + 24/24 + 17/17 = 87/87, compileall passed.
- Fresh PR #162 audit covered the lifecycle, asymmetric custody, public/symmetric binding, and final custody-bound break-glass surfaces.
- Issue #161 and PR #162 comments record the cutoff-substitution counterexample and merge prohibition.

## Known blockers / constraints

- PR #162 must remain draft until the custody enablement/cutoff is authenticated or equivalently derived from immutable authenticated history.
- Direct shell `git` access to GitHub is still DNS-unavailable in this runtime; GitHub connector reconstruction is the safe supported exact-source path.
- Whole-store rollback freshness remains a separate external-anchor responsibility; this blocker is narrower: an internally modified live DB must not be able to downgrade proof requirements by moving the custody cutoff forward.

## Exact next action

On the next invocation, resume Issue #161 and PR #162 at unchanged HEAD if possible. Implement an authenticated custody-enablement transition that binds at least the exact cutoff root `(authority_id, version, generation)`, the bound symmetric recovery authority ID, and the bound public recovery authority ID. Prefer a threshold-authorized immutable proof using the current authority/custody mechanisms rather than another unauthenticated cache field. Add a deterministic regression that performs a valid post-custody recovery, moves the stored cutoff forward and deletes its public proof, and requires restart verification to reject the downgrade. Then execute the exact LAB-085 corrected suite, LAB-080/082/083/084 regressions, unsafe seed and compileall; perform another full PR patch audit. Only if all are clean may PR #162 be marked ready and squash-merged and Issue #161 closed DONE.

## Backlog

- #161 / LAB-085 — IN_PROGRESS; cutoff-authentication blocker found in final audit.
- #163 / LAB-086 — READY after LAB-085; historical LAB-084 HMAC proof migration to asymmetric/public-verification history.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
