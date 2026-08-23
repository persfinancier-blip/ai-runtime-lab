# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-085 — recovery-authority lifecycle and asymmetric custody. Keep PR #162 draft while fixing a newly found supported-surface bypass before the exact-source regression gate.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-084.
- Active: Issue #161 / LAB-085 — IN_PROGRESS.
- Branch: `lab/085-recovery-authority-lifecycle`.
- Draft PR: #162 — open; current HEAD `140481c9252614ef3bf2ddac546930fc60bfc18d`.
- Follow-up: Issue #163 / LAB-086 — asymmetric migration of historical LAB-084 break-glass proofs after LAB-085.

## Last completed step

Read AGENTS.md, this state, SELF_RESUME.md, open issues, PR #162 metadata, branch comparison, and the full current LAB-085 changed-file surface through the GitHub connector. The branch is additive on LAB-085 paths (`ahead 17 / behind 3` versus main), so main's newer durable-state commits do not overlap these code paths.

A fresh final audit found a merge-blocking supported-surface bypass that is not covered by the current tests. `SupportedRecoveryCustodyLedger` inherits public `recover_rotation_authority()` from LAB-084/LAB-085. That inherited method still authorizes a new normal/root authority using the **symmetric HMAC recovery authority only**. Enabling Ed25519 public custody therefore protects recovery-authority lifecycle rotation, but does not protect the actual break-glass root recovery operation from a caller who holds the historical/current symmetric recovery quorum. This is inconsistent with the LAB-085 claim that custody is the supported recovery authority boundary and means the private-capability split can be bypassed for consequential recovery.

The current test `test_root_recovery_races_custody_rotation_and_exactly_one_successor_wins` explicitly calls this inherited symmetric-only `recover_rotation_authority`, confirming that the path remains reachable. This is not the LAB-086 legacy-history issue: old LAB-084 proofs may remain HMAC-verifiable, but **new** break-glass effects on the LAB-085 final supported surface must not be authorizable through the compatibility HMAC quorum alone.

## Evidence produced

- AGENTS.md blob: `acaf419028f616e2161727927c6013ebd59c6518`.
- PR #162 HEAD observed: `140481c9252614ef3bf2ddac546930fc60bfc18d`; 12 additive LAB-085 files; branch comparison `ahead 17 / behind 3`.
- Audited current files include:
  - `final_supported.py` blob `1f1f2b978404f888fb89daeb5bb8096b306c416f`;
  - `public_custody_supported.py` blob `3988e458df243574967772c8806d4fb94e7c0170`;
  - `supported.py` blob `df4f17152cddefb66dc7f4e7f76f3112d3ab4733`;
  - `asymmetric_custody.py` blob `920a2586e665aa5187a1a1e97e5fc6401cb49e29`;
  - `test_public_custody_supported.py` blob `19704b62b850d020b510cd5b02951cabe511ae37`.
- The bypass is structural: `SupportedRecoveryCustodyLedger -> SupportedPublicRecoveryAuthorityLifecycleLedger -> SupportedRecoveryAuthorityLifecycleLedger -> SupportedRecoveryThresholdProviderLedger.recover_rotation_authority`, whose LAB-084 implementation accepts only `RecoveryAuthority` HMAC signatures.
- Existing public-custody tests block plain symmetric **recovery-authority lifecycle rotation**, but do not block symmetric-only **root break-glass recovery**.
- No exact-source test run is claimed in this turn; the audit blocker invalidates merge before spending the regression gate.

## Known blockers / constraints

- No owner/product blocker.
- PR #162 must remain draft.
- Merge blocker: final supported custody surface still exposes inherited symmetric-only `recover_rotation_authority()` for new break-glass root effects.
- Existing LAB-084 historical break-glass proofs remain HMAC-based and must remain verification-only compatibility history until LAB-086; this does not justify allowing new HMAC-only break-glass effects after public custody enablement.
- After the bypass is fixed, current PR-head exact-source LAB-085 + LAB-084/083/082/080 regression execution and a fresh final audit are still mandatory.

## Exact next action

On branch `lab/085-recovery-authority-lifecycle`, harden the final/public-custody supported surface so callers cannot invoke a symmetric-HMAC-only new root recovery. Add an explicit custody-bound break-glass method whose canonical recovery intent is authorized by the current public Ed25519 recovery quorum (and, if compatibility requires retaining the LAB-084 proof row, require both the public quorum and the compatibility HMAC quorum in the same `BEGIN IMMEDIATE` transaction). Override/block inherited `recover_rotation_authority()` once public custody is enabled. Add regressions proving: (1) HMAC-only root recovery is rejected on the final supported surface; (2) public-only proof cannot accidentally create an unverifiable legacy LAB-084 row if compatibility history still requires HMAC; (3) the combined authorized recovery commits atomically; (4) recovery-vs-custody-rotation still serializes to one successor; and (5) restart verifies the resulting mixed history. Then reconstruct exact current bytes and run all LAB-085 suites, LAB-084/083/082/080 regressions, unsafe seed, compileall, and a fresh full PR audit. Merge only if clean.

## Backlog

- #161 / LAB-085 — recovery-authority lifecycle + asymmetric custody — IN_PROGRESS; new supported-surface break-glass bypass must be fixed before exact-source gate.
- #163 / LAB-086 — asymmetric break-glass proof migration/public-only historical recovery — READY after LAB-085; migrate legacy HMAC proof history, not the new-effect authorization bypass found above.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
