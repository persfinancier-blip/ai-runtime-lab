# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `2f8b4e4cd9a77470c4c9caddbd7d62a686d11429`.
- PR remains draft; full current-head merged-stack exact-source regression gate has not passed.

## Last completed step

A fresh consequential-writer audit found a cross-layer gap after the earlier inherited-writer fence work. Final root/provider/public writers verified LAB-086 root/recovery proofs but did not first run the lower LAB-080/082 durable verifier, so a new successor could commit over already-corrupt shared-anchor/provider history that only a later full restart would notice. In addition, a retained direct `SupportedAsymmetricBreakGlassLedger` could still call `recover_rotation_authority_asymmetric()` and update the normal-root head outside the final wrapper.

The branch now closes both paths. `final_supported.py` performs lower committed-history verification while already holding `BEGIN IMMEDIATE` before every consequential writer; provider rotation additionally verifies the uncommitted asymmetric-provider history before commit. The final surface now owns asymmetric recovery itself with pre/post verification. `strict_fence.py` adds a post-cutoff root-head UPDATE fence so a direct suffix recovery rolls back; only the final writer temporarily removes/reinstalls that fence inside its verified transaction.

Added a self-contained root-head fence regression and a real-stack lower-history/final-recovery regression. The exact updated SQL-fence layer was reconstructed from the published branch and executed: existing strict/conflict tests + inherited-writer tests + new root-head tests passed **14/14**; focused compileall passed. The new real-stack `final_supported.py` paths are published but are not yet counted as executed until the full dependency closure is reconstructed.

The cumulative exact lower-stack evidence remains: LAB-080 18/18 PASS, LAB-082 28/28 PASS, LAB-083 24/24 PASS, LAB-084 17/17 PASS, LAB-085 core 12/12 PASS plus LAB-085 asymmetric-custody 8/8 PASS.

## Evidence produced / reconfirmed

- Exact updated `strict_fence.py` blob `57cf5b11d927d5cd90f029f3db6dfbf9a9effd7e`; local bytes matched exactly.
- Exact unchanged `test_strict_fence.py` blob `4b651db3638c8b9f2341d52b512f075c4b3c31d2`.
- Exact unchanged `test_inherited_sql_fence.py` blob `e946b40d17a57f88421bb80a50bafed2ca27a728`.
- Exact new `test_root_head_fence.py` blob `376f70bafc26325d3710e536cf7f060105bbcdcb`; local bytes matched exactly.
- Updated SQL-fence modules: **14/14 PASS**; focused compileall PASS.
- Covered: forged proof row not mutation authority; DELETE/INSERT OR REPLACE/UPSERT/UPDATE OR REPLACE public paths; rollback restores fence; obsolete weak-trigger replacement; direct lower normal-root/provider canonical inserts denied; direct normal-root head UPDATE denied; controlled transaction-scoped fence removal/reinstallation succeeds.
- Current published `final_supported.py` blob `00cd339ff8a0fb5f00b9f75dcab294b0aea48c45` contains lower-history prechecks and the final asymmetric-recovery writer. Its new real-stack regression is `test_full_lower_history_guard.py`; execution is still pending the full reconstructed closure.
- Cumulative exact lower stack: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8; recorded lower unsafe baselines failed as expected.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.
- #168 remains a verification question, not an established defect: the earlier toy same-root counterexample omitted mandatory normal-root N→N+1 advancement by asymmetric recovery.

## Known blockers / constraints

- Full LAB-086 merge gate remains incomplete: finish exact LAB-085 final/public-custody tests in one connector-reconstructed closure, then execute all current LAB-086 real-schema tests including the new lower-history/final-recovery regressions, unsafe seed, full compileall and final audit.
- The new 14/14 result closes only the updated SQL-fence subgate; it is not a substitute for current-head real-schema integration execution.
- Current `final_supported.py` changed after the previously executed wrapper tests; do not count old wrapper evidence for blob `00cd339f...` until the real-stack tests execute.
- Shell GitHub transport is unavailable in this run; connector reconstruction works and is not an owner blocker.
- LAB-083/LAB-084 signer-noise issue #167 is fail-closed DoS/robustness and remains separate unless downstream results invalidate LAB-086.
- LAB-089 / #168 is now a verification question; run real supported-writer serializations before adding protocol complexity.
- LAB-086 SQLite fences protect against stale/alternate supported mutation paths, not arbitrary same-privilege raw SQLite DDL. That broader trust boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Finish exact LAB-085 `public_custody_supported.py` / `final_supported.py` dependency reconstruction and execute `test_public_custody_supported.py` + `test_final_supported.py`; verify all executable/test Git blobs.
2. Re-fetch the then-current PR #165 HEAD and reconstruct current LAB-086 `final_supported.py` plus all real-schema test dependencies. Execute the complete suite including `test_full_lower_history_guard.py`, migration v4 root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer/direct-surface, inherited/root-head fences, final verification snapshot, public-rotation history guard and rotation races.
3. Include a real supported-writer regression for #168 ordering: public rotation first then recovery, and recovery first then public rotation. Close #168 as invalid if both restart cleanly and root-version ordering remains unambiguous.
4. Run LAB-086 unsafe legacy-promotion seed and compileall over the full closure.
5. Perform the final security audit of every consequential writer/restart path and re-check branch/main divergence. Keep PR #165 draft until the entire current-head gate is clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; updated exact SQL-fence subgate 14/14 PASS; new lower-history/final-recovery code awaits real-stack execution.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; signer-noise robustness in LAB-083/LAB-084 threshold collectors.
- #168 / LAB-089 — VERIFY premise against real supported-writer serializations before implementation.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
