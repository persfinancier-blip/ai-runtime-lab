# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative live LAB-086 `strict_fence.py` predecessor: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Retained hidden-rowid patch: `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact previously derived/tested target: `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-091 / #170 remains fallback IN_PROGRESS on draft PR #173, branch `lab/091-mutable-shared-anchor-writer`, only while LAB-086 exact publication/execution is concretely tool-limited.
- Current LAB-091 PR head: `77c5ce6650cf282a18e9001dd9d5c63f386d0a6d`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172. LAB-090 / #169 remains READY.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. LAB-086 remains first priority. Current-run executable GitHub transport was probed again and remains unavailable: `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` failed with `Could not resolve host: github.com`. No supported machine-to-machine byte-preserving composition path for the exact 949-line LAB-086 predecessor plus retained hidden-rowid patch was observed, so no LAB-086 branch mutation was attempted.

Used the allowed LAB-091 fallback and continued the inherited constructor/restart/rotation identity-collation audit. Found a reachable adoption gap in `validate_existing_mutable_state_locked()`: receipt ownership used plain `i.request_id=r.request_id`. LAB-091 accepts legacy request-id columns that may retain a declared non-BINARY collation when a separate full-table BINARY UNIQUE index proves canonical byte-distinct identity. Under such a schema, SQLite NOCASE comparison can make case-distinct receipt request IDs appear owned by an intent.

Local SQLite mechanism reproduction:
- intent/receipt `request_id` columns declared `COLLATE NOCASE`;
- separate BINARY UNIQUE indexes on both identities;
- intent request `abc`, receipt request `ABC`;
- old/default-collation orphan query returned `None`;
- explicit BINARY orphan query returned `('ABC',)`.

Published on PR #173:
- fix commit `ec49b717f6fe4223485488ff92650fbe5168b736`, `adoption_validation.py` blob `8b676aadb5a5f88d7365e53740318d2788423ff5`: orphan ownership now compares `i.request_id COLLATE BINARY = r.request_id COLLATE BINARY`;
- regression/current head `77c5ce6650cf282a18e9001dd9d5c63f386d0a6d`, `test_adoption_collation_regression.py` blob `b177667fb2d565b5959a44cacaed3dd69545cb26`: accepted NOCASE-column/BINARY-index overlay must reject a case-distinct orphan receipt;
- post-write PR re-fetch confirmed head `77c5ce6650cf282a18e9001dd9d5c63f386d0a6d` and PR remains DRAFT.

Static rotation audit did not establish an equivalent valid-state alias for `generation_id`: it is recomputed canonical lowercase SHA-256 and durable verification rejects content/id mismatch, so no speculative generation-id patch was added.

Durable analysis: `research/2026-08-30-lab091-receipt-orphan-collation-alias.md`, main commit `5b5ae923692f9a029dca57de9b4a2d5e99efaa48`; issue #170 comment `5465203105`.

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
- LAB-091 identity lookup collation alias reproduced; final supported identity surface patched on `0d73b6bc...`; focused SQLite semantic probe PASS; exact published regression execution pending transport.
- LAB-091 constructor/restart BINARY-helper ordering gap patched on `a9fd1e14...`; local ordering mechanism probe PASS; exact regression execution pending transport.
- LAB-091 receipt orphan ownership collation alias reproduced; adoption predicate patched on `77c5ce66...`; local SQLite RED→GREEN mechanism probe PASS; exact published regression execution pending transport.
- LAB-091 alternate-write REPLACE / UPSERT / multi-row UPDATE all fail closed; no bypass established.
- LAB-091 published real-stack timeout/UNKNOWN regression blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05`; full execution pending.
- LAB-091 published process concurrency/crash regression blob `938877479d4c4b997ea52e8b5857bf89e5c3e246`; full final-ledger execution pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40f...`, applying only retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid candidate publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft. Identity-collation, constructor-ordering and receipt-orphan fixes are published but their latest exact pytest regressions are still unexecuted; timeout/UNKNOWN, process concurrency/crash, receipt-affinity and receipt-collation final-surface gates also remain pending exact branch execution.
- Do not represent focused semantic/mechanism reproductions as byte-for-byte branch execution.
- Do not add speculative SQLite guards without a reproduced reachable mutation or compatibility failure under actual supported semantics.

## Exact next action

1. LAB-086 first: if a supported machine-to-machine byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40f...`, apply only retained hidden-rowid patch, require exact target `b78e7c98...`, publish via normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates.
2. If LAB-086 remains concretely tool-limited, execute the exact PR #173 branch gate on current head `77c5ce6650cf282a18e9001dd9d5c63f386d0a6d` when executable transport is available, starting with `test_identity_lookup_collation_regression.py`, `test_constructor_binary_provider_history_regression.py`, and `test_adoption_collation_regression.py`, then timeout/UNKNOWN `92133cdc...`, process concurrency/crash `93887747...`, receipt-affinity `35baec3b...`, and receipt-collation `25f7eca3...` through the final supported class.
3. If exact execution remains unavailable, continue static reachability audit only for inherited LAB-082 provider/receipt constructor/restart/rotation predicates where a valid supported durable state can still trigger default-collation semantics; patch only a reproduced reachable compatibility/security failure and persist evidence.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; latest receipt-orphan collation fix published, exact branch/full behavioral gates pending.
