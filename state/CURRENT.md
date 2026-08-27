# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `1ba2c20c67cf4259e98e695aef5ea962b51a0342`; draft=true; mergeability observed false in this run and must be rechecked after the runtime fix/gate.
- Previous executable gate snapshot `4570a19fb92f1222db64cb07f7e4ce6312630879` is superseded for future full-gate counting because a new executable RED regression exists and a runtime fix is still required.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact execution/publication is concretely tool-limited.

## Last completed step

Resumed LAB-086 first and reconfirmed the current RED blocker: `asymmetric_provider_generations` has both content PK `generation_id` and SQL `UNIQUE(provider_id,generation)`. Published `strict_fence.py` blob `080eb9454437932a8ab419d66a4f2a69ed17c7ce` permanently protects the content key during transaction-scoped thaw, but does not yet protect the alternate semantic identity. The saved patch adds an existing `(provider_id,generation)` collision predicate while preserving legitimate creation of a genuinely new successor pair.

The exact runtime file can be read through connector line ranges, but the available write primitive for the existing ~800-line security-critical file is whole-file replacement. Direct git/raw GitHub transport is unavailable in this runtime. Manual transcription would violate the established byte-integrity gate, so no LAB-086 runtime rewrite or PASS was claimed in this run. Issue #163 was updated with this exact limitation and next action.

Used the permitted fallback to close a previously uncounted LAB-091 evidence gap. Reconstructed these exact published PR #173 blobs and verified each with local `git hash-object` before execution:
- `experiments/mutable_shared_anchor_writer/operation_permit.py` `637784a5cb61a024a1df3e0e983887b6d0a838be`;
- `experiments/mutable_shared_anchor_writer/convergent_operation_scoped.py` `7fe0d682c0be4c6388799dd6b8a6ba87f65dda3b`;
- `experiments/anchor_attestation/protocol.py` `15d8b7cf8ff093490ccb75679030d3a0fe41e401`;
- `experiments/mutable_shared_anchor_writer/tests/test_process_concurrency_and_crash.py` `776ab61e70b062233939a9b0e53045042989a063`.

Executed the exact published process regression: **2/2 PASS**. Two independent forked workers converged on the same durable `CONFIRMED` winner/receipt binding. A worker that consumed the exact permit, performed PREPARED→CONFIRMED, then exited via `os._exit(17)` before COMMIT left durable state at PREPARED/NULL after reopen. Focused compileall also returned rc=0. Artifact-tool spreadsheet warmup emitted unrelated startup noise only.

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
- Published pre-blocker LAB-086 thaw/fence exact subgate: 14/14 PASS + compileall on executable snapshot `4570a19f...`.
- LAB-086 alternate-UNIQUE RED regression remains published; runtime fix is not yet safely applied.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 reference layer exact 11/11 PASS + compileall; unsafe raw-DML seed failed as intended.
- LAB-091 one-shot primitive exact 6/6 PASS + compileall.
- LAB-091 full mutable-row guards + legacy persistence exact 12/12 PASS.
- LAB-091 v3 cross-table state-machine exact 6/6+ / later contiguous/single-pending regressions retained as recorded in #170/#173.
- LAB-091 v4 deterministic/history-binding published-source regression exact 9/9 PASS + compileall.
- LAB-091 persisted-trigger restart exact 3/3 PASS + compileall.
- LAB-091 process concurrency/crash published-source regression is now exact **2/2 PASS + focused compileall**.

## Known blockers / constraints

- LAB-086 remains first priority. Current blocker: publish/exact-test the alternate-UNIQUE collision fence for existing `(provider_id,generation)` rows in `asymmetric_provider_generations` during thaw.
- PR #165 must remain draft until that fix is published, the strict/thaw subgate is green, a new executable snapshot is pinned, and the complete branch-local LAB-080→086 real-ledger gate passes.
- Direct shell/raw GitHub transport remains unavailable; connector provides exact UTF-8 source but no archive/mount or line-patch write. Do not weaken byte-integrity requirements or hand-transcribe the large security-critical file.
- LAB-091 process 2/2 result is exact focused evidence, not a replacement for full real LAB-080/LAB-082 supported-surface integration.
- LAB-090/#169 provider handoff freshness remains separate. Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: apply `research/2026-08-27-lab086-thaw-alternate-unique-collision.patch` byte-safely to exact `strict_fence.py` blob `080eb9454437932a8ab419d66a4f2a69ed17c7ce`. Publish only if the full replacement can be reconstructed and hash-verified, never by manual transcription.
2. Execute `test_thaw_alternate_unique_collision_regression.py` together with `test_strict_fence.py`, `test_thaw_history_key_collision_regression.py`, `test_thaw_null_proof_key_regression.py`, `test_thaw_proof_replace_regression.py`, thaw-minimality/conflict regressions and compileall. Fix every failure.
3. Repin the executable snapshot after runtime/test bytes are final.
4. Reconstruct that branch-local LAB-080→086 closure, verify every local file with `git hash-object`, execute every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and full compileall.
5. Perform fresh final security/reconciliation audit and branch/main compare. Only a clean full gate may make PR #165 ready/integratable.
6. If LAB-086 publication remains concretely tool-limited, LAB-091 fallback should move from the now-proven focused process 2/2 sublayer to full supported LAB-080/LAB-082 worker/UNKNOWN integration rather than repeating the stub harness.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; alternate-UNIQUE thaw blocker RED regression published; byte-safe runtime fix next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; exact focused process concurrency/crash 2/2 now proven; complete real LAB-080/LAB-082 integration gate remains.
