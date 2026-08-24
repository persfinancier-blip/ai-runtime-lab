# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `b4e747927cb36bd6cae4b1309317e070743e9493`.
- PR is mergeable but remains draft; full current-head merged-stack exact-source regression gate has not passed.

## Last completed step

A fresh current-head SQL-fence audit found and fixed another post-cutoff durable-authority bypass. `provider_rotation_authority_head` had only a `BEFORE UPDATE` fence. SQLite `INSERT OR REPLACE` does not traverse that UPDATE trigger, and direct DELETE was also unfenced. An executable pre-fix counterexample replaced the authoritative singleton with attacker state and separately deleted it outright.

The branch now fences the root-head singleton on INSERT, UPDATE and DELETE. `remove_public_mutation_fence_locked()` removes/restores all three only for the final verified writer inside one `BEGIN IMMEDIATE`; `assert_public_mutation_fence_locked()` requires all three after cutoff. `test_root_head_fence.py` now includes explicit `INSERT OR REPLACE` and DELETE regressions.

Published commits:
- code fix `14bd6600a08d97b15eab9be083c7ba33bd06fe7d`;
- regression update / current HEAD `b4e747927cb36bd6cae4b1309317e070743e9493`.

Focused SQLite semantics after the fix were actually executed: UPDATE, INSERT OR REPLACE and DELETE were all blocked with the original root head unchanged; transaction-scoped final-writer remove -> mutate -> reinstall committed the intended successor. This is focused evidence only, not the full current-head real-schema regression gate.

## Evidence produced / reconfirmed

- Current branch `strict_fence.py` blob after fix: `03899f5446dd78fe8faf575219628a1ede3c60db`.
- Current branch `test_root_head_fence.py` blob after fix: `5ccdc88d192565e31a3541ce228261bd65e32c16`.
- Focused pre-fix counterexample: root-head `INSERT OR REPLACE` succeeded; root-head DELETE succeeded.
- Focused post-fix semantic run: UPDATE/REPLACE/DELETE all BLOCKED; state remained `(root-1,1,1)`; legitimate transaction-scoped final writer committed `(root-2,2,2)`.
- Cumulative exact lower-stack evidence remains: LAB-080 18/18 PASS, LAB-082 28/28 PASS, LAB-083 24/24 PASS, LAB-084 17/17 PASS, LAB-085 core 12/12 PASS, LAB-085 asymmetric-custody 8/8 PASS; lower unsafe baselines failed as expected.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.
- Current PR patch audit reconfirmed the final writer pattern: lower committed-history verification + LAB-086 verification before consequential mutation, transaction-scoped fence removal, fence reinstall/assertion, and post-mutation verification before commit.

## Known blockers / constraints

- Full LAB-086 merge gate remains incomplete after the new root-head DML fix: exact LAB-085 final/public-custody tests and all current-head LAB-086 real-schema tests must be executed together, followed by unsafe seed, compileall and final audit.
- The focused root-head run validates the newly added trigger semantics but is not exact full-module current-head evidence.
- LAB-083/LAB-084 signer-noise issue #167 remains fail-closed DoS/robustness and separate from LAB-086 unless downstream tests invalidate the candidate.
- LAB-089 / #168 remains a verification question; do not add ordering protocol complexity unless real supported-writer tests reproduce it.
- LAB-086 SQLite fences cover stale/alternate supported mutation paths and the audited DML boundary, not arbitrary same-privilege raw SQLite DDL/schema control. That broader trust boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct/execute the remaining exact LAB-085 `test_public_custody_supported.py`, `test_final_supported.py` and direct dependencies in one connector-sourced workspace; verify executable files by Git blob identity.
2. Re-fetch PR #165 HEAD (do not assume `b4e7479...` remains current), reconstruct current LAB-086 implementation/tests and execute the complete real-schema suite, including the new root-head REPLACE/DELETE regressions, inherited lower-writer fences, migration v4 root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer/direct-surface, strict conflict algorithms, final verification snapshot, public-rotation history guard and rotation races.
3. Execute a real supported-writer check for #168; close #168 as invalid if both valid serial orders restart cleanly.
4. Run unsafe legacy-promotion seed and full compileall over the reconstructed closure.
5. Perform a fresh full security audit of every consequential/restart mutation path and branch/main divergence. Keep PR #165 draft until all current-head tests are clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; root-head INSERT/REPLACE/DELETE fence blocker fixed; full current-head gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; signer-noise robustness in LAB-083/LAB-084 threshold collectors.
- #168 / LAB-089 — VERIFY premise against real supported-writer serializations before implementation.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
