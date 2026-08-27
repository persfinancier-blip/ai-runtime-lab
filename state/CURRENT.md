# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Previously pinned executable/runtime/test snapshot: `95fa5da3c457e3431cd596ec969d5939b0a1d925`; it remains the last fully enumerated snapshot, but a new RED regression and staged fix artifacts were added after it in this run. Do not treat the old 29-module inventory as the final merge gate until the runtime fix is applied and the snapshot is repinned.
- Current LAB-086 runtime `strict_fence.py` is still blob `5da01e28a9f813a136d138637f855940f04aab46`; the newly discovered thaw/REPLACE blocker is not yet fixed in runtime.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173.

## Last completed step

Resumed LAB-086 first and found a new merge blocker in the transaction-scoped proof-creation thaw. The current fence normally blocks proof INSERT/UPDATE/DELETE, but `remove_public_mutation_fence_locked()` intentionally drops only the proof creation trigger so the verified final writer can append a new proof key. Under SQLite's default `PRAGMA recursive_triggers=OFF`, `INSERT OR REPLACE` on an existing primary key deletes the conflicting row internally without reliably running the DELETE trigger. A focused executable SQLite counterexample observed direct UPDATE=blocked, DELETE=blocked and UPSERT=blocked, while `INSERT OR REPLACE` of an existing proof key succeeded and changed the row from `original` to `tampered` during thaw.

This violates LAB-086's least-privilege claim: existing authenticated proof history must remain immutable even while the final writer is temporarily allowed to create a new proof row.

Added a real-schema RED regression `experiments/asymmetric_break_glass_history/tests/test_thaw_proof_replace_regression.py` to PR #165. Its published blob is `c511ccfc4b88b050910561b3b8f7e99be5f33e93`; locally reconstructed bytes matched exactly via `git hash-object` and `py_compile` passed. The test requires, for both `provider_asymmetric_break_glass_proofs` and `provider_asymmetric_recovery_public_root_proofs`, that `INSERT OR REPLACE` of an existing key fail and leave the original row unchanged while plain INSERT of a genuinely new key still succeeds during thaw.

Saved the finding and minimal fix design as `research/2026-08-27-lab086-thaw-proof-replace-bypass.md` and staged unified patch `research/2026-08-27-lab086-thaw-proof-replace-bypass.patch`. The fix keeps a permanent collision/no-replace BEFORE INSERT trigger per proof table; only the blanket new-key creation deny is removed during verified thaw. `assert_public_mutation_fence_locked()` must require these permanent collision triggers.

Issue #163 was updated with the blocker and exact next action. Runtime `strict_fence.py` was deliberately not rewritten in this run because the available Contents API replaces the whole ~34 KB file; preserve byte discipline and apply the saved patch only against exact blob `5da01e28...`, then verify the resulting published diff/blob before counting tests.

## Evidence retained

- LAB-086 lower-stack exact evidence: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Last fully enumerated LAB-086 pinned snapshot had 29 normal modules + one unsafe seed; a new RED regression was added after that snapshot, so the post-fix gate must be repinned and re-enumerated.
- Current key runtime blobs before the new fix remain `migration_guard.py` `1a9209b...`, `strict_fence.py` `5da01e28...`, `suffix.py` `44847bde...`, `final_supported.py` `ceb7f48a...`.
- New RED regression exact published blob: `c511ccfc4b88b050910561b3b8f7e99be5f33e93`; exact local hash matched and syntax compilation passed.
- Focused SQLite counterexample: during thaw UPDATE/DELETE existing proof rows were blocked, UPSERT-existing was blocked, but `INSERT OR REPLACE` existing key was allowed with `recursive_triggers=OFF` and replaced the authenticated row. A separate focused candidate trigger (`BEFORE INSERT ... AND EXISTS(existing key)`) blocked REPLACE/UPSERT-existing while allowing a new key.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 retained exact evidence from prior runs: one-shot primitive 6/6; mutable-row guards + legacy persistence 12/12; v3 state-machine; v4 deterministic/history binding 9/9; restart 3/3; single-pending 2/2; process concurrency/crash 2/2; LAB-087 composition 2/2.

## Known blockers / constraints

- **New LAB-086 merge blocker:** proof history can be overwritten by `INSERT OR REPLACE` during transaction-scoped thaw because the blanket creation trigger is removed and SQLite conflict replacement does not necessarily traverse the DELETE trigger with default recursive triggers disabled.
- PR #165 must remain draft until the permanent no-replace collision trigger is installed for both post-cutoff proof tables, the new regression is green on exact published runtime, and the complete post-fix real-ledger gate is clean.
- Connector can return exact tree/blob contents but exposes no repository archive/mount; direct shell/raw GitHub transport remains unavailable. Whole-file Contents API updates are supported but security-critical large-file rewrites must be diff/hash audited.
- Never count manually reformatted/transcribed files as exact evidence; hash mismatch means discard the run.
- LAB-091 final candidate still needs full real LAB-080/LAB-082 supported-surface two-worker same-request and provider timeout/UNKNOWN reconciliation.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct exact current `strict_fence.py` blob `5da01e28a9f813a136d138637f855940f04aab46`, apply `research/2026-08-27-lab086-thaw-proof-replace-bypass.patch`, and publish through the Contents API only after byte/diff review.
2. Re-fetch the published `strict_fence.py`; require the PR diff to contain only the permanent proof-key collision triggers + fence assertion change. Execute exact `test_thaw_proof_replace_regression.py` plus existing `test_transaction_scoped_thaw_minimality.py`, `test_post_cutoff_evidence_dml_fence.py`, `test_post_cutoff_evidence_insert_authorization.py` and `test_strict_fence.py`.
3. Repin the executable snapshot after the runtime fix, regenerate the test inventory (expected previous 29 normal modules plus the new regression), reconstruct the branch-local LAB-080→086 closure and run the entire normal suite, unsafe legacy-promotion seed, full compileall and final security audit.
4. Only after a clean post-fix gate reconcile branch/main and mark PR #165 ready/merge.
5. If exact reconstruction is still transport-limited after the blocker fix, continue LAB-091 real supported-surface two-worker and timeout/UNKNOWN work, but LAB-086 remains the first priority.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; new thaw `INSERT OR REPLACE` proof-history blocker found; RED exact regression + research note + staged patch durable; runtime fix pending.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; real LAB-080/LAB-082 supported-surface concurrency/UNKNOWN gate remains.
