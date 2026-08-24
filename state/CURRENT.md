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
- PR remains draft; full current-head merged-stack exact-source regression gate has not passed.

## Last completed step

A fresh current-head DML audit found and fixed another post-cutoff durable-history gap. The inherited lower-history tables `provider_rotation_authority_transitions`, `provider_rotation_threshold_proofs`, and `asymmetric_provider_transitions` were fenced only on INSERT. Ordinary UPDATE or DELETE of an already committed authenticated row still succeeded after the LAB-086 cutoff, leaving persistent fail-closed state that would only be detected by a later verifier.

An executable pre-fix SQLite counterexample reproduced successful UPDATE and DELETE on all three tables. The branch now installs UPDATE/DELETE immutability triggers for each inherited history table in addition to the existing INSERT deny trigger. `remove_public_mutation_fence_locked()` removes/restores the complete set only for the verified final writer inside its `BEGIN IMMEDIATE`, and `assert_public_mutation_fence_locked()` requires all inherited DML triggers after cutoff. This does not expand the claim to arbitrary same-privilege DDL/schema control; that remains LAB-087 / #166.

Published commits:
- code fix `d689e161f360a0ccc55f113f7dfcc03da28f4b1e`;
- regression / current HEAD `d467c050cfcf8101650124f96c41aca33b35c017`.

The exact published `strict_fence.py`, `test_strict_fence.py`, new inherited-history regression, and root-head regression were reconstructed by Git blob identity and executed together. The current isolated SQL-fence slice passed **17/17** and compileall passed. The new inherited-history regression creates historical rows through the transaction-scoped final-writer path, reinstalls the fence, then proves UPDATE and DELETE fail with the original rows unchanged.

## Evidence produced / reconfirmed

- Exact current-head isolated SQL-fence slice: **17/17 PASS**.
- Exact current-head focused compileall for the fence package/tests: PASS.
- `strict_fence.py` blob: `62a9b602edb8692894cad3874ba6d5c211129aa5`.
- `test_strict_fence.py` blob: `4b651db3638c8b9f2341d52b512f075c4b3c31d2`.
- `test_inherited_sql_fence.py` blob: `7a2ce4ed521ce523250c4331ab14f1847d322d6a`.
- `test_root_head_fence.py` blob: `5ccdc88d192565e31a3541ce228261bd65e32c16`.
- Pre-fix executable counterexample: UPDATE and DELETE succeeded on all three inherited history tables.
- Prior current-head public-custody pre-commit guard remains on the branch: final consequential writers re-run LAB-085 public recovery Ed25519 transition verification before mutation.
- Previous root-head INSERT/REPLACE/DELETE fence fix remains on the branch.
- Cumulative exact lower-stack evidence remains: LAB-080 18/18 PASS, LAB-082 28/28 PASS, LAB-083 24/24 PASS, LAB-084 17/17 PASS, LAB-085 core 12/12 PASS, LAB-085 asymmetric-custody 8/8 PASS; lower unsafe baselines failed as expected.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.
- Fresh branch/main compare after this fix: ahead 96 / behind 43; all 32 LAB-086 paths remain additions with no path-level overlap against current main.
- Direct shell GitHub transport remains unavailable in this runtime; GitHub connector reconstruction/update is working and is the supported fallback.

## Known blockers / constraints

- Full LAB-086 merge gate remains incomplete after the new DML hardening: exact LAB-085 final/public-custody tests and all current-head LAB-086 real-schema tests must be executed together, followed by unsafe seed, compileall and final audit.
- The 17/17 result is exact current-head evidence for the isolated SQL-fence surface, not the full merged-stack gate.
- LAB-083/LAB-084 signer-noise issue #167 remains fail-closed DoS/robustness and separate from LAB-086 unless downstream tests invalidate the candidate.
- LAB-089 / #168 remains a verification question; do not add ordering protocol complexity unless real supported-writer tests reproduce it.
- LAB-086 fences cover the audited DML boundary and stale/alternate supported mutation paths, not arbitrary same-privilege raw SQLite DDL/schema control. That broader boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct/execute the remaining exact LAB-085 `test_public_custody_supported.py`, `test_final_supported.py` and direct dependencies in one connector-sourced workspace; verify executable files by Git blob identity.
2. Re-fetch PR #165 HEAD (do not assume `d467c050...` remains current), reconstruct current LAB-086 implementation/tests and execute the complete real-schema suite, explicitly including the inherited INSERT/UPDATE/DELETE fence regressions, public-custody history guard, root-head REPLACE/DELETE, migration v4 root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer/direct-surface, strict conflict algorithms, final verification snapshot, public-rotation history guard and rotation races.
3. Execute a real supported-writer check for #168; close #168 as invalid if both valid serial orders restart cleanly.
4. Run unsafe legacy-promotion seed and full compileall over the reconstructed closure.
5. Perform a fresh full security audit of every consequential/restart mutation path and branch/main divergence. Keep PR #165 draft until all current-head tests are clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; isolated current-head fence surface 17/17 PASS after inherited historical DML hardening; full current-head gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; signer-noise robustness in LAB-083/LAB-084 threshold collectors.
- #168 / LAB-089 — VERIFY premise against real supported-writer serializations before implementation.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
