# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current PR #165 HEAD: `f74f20cca7a4e8c63dd04325be28acbc929af194` (manifest-only after executable fix).
- Current executable pin: `1f90830fca21e2f43fc241012cdd34fd187ba96d`.
- Published `strict_fence.py` blob: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- GitHub reports PR #165 draft/mergeable=true. Mergeability is not a test/security result.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact reconstruction/execution is concretely tool-limited.

## Last completed step

Found and fixed a new LAB-086 restart blocker in the inherited LAB-082 provider-receipt fence.

Exact LAB-082 schema has `asymmetric_provider_receipts.request_id TEXT PRIMARY KEY` without explicit `NOT NULL`. SQLite rowid tables therefore admit NULL request identities. The previous LAB-086 `lab086_provider_receipt_no_replace` used `request_id=NEW.request_id`, so a post-cutoff NULL receipt bypassed the collision guard.

This is a LAB-086 merge blocker because exact LAB-082 durable verification enumerates every receipt row and constructs `SignedReceipt`; `SignedReceipt.validate()` requires a non-empty string request_id. A persisted NULL receipt therefore makes the next durable verification/restart fail closed. Pre-cutoff malformed receipts are already rejected by inherited LAB-082 verification before cutoff.

Durable RED/fix artifacts:
- regression `test_provider_receipt_null_identity_regression.py` blob `a66d9ddef2d4a41db937222b875f697c7ff74b75`;
- patch `research/2026-08-28-lab086-provider-receipt-null-identity.patch`;
- research note `research/2026-08-28-lab086-provider-receipt-null-identity.md`.

Published fix:
- executable commit `1f90830fca21e2f43fc241012cdd34fd187ba96d`;
- runtime blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`;
- compare from preceding branch head `2c854042...` is exactly one modified file (`strict_fence.py`), +7/-3;
- exact published source rejects `NEW.request_id IS NULL` and checks existing identities with `request_id IS NEW.request_id`.

Post-publication focused SQLite semantic check using the exact published predicate: NULL receipt BLOCKED; genuinely new non-NULL receipt ALLOWED; duplicate non-NULL request ID BLOCKED. This is semantic/source evidence only, not an exact published unittest-suite PASS.

Exact-gate manifest was repinned to executable `1f90830f...` in manifest-only commit `f74f20cca7a4e8c63dd04325be28acbc929af194`.

Fresh branch/main compare: ahead 185 / behind 134. All LAB-086/runtime/research paths in the compare remain additions relative to `main`; observed divergence is still historical/path-disjoint, not a proven content conflict.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Predecessor published LAB-086 thaw/fence exact subgate: 14/14 PASS + compileall.
- Alternate-UNIQUE regression/candidate evidence retained; previous runtime `eb219835...` was byte-identical to its focused corrected candidate.
- New receipt-NULL runtime publication is byte-safe by one-file +7/-3 compare and returned blob `d4a6a40f...`; post-publication focused semantic check passed the intended BLOCK/ALLOW/BLOCK behavior.
- No repinned exact unittest subgate PASS is claimed yet for executable `1f90830f...`.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.

## Known blockers / constraints

- LAB-086 remains first priority. Remaining work is now execution evidence, not another protocol redesign unless a new executable/source blocker appears.
- Direct shell/raw GitHub transport is still unavailable (`git ls-remote` fails DNS). Connector reads are byte-exact but large source transfer into the local executor remains file/chunk oriented.
- A reconstructed file counts as exact only if `git hash-object` equals the pinned Git blob. Focused semantic checks must not be promoted to exact-suite evidence.
- PR #165 must remain draft until the repinned strict/thaw subgate, complete branch-local LAB-080→086 real-ledger tests, unsafe seed, compileall and final security/reconciliation audit are all clean.
- LAB-090/#169 provider handoff freshness remains separate. Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct/hash-verify `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, new receipt-NULL regression blob `a66d9ddef2d4a41db937222b875f697c7ff74b75`, and retained strict/thaw regression modules from executable pin `1f90830f...`.
2. Execute the repinned strict/thaw subgate: receipt NULL identity, alternate-UNIQUE, primary/history/proof replacement, NULL proof identities, transaction-scoped thaw minimality, current-authority/root-head/conflict tests + compileall.
3. Reconstruct the complete branch-local LAB-080→086 dependency closure from the same pin; execute every normal LAB-086 real-schema module, unsafe legacy-promotion expected-failure seed and full compileall.
4. Perform final security/reconciliation audit and fresh branch/main compare. Only a completely clean gate may make PR #165 ready/integratable.
5. Use LAB-091 fallback only if LAB-086 exact reconstruction/execution is concretely tool-limited again.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; provider-receipt NULL identity blocker fixed/published; repinned exact execution gate next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; fallback only while LAB-086 is tool-limited.
