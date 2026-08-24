# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `adb16d43a0d0567da54f6d532957a7a9d99c9552`.
- PR remains draft; the one-shot exact current-head merged-stack regression gate has not passed.

## Last completed step

Performed a fresh source/patch audit of the current LAB-086 v4 cutoff/root-coauthorization path and the inherited LAB-085 public-custody surfaces. Re-read the current `migration_guard.py`, `strict_fence.py`, `suffix.py`, `final_supported.py`, plus LAB-085 `supported.py`, `asymmetric_custody.py` and `final_supported.py`. No new fail-open was established under the intended stale/alternate supported-writer model.

Established an important validation invariant by comparing the LAB-085 concurrency-fix merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509` to current `main`: the only changed path is `state/CURRENT.md`. Therefore executable LAB-080/082/083/084/085 code is byte-stable from the LAB-086 branch base to current main. The remaining exact-source gate can reconstruct one stable lower-stack dependency closure rather than reconcile changing implementation versions.

The GitHub connector remains the supported source/control-plane path. Direct shell GitHub DNS is unavailable in this runtime, and no shell-checkout evidence is claimed. The connector does not expose a repository source-archive download action, so exact execution must continue via file-by-file connector reconstruction plus Git blob verification.

Issue #163 was refreshed to match the actual current v4 architecture: migration cutoff requires both current Ed25519 recovery quorum and current root quorum; merely storing a proof row is not mutation capability; post-cutoff old/alternate supported writers remain unconditionally SQL-fenced; arbitrary same-privilege DDL remains explicitly delegated to LAB-087/#166.

## Evidence produced / reconfirmed

- Exact current-HEAD standalone LAB-086 corrected suite remains 12/12 PASS.
- Exact unsafe legacy-auto-promotion seed failed as expected.
- Current `migration_guard.py` Git blob: `332995323d8d74fcc0f377d0e74bb0f30b8735c1`.
- Current `final_supported.py` Git blob: `518297c1191c444478efabe8081ec5b1bf533952`.
- LAB-085 `asymmetric_custody.py` current-main Git blob: `771e2ae8cde15ce06297a9cf4a94c4b3f0d81dd4`.
- Earlier focused strict-fence evidence still applies to unchanged fence paths: 10/10 PASS; DELETE/REPLACE/UPSERT, forged-proof, stale-writer and trigger-upgrade paths covered.
- v4 cutoff/root-coauthorization focused checks remain 4/4; SQLite cutoff harness 3/3.
- Fresh compare `d2c9781... → main`: only `state/CURRENT.md` changed; executable LAB-080/082/083/084/085 implementation is byte-stable.
- Fresh current candidate audit found no new fail-open in v4 cutoff/root-proof binding, migration scrubbing, post-cutoff public rotation, or current final supported fence flow.

## Known blockers / constraints

- Remaining LAB-086 merge gate: current-head LAB-086 real-schema tests plus LAB-085/084/083/082/080 regressions have not yet been executed together from one connector-reconstructed exact dependency closure after migration payload v4/root coauthorization.
- The 12/12 standalone and focused results are exact evidence, but are not a substitute for that combined gate.
- Shell GitHub transport is a per-run environment limitation, not an owner blocker; continue using the GitHub connector and file-by-file blob-verified reconstruction.
- LAB-086 trigger fences protect against stale/alternate supported mutation paths; they do not protect against an arbitrary same-privilege raw SQLite DDL writer. That trust boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Reconfirm PR #165 HEAD is still `adb16d43a0d0567da54f6d532957a7a9d99c9552` before reconstruction.
2. Reconstruct the current LAB-086 real-schema executable/test set file-by-file through the GitHub connector, starting with `test_migration_guard.py`, `test_suffix.py`, `test_legacy_scrubbed_suffix.py`, `test_public_history_boundary.py`, stale/forged/direct-surface regressions, `test_strict_fence.py`, `strict_fence.py`, `migration_guard.py`, `suffix.py` and `final_supported.py`. For every reconstructed executable file, require local `git hash-object` == GitHub blob SHA.
3. Pull only the imported LAB-085/084/083/082/080 dependency/test files required by those tests; the lower stack is now proven byte-stable to current main. Continue fetching missing imports until the exact closure imports cleanly.
4. Execute all current LAB-086 real-schema tests from that closure, then LAB-085/084/083/082/080 regressions, unsafe seed and `python -m compileall`.
5. Perform a fresh full PR patch audit focused on cutoff/root/public proof substitution, same-root public rotations, alternate supported mutation entry points, transaction-scoped fence removal/restoration, restart snapshots and rotation races. Re-check branch/main divergence.
6. Keep PR #165 draft until the full gate is clean. If all exact-source tests and audit pass, mark ready and prefer normal squash merge; use file-scoped Contents API fallback only if the normal merge endpoint is unavailable/conflicted and a fresh path/conflict audit proves the audited additions can be safely applied without bypassing any gate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; architecture survives fresh audit and lower-stack byte stability is proven; full merged-stack exact-source gate remains.
- #166 / LAB-087 — READY; establish/enforce the SQLite schema-control trust boundary behind post-cutoff authority fences.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
