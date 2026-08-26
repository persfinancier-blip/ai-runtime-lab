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
- PR remains draft; runtime `migration_guard.py` is still blob `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2` and the staged own-proof-cardinality fix is not yet published.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173.

## Last completed step

Resumed LAB-086 and re-fetched the exact runtime migration guard. The source still matches blob `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`; the durable patch target remains candidate blob `7db4b53ff5d85483a4937b17d1d039fe954a9728`.

Tested a safer publication method before touching runtime: publish the full patched file to a temporary branch artifact, fetch its Git blob SHA, and replace runtime only if that SHA exactly equals the precomputed candidate. The safety gate worked and rejected both manual transfer attempts:

- first staging candidate blob: `9e0e08df8515a99c593616e12088d1c3d639f11f`; review found a dropped `old_rotation_authority_id` column during manual transfer;
- corrected staging candidate blob: `1a9209b16fdb2c3dcae8e4690658a030040f6ca2`; still not byte-identical to expected `7db4b53...`.

In both cases the runtime file was left untouched. Temporary artifacts were deleted. No test PASS is claimed for either staging candidate. Issue #163 now contains this verification report.

## Evidence produced / reconfirmed

- Exact runtime `migration_guard.py` remains blob `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
- Expected patched runtime blob remains `7db4b53ff5d85483a4937b17d1d039fe954a9728` from the prior local exact-source patch application and compile check.
- Staging/hash publication guard proved fail-safe: mismatched candidates `9e0e08df...` and `1a9209b...` were detected before runtime replacement.
- Current branch cleanup HEAD is `3208849ed14c9c4e6bf443fb779a1e8169c36e9a`; staging artifacts are removed.
- Cumulative exact lower-stack evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; exact standalone LAB-086 previously 12/12 and unsafe legacy auto-promotion failed as intended.
- LAB-087 remains merged/DONE with final exact 14/14 PASS + compileall.
- LAB-091 reference evidence remains 11/11 PASS + compileall; unsafe raw-DML seed failed as expected; real LAB-080/LAB-082 integration remains.

## Known blockers / constraints

- The pre-cutoff own-proof-cardinality fix must be published byte-exactly before LAB-086 can proceed to the final gate. Do not replace the large runtime file unless the published blob is exactly `7db4b53...`.
- Manual whole-file transfer through the connector has now produced two different wrong hashes and is not an acceptable publication method without an automated exact reconstruction/diff path.
- After publication, execute `test_pre_cutoff_lab086_proof_cardinality.py`, then the current real-ledger migration/suffix/final-supported/security suite, unsafe seed and full compileall on one exact LAB-080→086 closure.
- Direct shell/raw GitHub transport remains unavailable; connector reads/writes work.
- PR #165 is substantially diverged from current `main`; do not reconcile/integrate until the complete test/security gate is clean.
- LAB-088 PR #172 and LAB-091 PR #173 remain draft pending downstream/real integration work.
- LAB-090/#169 provider handoff freshness remains a separate correctness follow-up.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Do not retry manual full-file transcription. Obtain a byte-safe automated reconstruction of current blob `2ae3df...` from connector output into the local executor, apply `research/2026-08-26-lab086-pre-cutoff-own-proof-cardinality.patch`, and verify local Git blob exactly `7db4b53...`.
2. Publish those exact bytes to `migration_guard.py` only if GitHub returns exactly blob `7db4b53...`; otherwise abort without touching runtime.
3. Execute exact real-ledger `test_pre_cutoff_lab086_proof_cardinality.py`, then current `test_pre_cutoff_lower_evidence_cardinality.py`, migration-guard/suffix/final-supported/security modules, unsafe legacy-promotion seed and full compileall on the same LAB-080→086 closure.
4. Perform final LAB-086 security audit and branch/main reconciliation only after tests are clean; keep PR #165 draft until then.
5. If no byte-safe automated source-transfer path is available in a run, continue LAB-091 real integration rather than weakening LAB-086 publication discipline.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; pre-cutoff LAB-086-own-proof cardinality blocker staged, runtime fix not yet published.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173, reference writer exact-tested, real integration remains.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.