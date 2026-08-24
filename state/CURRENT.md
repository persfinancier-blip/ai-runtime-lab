# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed branch/PR HEAD: `d467c050cfcf8101650124f96c41aca33b35c017`.
- PR remains draft; full current-head merged-stack exact-source regression gate has not passed.

## Last completed step

Re-read `AGENTS.md`, `state/CURRENT.md` and `prompts/SELF_RESUME.md`, re-probed direct GitHub shell transport (still unavailable because DNS cannot resolve `github.com`), and continued through the GitHub connector.

Re-checked the current branch rather than trusting stale PR metadata. Current branch/PR HEAD is `d467c050cfcf8101650124f96c41aca33b35c017`. Fresh compare against current main is diverged `ahead 96 / behind 45`; all 32 PR paths remain additions with no current path-level overlap. PR mergeability is currently false because of branch divergence and the full gate remains incomplete.

Closed LAB-089 / Issue #168 as `not_planned` after verifying that its premise is impossible through the supported LAB-086 consequential writer. `recover_rotation_authority_asymmetric()` calls `_require_successor(old,new)`, requiring the normal/root version and generation to advance exactly one. A focused executable reproduction rejected `(v7,g7)->(v7,g7)` and accepted only `(v7,g7)->(v8,g8)`. Therefore the proposed sequence `asymmetric recovery under P1 while root remains vN -> later P1->P2 rotation also under vN` cannot occur on the supported path; no new ordering protocol is justified by that counterexample.

A fresh source audit of current `final_supported.py`, `strict_fence.py` and the inherited-writer regression surface found no new privilege-escalation blocker in this run. Current final writers still follow the intended pattern: full lower/LAB-086 verification, transaction-scoped fence removal, mutation, fence reinstall/assertion, and post-mutation verification before commit.

## Evidence produced / reconfirmed

- Current branch/PR HEAD: `d467c050cfcf8101650124f96c41aca33b35c017`.
- Current compare vs main: ahead 96 / behind 45; 32 changed paths, all additions.
- LAB-089/#168 closed `not_planned`; issue comment records the exact supported-writer invariant and focused executable reproduction.
- Focused successor invariant execution: `(v7,g7)->(v7,g7)` rejected; `(v7,g7)->(v8,g8)` accepted.
- Exact current-head isolated SQL-fence slice remains **17/17 PASS** with compileall PASS from the preceding run.
- Cumulative exact lower-stack evidence remains: LAB-080 18/18 PASS, LAB-082 28/28 PASS, LAB-083 24/24 PASS, LAB-084 17/17 PASS, LAB-085 core 12/12 PASS, LAB-085 asymmetric-custody 8/8 PASS; lower unsafe baselines failed as expected.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.
- Current branch contains the latest inherited-history INSERT/UPDATE/DELETE immutability and root-head INSERT/UPDATE/DELETE fence fixes recorded in Issue #163 and PR #165.

## Known blockers / constraints

- Remaining LAB-086 merge gate: exact LAB-085 `test_public_custody_supported.py` and `test_final_supported.py` plus their direct dependencies must still be executed in one connector-reconstructed workspace, followed by the entire current-head LAB-086 real-schema test suite, unsafe seed, compileall and final audit.
- Direct shell GitHub transport is unavailable in this runtime; connector reconstruction works and is not an owner-level blocker.
- LAB-083/LAB-084 signer-noise issue #167 remains fail-closed DoS/robustness and separate from LAB-086 unless downstream tests invalidate the candidate.
- LAB-089/#168 is closed as an invalid premise; do not add ordering-protocol complexity unless a real supported-writer execution later demonstrates a different ambiguity.
- LAB-086 SQLite fences cover stale/alternate supported mutation paths and the audited DML boundary, not arbitrary same-privilege raw SQLite DDL/schema control. That broader trust boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct exact main LAB-085 `public_custody_supported.py`, `final_supported.py`, `test_public_custody_supported.py`, `test_final_supported.py` and direct dependencies into one connector-sourced workspace; verify executable/test bytes against GitHub blob identities and execute those remaining LAB-085 tests.
2. Re-fetch PR #165 HEAD before execution, reconstruct all current LAB-086 implementation/tests, and run the complete real-schema suite: migration v4 root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer/direct-surface, inherited-history DML fences, strict conflict algorithms, root-head REPLACE/DELETE, final verification snapshot, inherited writer history guard and rotation races.
3. Run unsafe legacy-promotion seed and full `python -m compileall` over the reconstructed closure.
4. Perform one fresh full security audit of every consequential/restart mutation path plus branch/main conflict check. Fix every failure before changing PR #165 out of draft.
5. If the full gate is clean, mark PR #165 ready and integrate by normal merge if available; otherwise use only the documented audited file-scoped Contents API fallback after re-checking exact target state/conflicts.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; full current-head merged-stack gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary behind LAB-086 fences.
- #167 / LAB-088 — READY; signer-noise robustness in LAB-083/LAB-084 threshold collectors.
- #168 / LAB-089 — CLOSED `not_planned`; proposed same-root asymmetric-recovery sequence is impossible on the supported writer because root must advance exactly one.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
