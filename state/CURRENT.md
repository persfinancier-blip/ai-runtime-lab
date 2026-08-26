# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`; draft PR #165.
- Current observed PR head at start of this run: `3208849ed14c9c4e6bf443fb779a1e8169c36e9a`.
- Runtime `migration_guard.py` remains blob `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
- Staged own-proof-cardinality candidate remains `7db4b53ff5d85483a4937b17d1d039fe954a9728` and is NOT published.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173.

## Last completed step

Re-probed the byte-safe LAB-086 publication path. Exact source can be fetched losslessly from GitHub by blob SHA, and Contents API whole-file replacement works, but the available write action accepts only a caller-supplied complete UTF-8 string. There is still no supported operation that pipes fetched blob bytes through the saved patch into an update. A disposable branch probe confirmed the write endpoint itself works; it did not solve exact source transfer. Because two earlier manual transcriptions produced wrong hashes, PR #165 runtime was not touched.

While LAB-086 remains publication-blocked, audited the current published LAB-091 `real_integration.py` and its focused guard tests. The integration keeps authorization connection-local, enables it only after `BEGIN IMMEDIATE`, clears it before commit/rollback, and performs external provider calls outside authorization. No new authority bypass was found in this source audit. Published LAB-091 focused tests are still not counted as exact execution evidence until the published blobs are reconstructed in the executor.

A report of this run was added to Issue #163. A disposable branch `lab086-byte-transfer-20260826` was created solely to probe the Contents API and contains no authoritative work; do not use it for integration.

## Evidence retained

- LAB-086 exact runtime `migration_guard.py`: `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`; expected patched blob: `7db4b53ff5d85483a4937b17d1d039fe954a9728`.
- Exact lower-stack evidence remains LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; standalone LAB-086 previously 12/12; unsafe legacy auto-promotion failed as intended.
- LAB-087 remains merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 reference layer remains exact 11/11 PASS + compileall; unsafe raw-DML seed failed as intended.
- LAB-091 published real-integration source audit found no new bypass, but its published-byte execution gate is still outstanding.

## Known blockers / constraints

- Do not replace LAB-086 `migration_guard.py` unless the resulting Git blob is exactly `7db4b53...`.
- Manual whole-file transcription is not acceptable for this security-critical file after two hash mismatches.
- Connector exact reads and whole-file writes work; an automated exact read→patch→write transfer is still unavailable in this runtime.
- After LAB-086 publication, execute the exact real-ledger cardinality regression plus current migration/suffix/final-supported/security suite, unsafe seed and full compileall on one LAB-080→086 closure.
- LAB-091 published integration still needs exact published-source execution plus real provider/restart/concurrency/crash/UNKNOWN and LAB-087 restricted-worker composition tests.
- LAB-090/#169 provider handoff freshness remains a separate correctness follow-up.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 remains priority. Use a byte-safe automated source-transfer path only: fetch exact `2ae3df...`, apply `research/2026-08-26-lab086-pre-cutoff-own-proof-cardinality.patch`, verify local Git blob `7db4b53...`, and publish only if GitHub returns that exact blob.
2. If that transfer remains unavailable, continue LAB-091 by reconstructing exact published PR #173 blobs and executing them, then add real provider/restart/concurrency/UNKNOWN integration tests.
3. After LAB-086 publication, run the own-proof cardinality regression, lower-evidence cardinality, migration-guard/suffix/final-supported/security modules, unsafe legacy-promotion seed and full compileall on one exact LAB-080→086 closure.
4. Perform final LAB-086 security audit and branch/main reconciliation only after tests are clean; keep PR #165 draft until then.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; own-proof-cardinality blocker staged, runtime fix not yet published.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173 contains first real supported-stack integration slice.
