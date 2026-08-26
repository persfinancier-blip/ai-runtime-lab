# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `4d3da21ef2f8c0f782f5ce0146a04aaea0b62251`.
- PR remains draft; exact real-ledger current-head gate is incomplete.
- LAB-087 / Issue #166 is DONE; PR #171 squash-merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- LAB-088 / Issue #167 is IN_PROGRESS on branch `lab/088-threshold-signer-noise`, draft PR #172.

## Last completed step

Performed a fresh current-head source/security audit of LAB-086 through the GitHub connector after re-reading `migration_guard.py`, `strict_fence.py`, `suffix.py`, and `final_supported.py` from PR #165 HEAD `4d3da21...`.

No new privilege-escalation or stale-supported-writer bypass was established. The current final writer still follows the required serialized pattern under one `BEGIN IMMEDIATE`: verify committed lower/public history, verify complete LAB-086 history, verify the operation-specific authorization, remove only the least-privilege transaction-scoped fence subset, mutate, reinstall/assert the fence, re-verify affected LAB-086 history, then commit. Rollback restores temporary DDL changes together with data changes.

Migration guard reverse-cardinality was rechecked against LAB-083 semantics: root transitions must exactly cover all non-bootstrap roots with exactly one normal/recovery proof type, provider transitions must exactly cover all non-bootstrap provider generations, and threshold proofs must exactly cover provider transitions after threshold enablement. Boundary/projection/root-proof symmetry and post-cutoff public-recovery proof cardinality/cross-binding remain explicit.

Fresh branch/main compare: `ahead 146 / behind 92`. All 56 PR paths remain additions relative to current `main`, so the observed divergence is still history-only/path-nonoverlapping at file-path level. Issue #163 comment `5422572198` records this audit. This is source-audit evidence only; it does not replace the missing exact real-ledger execution gate.

## Evidence produced / reconfirmed

LAB-086 cumulative exact lower-stack evidence remains:
- LAB-080 18/18 PASS.
- LAB-082 28/28 PASS.
- LAB-083 24/24 PASS on pre-LAB-088 main source.
- LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS, asymmetric-custody 8/8 PASS, public/final 11/11 PASS.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.
- Current LAB-086 migration guard blob: `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
- Current LAB-086 least-privilege fence blob: `5da01e28a9f813a136d138637f855940f04aab46`.
- Current LAB-086 suffix blob: `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`.
- Current LAB-086 final-supported blob: `ceb7f48a55a931ba9923cac77d4ebf6c4cd2cfec`.
- Fresh compare: ahead 146 / behind 92; 56/56 PR paths are additions.

LAB-088 exact evidence remains:
- invalid-known-signer poisoning reproduced in all four affected LAB-083 collectors on old source;
- exact published corrected signer-noise suite 6/6 PASS;
- existing exact LAB-083 protocol/enablement/strict-type regressions 16/16 PASS on corrected source;
- combined 22/22 PASS + compileall PASS;
- draft PR #172 current observed HEAD `e6817daba5428d12818a3f8f4ee2c0b8318ff361`.

LAB-087 final exact evidence remains 14/14 PASS + compileall PASS and is merged/DONE.

## Known blockers / constraints

- LAB-086 remaining merge gate: execute current `test_pre_cutoff_lower_evidence_cardinality.py`, then the full current-head real-schema migration/suffix/final-supported/security suite from one exact LAB-080→086 dependency closure; run unsafe seed, compileall and final audit.
- Direct shell/raw GitHub transport remains unavailable. GitHub connector reads work; file-by-file exact reconstruction remains the safe execution path. A tested system raw-download fallback was also unavailable because raw web access is disabled in this runtime.
- The fresh audit found no new blocker but is not an executable current-head regression result.
- PR #165 is substantially diverged from current `main`; do not reconcile/integrate until the complete test/security gate is clean. Current file-level compare still shows additions only.
- LAB-088 PR #172 must remain draft until LAB-083 supported integration and downstream LAB-084/085/086 compatibility regressions pass.
- LAB-086 fences cover audited supported/DML paths. LAB-087 supplies the separate process/filesystem/write-handle boundary; root, broker UID, `CAP_DAC_OVERRIDE`, ACL/capability policy outside mode bits and privileged namespace replacement remain outside that claim.
- LAB-090/#169 provider handoff freshness and LAB-091/#170 mutable shared-ledger/new-receipt authorization remain separate follow-ups.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Resume LAB-086 as primary: connector-reconstruct the exact current LAB-080→086 closure required by `test_pre_cutoff_lower_evidence_cardinality.py`, verify executable files by Git blob, and execute the real regression against migration guard `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
2. On the same closure execute current `test_suffix.py` and all remaining LAB-086 migration/final-supported/security modules, then unsafe legacy-promotion seed and full compileall.
3. Perform the final LAB-086 security audit and branch/main reconciliation only after tests are clean; keep PR #165 draft until then.
4. LAB-088 follow-up: run LAB-083 supported-integration and downstream LAB-084/085/086 regressions on PR #172; if clean, final audit and integrate, otherwise fix before merge.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact current-head real-ledger gate remains primary.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172, exact 22/22 focused/core PASS, supported/downstream gate remains.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable shared-ledger plus new provider-receipt writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
