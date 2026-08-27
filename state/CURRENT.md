# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current PR #165 HEAD: `036f36c4a08242a25ecad5842fc3f8401f2f197f` (manifest-only after executable/test pin).
- Current executable/test pin: `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`.
- Published `strict_fence.py` blob: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- GitHub reports PR #165 draft/mergeable=true. Mergeability is not a test/security result.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact reconstruction/execution is concretely tool-limited.

## Last completed step

Closed the repinned LAB-086 strict/thaw execution subgate on exact published bytes.

First, a pinned-source audit found that inherited LAB-082 `asymmetric_provider_receipts.request_id TEXT PRIMARY KEY` accepts SQL NULL while LAB-082 durable verification rejects NULL receipt identities. The LAB-086 receipt collision trigger therefore gained an explicit `NEW.request_id IS NULL` rejection plus NULL-safe `request_id IS NEW.request_id` collision check. Runtime publication:
- executable fix commit `1f90830fca21e2f43fc241012cdd34fd187ba96d`;
- `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`;
- compare from preceding branch head changed exactly one file, +7/-3.

Exact connector line-range reconstruction then produced a local `strict_fence.py` whose `git hash-object` exactly matched `d4a6a40f...`. New receipt-NULL regression blob `a66d9ddef2d4a41db937222b875f697c7ff74b75` passed against it.

The expanded exact subgate exposed one test-only schema drift: `test_thaw_history_key_collision_regression.py` still modeled `asymmetric_provider_generations(generation_id, marker)`, while hardened runtime correctly reads real `provider_id/generation`. Runtime was not weakened. The test was updated to the real LAB-082 provider-generation schema and published byte-identical to the passing candidate:
- test commit/pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`;
- corrected test blob `55f3f2b20a02b566bbeb6461ac54910a7194a9f9`.

Final combined exact strict/thaw result on pin `1fa85a0e...`: **31/31 distinct tests PASS + compileall PASS**.

Coverage includes base strict/conflict algorithms, provider receipt append-only + NULL identity, alternate `(provider_id,generation)` UNIQUE collision, primary/history/proof replacement and NULL identities, transaction-scoped thaw least privilege, current root/provider authority DML/conflict, root-head mutation fencing and inherited lower root/provider SQL fences.

The exact-gate manifest was repinned to `1fa85a0e...` in manifest-only commit `036f36c4a08242a25ecad5842fc3f8401f2f197f`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Current repinned LAB-086 strict/thaw exact subgate: **31/31 PASS + compileall** on hash-verified published files.
- New provider receipt NULL identity regression blob `a66d9ddef2d4a41db937222b875f697c7ff74b75`.
- Corrected real-schema thaw-history regression blob `55f3f2b20a02b566bbeb6461ac54910a7194a9f9`.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.

## Known blockers / constraints

- LAB-086 remains first priority. The strict/thaw subgate is complete; remaining work is the complete branch-local LAB-080→086 real-ledger execution gate, unsafe seed, full compileall and final security/reconciliation audit.
- Direct shell/raw GitHub transport remains unavailable (`git ls-remote` fails DNS). Connector line-range reconstruction is byte-exact but file-by-file.
- A reconstructed file counts as evidence only if `git hash-object` equals the pinned Git blob.
- Non-LAB executor stderr included artifact-tool spreadsheet warmup failures and Python `ResourceWarning` messages from test DB handles; LAB unittest/compileall return codes were 0.
- PR #165 must remain draft until the full real-ledger gate and final audit are clean.
- LAB-090/#169 provider handoff freshness remains separate. Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct/hash-verify the complete branch-local LAB-080→086 implementation/test dependency closure from pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; reuse already exact local `strict_fence.py` and strict/thaw tests rather than rebuilding them.
2. Execute every normal LAB-086 real-schema test module from that same pin, then `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure.
3. Run full compileall over the reconstructed closure.
4. Perform final security/reconciliation audit and fresh branch/main compare. Only a completely clean gate may make PR #165 ready/integratable.
5. Use LAB-091 fallback only if exact LAB-086 reconstruction/execution is concretely tool-limited again.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; strict/thaw exact gate 31/31 clean; full branch-local real-ledger gate next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; fallback only while LAB-086 is tool-limited.
