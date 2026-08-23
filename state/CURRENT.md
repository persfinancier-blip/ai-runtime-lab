# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-085 — recovery-authority lifecycle and asymmetric custody. Exact PR-head execution has now found and fixed a real initialization defect; keep PR #162 draft until the remaining merged LAB-084/083/082/080 regressions and one fresh final audit are clean.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-084.
- Active: Issue #161 / LAB-085 — IN_PROGRESS.
- Branch: `lab/085-recovery-authority-lifecycle`.
- Draft PR: #162 — open, mergeable; current HEAD `aacb4af1855f8afadac57b1564fd4cb452cf490b`.
- Follow-up: Issue #163 / LAB-086 — migrate historical pre-cutoff LAB-084 HMAC break-glass proof history to asymmetric/public-only verification after LAB-085.

## Last completed step

Reconstructed every executable LAB-085 PR-head file through the GitHub connector and verified its Git blob identity locally. Also reconstructed the exact merged source dependencies used by LAB-080/LAB-082/LAB-083/LAB-084.

The first full exact-source LAB-085 execution exposed a real defect hidden by earlier partial checks: `SupportedRecoveryCustodyLedger` defined `_load_enablement_locked()`, unintentionally overriding LAB-083's threshold-enablement loader. During superclass initialization, dynamic dispatch therefore attempted to read `provider_recovery_custody_enablement` before the final LAB-085 schema existed and new ledgers failed to initialize.

Fixed this by separating the final-layer loader as `_load_break_glass_enablement_locked()`. Exact execution also showed that the public-custody rollback regression expected an overly narrow exception family: the implementation correctly failed closed with `CustodyRollback`, so the test now accepts that precise rollback class.

Published fixes:
- `final_supported.py` commit `78a6d5d15e07dad940b61aa7217e4ea73ca44cf7`, Git blob `44b460491753643a431cd98c98f497b1e50155c7`;
- `test_public_custody_supported.py` commit / current PR HEAD `aacb4af1855f8afadac57b1564fd4cb452cf490b`, Git blob `b1bbf0ec36ed9ab2dfe1b023559ec9dfcf3e62be`.

Both published bytes were re-fetched and matched locally with `git hash-object`. The current exact LAB-085 suite then passed **38/38**, and `python -m compileall -q experiments/provider_recovery_authority_lifecycle` passed.

## Evidence produced

- Exact LAB-085 current suite: 38/38 passed after the initialization fix.
- LAB-085 compileall: passed.
- Exact current implementation blobs were reconstructed through the GitHub connector; the two newly modified blobs match the locally executed bytes.
- The exact merged source stack for LAB-036/080/082/083/084 was reconstructed and blob-checked; lower-layer test files are the remaining reconstruction/execution work.
- Unsafe HMAC-only new break-glass entry point remains blocked on `SupportedRecoveryCustodyLedger`; new consequential recovery requires both Ed25519 public custody quorum and compatibility LAB-084 HMAC quorum in one SQLite transaction.
- Direct shell GitHub access was probed again and remains unavailable due DNS; connector reconstruction is the safe supported fallback.

## Known blockers / constraints

- No owner/product blocker.
- PR #162 must remain draft until the remaining regression and audit gate is complete.
- Historical LAB-084 break-glass proofs created before the final-custody cutoff remain HMAC-based compatibility history; Issue #163 / LAB-086 owns their asymmetric migration. This does not authorize HMAC-only new effects.
- The LAB-085 exact suite is clean, but the promised exact merged LAB-084/083/082/080 regression suites have not yet all been executed in this runtime.

## Exact next action

Continue from PR #162 HEAD `aacb4af1855f8afadac57b1564fd4cb452cf490b` without repeating the LAB-085 reconstruction. Reconstruct the exact corrected test files from merged `main` for LAB-084 (`provider_rotation_recovery`), LAB-083 (`provider_threshold_rotation`), LAB-082 (`asymmetric_provider_history`), and LAB-080 (`shared_anchor_intent_ledger`) through the GitHub connector; verify each with `git hash-object` against its GitHub blob ID and execute their corrected regression suites against the already reconstructed exact source stack. Then run the LAB-085 unsafe seed (expected failure) and compileall.

If those are clean, perform one fresh full PR #162 patch audit, re-fetch PR metadata and confirm the HEAD is unchanged. Mark PR ready and squash-merge only if both execution and audit remain clean. Then close Issue #161 DONE and advance Issue #163 / LAB-086. If any regression or audit defect appears, fix it on the branch, repeat the affected exact-source tests, and keep PR draft.

## Backlog

- #161 / LAB-085 — recovery-authority lifecycle + asymmetric custody — IN_PROGRESS; exact LAB-085 38/38 clean after fixing real initialization defect; lower-layer regression/final-audit gate remains.
- #163 / LAB-086 — asymmetric migration of historical pre-cutoff LAB-084 break-glass proofs — READY after LAB-085.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
