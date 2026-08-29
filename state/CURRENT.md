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

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open work/PRs. LAB-086 remains byte-transfer blocked. Connector reads/normal Contents writes are available, but this run's shell transport probe still fails at DNS (`Could not resolve host: github.com`) and no supported machine-to-machine byte-preserving bridge exists to compose the exact 949-line predecessor with the retained hidden-rowid patch. Do not manually/model-reserialize that security-critical file.

Used the allowed LAB-091 fallback and completed the next receipt-schema collation audit. Reproduced that durable `TEXT COLLATE NOCASE` on protected receipt fields can preserve canonical TEXT affinity/NOT NULL while widening trigger comparisons: lowercase `reconcile` matched canonical `RECONCILE`, case-variant provider IDs matched, and case-variant stable bindings could satisfy the previous v4 confirmation predicate.

Published targeted byte-exact SQL semantics by forcing only the receipt/state-machine comparisons that require exact matching to `COLLATE BINARY`:
- `cross_table_guards.py` authoritative REST commit `078bdfe35b415b0a35dbcbf538cd0a6829c4704f`, blob `f76809e067d9d92aa0e7c96145c282757e1fbf0b`;
- `history_binding_guards.py` authoritative REST commit `89a7701437c1675e8107221b2610a95c0bd747ab`, blob `adb586f953816574a4f4f7380aace7305cf088b8`;
- `test_receipt_collation_exactness_regression.py` commit `3078e64307b66687ff96b172a42dd136eb89d7a0`, blob `25f7eca3833c57b5246e82514a03e5a1ddf1b516`.

Focused sqlite3 semantic harness: **4/4 PASS + compileall PASS**. Exact published-byte/full-branch pytest execution was not claimed because branch-to-executable-FS transport is unavailable. Durable evidence: `research/2026-08-29-lab091-receipt-collation-exactness-gap.md`, corrected authoritative-hash commit `e4a7754109253281f1781dd29a9e0f6e883cbddf`. Issue #170 updated. An earlier connector response surfaced inconsistent commit/blob identifiers; the REST commit history above is authoritative and the evidence/comment were corrected.

Follow-up audited `shared_anchor_intents.status TEXT COLLATE NOCASE`. No second supported-path bypass was demonstrated: final writer code hard-codes `PREPARED`/`CONFIRMED`, one-shot permits bind exact Python row tokens, first-adoption validates existing rows under the writer reservation, and unknown persisted triggers are rejected. No speculative BINARY churn was added. Negative evidence: `research/2026-08-29-lab091-status-collation-reachability-audit.md`, commit `3f12998ffc3021cb5f904a08f42ada1cef5d21f4`.

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
- LAB-091 alternate-write REPLACE / UPSERT / multi-row UPDATE all fail closed; no bypass established.
- LAB-091 published real-stack timeout/UNKNOWN regression blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05e`; full execution pending.
- LAB-091 published process concurrency/crash regression blob `938877479d4c4b997ea52e8b5857bf89e5c3e246`; full final-ledger execution pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40f...`, applying only retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid candidate publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft until exact full-stack timeout/UNKNOWN and process concurrency/crash regressions execute GREEN against the actual supported final class and LAB-087 composition is reconfirmed.
- Published receipt-affinity and receipt-collation regressions also need exact branch execution when executable transport becomes available; do not represent focused semantic reproductions as byte-for-byte branch execution.
- Shell GitHub transport in this run: DNS failure. Treat this as per-run evidence, not a permanent capability assumption.
- Do not repeat closed LAB-091 hidden-rowid, exception-taxonomy, intent-affinity, receipt-affinity/domain, receipt-collation, status-collation, or narrow adoption-index audits unless pinned blobs/supported surfaces change.
- Do not add speculative SQLite guards without a reproduced reachable mutation or compatibility failure under actual supported semantics.

## Exact next action

1. LAB-086 first: if a supported machine-to-machine byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40f...`, apply only retained hidden-rowid patch, require exact target `b78e7c98...`, publish via normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates.
2. If LAB-086 remains concretely tool-limited, prioritize obtaining a supported branch-to-executable-FS path for LAB-091 and execute exact timeout/UNKNOWN `92133cdc...`, process concurrency/crash `93887747...`, receipt-affinity `35baec3b...`, and receipt-collation `25f7eca3...` regressions against `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`.
3. If execution transport still remains unavailable, continue only demonstrably reachable LAB-091 audits. Next useful target: durable provider-history lookup/matching schema properties or implicit SQLite execution surfaces that can alter values not canonicalized by the supported writer. Reproduce a supported-path failure/bypass before changing runtime.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; two full real-stack behavioral gates plus exact receipt-affinity/collation pytest execution pending.
