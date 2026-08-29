# Current Lab State

Last updated: 2026-08-29

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative live LAB-086 `strict_fence.py` predecessor: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Retained hidden-rowid patch: `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact previously derived/tested target: `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-091 / #170 remains fallback IN_PROGRESS on draft PR #173, branch `lab/091-mutable-shared-anchor-writer`, only while LAB-086 exact publication/execution is concretely tool-limited.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172. LAB-090 / #169 remains READY.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. LAB-086 remains first priority but this run still exposes no supported machine-to-machine byte-preserving composition path from the exact 949-line predecessor plus retained hidden-rowid patch into a normal Contents write. Do not manually/model-reserialize that security-critical file.

Used the allowed LAB-091 fallback and completed the previously required final-surface identity-collation inventory/fix. The reproduced defect was broader than `reserve()`: legacy NOCASE identity columns plus separate canonical BINARY UNIQUE indexes can make plain supported predicates alias byte-distinct intent, component and receipt identities.

Published on PR #173 head `0d73b6bc4d51e8dc018627bd1df1dc2b7ddd0383`:
- `binary_identity_provider_history.py` blob `d412d3b6abb70b5947243dcf5988314733f6f6df` — final receipt load/maybe-load/store use explicit BINARY request identity;
- `history_bound_operation_scoped.py` blob `5cb106fc26ac79d0f7c09c732b176b17ac4665f0` — final class installs the binary receipt helper and overrides `entry()` / `watermark()` with BINARY reads;
- `operation_scoped_integration.py` blob `577979b1c3643c6232fd76cccd942429214542ca` — reachable intent/watermark lookup and CAS predicates are BINARY;
- `convergent_operation_scoped.py` blob `f93e67f8140782aec824fb4057832d568c761712` — convergent confirmation lookup/CAS is BINARY;
- `full_operation_guards.py` blob `6ff1f5eedac80c524163a7e78ea03cd1f0460742` — v2 freshness checks use BINARY intent/request/component/receipt identity;
- `test_identity_lookup_collation_regression.py` blob `c35c4280d26ba7c90a88a891fbce697c83ffb7f5`.

Focused local SQLite semantic probe: PASS. It reconfirmed the old NOCASE aliases and proved the new explicit BINARY predicate form distinguishes case-distinct intent/component/receipt identities; a BINARY freshness trigger accepts a genuinely byte-distinct identity and rejects an exact duplicate. This is mechanism evidence only, not exact published pytest execution.

Durable analysis: `research/2026-08-29-lab091-binary-identity-supported-surface-fix.md`, main commit `bd8007b76559a103fffe3cf577038e7d932fd881`; PR #173 comment `5464675734`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED→GREEN evidence retained; exact predecessor `d4a6a40f...` -> candidate `b78e7c98...` previously byte-rederived and focused mechanism-tested; publication/full gate still pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption hardening combined focused gate 17/17 PASS before later affinity/collation fixes.
- LAB-091 missing-singleton 2/2 PASS; persisted-trigger confused-deputy 3/3 PASS + compileall; legacy intent affinity regression 3/3 PASS + compileall.
- LAB-091 receipt affinity/domain focused semantic gate 4/4 PASS; exact published pytest execution pending transport.
- LAB-091 receipt collation focused semantic gate 4/4 PASS + compileall; exact published pytest execution pending transport.
- LAB-091 status-collation follow-up found no supported-path bypass; no speculative patch added.
- LAB-091 identity lookup collation alias reproduced, final supported identity surface patched, focused SQLite semantic probe PASS; exact published regression execution pending transport.
- LAB-091 alternate-write REPLACE / UPSERT / multi-row UPDATE all fail closed; no bypass established.
- LAB-091 published real-stack timeout/UNKNOWN regression blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05`; full execution pending.
- LAB-091 published process concurrency/crash regression blob `938877479d4c4b997ea52e8b5857bf89e5c3e246`; full final-ledger execution pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40f...`, applying only retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid candidate publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft. Identity-collation runtime patch is published but its exact pytest regression is still unexecuted; timeout/UNKNOWN, process concurrency/crash, receipt-affinity and receipt-collation final-surface gates also remain pending exact branch execution.
- Published receipt-affinity and receipt-collation regressions still need exact branch execution when executable transport becomes available; do not represent focused semantic reproductions as byte-for-byte branch execution.
- Do not add speculative SQLite guards without a reproduced reachable mutation or compatibility failure under actual supported semantics.

## Exact next action

1. LAB-086 first: if a supported machine-to-machine byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40f...`, apply only retained hidden-rowid patch, require exact target `b78e7c98...`, publish via normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates.
2. If LAB-086 remains concretely tool-limited, execute/reconstruct as much of the exact PR #173 branch gate as the runtime permits, starting with `test_identity_lookup_collation_regression.py` on current head `0d73b6bc...`, then timeout/UNKNOWN `92133cdc...`, process concurrency/crash `93887747...`, receipt-affinity `35baec3b...`, and receipt-collation `25f7eca3...` through the final supported class.
3. Audit the new binary identity wiring for constructor/restart compatibility and any remaining inherited plain identity predicates before treating the collation blocker as closed.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; identity-collation fix published, exact branch regression/full behavioral gates pending.
