# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed branch HEAD: `5ff56ec39673803acff49960a914951df16d6e46`.
- PR remains draft; full current-head real-ledger migration/suffix/final-supported regression gate has not passed.

## Last completed step

Audited the current LAB-086 test suite against the strengthened post-cutoff DML fence. Found test-harness drift rather than a runtime defect: several older verifier-corruption tests attempted raw post-cutoff UPDATE/INSERT and expected the verifier to detect corruption later, but the hardened runtime now correctly blocks those writes earlier.

Updated only the affected corruption-injection tests so they explicitly drop one exact fence trigger to simulate out-of-band durable corruption, then verify that restart/final-writer authentication still fails closed. Ordinary DML protection remains tested separately by strict-fence regressions. Updated files:
- `test_migration_guard.py` blob `38f482e1488dd0c8b36584ffb3d6d09812172898`;
- `test_public_custody_history_guard.py` blob `a78fedb3223768663b16a9b8a5e36ba1bb7269a3`;
- `test_public_rotation_cross_binding.py` blob `0476e7a87bb7a7a6b6cfbc732edff0789a6669f8`;
- `test_public_rotation_history_guard.py` blob `c06599743802122c76dadafcf8f8ae52084ed10b`;
- `test_inherited_writer_history_guard.py` blob `d089df23d88dda35262f19e9e4a163941f166e4e`;
- `test_suffix.py` blob `9e322cf82af53fd4858ec8b4ae7c50dc4b691146`.

Patch-wide search after these edits found no remaining post-cutoff verifier-corruption test that unintentionally relies on ordinary DML bypass. The remaining raw corruption of `provider_recovery_public_transitions` occurs pre-cutoff and intentionally remains allowed. Runtime implementation files were not changed in this pass.

No PASS is claimed for the newly edited test bytes: direct shell GitHub transport remains unavailable and the complete dependency closure was not reconstructed in this run.

## Evidence produced / reconfirmed

- Issue #163 audit comment: `5411497161`.
- Fresh branch/main compare: `ahead 124 / behind 64`; all 45 PR paths remain additions, so no path-level content collision with current `main` is observed.
- Existing exact lower-stack evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, LAB-085 public/final 11/11; lower unsafe baselines failed as intended.
- Exact standalone LAB-086 corrected suite remains 12/12 PASS; unsafe legacy-auto-promotion seed failed as intended.
- Latest branch-exact strict-fence focused regression before this test-only pass: 12/12 PASS; focused compileall PASS.

## Known blockers / constraints

- Remaining merge gate is full exact current-head real-ledger execution of `migration_guard + suffix + final_supported`, including the newly adapted corruption tests, then unsafe seed, full compileall and final security audit.
- The six test-harness edits above are not yet executed as one exact-source suite; do not treat them as passing until observed.
- Local dependency reconstruction is per-run and not durable. Connector reconstruction works but is slower than a normal checkout; direct shell GitHub transport remains unavailable.
- SQLite fences cover audited ordinary DML/stale supported paths, not arbitrary same-privilege SQLite schema/DDL authority; LAB-087/#166 owns that stronger boundary.
- LAB-083/LAB-084 signer-noise robustness remains LAB-088/#167 and is fail-closed availability work.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Re-fetch PR #165 HEAD; reconstruct the exact LAB-080→085 dependency closure plus current LAB-086 implementation and all real-ledger tests using the GitHub connector, verifying executable/test files by Git blob identity.
2. Execute the complete current-head LAB-086 suite, including migration v4/root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, orphan/partial state, full lower/public-history guards, public-rotation cross-binding, inherited/direct surfaces, strict fences, final verification snapshot and rotation races.
3. Run unsafe legacy-promotion seed and full `python -m compileall` over the reconstructed closure.
4. Perform a fresh full security audit of consequential/restart paths and branch/main divergence. Fix every blocker. Only after a clean current-head gate may PR #165 be marked ready and integrated.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; runtime fence blockers fixed; stale verifier-corruption tests now aligned with the stronger DML boundary; full current-head execution remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
