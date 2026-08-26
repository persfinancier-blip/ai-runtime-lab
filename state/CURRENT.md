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

## Last completed step

Finished LAB-087 exactly while LAB-086 bulk dependency export remains unavailable in this runtime.

Exact current LAB-087 source/test blobs were reconstructed and executed. The pre-audit suite passed 12/12. A separate adversarial filesystem audit then reproduced a namespace bypass: with the protected DB directory under a broker-owned `0777` non-sticky ancestor, the distinct worker UID could rename the entire protected directory and create a replacement without writing inside the protected directory.

LAB-087 now verifies the full lexical ancestor chain in addition to the immediate DB directory/file: ancestors must be root/broker-owned; group/world-writable ancestors are rejected unless sticky-bit semantics protect broker-owned child names (for example `/tmp`). The corrected published blobs are `process_boundary.py` `87456dfcbeac0c0e795fc0bcdeb3502cf57fcdd0` and `test_process_boundary.py` `eacffa649db7e848de6b17cbf734b4fbc7f6cae3`. Exact full suite after publication: **14/14 PASS**; compileall PASS. Final audit found no remaining blocker inside the stated Unix-DAC/process boundary. Issue #166 was closed completed.

Returned to LAB-086 after integration. Fresh branch/main compare after the LAB-087 merge is `ahead 146 / behind 89`; all 56 PR paths remain additions relative to main. A current-head source audit of `migration_guard -> strict_fence -> suffix` found no new privilege-escalation/stale-supported-writer blocker in this run. Issue #163 comment `5421449169` records the continuation report.

## Evidence produced / reconfirmed

LAB-087 final exact evidence:
- `experiments/sqlite_schema_control/protocol.py` blob `5c999166c2155baa5ce3f644c36efe0e01e4e3fe`.
- `experiments/sqlite_schema_control/process_boundary.py` blob `87456dfcbeac0c0e795fc0bcdeb3502cf57fcdd0`.
- `tests/test_protocol.py` blob `3f795d22d844293d62a09a0c1285764443db2279`.
- `tests/test_process_boundary.py` blob `eacffa649db7e848de6b17cbf734b4fbc7f6cae3`.
- Full exact suite: 14/14 PASS; compileall PASS.
- Process negative controls: broker UID remains writable; an unrestricted writable SQLite connection bypasses connection-scoped authorizer as expected.
- Filesystem negative control/fix: writable non-sticky ancestor replacement attack reproduced pre-fix and rejected post-fix.

LAB-086 cumulative exact lower-stack evidence remains:
- LAB-080 18/18 PASS.
- LAB-082 28/28 PASS.
- LAB-083 24/24 PASS.
- LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS, asymmetric-custody 8/8 PASS, public/final 11/11 PASS.
- Exact standalone LAB-086 corrected suite previously passed 12/12; focused migration/fence evidence remains recorded in Issue #163 / PR #165.
- Current migration guard blob: `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
- Current least-privilege fence blob: `5da01e28a9f813a136d138637f855940f04aab46`.
- Current suffix blob: `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`.

## Known blockers / constraints

- LAB-086 remaining merge gate: execute current `test_pre_cutoff_lower_evidence_cardinality.py`, then the full current-head real-schema migration/suffix/final-supported/security suite from one exact LAB-080→086 dependency closure; run unsafe seed, compileall and final audit.
- Direct shell/raw GitHub transport remains unavailable; connector reads work, but no safe bulk exact-byte repository export into the local executor was observed. File-by-file exact reconstruction remains the safe path.
- LAB-086 branch is substantially diverged (`ahead 146 / behind 89` after LAB-087 merge); reconcile only after the test/security gate is clean.
- LAB-086 fences cover audited supported/DML paths. LAB-087 now supplies the separate process/filesystem/write-handle boundary; root, broker UID, `CAP_DAC_OVERRIDE`, ACL/capability policy outside mode bits and privileged namespace replacement remain outside that claim.
- LAB-088/#167 signer-noise, LAB-090/#169 provider handoff freshness, and LAB-091/#170 mutable shared-anchor/new-receipt authorization remain separate follow-ups.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct the exact current LAB-086 dependency closure required by `test_pre_cutoff_lower_evidence_cardinality.py`, verify executable files with `git hash-object`, and execute that regression against migration guard blob `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
2. Execute current `test_suffix.py` and every remaining LAB-086 real-schema migration/final-supported/security module on the same closure, followed by unsafe legacy-promotion seed and full compileall.
3. Perform a fresh final security audit focused on reverse evidence cardinality, cutoff/root/public proof binding, alternate supported mutation paths, transaction-scoped thaw/restoration, restart snapshots and rotation races.
4. Re-check branch/main divergence. Keep PR #165 draft until the complete current-head gate is clean; only then reconcile and integrate using supported auditable operations.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact current-head real-ledger gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable shared-ledger plus new provider-receipt writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
