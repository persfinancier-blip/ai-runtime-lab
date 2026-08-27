# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `91b41d997e7498e45e7c108e70c766f5b447655f`; draft=true; latest observed mergeable=false and must be rechecked after the runtime fix/gate.
- Previous executable snapshot is superseded for future full-gate counting because the alternate-UNIQUE regression/test bytes changed and runtime fix remains unpublished.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact publication/execution is concretely tool-limited.

## Last completed step

Resumed LAB-086 first and removed uncertainty around the current alternate-UNIQUE thaw blocker.

Reconstructed the exact published `experiments/asymmetric_break_glass_history/strict_fence.py` from GitHub connector line ranges. Before modification, local `git hash-object` exactly matched published blob `080eb9454437932a8ab419d66a4f2a69ed17c7ce` (935 lines).

Applied `research/2026-08-27-lab086-thaw-alternate-unique-collision.patch` programmatically to those exact bytes. Resulting local candidate blob is `eb2198354d222ad0ad6b7d751bf5c649157b6b36`; `py_compile` PASS.

The previously published RED regression itself had an incomplete fixture: it created only migration boundary + `asymmetric_provider_generations`, while `install_public_mutation_fence_locked()` unconditionally installs triggers on `provider_recovery_public_authorities`, `provider_recovery_public_transitions`, and `provider_recovery_public_head`. The old test therefore failed with `sqlite3.OperationalError` before reaching the intended attack.

Corrected the test fixture and published commit `4d9cfa6fff9d397f7490d29baa56b793e4d2c93a`; published test blob `a767e6bbb5e164a846c93d04b9c8c3f7980bba38`.

Executed true RED→GREEN using those corrected exact test bytes:
- exact published runtime `080eb945...`: RED as intended — `INSERT OR REPLACE` with a new `generation_id` and existing `(provider_id,generation)` was allowed;
- exact reconstructed/patched candidate `eb219835...`: GREEN 1/1 — attack blocked, original authenticated row unchanged, legitimate new successor pair remains insertable.

Broader schema audit of every INSERT-thawed authenticated-history table found the only secondary SQL UNIQUE identity is `asymmetric_provider_generations UNIQUE(provider_id,generation)`. Other inspected thawed tables use only their primary successor/content key. Therefore the staged semantic collision predicate can remain narrowly scoped instead of adding speculative policy.

Durable verification note: `research/2026-08-27-lab086-alternate-unique-red-green-verification.md` (commit `91b41d997e7498e45e7c108e70c766f5b447655f`).

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
- Published pre-blocker LAB-086 thaw/fence exact subgate: 14/14 PASS + compileall on the previous executable snapshot.
- Alternate-UNIQUE corrected regression exact blob: `a767e6bbb5e164a846c93d04b9c8c3f7980bba38`.
- Exact current runtime reconstruction: `080eb9454437932a8ab419d66a4f2a69ed17c7ce`.
- Exact staged candidate: `eb2198354d222ad0ad6b7d751bf5c649157b6b36`; py_compile PASS; corrected regression GREEN 1/1.
- Exact current runtime with corrected regression: RED as intended.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 focused/process/restart evidence remains as recorded in #170/#173; no LAB-091 result substitutes for the LAB-086 gate.

## Known blockers / constraints

- LAB-086 remains first priority. Current blocker is publication, not design uncertainty: safely replace `strict_fence.py` with the already exact reconstructed candidate `eb219835...`, then verify the GitHub-returned blob and rerun the published strict/thaw subgate.
- Available GitHub write primitive for this existing ~935-line security-critical file is whole-file text replacement. Direct shell/raw GitHub transport remains unavailable. Do not hand-transcribe the file or weaken the blob-integrity gate.
- PR #165 must remain draft until the runtime fix is published, strict/thaw tests are green on published bytes, a new executable snapshot is pinned, and the complete branch-local LAB-080→086 real-ledger gate passes.
- LAB-090/#169 provider handoff freshness remains separate. Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: publish the already reconstructed candidate `strict_fence.py` only through a byte-safe full-payload path. Expected local candidate blob before publication: `eb2198354d222ad0ad6b7d751bf5c649157b6b36`; current remote source blob: `080eb9454437932a8ab419d66a4f2a69ed17c7ce`.
2. Immediately fetch the published file and require its Git blob to equal the candidate bytes. If it differs, revert/fix before counting any test.
3. Execute corrected `test_thaw_alternate_unique_collision_regression.py` together with `test_strict_fence.py`, thaw history/null/proof replacement regressions, thaw-minimality/conflict regressions, and compileall. Fix every failure.
4. Repin the executable snapshot after runtime/test bytes are final.
5. Reconstruct that branch-local LAB-080→086 closure, verify every local file with `git hash-object`, execute every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and full compileall.
6. Perform fresh final security/reconciliation audit and branch/main compare. Only a clean full gate may make PR #165 ready/integratable.
7. If publication remains concretely tool-limited, continue LAB-091 real supported LAB-080/LAB-082 worker/UNKNOWN integration rather than repeating focused stubs.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; alternate-UNIQUE blocker true RED→GREEN proven on exact reconstructed bytes; byte-safe runtime publication next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; complete real LAB-080/LAB-082 integration gate remains.
