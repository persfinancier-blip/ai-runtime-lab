# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current PR #165 HEAD: `e6bf48d81129914b8dbe3e23a2b1a416fab11e24`; current executable pin: `05d8e75a636818afcb32e085d464c9fa9171dea5`.
- Fresh GitHub status: PR #165 is draft + mergeable=true. Mergeability is not a substitute for the execution gate.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact reconstruction/execution is concretely tool-limited.

## Last completed step

Resumed the exact published LAB-086 execution gate at pinned snapshot `05d8e75a...`. The connector now supports exact line-range reads of the 945-line `strict_fence.py`, so the previous display-truncation problem can be avoided. A complete local text reconstruction was attempted and then rejected by the mandatory Git blob gate: local `956472d15be506f94db8849cc43bd83eb7fcb0f2` != published `eb2198354d222ad0ad6b7d751bf5c649157b6b36`. No test execution from that reconstruction was counted. Connector base64 paging is also available, but there is still no supported machine pipe/mount from connector response bytes into the local executor; manually transcribing a security-critical 37 KB blob remains non-evidence.

Because that exact-execution path remained concretely tool-limited, performed the allowed LAB-091 fallback source audit. The final inheritance path is `history_bound_operation_scoped -> state_machine_operation_scoped -> convergent_operation_scoped -> operation_scoped_integration`. The broad `except Exception -> PendingIntent` in the base prototype is not reachable through the final execute method: the convergent override narrows retryable conversion to `ProviderUnavailable` / `UnknownOutcome`. Also confirmed LAB-082 cached receipt loading is cryptographic, not raw-row trust: `_maybe_load_receipt_locked()` calls `_verify_receipt_locked()` and checks stable binding. No new LAB-091 blocker was established.

Issue #163 and Issue #170 were updated with these exact observations. No LAB-086 or LAB-091 runtime code changed in this run.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Predecessor published LAB-086 thaw/fence exact subgate: 14/14 PASS + compileall.
- Corrected LAB-086 alternate-UNIQUE regression blob `a767e6bbb5e164a846c93d04b9c8c3f7980bba38`.
- Published LAB-086 `strict_fence.py` blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36` is byte-identical to the corrected candidate that passed focused alternate-UNIQUE 1/1 + `py_compile` before publication.
- Current run: failed reconstruction hash was explicitly rejected; zero new LAB-086 PASS claims were added.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 exact published secondary-UNIQUE intent regression: 2/2 PASS + compileall, blob `cb034b5b62e59ecf52038c69c652a74a9c9783d8`.
- Current LAB-091 source audit: final execute path uses the convergent narrow exception policy; cached receipts are cryptographically reverified before use.

## Known blockers / constraints

- LAB-086 remains first priority. Remaining work is the exact published execution gate, not more protocol redesign unless a new executable/source audit blocker appears.
- The retained predecessor 14/14 thaw/fence result must still be rerun on repinned snapshot `05d8e75a...`.
- Direct shell/raw GitHub transport is unavailable. Connector reads are byte-exact and support ranges/base64, but there is no supported binary/text stream handoff into the local executor; large manual reconstruction must continue to fail the evidence gate unless the local blob hash matches exactly.
- PR #165 must remain draft until the repinned strict/thaw subgate, complete branch-local LAB-080→086 real-ledger tests, unsafe seed, compileall and final security/reconciliation audit are all clean.
- LAB-090/#169 provider handoff freshness remains separate. Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Continue exact `strict_fence.py` reconstruction from executable pin `05d8e75a...` using connector range/base64 reads, but execute nothing until local `git hash-object` equals `eb2198354d222ad0ad6b7d751bf5c649157b6b36`.
2. Once exact, reconstruct/hash-verify the strict/thaw regression modules and run the repinned subgate: alternate-UNIQUE, primary/history/proof replacement, NULL identities, transaction-scoped thaw minimality, conflict/current-authority/root-head tests + compileall.
3. Reconstruct the complete branch-local LAB-080→086 dependency closure from the same executable pin, execute every normal LAB-086 real-schema module, unsafe legacy-promotion expected-failure seed and full compileall.
4. Perform final security/reconciliation audit and fresh branch/main compare. Only a completely clean gate may make PR #165 ready/integratable.
5. Use LAB-091 fallback only when exact LAB-086 reconstruction/execution is concretely tool-limited; next fallback target remains the full real LAB-080/LAB-082 supported-surface two-worker/crash/UNKNOWN gate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; alternate-UNIQUE fix published byte-exact; repinned execution gate next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; no new blocker from inheritance/receipt-verification audit; full real-stack gate remains.
