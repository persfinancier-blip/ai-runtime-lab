# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current PR #165 HEAD after RED/research artifacts: `2c8540420f55cd41ccf12c953d2f7521790902b1`.
- Last executable pin remains `05d8e75a636818afcb32e085d464c9fa9171dea5`; published `strict_fence.py` remains blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36`.
- PR #165 is draft/mergeable; mergeability does not substitute for the execution gate.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact reconstruction/execution is concretely tool-limited.

## Last completed step

Fresh pinned-source audit found a new LAB-086 merge blocker in the LAB-082 provider-receipt fence.

Exact pinned LAB-082 schema defines `asymmetric_provider_receipts.request_id` as `TEXT PRIMARY KEY` without explicit `NOT NULL`. Current LAB-086 `lab086_provider_receipt_no_replace` compares `request_id=NEW.request_id` and therefore does not reject `NEW.request_id IS NULL`. A focused SQLite reproduction using the exact table shape/current predicate accepted multiple NULL request IDs.

This is a real LAB-086 restart blocker, not only LAB-091 arbitrary-writer hardening: exact pinned `IntegratedAsymmetricProviderHistory._verify_durable_locked()` enumerates every persisted receipt, and `SignedReceipt.validate()` requires `request_id`, `kind`, and `challenge` to be non-empty strings. Therefore one post-cutoff NULL receipt accepted by the current fence deterministically makes the next durable verification/restart fail closed.

Pre-cutoff malformed receipts do not escape migration because LAB-086 verifies inherited LAB-082 durable history before establishing the cutoff.

Staged minimal predicate:
`NEW.request_id IS NULL OR EXISTS(SELECT 1 FROM asymmetric_provider_receipts WHERE request_id IS NEW.request_id)`.
Focused RED→GREEN semantics: current predicate allowed NULL; staged predicate blocked NULL while preserving a genuinely new non-NULL receipt insert.

Durable artifacts on PR #165 branch:
- RED regression `experiments/asymmetric_break_glass_history/tests/test_provider_receipt_null_identity_regression.py`, commit `20fd52bd6066c158de5464ebc9d5e61bd0563bd3`;
- exact patch `research/2026-08-28-lab086-provider-receipt-null-identity.patch`, commit `5c09a5ed774072f1c9d68f3c960bf1bc39ebb25a`;
- research/evidence note `research/2026-08-28-lab086-provider-receipt-null-identity.md`, commit `2c8540420f55cd41ccf12c953d2f7521790902b1`.

Runtime `strict_fence.py` has not yet been rewritten for this blocker, so no post-fix exact-suite PASS is claimed.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Predecessor published LAB-086 thaw/fence exact subgate: 14/14 PASS + compileall.
- Alternate-UNIQUE regression blob `a767e6bbb5e164a846c93d04b9c8c3f7980bba38`; current published runtime `eb219835...` is byte-identical to that focused corrected candidate.
- New provider-receipt NULL-identity focused counterexample/fix semantics executed as described above; exact post-fix runtime execution is still pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 retained exact/focused evidence remains durable; it is not the active priority while this LAB-086 blocker is open.

## Known blockers / constraints

- LAB-086 remains first priority. The new provider-receipt NULL-identity blocker must be fixed before resuming the repinned full execution gate.
- Direct shell/raw GitHub transport remains unavailable. Connector reads are byte-exact but large source transfer into the local executor is file/chunk oriented; manual reconstruction is non-evidence unless `git hash-object` matches the published blob.
- PR #165 must remain draft until the NULL receipt fix is published byte-exact, the strict/thaw subgate is rerun on the new pin, the complete branch-local LAB-080→086 real-ledger tests/unsafe seed/compileall are clean, and final security/reconciliation audit passes.
- LAB-090/#169 provider handoff freshness remains separate. Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Apply `research/2026-08-28-lab086-provider-receipt-null-identity.patch` only to current `strict_fence.py` blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36` using a byte-safe whole-file Contents API path; verify the returned blob and exact diff before counting the fix.
2. Execute `test_provider_receipt_null_identity_regression.py` plus the repinned strict/thaw subgate (alternate-UNIQUE, history/proof replacement, NULL identities, thaw minimality, current-authority/root-head/conflict tests) and compileall from hash-verified published bytes.
3. Repin the executable snapshot, reconstruct the complete branch-local LAB-080→086 closure, execute every normal LAB-086 real-schema module, unsafe legacy-promotion expected-failure seed and full compileall.
4. Perform final security/reconciliation audit and fresh branch/main compare. Only a completely clean gate may make PR #165 ready/integratable.
5. Use LAB-091 fallback only if LAB-086 exact write/reconstruction is concretely tool-limited again.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; provider-receipt NULL identity blocker confirmed; RED regression + exact patch durable; runtime fix next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; fallback only while LAB-086 is tool-limited.
