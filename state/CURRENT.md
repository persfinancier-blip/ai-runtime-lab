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

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open work. LAB-086 remains byte-transfer blocked: connector reads/Contents writes are available, but no supported machine-to-machine byte-preserving bridge exists to compose the exact 949-line predecessor with the retained hidden-rowid patch. Do not manually/model-reserialize that security-critical file.

Used the LAB-091 fallback and completed the next handoff audit against the protected `asymmetric_provider_receipts` table. Reproduced that a legacy `generation TEXT NOT NULL` declaration causes SQLite to coerce a bound integer generation to string before a `BEFORE INSERT` trigger/UDF sees `NEW.generation`, diverging from the exact one-shot receipt permit/token semantics after an otherwise clean adoption.

Published fail-closed receipt schema-domain hardening on `lab/091-mutable-shared-anchor-writer`:
- `adoption_schema_domains.py` commit `627f7257437f3da2438e32c2e6b7871c0a76a246`, blob `3688066de1ba12bc485a3dcc5846033685cbcb96`;
- `test_receipt_adoption_affinity_regression.py` commit `d4ad82916a4a4a2cb79ef7ebe6c8466a0e32d820`, blob `35baec3bf65c23b6af2fadae3695fa879c4499f2`.

The validator now requires canonical LAB-082 receipt affinities (`generation`/`position` INTEGER; text fields TEXT) and canonical NOT NULL receipt domains. Focused semantic SQLite gate covering canonical acceptance, TEXT-generation rejection, nullable-binding rejection, and pre-trigger coercion reproduction: **4/4 PASS**. Exact byte-for-byte branch pytest execution was not claimed because branch-to-executable-FS transport is still unavailable. Durable evidence: `research/2026-08-29-lab091-receipt-affinity-adoption-gap.md`, commit `07acda8e6ac635c31f1b13e310c5556c38326490`. Issue #170 updated.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED→GREEN evidence retained; exact predecessor `d4a6a40f...` -> candidate `b78e7c98...` previously byte-rederived and focused mechanism-tested; publication/full gate still pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption hardening combined focused gate 17/17 PASS before later affinity fixes.
- LAB-091 missing-singleton 2/2 PASS; persisted-trigger confused-deputy 3/3 PASS + compileall; legacy intent affinity regression 3/3 PASS + compileall.
- LAB-091 receipt affinity/domain focused semantic gate 4/4 PASS; exact published pytest execution pending transport.
- LAB-091 alternate-write REPLACE / UPSERT / multi-row UPDATE all fail closed; no bypass established.
- LAB-091 published real-stack timeout/UNKNOWN regression blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05e`; full execution pending.
- LAB-091 published process concurrency/crash regression blob `938877479d4c4b997ea52e8b5857bf89e5c3e246`; full final-ledger execution pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40f...`, applying only retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid candidate publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft until exact full-stack timeout/UNKNOWN and process concurrency/crash regressions execute GREEN against the actual supported final class and LAB-087 composition is reconfirmed.
- Newly published receipt-affinity pytest also needs exact branch execution when executable transport becomes available; do not represent the focused semantic reproduction as byte-for-byte branch execution.
- Do not repeat closed LAB-091 hidden-rowid, exception-taxonomy, intent-affinity, receipt-affinity/domain, or narrow adoption-index audits unless pinned blobs/supported surfaces change.
- Do not add speculative SQLite guards without a reproduced reachable mutation or compatibility failure under actual supported semantics.

## Exact next action

1. LAB-086 first: if a supported machine-to-machine byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40f...`, apply only retained hidden-rowid patch, require exact target `b78e7c98...`, publish via normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates.
2. If LAB-086 remains concretely tool-limited, prioritize obtaining a supported branch-to-executable-FS path for LAB-091 and execute exact timeout/UNKNOWN `92133cdc...`, process concurrency/crash `93887747...`, and the new receipt-affinity regression `35baec3b...` against the final supported class.
3. If execution transport still remains unavailable, continue only demonstrably reachable LAB-091 adoption/write-surface audits. Next useful target: verify whether protected receipt schema CHECK/collation semantics beyond affinity/NOT NULL can admit a clean legacy state but alter exact future guarded writes; reproduce before changing runtime.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; two full real-stack behavioral gates plus exact receipt-affinity pytest execution pending.
