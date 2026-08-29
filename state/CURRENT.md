# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative live LAB-086 `strict_fence.py` predecessor: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Retained hidden-rowid patch: `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact previously derived/tested target: `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-091 / #170 remains fallback IN_PROGRESS on draft PR #173, branch `lab/091-mutable-shared-anchor-writer`, only while LAB-086 exact publication/execution is concretely tool-limited.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172. LAB-090 / #169 remains READY.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. LAB-086 remains first priority. This run again observed no supported machine-to-machine byte-preserving composition path for the exact 949-line predecessor plus retained hidden-rowid patch; executable filesystem DNS to GitHub raw failed. Do not manually/model-reserialize that security-critical file.

Used the allowed LAB-091 fallback and audited constructor/restart compatibility of the 2026-08-29 BINARY identity fix. Found a reachable ordering gap: LAB-082 installs `IntegratedAsymmetricProviderHistory` before entering LAB-091 parent construction, and `SupportedMutableAsymmetricSharedAnchorLedger.__init__()` dynamically invokes final `_install_guards()` / `verify_durable()` before final LAB-091 `__init__()` previously replaced the helper. First adoption/restart durable verification could therefore still execute inherited default-collation receipt request-id operations on an admitted legacy NOCASE identity column.

Published on PR #173:
- runtime fix commit `7de557add95ca877ec843faaaf3977de414c8e20`, `history_bound_operation_scoped.py` blob `11c8b8f512c888e52dcbcee463470967283be0bf`: `_ensure_binary_provider_history()` is invoked at the start of final `_install_guards()` before durable verification and again idempotently after `super()`;
- regression commit / current head `a9fd1e1422d01088ac34248dd36fc83be0f750f3`: `test_constructor_binary_provider_history_regression.py` asserts binary helper replacement precedes `verify_durable()`;
- post-write PR re-fetch confirmed head `a9fd1e1422d01088ac34248dd36fc83be0f750f3` and PR remains DRAFT;
- local mechanism ordering probe PASS (`binary` before `verify`); this is mechanism evidence only, not exact branch pytest execution.

Durable analysis: `research/2026-08-30-lab091-constructor-binary-helper-ordering.md`, main commit `4533e8b2a5b6e81244b6da09890bf99823db9670`; issue #170 comment `5464969685`.

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
- LAB-091 alternate-write REPLACE / UPSERT / multi-row UPDATE all fail closed; no bypass established.
- LAB-091 published real-stack timeout/UNKNOWN regression blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05`; full execution pending.
- LAB-091 published process concurrency/crash regression blob `938877479d4c4b997ea52e8b5857bf89e5c3e246`; full final-ledger execution pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40f...`, applying only retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid candidate publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft. Identity-collation runtime patch and constructor-ordering fix are published but exact pytest regressions are still unexecuted; timeout/UNKNOWN, process concurrency/crash, receipt-affinity and receipt-collation final-surface gates also remain pending exact branch execution.
- Do not represent focused semantic/mechanism reproductions as byte-for-byte branch execution.
- Do not add speculative SQLite guards without a reproduced reachable mutation or compatibility failure under actual supported semantics.

## Exact next action

1. LAB-086 first: if a supported machine-to-machine byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40f...`, apply only retained hidden-rowid patch, require exact target `b78e7c98...`, publish via normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates.
2. If LAB-086 remains concretely tool-limited, execute the exact PR #173 branch gate on current head `a9fd1e1422d01088ac34248dd36fc83be0f750f3` when executable transport is available, starting with `test_identity_lookup_collation_regression.py` and `test_constructor_binary_provider_history_regression.py`, then timeout/UNKNOWN `92133cdc...`, process concurrency/crash `93887747...`, receipt-affinity `35baec3b...`, and receipt-collation `25f7eca3...` through the final supported class.
3. If exact execution remains unavailable, continue static reachability audit only for inherited constructor/restart/rotation paths that can still invoke plain identity predicates from LAB-082; patch only a reproduced reachable compatibility/security failure and persist evidence.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; identity and constructor ordering fixes published, exact branch/full behavioral gates pending.
