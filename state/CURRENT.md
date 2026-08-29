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

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and draft PRs #165/#173.

LAB-086 was probed first. `strict_fence.py` was re-fetched from branch `lab/086-asymmetric-break-glass-history` in four non-overlapping ranges covering lines 1-949; every range reported the exact expected predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`. This proves complete connector-readable coverage, but the current tool surface still does not provide machine-to-machine byte-preserving composition of those exact chunks plus the retained unified patch into `update_file`. Manual/model reserialization remains prohibited; no LAB-086 branch mutation was attempted.

A fresh local checkout probe also failed: `git clone --depth 1 --branch lab/091-mutable-shared-anchor-writer https://github.com/persfinancier-blip/ai-runtime-lab.git` returned `Could not resolve host: github.com`.

Used the LAB-091 fallback for a new hidden-rowid reachability audit motivated by LAB-086. Inspected exact final `_con()`/writer/adoption files and searched repository code for `recursive_triggers` and `foreign_keys`. No supported LAB-091 final DML exposes explicit SQLite `rowid`; consequential fixed INSERT/UPDATE statements carry exact one-shot permits; arbitrary raw-DML/permit minting would require same-privilege writable-worker execution already owned by LAB-087. No reachable hidden-rowid or cascade bypass was established, so no speculative guard was added.

Durable evidence: `research/2026-08-29-lab091-hidden-rowid-reachability-audit.md`, main commit `4f521ba22d5877a6fdfe9e570ec46929b6952bc2`. Issue #170 was updated.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED→GREEN evidence retained; exact predecessor `d4a6a40f...` -> candidate `b78e7c98...` previously byte-rederived and focused mechanism-tested; publication/full gate still pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption hardening combined focused gate 17/17 PASS.
- LAB-091 missing-singleton regression 2/2 PASS.
- LAB-091 persisted-trigger confused-deputy regression 3/3 PASS + compileall.
- LAB-091 alternate-write one-shot probe: REPLACE / UPSERT / multi-row UPDATE all fail closed; no bypass established.
- LAB-091 hidden-rowid reachability audit: no reachable supported final-writer path; no speculative guard added.
- LAB-091 published real-stack timeout/UNKNOWN regression blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05e`; full execution still pending.
- LAB-091 published process concurrency/crash regression blob `938877479d4c4b997ea52e8b5857bf89e5c3e246`; full final-ledger execution still pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40f...`, applying only retained hidden-rowid patch through a byte-preserving supported path, requiring exact target blob `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Range-based connector reads are not by themselves a byte-preserving write bridge unless the exact fetched bytes can be passed machine-to-machine into composition/update without model regeneration.
- PR #165 remains draft until exact rowid candidate publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft until exact full-stack timeout/UNKNOWN and process concurrency/crash regressions execute GREEN against the actual supported final class and LAB-087 composition is reconfirmed.
- Do not repeat narrow LAB-091 adoption/rowid gates unless pinned blobs or supported DML surface change.
- Do not add speculative SQLite guards without a reproduced reachable mutation path under actual supported `_con()` semantics.

## Exact next action

1. LAB-086 first: re-fetch `strict_fence.py`; if it remains `d4a6a40f...` and a supported machine-to-machine byte-preserving composition/transfer bridge exists, apply only `research/2026-08-28-lab086-hidden-rowid-replace.patch`, require exact target `b78e7c98...`, publish via normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates.
2. If LAB-086 remains concretely tool-limited, prioritize obtaining a supported branch-to-executable-FS path for LAB-091 and execute exact timeout/UNKNOWN `92133cdc...` plus process concurrency/crash `93887747...`; fix any real defect without weakening either regression.
3. Only if execution transport remains unavailable, continue alternate-write/reentrancy audit for demonstrably reachable SQLite mechanisms under actual final `_con()` configuration; do not repeat hidden-rowid analysis unless the supported DML surface changes.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; two full real-stack behavioral gates pending.
