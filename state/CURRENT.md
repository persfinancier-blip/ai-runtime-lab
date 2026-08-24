# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed branch remains draft/mergeable; full current-head merged-stack exact-source regression gate has not passed.

## Last completed step

The cumulative exact lower-stack gate already recorded remains: LAB-080 18/18 PASS, LAB-082 28/28 PASS, LAB-083 24/24 PASS, LAB-084 17/17 PASS, LAB-085 core 12/12 PASS plus LAB-085 asymmetric-custody 8/8 PASS. Current LAB-086 final wrapper/SQL-fence candidate was re-read from the live branch; inherited normal-root/provider writers remain explicitly guarded/fenced after cutoff.

A fresh semantic audit found a separate fail-closed ordering ambiguity in `_verify_public_recovery_rotations_locked()`: public-recovery activation windows are derived from normal-root version only. Executable counterexample: cutoff at root v7 with P1 -> asymmetric recovery under P1 while root remains v7 -> later P1->P2 public-recovery rotation also under root v7. The current derived windows become `P1=[7,7)`, `P2=[7,∞)`, so restart rejects the earlier valid P1 recovery (`7 >= 7`). This is availability/history-ordering ambiguity, not an authority escalation. It is now tracked as LAB-089 / Issue #168 rather than silently expanding LAB-086.

## Evidence produced / reconfirmed

- Cumulative exact lower stack: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8; recorded lower unsafe baselines failed as expected.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.
- Live branch `final_supported.py` currently contains explicit pre/post `_verify_lab086_locked` guards for normal root/provider/public recovery consequential writers plus transaction-scoped SQL fence removal/restoration.
- Fresh branch/main compare observed diverged state at ahead 84 / behind 36 with LAB-086 paths remaining additions.
- LAB-089 / #168 created with executable same-root ordering counterexample and acceptance criteria.

## Known blockers / constraints

- Full LAB-086 merge gate remains incomplete: finish exact LAB-085 final/public-custody tests in one connector-reconstructed closure, then execute all current LAB-086 real-schema tests, unsafe seed, full compileall and final audit.
- Focused/static evidence is not a substitute for the current-head merged-stack run.
- File-by-file connector reconstruction is slower because shell GitHub transport is unavailable; connector reconstruction works and is not an owner blocker.
- LAB-083/LAB-084 signer-noise issue #167 is fail-closed DoS/robustness and remains separate unless downstream results invalidate LAB-086.
- Same-root public-recovery ordering ambiguity is LAB-089 / #168. Treat as a LAB-086 blocker only if the merged-stack gate or acceptance criteria require that sequence to be valid before merge.
- LAB-086 SQLite fences protect against stale/alternate supported mutation paths, not arbitrary same-privilege raw SQLite DDL. That broader boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Finish connector reconstruction/execution of exact LAB-085 `asymmetric_custody.py`, `custody_break_glass.py`, `supported.py`, `public_custody_supported.py`, `final_supported.py` and their remaining corrected tests; verify Git blob identities and run together with compileall.
2. Re-fetch the then-current PR #165 HEAD and execute the complete LAB-086 real-schema suite, including inherited-writer/direct-surface/SQL-fence, migration v4 root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer, strict conflict algorithms, final verification snapshot and rotation races.
3. Run LAB-086 unsafe legacy-promotion seed and compileall over the full closure.
4. Perform the final security audit of every consequential writer/restart path and re-check branch/main divergence. If the same-root ordering scenario is exposed by current acceptance tests, fix it in LAB-086; otherwise keep it isolated in #168.
5. Keep PR #165 draft until the entire current-head gate is clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; full merged-stack gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; signer-noise robustness in LAB-083/LAB-084 threshold collectors.
- #168 / LAB-089 — READY; authenticated ordering for public-recovery rotation vs asymmetric recovery under the same normal-root version.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
