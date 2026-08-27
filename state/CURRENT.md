# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `e07ce4d093dffdf7bc20e8c9068140add87aa702`; draft=true, mergeable=true.
- Previous pinned executable snapshot `3d22efc4c562103e8b0bc18fb8f99559411b55fc` is now superseded for the eventual full gate because a new NULL proof-key thaw blocker was discovered after it.
- Current published runtime `strict_fence.py` remains blob `cea0ca3b42723790971ba9415b70a7e9fa0c7368`; NULL-safe fix is staged but not yet applied to runtime.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173.

## Last completed step

Fresh audit of the post-cutoff proof collision trigger found a SQLite NULL-identity bypass. Both LAB-086 proof tables declare identity as ordinary rowid-table `TEXT PRIMARY KEY` columns without explicit `NOT NULL`:

- `provider_asymmetric_break_glass_proofs.new_rotation_authority_id`;
- `provider_asymmetric_recovery_public_root_proofs.new_public_authority_id`.

The permanent collision trigger compares identity with SQL `=`. SQLite permits NULL in non-`INTEGER PRIMARY KEY` columns of ordinary rowid tables, and `NULL = NULL` is not true. Focused execution reproduced the bypass: a table containing one NULL PK row accepted `INSERT OR REPLACE` with another NULL PK row, leaving two NULL-identity rows. During LAB-086 transaction-scoped proof-creation thaw this can create unexplained durable proof evidence that later verification rejects. This is fail-closed durable-state damage / least-privilege-thaw bypass, not authority escalation.

A corrected RED regression is now committed on PR #165:
`experiments/asymmetric_break_glass_history/tests/test_thaw_null_proof_key_regression.py`, blob `fce5c57c8cfaa18f6761ae9b47c211813801aae0`.

Research note and staged minimal patch are also durable:
- `research/2026-08-27-lab086-null-proof-key-thaw.md`;
- `research/2026-08-27-lab086-null-proof-key-thaw.patch`.

Required trigger predicate:

`NEW.key IS NULL OR EXISTS(SELECT 1 FROM proof_table WHERE key IS NEW.key)`.

Focused SQLite execution of this candidate condition confirmed for both proof-table shapes: new NULL key BLOCKED, new unique non-NULL key ALLOWED, replace existing non-NULL key BLOCKED.

## Evidence retained

- LAB-086 lower-stack exact evidence: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Previous thaw/REPLACE fix at executable snapshot `3d22efc4...`: focused post-publication REPLACE/UPSERT-existing semantics passed for non-NULL proof identities; that snapshot is no longer sufficient for the final gate because the NULL identity bypass was found afterwards.
- New NULL bypass was actually reproduced with SQLite using ordinary `TEXT PRIMARY KEY` semantics.
- Corrected RED regression blob: `fce5c57c8cfaa18f6761ae9b47c211813801aae0`.
- Staged NULL-safe candidate semantics: NULL proof key blocked; unique non-NULL key allowed; existing non-NULL key replacement blocked.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 retained exact/focused evidence remains as previously recorded; it is fallback only while LAB-086 is tool-limited.

## Known blockers / constraints

- LAB-086 remains first priority. PR #165 must remain draft until the NULL proof-key runtime blocker is fixed and the complete post-fix exact branch-local LAB-080→086 execution gate is clean.
- `strict_fence.py` is security-critical and ~872 lines; available GitHub write path is whole-file replacement. Do not hand-rewrite it without byte/diff verification.
- Connector exact reads work and the full PR file patch is available; direct shell/raw GitHub transport still is not a dependable bulk checkout path.
- The new NULL-safe run is focused semantic evidence, not the exact full-module/closure regression result.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Apply `research/2026-08-27-lab086-null-proof-key-thaw.patch` to the exact current `strict_fence.py` runtime bytes. Verify the resulting GitHub commit diff changes only the intended permanent proof-collision predicate and record the new runtime blob.
2. Execute the exact published `test_thaw_null_proof_key_regression.py` together with `test_thaw_proof_replace_regression.py`, transaction-scoped thaw minimality, post-cutoff evidence DML/insert authorization and strict-fence conflict-algorithm tests. Fix any failure before proceeding.
3. Repin `research/2026-08-27-lab086-exact-gate-manifest.md` to the new executable commit/blob.
4. Reconstruct the minimal branch-local LAB-080→086 closure from that new executable snapshot and execute every normal LAB-086 real-schema module, then the unsafe legacy-promotion seed separately, full compileall and final security audit.
5. Keep PR #165 draft until the entire gate is clean; only then mark ready/reconcile/integrate. If exact reconstruction is concretely tool-limited after progress, fallback to LAB-091 real supported-worker integration without weakening LAB-086 acceptance criteria.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; NULL proof-key thaw blocker discovered, RED regression + staged patch durable, runtime fix pending.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; fallback only while LAB-086 exact gate is tool-limited.
