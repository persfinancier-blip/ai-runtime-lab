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

The cumulative exact lower-stack evidence remains: LAB-080 18/18 PASS, LAB-082 28/28 PASS, LAB-083 24/24 PASS, LAB-084 17/17 PASS, LAB-085 core 12/12 PASS plus LAB-085 asymmetric-custody 8/8 PASS.

## Evidence produced / reconfirmed

- Exact current-head `strict_fence.py` blob `9506a7a9996b35eb1e52092c01966e64fddd177d`; local bytes matched exactly.
- Exact current-head `test_strict_fence.py` blob `4b651db3638c8b9f2341d52b512f075c4b3c31d2`; local bytes matched exactly.
- Exact current-head `test_inherited_sql_fence.py` blob `e946b40d17a57f88421bb80a50bafed2ca27a728`; local bytes matched exactly.
- Current-head SQL-fence modules: **12/12 PASS**.
- Covered: forged proof row not becoming mutation authority; DELETE/INSERT OR REPLACE/UPSERT/UPDATE OR REPLACE public paths; transaction rollback restoring the fence; obsolete weak-trigger replacement; direct lower normal-root/provider canonical inserts denied; controlled transaction-scoped fence removal/reinstallation succeeds.
- Cumulative exact lower stack: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8; recorded lower unsafe baselines failed as expected.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.
- LAB-089 / #168 remains the separate same-root ordering ambiguity; no authority escalation is claimed from it.

## Known blockers / constraints

- Full LAB-086 merge gate remains incomplete: finish exact LAB-085 final/public-custody tests in one connector-reconstructed closure, then execute all current LAB-086 real-schema tests, unsafe seed, full compileall and final audit.
- The new 12/12 result closes only the current-head SQL-fence subgate; it is not a substitute for current-head real-schema integration execution.
- Shell GitHub transport is unavailable in this run; connector reconstruction works and is not an owner blocker.
- LAB-083/LAB-084 signer-noise issue #167 is fail-closed DoS/robustness and remains separate unless downstream results invalidate LAB-086.
- Same-root public-recovery ordering ambiguity is LAB-089 / #168. Treat as a LAB-086 blocker only if merged-stack acceptance tests require that sequence before merge.
- LAB-086 SQLite fences protect against stale/alternate supported mutation paths, not arbitrary same-privilege raw SQLite DDL. That broader trust boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Finish exact LAB-085 `public_custody_supported.py` / `final_supported.py` dependency reconstruction and execute the remaining corrected public-custody/final tests; verify all executable/test Git blobs.
2. Re-fetch the then-current PR #165 HEAD and execute the complete LAB-086 real-schema suite, including migration v4 root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer/direct-surface, inherited-writer guards, final verification snapshot, public-rotation history guard and rotation races.
3. Run LAB-086 unsafe legacy-promotion seed and compileall over the full closure.
4. Perform the final security audit of every consequential writer/restart path and re-check branch/main divergence. If the same-root ordering scenario is exposed by current acceptance tests, fix it in LAB-086; otherwise keep it isolated in #168.
5. Keep PR #165 draft until the entire current-head gate is clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact current-head SQL-fence subgate now 12/12 PASS; full merged-stack gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; signer-noise robustness in LAB-083/LAB-084 threshold collectors.
- #168 / LAB-089 — READY; authenticated ordering for public-recovery rotation vs asymmetric recovery under the same normal-root version.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
