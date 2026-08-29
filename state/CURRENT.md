# Current Lab State

Last updated: 2026-08-29

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Authoritative live LAB-086 `strict_fence.py` blob: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Durable hidden-rowid patch: `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact previously derived/tested target: `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Older `eb219835...` lineage is historical evidence only and must not be used as the predecessor for the pending hidden-rowid publication.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact publication/execution is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs #165/#173 and the live LAB-086 branch.

LAB-086 was rechecked first. Live `experiments/asymmetric_break_glass_history/strict_fence.py` re-fetches as exact blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch re-fetches as blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`. Local `git ls-remote https://github.com/...` again failed with `Could not resolve host: github.com`. The connector can retrieve the whole PR-added file and provides normal Contents writes, but the 949-line payload is truncated at the tool presentation boundary and there is still no supported operation that composes exact fetched bytes + unified patch into a byte-preserving write. No LAB-086 branch mutation was attempted.

A control-plane inconsistency was fixed: Issue #163 and PR #165 still described the older `eb219835...` executable lineage. Issue #163 is now rewritten around the authoritative live predecessor `d4a6a40f...` and exact target `b78e7c98...`; PR #165 received a reconciliation comment. Durable note: `research/2026-08-29-lab086-control-plane-lineage-reconciliation.md`, main commit `369331ea1bffd10e1417671e59501a4e24550958`.

LAB-091 fallback code was also re-inspected only to confirm actual connection semantics: final `_con()` uses a normal `sqlite3` connection with `busy_timeout`, the LAB-091 permit UDFs and row-token/state-machine UDFs; it does not enable `foreign_keys` or install a broader transaction-wide authority. No new reachable mutation bypass was established in this run, so no speculative guard was added.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED→GREEN evidence retained; exact predecessor `d4a6a40f...` -> candidate `b78e7c98...` previously byte-rederived and focused mechanism-tested; publication/full gate still pending.
- Current runtime reconfirmed source retrieval and normal Contents writes are individually available; missing capability is byte-preserving composition/transfer of the 949-line security-critical file. Shell GitHub transport remains DNS-blocked.
- Control-plane lineage is now reconciled in Issue #163 and durable research note; do not regress to `eb219835...` as publication predecessor.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption hardening combined focused gate remains 17/17 PASS over identity/index/collation + NOT NULL + weakened-watermark-CHECK logic.
- LAB-091 missing-singleton adoption-write regression 2/2 PASS on published source.
- LAB-091 persisted-trigger confused-deputy regression 3/3 PASS + compileall on exact published helper/test blobs.
- LAB-091 incoming-FK cascade generic mechanism reproduced with FK enforcement enabled, but actual supported `_con()` does not enable FKs; no current reachable bypass.
- LAB-091 schema-expression audit remains fail-closed; no new reachable bypass established.
- LAB-091 published real-stack timeout/UNKNOWN regression remains blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05e`; full execution still pending.
- LAB-091 real-stack process concurrency/crash regression remains blob `938877479d4c4b997ea52e8b5857bf89e5c3e246`; full final-ledger execution pending.

## Known blockers / constraints

- LAB-086 remains first priority. Current live security delta is rowid-only hardening; do not reapply alternate-UNIQUE or provider-receipt NULL patches as separate changes because current `d4a6a40f...` already contains those protections.
- LAB-086 publication requires byte-preserving composition of exact predecessor `d4a6a40f...` with only the retained hidden-rowid patch. Do not manually/model-reserialize the whole 949-line file.
- PR #165 remains draft until exact rowid candidate publication/hash verification, focused rowid + existing receipt-NULL + alternate-UNIQUE regressions, complete strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- PR #173 remains draft. Timeout/UNKNOWN and process concurrency/crash real-stack tests still have not been behaviorally executed against an executable exact branch dependency closure.
- Do not repeat narrow LAB-091 adoption gates unless their pinned source blobs change.
- Do not add speculative SQLite schema guards without a reproduced reachable mutation path under actual supported connection semantics.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: re-check `strict_fence.py` remains `d4a6a40f...`. If a supported byte-preserving composition/transfer bridge becomes available, combine exact live source with only `research/2026-08-28-lab086-hidden-rowid-replace.patch`, require exact target blob `b78e7c98...`, predecessor conflict-check, publish via normal Contents API, then re-fetch/hash-verify and run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080->086 real-ledger gates.
2. If LAB-086 remains tool-limited, LAB-091: prioritize obtaining a supported branch-to-executable-FS path to execute exact published timeout/UNKNOWN blob `92133cdc...` and process concurrency/crash blob `93887747...`. Fix any real-stack defect; do not weaken either regression.
3. Only if execution transport remains unavailable, continue alternate-write/reentrancy audit for reachable SQLite mechanisms under actual `_con()` configuration; no speculative guards.
4. After both real-stack tests are GREEN, retain/reconfirm LAB-087 restricted-worker composition before PR #173 can leave draft.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; authoritative live predecessor `d4a6a40f...`, exact hidden-rowid target `b78e7c98...`, publication/full gate pending.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; real-stack timeout/UNKNOWN and process concurrency/crash full execution pending.
