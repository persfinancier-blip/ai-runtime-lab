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
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current PR #173 HEAD `4afe558d899057c03e57a3c2a6cf7742d0ab1525`; fallback only while LAB-086 exact work is concretely tool-limited.

## Last completed step

LAB-086 publication was probed first. Direct shell/raw GitHub transfer remains unavailable in this runtime and the connector still returns exact repository bytes without mounting ordinary blobs into the local executor. The ~40 KB security-critical `strict_fence.py` hidden-rowid candidate was therefore not manually reserialized; byte-exact publication remains the blocker and PR #165 stays draft.

Used the allowed LAB-091 fallback and found a second real first-adoption fail-closed gap after the prior history/contiguity fix. Exact published `adoption_validation.py` blob `36551cce4351e9305262d8f3476ad633d3246564` verified deterministic request IDs and history shape, but did not validate intent/provider field domains. Because the deterministic request ID can be recomputed over arbitrary persisted fields, the old validator accepted rows that supported LAB-080 could not create: unknown intent type, empty intent identity, non-canonical payload digest, empty provider identity, and provider generation `0`.

Published LAB-091 domain fix on PR #173:
- `adoption_validation.py` commit `ad0c6a0cf791577b1e14e8cd37e91a8d65ff4bb2`, blob `c410887dacac46ede2ae4e0cf78b54ca2666205b`;
- new regression `test_adoption_field_domain_regression.py` commit `4afe558d899057c03e57a3c2a6cf7742d0ab1525`, blob `d819018dbbed4160e8b30bcb6101785a23de9038`.

The validator now additionally imports LAB-080 `ALLOWED_INTENT_TYPES` and requires non-empty intent/component/provider identities, supported intent type, canonical lowercase 64-hex payload digest, and positive integer provider generation before the existing request-id/contiguity/status checks.

Exact/focused evidence for this fallback slice:
- old pre-fix `adoption_validation.py` `36551cce...` plus `operation_permit.py` `637784a5...` and `state_machine_udfs.py` `8c1d6d0c...` were byte-matched before reproduction; all five malformed-domain examples were accepted by the old validator;
- published fixed `adoption_validation.py` blob `c410887d...` exactly equals the executed candidate;
- new published regression blob `d819018d...` exactly equals the executed candidate;
- pre-existing `test_adoption_validation.py` blob `ef19e3f21994e5d5282eec30a785a1cfe101f3ed` MATCH;
- pre-existing `test_adoption_history_regression.py` blob `9f705187059b577c131535959a347f52a55178e9` MATCH;
- combined adoption gate: **23/23 PASS + compileall PASS**.

Issue #170 comments `5447979300` and `5447986867` record the finding, publication hashes and combined evidence. PR #173 remains draft because this does not replace the full real LAB-080/LAB-082 concurrency/crash/UNKNOWN supported-surface gate.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Previous repinned LAB-086 strict/thaw exact subgate: 31/31 PASS + compileall on pin `1fa85a0e...`; it is not sufficient for merge because hidden-rowid conflict was not covered.
- Hidden-rowid exact RED→GREEN retained: predecessor RED 3/3, candidate `b78e7c98...` GREEN 3/3 + compileall; fresh independent byte-transition revalidation also matched both hashes.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption-state history/contiguity fix previously reached exact 15/15 + compileall; after the new domain-validation regression the combined published adoption gate is now **23/23 PASS + compileall**.

## Known blockers / constraints

- LAB-086 remains first priority. Hidden-rowid fix must be published byte-exact before the full real-ledger gate resumes.
- Direct shell/raw GitHub transport remains unavailable. Connector reads are byte-exact but file-by-file and do not mount ordinary repository files into the local executor.
- The available Contents write cannot consume the exact local candidate file by reference; manually transcribing/reformatting the large security-critical file would weaken the established exact-blob discipline.
- A reconstructed file counts as execution evidence only if `git hash-object` equals the GitHub blob.
- PR #165 must remain draft until rowid fix publication, repinned strict/thaw subgate, complete real-ledger gate, unsafe seed, compileall and final audit are all clean.
- LAB-091 PR #173 remains draft; its remaining gate is full real LAB-080/LAB-082 two-worker/crash/UNKNOWN supported-surface execution, LAB-087 composition and final alternate-surface/reentrancy audit.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: obtain a byte-safe supported transfer path for exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` into `experiments/asymmetric_break_glass_history/strict_fence.py` on PR #165. Publish only if branch predecessor remains `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` and GitHub returns exactly `b78e7c98...`.
2. Re-fetch/hash-verify the published runtime, execute exact `test_thaw_rowid_collision_regression.py` plus the complete strict/thaw conflict subgate and compileall, then repin only after green evidence.
3. Resume complete branch-local LAB-080→086 real-ledger modules, unsafe legacy-promotion expected-failure seed, full compileall and final security/reconciliation audit.
4. If LAB-086 publication is still concretely tool-limited, continue LAB-091 with the full real LAB-080/LAB-082 two-worker/crash/UNKNOWN supported-surface execution; do not substitute focused stubs unless a new executable blocker is first reproduced.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; hidden-rowid blocker has exact RED→GREEN candidate evidence; byte-exact runtime publication is next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; adoption-state/domain gate now 23/23 PASS + compileall; full real-stack gate remains.
