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

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs #165/#172/#173. Probed local GitHub transport again: `git ls-remote` still fails with `Could not resolve host: github.com`. Connector reads and normal Contents writes remain available; no branch/archive-to-executable-FS bridge appeared.

LAB-086 therefore remains byte-transfer blocked: do not model/manual-reserialize the 949-line security-critical `strict_fence.py`.

Used the LAB-091 fallback and found a new first-adoption schema-contract defect. Existing validation checked NOT NULL and canonical identity constraints but not SQLite column affinity. SQLite applies affinity before BEFORE-trigger `NEW.*`; an integer `1` inserted into a legacy `position TEXT NOT NULL` column is observed by the trigger as string `"1"`, diverging from exact one-shot permit/token semantics after an otherwise clean adoption.

Published fail-closed fix on `lab/091-mutable-shared-anchor-writer`:
- `adoption_schema_domains.py` commit `4806c7f0a4d7ea34b239d9a1f639479c1d32bac9`, blob `36a94d721cc627707be89a0ae1ef99d8bbcaa673`;
- `test_adoption_affinity_regression.py` commit `d18ffff9565ed3ad8c1afeeb672aae09f561975c`, blob `4f1cf3789d6bad0af8943ad612f430f891d3dd90`.

Executed focused candidate before publication: canonical affinity accepted; `position TEXT NOT NULL` rejected; BEFORE-trigger coercion reproduced; **3/3 PASS + compileall PASS**. Post-publication re-fetch confirmed exact tested logic/blobs. Durable evidence: `research/2026-08-29-lab091-legacy-column-affinity-adoption-gap.md`, main commit `81606fb03909273158b1800b31185f5dd5771b0e`. Issue #170 updated.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED→GREEN evidence retained; exact predecessor `d4a6a40f...` -> candidate `b78e7c98...` previously byte-rederived and focused mechanism-tested; publication/full gate still pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption hardening combined focused gate 17/17 PASS before later affinity fix.
- LAB-091 missing-singleton 2/2 PASS; persisted-trigger confused-deputy 3/3 PASS + compileall; legacy affinity regression 3/3 PASS + compileall.
- LAB-091 alternate-write REPLACE / UPSERT / multi-row UPDATE all fail closed; no bypass established.
- LAB-091 published real-stack timeout/UNKNOWN regression blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05e`; full execution pending.
- LAB-091 published process concurrency/crash regression blob `938877479d4c4b997ea52e8b5857bf89e5c3e246`; full final-ledger execution pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40f...`, applying only retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid candidate publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft until exact full-stack timeout/UNKNOWN and process concurrency/crash regressions execute GREEN against the actual supported final class and LAB-087 composition is reconfirmed.
- Do not repeat closed LAB-091 hidden-rowid, exception-taxonomy, or narrow adoption-index audits unless pinned blobs/supported surfaces change.
- Do not add speculative SQLite guards without a reproduced reachable mutation or compatibility failure under actual supported semantics.

## Exact next action

1. LAB-086 first: if a supported machine-to-machine byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40f...`, apply only retained hidden-rowid patch, require exact target `b78e7c98...`, publish via normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates.
2. If LAB-086 remains concretely tool-limited, prioritize obtaining a supported branch-to-executable-FS path for LAB-091 and execute exact timeout/UNKNOWN `92133cdc...` plus process concurrency/crash `93887747...` against the final supported class.
3. If execution transport still remains unavailable, continue only demonstrably reachable LAB-091 schema/adoption/write-surface audits. The next high-value audit is whether the protected `asymmetric_provider_receipts` legacy schema has the same unverified affinity/domain compatibility problem; reproduce before changing runtime.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; two full real-stack behavioral gates pending.
