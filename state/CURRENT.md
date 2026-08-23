# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-085 — finish recovery-authority lifecycle and asymmetric custody with an authenticated immutable public-custody enablement boundary.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-084.
- Active: Issue #161 / LAB-085 — IN_PROGRESS.
- Active branch: `lab/085-recovery-authority-lifecycle`.
- Active PR: #162 — draft, mergeable at current HEAD `c0295257dbe4ef46c012b9c3f8ff6817f1dd3fff`.
- Follow-up after LAB-085: Issue #163 / LAB-086 — migrate historical LAB-084 HMAC recovery proofs to asymmetric/public-verification history.

## Last completed step

The remaining lower-layer regression gate was executed from connector-reconstructed exact Git blobs because direct shell GitHub access remains DNS-unavailable in this runtime. Results were clean:

- LAB-080 / shared anchor intent ledger: 18/18 passed.
- LAB-082 / asymmetric provider history: 28/28 passed.
- LAB-083 / threshold-authorized provider rotation: 24/24 passed.
- LAB-084 / provider rotation recovery: 17/17 passed.
- Total lower-layer regressions: 87/87 passed.
- `python -m compileall -q experiments`: passed for the reconstructed lower stack.

A fresh final PR audit then found a real cutoff-downgrade defect: `provider_recovery_custody_enablement.start_rotation_version` was mutable unauthenticated SQL state, yet it decided which historical recovery edges were allowed to remain HMAC-only compatibility history. Moving that cutoff forward could weaken the proof requirement for an already post-custody recovery.

The defect has now been fixed on PR #162. The branch adds a canonical `custody_enablement_payload` that binds the exact cutoff root `(authority_id, version, generation)` plus the exact bound symmetric and public recovery-authority identities. A new `provider_recovery_custody_enablement_proof` stores a threshold of Ed25519 public-recovery signatures over that payload. First enablement requires explicit quorum signatures; restart re-verifies the stored proof from durable public verification material. A missing proof cannot silently re-bootstrap without a fresh quorum.

A deterministic regression was added for the discovered attack: perform a valid custody-bound recovery, move the stored cutoff forward to the successor root, delete the recovery public proof and the enablement proof, then require restart to fail closed.

## Evidence produced

- Exact lower-stack results in this run: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17 — 87/87 total.
- Published cutoff-fix implementation blobs were re-fetched and byte-checked locally:
  - `experiments/provider_recovery_authority_lifecycle/custody_break_glass.py` — `f49139d80d13a3716817b79f0733cc0bc5d5bcac`;
  - `experiments/provider_recovery_authority_lifecycle/final_supported.py` — `7789b1c65535544d1416153c3ff26143aa9c44c1`.
- Both changed implementation files pass local Python compilation.
- New regression is in `tests/test_custody_break_glass.py`; final-surface bootstrap tests now provide the authenticated custody-enablement quorum.
- Issue #161 and PR #162 record both the discovered counterexample and the published fix.

## Known blockers / constraints

- PR #162 remains draft only because the latest cutoff-authentication changes were published after the previous exact LAB-085 38/38 run. They require a fresh exact-current-head execution before merge.
- Direct shell `git` access to GitHub remains DNS-unavailable in this runtime; GitHub connector reconstruction is the safe supported exact-source path.
- Historical LAB-084 break-glass proofs before the authenticated custody cutoff remain compatibility history. Issue #163 / LAB-086 owns their later asymmetric migration.
- Whole-store rollback freshness remains a separate external-anchor responsibility.

## Exact next action

Reconstruct exact executable/test bytes for PR #162 HEAD `c0295257dbe4ef46c012b9c3f8ff6817f1dd3fff` through the GitHub connector and verify Git blob identities. Execute the full current LAB-085 corrected suite including the new forward-cutoff downgrade regression, the LAB-085 unsafe self-swap seed, compileall, and the exact LAB-080/082/083/084 regression stack. If any failure occurs, fix and repeat. Then perform one fresh full PR patch audit focused on cutoff immutability, public-proof restart semantics, recovery/custody rotation races, and historical compatibility. Only if the current HEAD is unchanged and all gates are clean may PR #162 be marked ready, squash-merged, Issue #161 closed DONE, and LAB-086 selected next.

## Backlog

- #161 / LAB-085 — IN_PROGRESS; authenticated cutoff fix published, exact-current-head test/audit gate remains.
- #163 / LAB-086 — READY after LAB-085; historical LAB-084 HMAC proof migration to asymmetric/public-verification history.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
