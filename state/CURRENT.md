# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed branch HEAD: `3208849ed14c9c4e6bf443fb779a1e8169c36e9a`.
- Runtime `migration_guard.py` remains blob `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`; staged own-proof-cardinality candidate remains `7db4b53ff5d85483a4937b17d1d039fe954a9728` and is not published.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173, now with a first real supported-stack integration slice.

## Last completed step

Re-probed the LAB-086 byte-safe publication path. Exact source can now be read losslessly from GitHub blob responses/resources, but the available write action still requires a complete UTF-8 content string; there is no file-upload/line-patch action. Because prior manual whole-file transfers produced wrong hashes, the LAB-086 runtime guard was not touched.

Per the explicit fallback in this state, continued LAB-091 real integration instead of weakening LAB-086 publication discipline.

Published on PR #173:
- `experiments/mutable_shared_anchor_writer/real_integration.py` commit `efed44017cebe6c05ce0d06f0b397092253c5e13`, blob `e1c78a9208c64f3057c3692dcd0e91da9af3bc1a`;
- `tests/test_real_integration_guards.py` commit/current HEAD `79dcda07a6c42b7ab1cc1a57b6ec27638b1df524`, blob `f20b9d0bdb0e87cb0be2d21339dcdb127cf471f2`.

The new LAB-091 integration subclasses the actual LAB-082 `SupportedAsymmetricHistoricalSharedAnchorLedger`. Authorization is connection-local and active only in narrow `BEGIN IMMEDIATE` SQL mutation sections; it is reset before commit/rollback. External provider calls therefore occur with no SQL writer authorization. Reserve, asymmetric receipt persistence, PREPARED→CONFIRMED commit and watermark commit use the narrow boundary. No public raw writable-connection property is added.

A development audit caught and fixed `sqlite3.executescript()` after `BEGIN IMMEDIATE`; guard installation now executes individual trigger statements under one transaction.

Focused local real-schema authorization tests passed 7/7. However the local candidate blobs (`real_integration.py` `98e7f55c...`, test `b7087f50...`) differ from the published formatting blobs above, so 7/7 is design/focused evidence only and is not counted as exact published-source evidence.

## Evidence produced / reconfirmed

- LAB-086 exact runtime `migration_guard.py` still `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`; expected patched blob remains `7db4b53ff5d85483a4937b17d1d039fe954a9728`.
- Exact-source cumulative lower-stack evidence remains LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; standalone LAB-086 previously 12/12; unsafe legacy auto-promotion failed as intended.
- LAB-087 remains merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 reference layer remains exact 11/11 PASS + compileall; unsafe raw-DML seed failed as intended.
- New LAB-091 focused real-schema authorization harness: 7/7 PASS against the local formatting-equivalent candidate, covering unauthorized DML, connection-local authorization, valid reserve/confirm/watermark/receipt flow, receipt REPLACE denial, intent identity mutation denial, watermark rollback denial, and rollback/authorization reset.
- PR #173 remains draft/mergeable on HEAD `79dcda07a6c42b7ab1cc1a57b6ec27638b1df524`.

## Known blockers / constraints

- LAB-086 own-proof-cardinality fix must still be published byte-exactly. Do not replace `migration_guard.py` unless the resulting Git blob is exactly `7db4b53...`.
- Manual whole-file transcription is not an acceptable LAB-086 publication method after two hash mismatches. Exact reading is solved; automated exact write transfer is not.
- After LAB-086 publication, execute the exact real-ledger cardinality regression plus current migration/suffix/final-supported/security suite, unsafe seed and full compileall on one LAB-080→086 closure.
- LAB-091 new real integration is published but not exact-tested: published blobs differ from the locally executed candidates. Reconstruct and execute the published bytes before counting the integration gate.
- LAB-091 still needs real provider/restart/concurrency/crash/UNKNOWN and LAB-087 restricted-worker composition tests.
- Direct shell/raw GitHub transport remains unavailable; connector reads/writes work.
- LAB-090/#169 provider handoff freshness remains a separate correctness follow-up.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 remains priority. If a byte-safe automated write path appears, reconstruct current blob `2ae3df...`, apply `research/2026-08-26-lab086-pre-cutoff-own-proof-cardinality.patch`, verify exact local blob `7db4b53...`, and publish only if GitHub returns that exact blob.
2. If LAB-086 write remains file-transfer blocked, reconstruct the exact published PR #173 blobs `e1c78a9...` and `f20b9d0...` into the executor and run their focused suite, then add real LAB-080/LAB-082 provider/restart/concurrency/UNKNOWN integration tests.
3. After LAB-086 publication, run `test_pre_cutoff_lab086_proof_cardinality.py`, lower-evidence cardinality, migration-guard/suffix/final-supported/security modules, unsafe legacy-promotion seed and full compileall on one exact LAB-080→086 closure.
4. Perform final LAB-086 security audit and branch/main reconciliation only after tests are clean; keep PR #165 draft until then.
5. Keep PR #173 draft until its exact published-source and real-stack integration gates are clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; own-proof-cardinality blocker staged, runtime fix not yet published.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173 now contains first real supported-stack integration slice; exact published-source and real provider integration remain.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
