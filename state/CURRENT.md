# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current PR #165 HEAD observed this run: `3cc63c2133507fd8d468471e1fe0fe5b3680e12c`; last fully executed published runtime/test pin before the hidden-rowid blocker: `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`.
- Published LAB-086 runtime at that pin: `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Hidden-rowid candidate remains `b78e7c98e35138719f77c482c7f1aab36b702de7`; runtime is intentionally still unpatched.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact work is concretely tool-limited.

## Last completed step

LAB-086 publication was probed first. Direct shell/raw GitHub transfer remains unavailable and the normal Contents update accepts only a complete UTF-8 payload, not the locally reconstructed exact candidate file. The ~40 KB security-critical `strict_fence.py` was therefore not manually reserialized; byte-exact publication remains the blocker.

Used the allowed LAB-091 fallback and found a real adoption-state integrity gap. Persistent v2/v3/v4 triggers constrain only future DML, while the prior `validate_existing_mutable_state_locked()` checked only deterministic request IDs and orphan receipts. A DB with `shared_anchor_meta.reserved_position=5` and `component_anchor_watermarks('component-A',5)` but zero intent rows was accepted by the old validator. That is not only fail-closed availability risk: LAB-080 returns immediately when authenticated external position equals the local watermark, so inherited verification progress could exist without corresponding durable history.

Published LAB-091 fix on PR #173:
- `adoption_validation.py` commit `fc18282688591839604bf4057be3691cccb719a5`, blob `36551cce4351e9305262d8f3476ad633d3246564`;
- expanded adoption tests commit `c22b6d88c629ba0bd7f26aa1ac396b07befda656`, blob `ef19e3f21994e5d5282eec30a785a1cfe101f3ed`;
- focused exact regression `test_adoption_history_regression.py` commit `7ec1fcaf32bef7ba6e9519201592d066644220f5`, blob `9f705187059b577c131535959a347f52a55178e9`;
- research note updated in commit `0df6602a95440253c645c989fe7f0c8e7a4ba7bd`.

The validator now requires a valid meta singleton; reserved tail exactly equal to contiguous intent history; exact predecessor/position chain; deterministic request IDs; at most one PREPARED row and only at the tail; CONFIRMED rows with receipt bindings; no orphan receipts; and inherited component watermarks backed by complete contiguous CONFIRMED history.

Exact published-source execution evidence:
- `operation_permit.py` blob `637784a5cb61a024a1df3e0e983887b6d0a838be` matched;
- `state_machine_udfs.py` blob `8c1d6d0cd075285aed3a90ac337b60b60c1d608b` matched;
- patched `adoption_validation.py` blob `36551cce4351e9305262d8f3476ad633d3246564` matched;
- extended `test_adoption_validation.py` blob `ef19e3f21994e5d5282eec30a785a1cfe101f3ed` matched;
- focused regression blob `9f705187059b577c131535959a347f52a55178e9` matched;
- combined exact adoption gate: **15/15 PASS + compileall PASS**.

Issue #170 comments `5447592284` and `5447603930` record the finding/fix and exact evidence. PR #173 remains draft.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Previous repinned LAB-086 strict/thaw exact subgate: 31/31 PASS + compileall on pin `1fa85a0e...`; it is not sufficient for merge because hidden-rowid conflict was not covered.
- Hidden-rowid exact RED→GREEN retained: predecessor RED 3/3, candidate `b78e7c98...` GREEN 3/3 + compileall; fresh independent byte-transition revalidation also matched both hashes.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption-state fix: exact published-source **15/15 PASS + compileall**.

## Known blockers / constraints

- LAB-086 remains first priority. Hidden-rowid fix must be published byte-exact before the full real-ledger gate resumes.
- Direct shell/raw GitHub transport remains unavailable. Connector reads are byte-exact but file-by-file and do not mount ordinary repository files into the local executor.
- The available Contents write cannot consume the exact local candidate file by reference; manually transcribing/reformatting the large security-critical file would weaken the established exact-blob discipline.
- A reconstructed file counts as execution evidence only if `git hash-object` equals the GitHub blob.
- PR #165 must remain draft until rowid fix publication, repinned strict/thaw subgate, complete real-ledger gate, unsafe seed, compileall and final audit are all clean.
- LAB-091 PR #173 remains draft; its remaining gate is full real LAB-080/LAB-082 two-worker/crash/UNKNOWN supported-surface execution, LAB-087 composition and final alternate-surface/reentrancy audit.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: obtain a byte-safe supported transfer path for exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` into `experiments/asymmetric_break_glass_history/strict_fence.py` on PR #165. Publish only if branch predecessor remains `d4a6a40f...` and GitHub returns exactly `b78e7c98...`.
2. Re-fetch/hash-verify the published runtime, execute exact `test_thaw_rowid_collision_regression.py` plus the complete strict/thaw conflict subgate and compileall, then repin only after green evidence.
3. Resume complete branch-local LAB-080→086 real-ledger modules, unsafe legacy-promotion expected-failure seed, full compileall and final security/reconciliation audit.
4. If LAB-086 publication is still concretely tool-limited, continue LAB-091 with the full real LAB-080/LAB-082 two-worker/crash/UNKNOWN supported-surface execution; do not substitute focused stubs.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; hidden-rowid blocker has exact RED→GREEN candidate evidence; byte-exact runtime publication is next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; adoption-state gap fixed with exact 15/15 evidence; full real-stack gate remains.
