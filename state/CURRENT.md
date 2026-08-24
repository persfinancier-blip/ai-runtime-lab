# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `376d1ed454c60d869605769473d903da2bb51f6f`.
- PR is open/draft; full current-head merged-stack exact-source regression gate has not passed.

## Last completed step

Continued the one-shot exact-source merged-stack gate in a single connector-reconstructed workspace. The already proven LAB-036/LAB-080 implementation layer was reconstructed again as dependencies, then exact LAB-082 `asymmetric_provider_history/{protocol,integration,supported}.py` and all three corrected LAB-082 tests were reconstructed from the byte-stable merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`.

Every LAB-082 executable/test file was checked with local `git hash-object` against its GitHub blob before execution. The cumulative corrected LAB-082 regression set then ran on top of that same LAB-036/LAB-080 workspace: 28/28 PASS. `python -m compileall` over LAB-036/LAB-080/LAB-082 also passed.

A fresh source audit of current LAB-086 `migration_guard.py`, `strict_fence.py`, `suffix.py`, `final_supported.py` and LAB-085 public custody code did not establish a new fail-open in the intended stale/alternate supported-writer model. The remaining evidence gap is now LAB-083→086, not LAB-080/082.

## Evidence produced / reconfirmed

- Prior exact LAB-080 corrected regression run: 18/18 PASS.
- Exact LAB-082 implementation blobs matched local bytes:
  - `protocol.py` `a2fc3456233930d94aaaca5fe57b1debd50cbdab`
  - `integration.py` `23ae688c22a1b74bde49ac506544778b2659bad6`
  - `supported.py` `d61bcd544c001de7108de42aafdc54069d0029bf`
- Exact LAB-082 corrected test blobs matched:
  - `test_protocol.py` `f737f71559e90e9a748fc3bd3d3e0cf90872a898`
  - `test_integration.py` `b659bca2a6c05999a13c6e6c84131039f337ee5d`
  - `test_supported.py` `cf5fd028f27b312aba98d8d74c300c8858e97a4a`
- Exact cumulative LAB-082 corrected regression run: 28/28 PASS.
- Compileall for reconstructed LAB-036/LAB-080/LAB-082 packages: PASS.
- Current PR #165 HEAD last observed as `376d1ed454c60d869605769473d903da2bb51f6f`; fetch current-head LAB-086 bytes again before final counting because the branch may advance independently.
- Previous current-implementation evidence remains relevant: exact standalone LAB-086 12/12 PASS; strict-fence/conflict-algorithm focused evidence and v4 cutoff/root-coauthorization evidence remain recorded in PR/Issue #163.

## Known blockers / constraints

- Remaining LAB-086 merge gate: continue the same exact-source reconstructed closure through LAB-083, LAB-084, LAB-085 and current-head LAB-086 real-schema tests; then unsafe seed + compileall + final audit.
- File-by-file connector reconstruction is slower because shell GitHub transport is unavailable, but it is working and is not an owner blocker.
- LAB-086 SQL fences protect against stale/alternate supported mutation paths, not arbitrary same-privilege raw SQLite DDL. That broader trust boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Continue from the same exact reconstructed dependency model by reconstructing LAB-083 provider-threshold-rotation implementation/support/tests at merge-base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`; verify every executable/test file by Git blob identity and run its corrected suite on top of the already proven LAB-080/082 layers.
2. Repeat cumulatively for LAB-084 provider-rotation recovery and LAB-085 provider-recovery-authority lifecycle.
3. Fetch the then-current PR #165 HEAD LAB-086 executable/tests, verify blob identities, and execute all real-schema migration/fence/suffix/final-supported tests including direct-surface, forged-proof, strict-fence conflict algorithms, cutoff/root coauthorization, scrubbed-prefix/asymmetric-suffix, restart and rotation-race cases.
4. Run unsafe legacy-promotion seed and `python -m compileall` over the complete reconstructed closure.
5. Perform a fresh full audit focused on final single-snapshot verification, cutoff/root/public proof substitution, alternate supported mutation entry points, transaction-scoped fence removal/restoration, predecessor/root binding, restart snapshots and rotation races. Re-check branch/main divergence and integrate only after the full gate is clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; cumulative exact merged-stack gate now has LAB-080 18/18 + LAB-082 28/28 + compileall; LAB-083→086 remain.
- #166 / LAB-087 — READY; establish/enforce the SQLite schema-control trust boundary behind post-cutoff authority fences.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
