# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `91b41d997e7498e45e7c108e70c766f5b447655f`; draft=true; mergeable=true at this observation.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact publication/execution is concretely tool-limited.

## Last completed step

Resumed LAB-086 first and synchronized durable control-plane state with the actual PR blocker.

Current published `experiments/asymmetric_break_glass_history/strict_fence.py` remains exact blob `080eb9454437932a8ab419d66a4f2a69ed17c7ce`. The current blocker is the alternate semantic identity on `asymmetric_provider_generations`: `generation_id` is the content PK, but the schema also has `UNIQUE(provider_id,generation)`. During transaction-scoped thaw, SQLite `INSERT OR REPLACE` using a new `generation_id` and an already-authenticated `(provider_id,generation)` can replace history.

The corrected published regression is `test_thaw_alternate_unique_collision_regression.py` blob `a767e6bbb5e164a846c93d04b9c8c3f7980bba38`. Exact RED→GREEN is already established on reconstructed bytes:
- published runtime `080eb945...`: RED — attack allowed;
- saved candidate `eb2198354d222ad0ad6b7d751bf5c649157b6b36`: GREEN 1/1, original row unchanged, genuine new successor still insertable;
- `py_compile` PASS.

Saved patch: `research/2026-08-27-lab086-thaw-alternate-unique-collision.patch`. The broader inspected INSERT-thawed schemas did not expose another secondary SQL UNIQUE identity, so the fix remains narrowly scoped to `(provider_id,generation)`.

This run re-probed the publication path. Connector reads exact file ranges/blobs and Contents API can replace a whole file, but no line-patch/file-upload primitive is available; direct/raw GitHub transport is unavailable. The ~935-line security-critical runtime file was therefore not hand-transcribed. Runtime remains unchanged until a byte-safe complete payload can be supplied and GitHub returns the expected candidate blob.

Because LAB-086 publication is concretely tool-limited, continued the allowed LAB-091 fallback and upgraded a previously non-counted process test to exact published-source evidence. Reconstructed and hash-verified current published bytes:
- `operation_permit.py` `637784a5cb61a024a1df3e0e983887b6d0a838be` — MATCH;
- `convergent_operation_scoped.py` `7fe0d682c0be4c6388799dd6b8a6ba87f65dda3b` — MATCH;
- `test_process_concurrency_and_crash.py` `776ab61e70b062233939a9b0e53045042989a063` — MATCH.

Executed result: LAB-091 process concurrency/crash **2/2 PASS + compileall PASS**. Two independent OS processes converged on one CONFIRMED winner for the same PREPARED request; a worker killed with `os._exit(17)` after an authorized PREPARED→CONFIRMED update but before COMMIT left durable state PREPARED/NULL after reopen. The published test intentionally stubs the parent surface, so this is exact evidence for convergence/transaction semantics, not the remaining full LAB-080/LAB-082 supported-surface gate.

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
- Published pre-blocker LAB-086 thaw/fence exact subgate: 14/14 PASS + compileall.
- Alternate-UNIQUE corrected regression blob `a767e6bbb5e164a846c93d04b9c8c3f7980bba38`.
- Current LAB-086 runtime blob `080eb9454437932a8ab419d66a4f2a69ed17c7ce`.
- Exact staged LAB-086 candidate `eb2198354d222ad0ad6b7d751bf5c649157b6b36`; py_compile PASS; corrected regression GREEN 1/1.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 one-shot/v2/v3/v4/restart/single-pending evidence remains as recorded in #170/#173.
- LAB-091 current published process convergence/crash evidence: exact hashes matched; 2/2 PASS + compileall.

## Known blockers / constraints

- LAB-086 remains first priority. Current blocker is byte-safe publication of already-proven candidate `eb219835...`, not protocol/design uncertainty.
- Available GitHub write primitive for existing `strict_fence.py` is whole-file text replacement. Do not hand-transcribe the security-critical file or weaken the Git-blob integrity gate.
- PR #165 must remain draft until the runtime fix is published, exact thaw/strict tests are green on published bytes, a new executable snapshot is pinned, and the complete branch-local LAB-080→086 real-ledger gate passes.
- LAB-091 still needs the same process/restart/UNKNOWN properties through the full real LAB-080/LAB-082 supported surface; focused parent-stub evidence does not substitute for that gate.
- LAB-090/#169 provider handoff freshness remains separate. Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: publish the already reconstructed `strict_fence.py` candidate only through a byte-safe full-payload path. Expected candidate blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36`; current remote blob `080eb9454437932a8ab419d66a4f2a69ed17c7ce`.
2. Fetch published runtime and require exact Git blob equality; if it differs, repair/revert before counting tests.
3. Execute corrected alternate-UNIQUE regression with `test_strict_fence.py`, thaw history/null/proof replacement/minimality/conflict suites and compileall; fix every failure.
4. Repin executable snapshot, reconstruct exact branch-local LAB-080→086 closure, verify every local file with `git hash-object`, execute every normal LAB-086 real-schema test, unsafe expected-failure seed and full compileall.
5. Perform fresh final security/reconciliation audit and branch/main compare; only a clean full gate may make PR #165 ready/integratable.
6. If publication remains concretely tool-limited, continue LAB-091 by moving the now-exact process concurrency/crash semantics through `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` with real LAB-080/LAB-082 dependencies, then full UNKNOWN reconciliation.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; alternate-UNIQUE blocker exact RED→GREEN candidate proven; byte-safe runtime publication next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; exact published process convergence/crash 2/2 + compileall now proven; full real LAB-080/LAB-082 integration gate remains.
