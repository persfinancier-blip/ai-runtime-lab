# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `b17681f4716d6193463f553c26fec3e0e7e5b1da`.
- PR remains draft; full current-head merged-stack exact-source regression gate has not passed.

## Last completed step

Closed the current-head SQL-fence subgate with exact-source execution rather than a semantic harness. Direct shell GitHub transport was probed and remains unavailable (`Could not resolve host: github.com`), so connector reconstruction was used.

Exact PR #165 `strict_fence.py`, `test_strict_fence.py`, and `test_inherited_sql_fence.py` were reconstructed and verified by local `git hash-object` against GitHub blobs. Both test modules were executed together: **12/12 PASS**. This covers public mutation conflict algorithms plus direct lower normal-root/provider canonical write points after cutoff.

A fresh state-machine audit also corrected the LAB-089 premise: the previously recorded same-root counterexample omitted the fact that `recover_rotation_authority_asymmetric()` always advances the normal-root head N→N+1. Therefore a later public-recovery rotation cannot still be coauthorized by the old root N through supported writers. #168 remains open only until a real-stack regression executes both serializations/race; do not design a new ordering protocol unless that regression disproves the correction.

The cumulative exact lower-stack evidence remains: LAB-080 18/18 PASS, LAB-082 28/28 PASS, LAB-083 24/24 PASS, LAB-084 17/17 PASS, LAB-085 core 12/12 PASS plus LAB-085 asymmetric-custody 8/8 PASS.

## Evidence produced / reconfirmed

- Exact current-head `strict_fence.py` blob `9506a7a9996b35eb1e52092c01966e64fddd177d`; local bytes matched exactly.
- Exact current-head `test_strict_fence.py` blob `4b651db3638c8b9f2341d52b512f075c4b3c31d2`; local bytes matched exactly.
- Exact current-head `test_inherited_sql_fence.py` blob `e946b40d17a57f88421bb80a50bafed2ca27a728`; local bytes matched exactly.
- Current-head SQL-fence modules: **12/12 PASS**; focused compileall PASS.
- Covered: forged proof row not becoming mutation authority; DELETE/INSERT OR REPLACE/UPSERT/UPDATE OR REPLACE public paths; transaction rollback restoring the fence; obsolete weak-trigger replacement; direct lower normal-root/provider canonical inserts denied; controlled transaction-scoped fence removal/reinstallation succeeds.
- Cumulative exact lower stack: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8; recorded lower unsafe baselines failed as expected.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.
- #168 comment now records why the earlier same-root counterexample is impossible under the supported root-successor transition; pending real-stack confirmation rather than assumed blocker status.

## Known blockers / constraints

- Full LAB-086 merge gate remains incomplete: finish exact LAB-085 final/public-custody tests in one connector-reconstructed closure, then execute all current LAB-086 real-schema tests, unsafe seed, full compileall and final audit.
- The new 12/12 result closes only the current-head SQL-fence subgate; it is not a substitute for current-head real-schema integration execution.
- Shell GitHub transport is unavailable in this run; connector reconstruction works and is not an owner blocker.
- LAB-083/LAB-084 signer-noise issue #167 is fail-closed DoS/robustness and remains separate unless downstream results invalidate LAB-086.
- LAB-089 / #168 is now a verification question, not an established defect: run real supported-writer serializations before adding protocol complexity.
- LAB-086 SQLite fences protect against stale/alternate supported mutation paths, not arbitrary same-privilege raw SQLite DDL. That broader trust boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Finish exact LAB-085 `public_custody_supported.py` / `final_supported.py` dependency reconstruction and execute the remaining corrected public-custody/final tests; verify all executable/test Git blobs.
2. Re-fetch the then-current PR #165 HEAD and execute the complete LAB-086 real-schema suite, including migration v4 root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer/direct-surface, inherited-writer guards, final verification snapshot, public-rotation history guard and rotation races.
3. Include a real supported-writer regression for the #168 ordering question: public rotation first then recovery, and recovery first then public rotation. Close #168 as invalid if both restart cleanly and root-version ordering remains unambiguous.
4. Run LAB-086 unsafe legacy-promotion seed and compileall over the full closure.
5. Perform the final security audit of every consequential writer/restart path and re-check branch/main divergence. Keep PR #165 draft until the entire current-head gate is clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact current-head SQL-fence subgate now 12/12 PASS; full merged-stack gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; signer-noise robustness in LAB-083/LAB-084 threshold collectors.
- #168 / LAB-089 — VERIFY premise against real supported-writer serializations before implementation; prior toy counterexample omitted mandatory root N→N+1 advancement.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
