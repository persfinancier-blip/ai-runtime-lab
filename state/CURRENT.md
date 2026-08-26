# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `6a368a26e85c5d0672a527481f44f47283c8f951`.
- PR is mergeable but remains draft; full current-head real-ledger gate is not complete.
- Parallel LAB-087/#166 remains IN_PROGRESS; its exact authorizer/process/filesystem gate was previously 12/12 PASS.

## Last completed step

Continued the current-head LAB-086 gate audit after exact migration-guard 11/11 and corrected scrubbed-prefix/final-writer 1/1 had passed.

The strengthened least-privilege fence exposed the same stale test-harness assumption in `test_suffix.py`: three tests performed *successful* consequential asymmetric recovery directly through `SupportedAsymmetricBreakGlassLedger` after cutoff, although direct suffix mutation is intentionally denied and only `SupportedFencedAsymmetricBreakGlassLedger` may thaw the creation/head-update gates.

Only the successful mutation cases were changed to wrap the migrated ledger with `SupportedFencedAsymmetricBreakGlassLedger.from_existing(...)`; negative tests that must fail before mutation remain on the underlying suffix surface. No runtime fence was weakened.

Branch commit `6a368a26e85c5d0672a527481f44f47283c8f951`; new `test_suffix.py` blob `14b87522974a365738a56d82923ed9ae377a752e`.

Direct shell GitHub transport is unavailable in this run (`Could not resolve host: github.com`); connector read/write works and is not an owner blocker.

## Evidence produced / reconfirmed

- Exact LAB-086 migration guard integration: 11/11 PASS from the prior reconstructed current-head closure.
- Exact corrected scrubbed-prefix → final-writer → restart regression: 1/1 PASS.
- Current LAB-086 implementation blobs previously reconstructed exactly: migration guard `5a5bb928...`, strict fence `5da01e28...`, suffix `44847bde...`, final supported `ceb7f48a...`.
- The current source audit found and corrected three stale successful direct-suffix mutation calls in `test_suffix.py`; no new PASS count is claimed for that changed module until it is executed in the exact closure.
- Cumulative exact lower-stack evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric-custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.

## Known blockers / constraints

- Full current-head LAB-086 gate is still incomplete: the updated exact `test_suffix.py` and remaining final-supported/security modules must be connector-reconstructed and executed, followed by unsafe legacy-promotion seed, full compileall and final audit.
- Do not weaken the runtime fence to satisfy old direct-suffix tests. Successful consequential mutation after cutoff must use the final fenced surface.
- Direct shell GitHub transport is unavailable in this runtime; connector reconstruction works.
- LAB-086 SQL fences cover audited supported/DML paths, not arbitrary same-privilege schema/DDL authority; LAB-087/#166 owns that boundary.
- LAB-088/#167 signer-noise, LAB-090/#169 provider handoff freshness, and LAB-091/#170 mutable shared-anchor/new-receipt authorization remain separate follow-ups.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct and execute exact current `test_suffix.py` blob `14b87522974a365738a56d82923ed9ae377a752e` against the already proven LAB-080→085 closure and current LAB-086 implementation bytes.
2. Continue the remaining current-head real-ledger security modules: orphan/partial migration, full lower/public-history guards, public-rotation cross-binding/history, inherited/direct surfaces, rotation races, final single-snapshot verification and strict DML/fence regressions not already counted in this closure.
3. Run unsafe legacy-promotion seed and full compileall over the complete reconstructed closure.
4. Perform a fresh security audit of every consequential/restart path and re-check branch/main divergence. Fix every blocking failure before ready/merge.
5. Only after the complete current-head gate is clean, mark PR #165 ready and integrate; otherwise keep it draft with exact evidence and next action recorded.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; migration guard 11/11 and corrected scrubbed-suffix 1/1 PASS; `test_suffix.py` successful mutation paths now corrected to final writer and await exact execution.
- #166 / LAB-087 — IN_PROGRESS; prior exact current slice 12/12 PASS.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable/shared-ledger plus new provider-receipt writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
