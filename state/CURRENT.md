# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `6a368a26e85c5d0672a527481f44f47283c8f951`.
- PR is mergeable but remains draft; full current-head real-ledger gate is not complete.
- Parallel LAB-087/#166 remains IN_PROGRESS; its exact authorizer/process/filesystem gate was previously 12/12 PASS.

## Last completed step

Solved the exact-source transport bottleneck without weakening the gate. Direct shell/raw GitHub transport is still unavailable, but the GitHub connector exposes blob-by-SHA reads. `fetch_blob` returns byte-stable source suitable for local execution and `git hash-object` verification.

Reconstructed the LAB-080 shared-anchor implementation through this path and verified exact identities locally:
- `experiments/shared_anchor_intent_ledger/protocol.py` → `68834409363c93eee4e9a9a7b9ec076098af0acf`;
- `experiments/shared_anchor_intent_ledger/supported.py` → `22a05c04831f65c1d7fe9077df3bb780c4008e09`.

A fresh current-head source/schema coverage audit rechecked `migration_guard.py`, `suffix.py`, `final_supported.py`, `strict_fence.py`, LAB-085 public custody/final tables and LAB-082 provider history. No new privilege-escalation or stale-supported-writer bypass was established. The remaining intentionally mutable/unrestricted boundaries are already tracked in LAB-091/#170 (shared-anchor/new-receipt writer authorization) and LAB-087/#166 (arbitrary same-privilege DDL/schema control).

No new PASS is claimed for the changed `test_suffix.py`; exact execution still requires reconstructing the remaining LAB-082→085 implementation closure and current LAB-086 files.

## Evidence produced / reconfirmed

- Exact LAB-086 migration guard integration: 11/11 PASS from the prior current-head closure.
- Exact corrected scrubbed-prefix → final-writer → restart regression: 1/1 PASS.
- Current LAB-086 implementation blobs previously reconstructed exactly: migration guard `5a5bb928b39a96f93f019b103b483dfb9bf43c6d`, strict fence `5da01e28a9f813a136d138637f855940f04aab46`, suffix `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`, final supported `ceb7f48a55a931ba9923cac77d4ebf6c4cd2cfec`.
- Current `test_suffix.py` blob: `14b87522974a365738a56d82923ed9ae377a752e`; successful post-cutoff mutations use the final fenced surface, negative tests remain on the underlying suffix surface.
- Cumulative exact lower-stack evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric-custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Fresh branch/main compare: ahead 142 / behind 83; the LAB-086 PR paths remain additions relative to main, so the observed divergence is history/path-nonoverlap rather than a current path-level conflict.
- Exact connector reconstruction path is now proven by blob SHA and local `git hash-object`; manual line-range reconstruction must not be counted as evidence.

## Known blockers / constraints

- Full current-head LAB-086 gate is still incomplete: updated exact `test_suffix.py` and remaining final-supported/security modules must be executed on one exact reconstructed closure, followed by unsafe legacy-promotion seed, full compileall and final audit.
- Direct shell GitHub transport remains unavailable; connector `fetch_blob` is the supported exact-source fallback and is not an owner blocker.
- Do not weaken the runtime fence to satisfy stale tests. Successful consequential mutation after cutoff must use the final fenced surface.
- LAB-086 SQL fences cover audited supported/DML paths, not arbitrary same-privilege schema/DDL authority; LAB-087/#166 owns that boundary.
- LAB-088/#167 signer-noise, LAB-090/#169 provider handoff freshness, and LAB-091/#170 mutable shared-anchor/new-receipt authorization remain separate follow-ups.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Use connector `fetch_blob` by known Git SHA to reconstruct the exact LAB-082→085 implementation closure into one local workspace, verifying each executable file with `git hash-object`; replace any earlier manual/non-exact local copies before testing.
2. Add the current exact LAB-086 implementation and `test_suffix.py` blob `14b87522974a365738a56d82923ed9ae377a752e`, then execute it.
3. Execute the remaining current-head real-ledger security modules: orphan/partial migration, full lower/public-history guards, public-rotation cross-binding/history, inherited/direct surfaces, rotation races, final single-snapshot verification and strict DML/fence regressions not already counted in this closure.
4. Run unsafe legacy-promotion seed and full compileall over the complete reconstructed closure.
5. Perform a fresh security audit and branch/main conflict check. Fix every blocking failure before ready/merge; only after a clean complete gate may PR #165 be marked ready and integrated.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact blob transport solved; migration guard 11/11 and corrected scrubbed-suffix 1/1 PASS; current `test_suffix.py` awaits exact closure execution.
- #166 / LAB-087 — IN_PROGRESS; prior exact current slice 12/12 PASS.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable/shared-ledger plus new provider-receipt writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
