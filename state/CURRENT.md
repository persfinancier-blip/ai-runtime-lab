# Current Lab State

Last updated: 2026-08-23

## Active objective

Finish LAB-085 by validating and integrating the newly found post-merge concurrency fix: intermediate public-custody verification must observe symmetric history, public history, and their binding under one write-excluding SQLite interval.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-084.
- Active: Issue #161 / LAB-085 — IN_PROGRESS.
- Previously integrated LAB-085 PR: #162 — squash-merged as `9aa67f3aae9a3cb25aadd50e62c85c29af533980`.
- Active fix branch: `lab/085-postmerge-snapshot-fix`.
- Active draft PR: #164 `[LAB-085] Fence intermediate custody verification to one SQLite snapshot`.
- PR #164 audited HEAD: `dbc5e440378e4bb6e6ed29600362645c0c47b722`.
- Follow-up only after LAB-085 is truly DONE: Issue #163 / LAB-086.

## Last completed step

A fresh post-merge source audit found that `SupportedPublicRecoveryAuthorityLifecycleLedger.verify_durable()` performed three authoritative checks in separate SQLite snapshots: symmetric recovery-lifecycle verification, public Ed25519 custody-history verification, and cross-history binding verification. A concurrent writer could commit after one proof verifier returned but before the final binding-only pass, which does not re-run every threshold-signature verifier.

The defect was patched in draft PR #164. The intermediate supported surface now holds `BEGIN IMMEDIATE` across all three verification layers. Because the final `SupportedRecoveryCustodyLedger` already had an outer write-excluding guard, its verifier was refactored to invoke the lower authoritative layers directly under that one guard rather than nesting the intermediate guard.

A new regression places a writer exactly at the transition to public-history verification. A focused SQLite schedule reproduction observed the expected distinction: the old separate-snapshot schedule allowed the writer to commit between phases, while the fixed schedule kept the writer blocked until verification completed.

A fresh remote patch audit of PR #164 found exactly three intended files changed and no additional blocking defect.

## Evidence produced

- Draft PR #164 / branch `lab/085-postmerge-snapshot-fix`.
- `public_custody_supported.py` fix commit `d18b9f9d23469ccc31fed1fdf06bb93a2c20b7c2`.
- `final_supported.py` nested-guard refactor commit `ec8c0fa415c49c1a9394231d0fed0ed0dfba7e76`.
- regression commit / current PR HEAD `dbc5e440378e4bb6e6ed29600362645c0c47b722`.
- Focused SQLite scheduler reproduction: old model observed writer completion between phases; fixed `BEGIN IMMEDIATE` model did not.
- PR #164 patch audit: only `final_supported.py`, `public_custody_supported.py`, and `tests/test_public_custody_supported.py`; no unrelated paths.
- Prior immutable evidence still exists but is not rewritten as current-head execution: LAB-085 38/38; LAB-080/082/083/084 87/87; focused custody 8/8; unsafe seed expected failure; compileall passed.

## Known blockers / constraints

- Direct shell GitHub access is still unavailable in the current runtime: DNS resolution fails, and a direct-IP fallback also could not connect. GitHub connector reconstruction remains the supported exact-source route.
- PR #164 has not yet passed the full exact-source current-head regression stack. Do not merge it or mark LAB-085 DONE before that gate.
- Historical LAB-084 break-glass proofs before the authenticated custody cutoff remain HMAC-verifiable compatibility history. LAB-086 owns their migration only after LAB-085 closes.
- Whole-store rollback freshness remains a separate external-anchor responsibility.

## Exact next action

Reconstruct exact PR #164 HEAD `dbc5e440378e4bb6e6ed29600362645c0c47b722` plus merged LAB-080/082/083/084 executable/test dependencies through the GitHub connector and verify each local file against its Git blob identity. Execute the LAB-085 corrected suite including `test_intermediate_verification_holds_one_write_excluding_interval`, then LAB-080/082/083/084 regressions, LAB-085 unsafe seed, and compileall. If any test fails, fix and repeat. If clean, perform one more remote patch audit, mark PR #164 ready, merge normally, verify the merged file identities, close Issue #161 DONE, and only then begin Issue #163 / LAB-086.

## Backlog

- #161 / LAB-085 — IN_PROGRESS; post-merge concurrency defect patched in draft PR #164, exact-source gate pending.
- #163 / LAB-086 — READY only after LAB-085 DONE; migrate historical LAB-084 HMAC recovery proofs to asymmetric/public-verification history.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
