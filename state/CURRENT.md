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
- PR remains draft; full current-head merged-stack regression gate has not passed.

## Last completed step

Reconstructed the exact current-HEAD standalone LAB-086 protocol/test/unsafe-seed bytes through the GitHub connector, verified their Git blob identities locally, and executed them directly. The corrected standalone suite passed 12/12. The unsafe legacy auto-promotion seed failed exactly as intended because the unsafe implementation promotes a legacy HMAC proof into asymmetric authority.

A fresh PR patch/compare audit was also performed. PR #165 is currently diverged from main (ahead 71 / behind 23); all 22 PR paths remain additions with no path overlap against current main. The current v4 migration/root-coauthorization implementation and SQL-fence surfaces were re-inspected; no new blocker was established in this run, but the full merged dependency closure has not yet been executed together.

## Evidence produced

- Exact current-HEAD `experiments/asymmetric_break_glass_history/protocol.py` Git blob: `cccb531fa13b8f8d4e3a7c3163dd7c7cbeb3ec41`; locally reconstructed bytes matched exactly.
- Exact current-HEAD `tests/test_protocol.py` Git blob: `b423cf2d78bc75686b0e4e7dea5ea310ca5721ea`; locally reconstructed bytes matched exactly.
- Exact unsafe seed Git blob: `d92640ba77f7b1b592faf00f7afcea03cf3fbc4a`; locally reconstructed bytes matched exactly.
- Exact standalone corrected suite: 12/12 PASS.
- Exact unsafe legacy-auto-promotion seed: FAILED as expected (`UnsafeLegacyAutoPromotion.promote(...)` returned True while the expected-failure test requires False).
- Python emitted unrelated artifact-tool spreadsheet warmup warnings during process startup; the unittest results above were still observed and are the evidence counted.
- Current published `migration_guard.py` Git blob remains `332995323d8d74fcc0f377d0e74bb0f30b8735c1` with v4 cutoff + current-root coauthorization.
- Earlier focused evidence still stands for unchanged SQL-fence paths: exact strict-fence suite 10/10 passed before the v4 cutoff change; DELETE/REPLACE/UPSERT, forged-proof and stale-writer paths were covered.
- Fresh compare: ahead 71 / behind 23; all 22 PR files are additions with no current-main path overlap.
- Direct shell Internet/GitHub transport is not required for this run's evidence; GitHub connector remained healthy and was the durable source/control-plane path.

## Known blockers / constraints

- Remaining LAB-086 merge gate: exact current-head LAB-086 real-schema tests plus merged LAB-085/084/083/082/080 regressions have not yet been executed together from one connector-reconstructed dependency closure after migration payload v4/root coauthorization.
- The 12/12 standalone result is exact current-head evidence, but it is not a substitute for the real-schema merged-stack gate.
- LAB-086 trigger fences protect against stale/alternate supported mutation paths; they are not protection from an arbitrary same-privilege raw SQLite DDL writer. That broader boundary is LAB-087 / #166.
- Logical SQLite scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Finish connector reconstruction of the exact current PR HEAD `adb16d43a0d0567da54f6d532957a7a9d99c9552` dependency closure required by LAB-086 real-schema tests: LAB-085 provider-recovery-authority-lifecycle, LAB-084/083 threshold/recovery layers, LAB-082 asymmetric provider history, LAB-080 shared-anchor ledger, and their direct dependencies/tests. Verify executable files by Git blob identity.
2. Execute all current LAB-086 real-schema tests, prioritizing migration v4 root coauthorization/restart, missing/tampered/orphan root proof, stale-public cutoff rebinding, scrubbed-prefix + asymmetric suffix, forged-proof/stale-writer/direct-suffix, strict-fence conflict algorithms, trigger upgrade, final-supported rotation, and temporary-fence rollback.
3. Execute merged LAB-085/084/083/082/080 regressions from the same closure, then unsafe seed and compileall.
4. Perform a fresh full audit focused on cutoff/public/root proof substitution, same-root public rotations, alternate supported mutation entry points, transaction-scoped fence removal, predecessor/root binding, restart snapshots, and rotation races. Keep arbitrary raw SQLite DDL authority explicitly out of the LAB-086 claim and tracked in #166.
5. Re-check branch/main divergence. Keep PR #165 draft until the full gate is clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact current-head standalone 12/12 now reconfirmed, full merged-stack exact-source gate remains.
- #166 / LAB-087 — READY; establish/enforce the SQLite schema-control trust boundary behind post-cutoff authority fences.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
