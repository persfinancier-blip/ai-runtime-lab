# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `3d23d457e4136e200d152aff75b8436444e01288`; draft=true, mergeable=true.
- Current published runtime `strict_fence.py` remains blob `cea0ca3b42723790971ba9415b70a7e9fa0c7368` from executable commit `3d22efc4c562103e8b0bc18fb8f99559411b55fc`.
- That executable snapshot is superseded for the eventual full gate: two adjacent thaw key-identity blockers are now RED on the branch and require one combined `strict_fence.py` fix before repinning.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact execution is concretely tool-limited.

## Last completed step

Resumed LAB-086 first and obtained the exact published `strict_fence.py` through the connector. The earlier proof REPLACE fix was rechecked with focused current-snapshot SQL semantics: for both LAB-086 proof tables, transaction-scoped thaw still blocks REPLACE of an existing non-NULL key while allowing a new unique key.

The branch already contained a newer RED regression for a NULL identity bypass in those proof collision triggers. Ordinary SQLite rowid tables permit NULL in non-`INTEGER PRIMARY KEY` columns; `NULL = NULL` is not true. The staged proof fix therefore changes the collision predicate to `NEW.key IS NULL OR EXISTS(... key IS NEW.key)`.

A fresh audit then found the same least-privilege-thaw class on seven other authenticated-history tables whose INSERT-deny is intentionally removed for the final writer while UPDATE/DELETE guards remain:

- `provider_recovery_public_authorities.authority_id`;
- `provider_recovery_public_transitions.new_authority_id`;
- `provider_rotation_authorities.authority_id`;
- `provider_rotation_authority_transitions.new_authority_id`;
- `provider_rotation_threshold_proofs.new_provider_generation_id`;
- `asymmetric_provider_generations.generation_id`;
- `asymmetric_provider_transitions.new_generation_id`.

Exact lower source confirms these are `TEXT PRIMARY KEY` identities. Focused SQLite execution reproduced the bypass: during the current thaw policy, `INSERT OR REPLACE` changed an existing public authority from `original` to `tampered` and changed an existing public transition from `bootstrap/root` to attacker values. The same REPLACE pattern and a NULL identity insert were accepted for all seven modeled INSERT-thawed tables. This is durable fail-closed authenticated-history damage / violation of the least-privilege thaw contract, not authority escalation for a process without access to the final-writer connection.

Durable artifacts added to PR #165:

- RED regression `experiments/asymmetric_break_glass_history/tests/test_thaw_history_key_collision_regression.py`, blob `88ba35e933c123d10af65597d6bb51f4f11068ec`;
- `research/2026-08-27-lab086-thaw-history-key-collisions.md`;
- staged combined patch `research/2026-08-27-lab086-thaw-history-key-collisions.patch`.

The combined patch is designed to retain a permanent NULL-safe existing-key collision trigger for every INSERT-thawed authenticated-history table, never remove those triggers in `remove_public_mutation_fence_locked()`, require them in `assert_public_mutation_fence_locked()`, and simultaneously apply the pending NULL-safe predicate to the two LAB-086 proof-table collision triggers. New unique non-NULL keys remain insertable during legitimate final-writer thaw.

## Evidence retained

- LAB-086 lower-stack exact evidence: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Published proof REPLACE fix at `strict_fence.py` blob `cea0ca3b...`: focused current-snapshot SQL check still blocks existing non-NULL proof-key replacement and permits a new key.
- NULL proof-key bypass: reproduced; branch RED regression `test_thaw_null_proof_key_regression.py` blob `fce5c57c8cfaa18f6761ae9b47c211813801aae0`.
- Broader thaw history-key bypass: reproduced for REPLACE-existing and NULL identity across all seven INSERT-thawed history surfaces; branch RED regression blob `88ba35e9...`.
- Exact source used to confirm key schemas includes LAB-083 `protocol.py` blob `688f3961...`, LAB-082 `protocol.py` blob `a2fc3456...`, and LAB-085 public custody `asymmetric_custody.py` blob `771e2ae8...`.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 retained evidence remains fallback only.

## Known blockers / constraints

- PR #165 must remain draft. The current runtime has two related thaw key-identity blockers: pending NULL-safe proof collision semantics plus missing permanent collision/NULL guards on seven other INSERT-thawed authenticated-history tables.
- `strict_fence.py` is security-critical and large; the available high-level write operation is whole-file replacement. Do not hand-rewrite it without byte/diff verification. Apply the two staged changes as one reviewed candidate against exact blob `cea0ca3b...`.
- The new focused SQLite runs are semantic evidence, not the exact full-module/branch-local regression gate.
- Direct shell/raw GitHub transport remains unavailable; connector exact reads work.
- LAB-090/#169 provider handoff freshness remains separate. Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Build one byte-verified candidate from exact `strict_fence.py` blob `cea0ca3b42723790971ba9415b70a7e9fa0c7368` that applies both staged changes: NULL-safe `IS` collision semantics for post-cutoff proof keys and permanent NULL-safe existing-key collision triggers for every other INSERT-thawed authenticated-history table. Verify the candidate diff contains only those intended changes before publishing runtime.
2. Execute exact published `test_thaw_null_proof_key_regression.py` and `test_thaw_history_key_collision_regression.py` together with `test_thaw_proof_replace_regression.py`, `test_strict_fence.py`, inherited SQL-fence/direct-surface and conflict-algorithm regressions. New unique non-NULL rows must remain creatable by legitimate thaw; existing/NULL identities must remain blocked.
3. Repin `research/2026-08-27-lab086-exact-gate-manifest.md` to the post-fix executable commit/blob.
4. Reconstruct that exact branch-local LAB-080→086 closure and execute every normal LAB-086 real-schema module, then unsafe legacy-promotion seed separately, full compileall and final security/reconciliation audit.
5. Keep PR #165 draft until the entire post-fix gate is clean; only then mark ready/reconcile/integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; combined thaw key-identity fix pending runtime publication and exact regressions.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; fallback only while LAB-086 exact gate is tool-limited.
