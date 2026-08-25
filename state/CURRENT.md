# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `d467c050cfcf8101650124f96c41aca33b35c017`.
- PR is open/draft/mergeable; the migration/suffix/final-supported current-head real-schema gate remains.

## Last completed step

Closed three current-head evidence slices in the connector-reconstructed workflow.

First, the remaining LAB-085 public-custody/final tests were executed from Git-blob-verified current-main bytes:
`test_public_custody_supported + test_final_supported` => **11/11 PASS**. Compileall over the reconstructed LAB-036/080/082/083/084/085 closure passed.

Second, current-head LAB-086 DML-fence regressions were reconstructed from branch bytes and verified by `git hash-object`:
- `strict_fence.py` `62a9b602edb8692894cad3874ba6d5c211129aa5`;
- `test_strict_fence.py` `4b651db3638c8b9f2341d52b512f075c4b3c31d2`;
- `test_inherited_sql_fence.py` `7a2ce4ed521ce523250c4331ab14f1847d322d6a`;
- `test_root_head_fence.py` `5ccdc88d192565e31a3541ce228261bd65e32c16`.
Combined current-head fence execution => **17/17 PASS** plus compileall.

Third, the current-head final single-snapshot verifier was reconstructed and executed. Exact `final_supported.py` Git blob `9f0198d2db85d08ec64f614d6288323c1d642383` matched the locally executed implementation; exact `test_final_verification_snapshot.py` blob `0426dcfe61bef665bcbc5c21b937d805f223da64` also matched. The exact test passed **1/1** using import-only lower-layer stubs; the test intentionally monkeypatches the lower verifier and isolates only the transaction serialization contract. It observed the final `BEGIN IMMEDIATE` already held while the lower verifier ran, the public-custody verifier ran, and the LAB-086 locked verifier ran; a competing writer was blocked. This is focused current-head evidence, not a substitute for the remaining real-schema migration/suffix gate.

## Evidence produced / reconfirmed

- Lower-stack exact gate is complete:
  - LAB-080 18/18 PASS.
  - LAB-082 28/28 PASS.
  - LAB-083 24/24 PASS.
  - LAB-084 17/17 PASS.
  - LAB-085 core 12/12 PASS.
  - LAB-085 asymmetric-custody 8/8 PASS.
  - LAB-085 public/final 11/11 PASS.
  - Lower unsafe baselines failed as expected; compileall passed on reconstructed layers.
- Current-head LAB-086 exact fence subgate: **17/17 PASS** + compileall PASS.
- Current-head LAB-086 exact final single-snapshot contract: **1/1 PASS**; exact implementation blob `9f0198d2...`, exact test blob `0426dcfe...`.
- Current PR #165 implementation manifest at HEAD `d467c050...`:
  - `final_supported.py` `9f0198d2db85d08ec64f614d6288323c1d642383`.
  - `migration_guard.py` `332995323d8d74fcc0f377d0e74bb0f30b8735c1`.
  - `protocol.py` `cccb531fa13b8f8d4e3a7c3163dd7c7cbeb3ec41`.
  - `strict_fence.py` `62a9b602edb8692894cad3874ba6d5c211129aa5`.
  - `suffix.py` `bb9f8e55fb03424ac19c152ae2d8aceaf2e1c078`.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.
- Branch/main compare previously observed: ahead 96 / behind 47; all 32 LAB-086 paths are additions. Re-check immediately before integration.
- LAB-089/#168 is CLOSED `not_planned`; do not treat it as active backlog.

## Known blockers / constraints

- Remaining LAB-086 merge gate is the current-head migration/suffix real-schema tests and remaining final-supported integration/history-guard tests, unsafe legacy-promotion seed, full compileall over the complete closure, and one final security audit.
- Direct shell GitHub transport is unavailable; connector reconstruction works and is not an owner-level blocker.
- The final single-snapshot 1/1 test uses exact branch implementation/test bytes but import-only stubs for lower modules by design of that isolated test; lower real implementations are separately covered by the completed LAB-080–085 gate.
- LAB-083/LAB-084 signer-noise issue #167 remains fail-closed DoS/robustness and separate from LAB-086 unless downstream tests invalidate the candidate.
- LAB-086 SQLite fences cover stale/alternate supported mutation paths and audited DML, not arbitrary same-privilege raw SQLite DDL/schema control; that broader boundary is LAB-087/#166.
- Logical SQL scrubbing is not forensic erasure. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Continue exact reconstruction of current PR #165 HEAD `d467c050cfcf8101650124f96c41aca33b35c017` beginning with `migration_guard.py`, `suffix.py` and their real-schema tests; verify every written file by Git blob identity.
2. Execute migration v4 root-coauthorization/restart, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer/direct-surface, full lower/public history guards and rotation-race tests. The strict/inherited/root-head fence slice and final single-snapshot contract are already done and need not be repeated unless a dependency changes.
3. Execute unsafe legacy-promotion expected-failure seed and full compileall over the complete closure.
4. Perform a fresh full security audit of every consequential/restart writer plus branch/main divergence. Fix every failure before changing PR #165 out of draft.
5. If the full gate is clean, mark PR #165 ready and integrate by normal merge when available; otherwise use only the documented audited file-scoped Contents API fallback after exact conflict checking.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; lower stack, current-head DML fence subgate, and final single-snapshot contract are clean; migration/suffix/full integration gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
