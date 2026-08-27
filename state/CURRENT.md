# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `1ba2c20c67cf4259e98e695aef5ea962b51a0342`; draft=true; mergeable=true.
- Previous executable gate snapshot `4570a19fb92f1222db64cb07f7e4ce6312630879` is now superseded for future full-gate counting because a new executable RED regression was added after the pin and a runtime fix is still required.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact execution is concretely tool-limited.

## Last completed step

Fresh audit of the published transaction-scoped thaw collision policy found a new merge-blocker in the real LAB-082 schema.

`asymmetric_provider_generations` has both content PK `generation_id` and SQL `UNIQUE(provider_id,generation)`. The permanent thaw collision trigger in published `strict_fence.py` blob `080eb9454437932a8ab419d66a4f2a69ed17c7ce` is NULL-safe and protects existing `generation_id`, but does not protect the alternate SQL unique identity.

Executed SQLite counterexample with the exact LAB-082 table shape and default `PRAGMA recursive_triggers=OFF`:

- current PK-only guard allowed `INSERT OR REPLACE` with new `generation_id` plus existing `(provider_id,generation)`;
- authenticated row `('generation-1-id','anchor-A',1,'original-key')` was replaced by `('attacker-generation-id','anchor-A',1,'attacker-key')`;
- focused candidate adding a permanent `(provider_id,generation)` collision predicate blocked the replacement while still allowing a legitimate new `(anchor-A,2)` successor.

Published RED regression:
- `experiments/asymmetric_break_glass_history/tests/test_thaw_alternate_unique_collision_regression.py` — Git blob `a05e94ef6cacc45cd819ea5e6f46ab6f7400769e`; locally reconstructed bytes matched `git hash-object`; `py_compile` passed.

Durable research artifacts:
- `research/2026-08-27-lab086-thaw-alternate-unique-collision.md`;
- `research/2026-08-27-lab086-thaw-alternate-unique-collision.patch`.

Scope audit of pinned schemas found this extra alternate SQL UNIQUE identity on `asymmetric_provider_generations`; the other currently INSERT-thawed authenticated-history tables use their primary identity only for SQL uniqueness.

PR #165 body and Issue #163 were updated. Runtime `strict_fence.py` is intentionally unchanged, so the new regression remains RED rather than being hidden by an unverified whole-file rewrite.

## Evidence retained

- LAB-080 18/18 PASS.
- LAB-082 28/28 PASS.
- LAB-083 24/24 PASS.
- LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS.
- LAB-085 asymmetric custody 8/8 PASS.
- LAB-085 public/final 11/11 PASS.
- Lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Published pre-blocker thaw/fence exact subgate: 14/14 PASS + compileall on executable snapshot `4570a19f...`.
- New alternate-UNIQUE counterexample: current guard RED; focused semantic-collision candidate GREEN and preserves legitimate successor creation.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.

## Known blockers / constraints

- New LAB-086 blocker: transaction-scoped thaw must preserve an alternate-UNIQUE collision fence for existing `(provider_id,generation)` rows in `asymmetric_provider_generations`.
- PR #165 must remain draft until this fix is published/exact-tested and the complete branch-local LAB-080→086 real-ledger gate is clean.
- Direct shell/raw GitHub transport remains unavailable; connector provides exact UTF-8 blobs but no repository archive/mount into the local executor. Do not weaken byte-integrity requirements or count hand-transcribed source as exact.
- LAB-090/#169 provider handoff freshness remains separate. Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Apply `research/2026-08-27-lab086-thaw-alternate-unique-collision.patch` byte-safely to the current exact `strict_fence.py` (`080eb945...`). The permanent trigger for `asymmetric_provider_generations` must reject both existing/NULL `generation_id` and an existing `(provider_id,generation)` semantic identity, while allowing a genuinely new successor pair.
2. Execute the new exact regression together with `test_strict_fence.py`, `test_thaw_history_key_collision_regression.py`, `test_thaw_null_proof_key_regression.py`, `test_thaw_proof_replace_regression.py`, and transaction-scoped thaw minimality/conflict-algorithm regressions; run compileall. Fix any failure.
3. Repin the executable snapshot after runtime/test bytes are final.
4. Reconstruct that branch-local LAB-080→086 closure, verify every local file via `git hash-object`, execute every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and full compileall.
5. Perform fresh final security/reconciliation audit and branch/main compare. Only a clean full gate may make PR #165 ready/integratable.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; alternate-UNIQUE thaw blocker RED regression published; runtime fix next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; fallback only while LAB-086 exact gate is tool-limited.
