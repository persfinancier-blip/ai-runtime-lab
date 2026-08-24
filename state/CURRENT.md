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
- PR is open/draft/mergeable; full current-head merged-stack exact-source regression gate has not passed.

## Last completed step

Started the one-shot merged-stack gate by reconstructing the exact LAB-080 dependency layer from the byte-stable LAB-086 merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`. Reconstructed `anchor_attestation/protocol.py`, `shared_anchor_intent_ledger/protocol.py`, `shared_anchor_intent_ledger/supported.py`, and all three corrected LAB-080 test files. Every reconstructed executable/test file was checked with local `git hash-object` against its GitHub blob before execution.

The exact LAB-080 corrected regression set then ran from that same reconstructed workspace: 18/18 PASS. `python -m compileall` over the reconstructed LAB-036/LAB-080 packages also passed. This advances the combined LAB-086 merge gate rather than relying on another isolated harness.

During the run PR #165 advanced from `4b786939...` to `376d1ed454c60d869605769473d903da2bb51f6f`. The new commit only changes `tests/test_unfenced_supported_surface_regression.py` to obtain the historical public-custody head via the audited locked lookup rather than a nonexistent/unsupported convenience call; lower LAB-080/082/083/084/085 executable code remains at the same merge-base bytes.

## Evidence produced / reconfirmed

- Exact LAB-036 `experiments/anchor_attestation/protocol.py` blob `15d8b7cf8ff093490ccb75679030d3a0fe41e401` matched local bytes.
- Exact LAB-080 `shared_anchor_intent_ledger/protocol.py` blob `68834409363c93eee4e9a9a7b9ec076098af0acf` matched local bytes.
- Exact LAB-080 `shared_anchor_intent_ledger/supported.py` blob `22a05c04831f65c1d7fe9077df3bb780c4008e09` matched local bytes.
- Exact LAB-080 corrected test blobs matched: `d2d127fb67147dda2c5f6786731c0a3310a067e6`, `aa9b0f3784f97b14b59b128a2e7686e94848d377`, `763ee7f6958ed6fda1adde402452fedde5046ea1`.
- Exact LAB-080 corrected regression run: 18/18 PASS.
- Compileall for reconstructed LAB-036/LAB-080 packages: PASS.
- Current PR #165 HEAD `376d1ed454c60d869605769473d903da2bb51f6f`; latest commit is test-only and does not invalidate the completed LAB-080 layer evidence.
- Previous current-implementation evidence remains relevant: exact standalone LAB-086 12/12 PASS; focused final single-snapshot regression 1/1 PASS; unchanged v4 migration/root-coauthorization and strict-fence evidence remain recorded in PR/Issue #163.

## Known blockers / constraints

- Remaining LAB-086 merge gate: continue the same exact-source reconstructed closure through LAB-082, LAB-083, LAB-084, LAB-085 and current-head LAB-086 real-schema tests; then unsafe seed + compileall + final audit.
- File-by-file connector reconstruction is slower because shell GitHub transport is unavailable, but it is working and is not an owner blocker.
- PR #165 changed during this run only in a LAB-086 test file; fetch current-head LAB-086 test bytes before counting the final LAB-086 run.
- LAB-086 SQL fences protect against stale/alternate supported mutation paths, not arbitrary same-privilege raw SQLite DDL. That broader trust boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Continue from the existing exact reconstructed workspace: reconstruct LAB-082 `asymmetric_provider_history/{protocol,integration,supported}.py` plus its corrected tests at merge-base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`; verify every file by Git blob identity and run the LAB-082 corrected suite on top of the already passing LAB-080 closure.
2. Repeat cumulatively for LAB-083 provider-threshold rotation, LAB-084 provider-rotation recovery, and LAB-085 provider-recovery-authority lifecycle, always keeping the same exact lower dependency workspace.
3. Fetch the current PR HEAD `376d1ed454c60d869605769473d903da2bb51f6f` LAB-086 executable/tests, verify blob identities, and execute all real-schema migration/fence/suffix/final-supported tests including the updated direct-surface regression and final single-snapshot regression.
4. Run unsafe legacy-promotion seed and `python -m compileall` over the complete reconstructed closure.
5. Perform a fresh full audit focused on final single-snapshot verification, cutoff/root/public proof substitution, alternate supported mutation entry points, transaction-scoped fence removal/restoration, predecessor/root binding, restart snapshots and rotation races. Re-check branch/main divergence and integrate only after the full gate is clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; cumulative merged-stack gate has now completed exact LAB-080 18/18 + compileall; LAB-082→086 remain.
- #166 / LAB-087 — READY; establish/enforce the SQLite schema-control trust boundary behind post-cutoff authority fences.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
