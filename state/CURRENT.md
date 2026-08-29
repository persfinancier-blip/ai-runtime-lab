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

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open work and PR #173. LAB-086 remains first priority but still lacks a supported machine-to-machine byte-preserving path for composing the exact 949-line predecessor with the retained hidden-rowid patch; do not manually/model-reserialize that security-critical file.

Used the allowed LAB-091 fallback and audited durable identity lookup/matching semantics. Reproduced a supported-path compatibility defect: `adoption_validation._unique_key_sets()` can accept a BINARY identity index while the underlying legacy identity column remains `COLLATE NOCASE`. Supported predicates such as `WHERE intent_id=?` then inherit NOCASE and alias byte-distinct identities (`Alpha` / `alpha`). A local sqlite3 semantic harness confirmed: the BINARY key is recognized, ordinary lookup aliases, and explicit `COLLATE BINARY` does not.

Durable artifacts:
- reproduction test on `lab/091-mutable-shared-anchor-writer`: `experiments/mutable_shared_anchor_writer/tests/test_identity_lookup_collation_reproduction.py`, commit `1eb30e021667990352c431112da04185148f7931`;
- analysis: `research/2026-08-29-lab091-identity-lookup-collation-alias.md`, main commit `f836a308c87dc75bcc8768e95e0d4ea8516a6800`;
- PR #173 comment `5464353538` records the defect and decision.

This is a real supported-method correctness defect, not a same-privilege DDL bypass: current LAB-091 adoption accepts the legacy schema and the final supported writer can then alias distinct IDs. No runtime patch was added in this step because the correct fix requires an inventory of all final-surface identity-sensitive lookup/CAS predicates (`intent_id`, `request_id`, `component_id`) rather than a one-off change that leaves sibling aliases behind.

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
- LAB-091 identity lookup collation alias reproduced with focused sqlite3 semantics; branch reproduction artifact committed, runtime fix pending complete final-surface inventory.
- LAB-091 alternate-write REPLACE / UPSERT / multi-row UPDATE all fail closed; no bypass established.
- LAB-091 published real-stack timeout/UNKNOWN regression blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05e`; full execution pending.
- LAB-091 published process concurrency/crash regression blob `938877479d4c4b997ea52e8b5857bf89e5c3e246`; full final-ledger execution pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40f...`, applying only retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid candidate publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft. In addition to the pending exact full-stack timeout/UNKNOWN and process concurrency/crash gates, the newly reproduced identity-collation alias must be fixed across the complete final supported lookup/CAS surface and regression-tested.
- Published receipt-affinity and receipt-collation regressions still need exact branch execution when executable transport becomes available; do not represent focused semantic reproductions as byte-for-byte branch execution.
- Do not add speculative SQLite guards without a reproduced reachable mutation or compatibility failure under actual supported semantics.

## Exact next action

1. LAB-086 first: if a supported machine-to-machine byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40f...`, apply only retained hidden-rowid patch, require exact target `b78e7c98...`, publish via normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates.
2. If LAB-086 remains concretely tool-limited, continue LAB-091 by inventorying every identity-sensitive SQL predicate reachable from `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` for `intent_id`, `request_id`, and `component_id`; patch all identity lookup/CAS predicates that rely on inherited legacy collation to explicit `COLLATE BINARY`, then add case-distinct supported-method regressions. Do not fix only the first `reserve()` lookup.
3. After that fix, execute/reconstruct as much of the exact branch gate as the runtime permits, then return to timeout/UNKNOWN `92133cdc...`, process concurrency/crash `93887747...`, receipt-affinity `35baec3b...`, and receipt-collation `25f7eca3...` final-surface regressions.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; identity-collation alias newly reproduced and now a merge blocker in addition to pending behavioral gates.
