# Current Lab State

Last updated: 2026-08-29

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Live LAB-086 `strict_fence.py` blob remains `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Durable hidden-rowid patch is `research/2026-08-28-lab086-hidden-rowid-replace.patch`; exact previously derived/tested candidate is `b78e7c98e35138719f77c482c7f1aab36b702de7`. Do not publish unless the whole replacement is byte-preserved and re-fetched blob matches that target.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact publication/execution is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active PRs #165/#172/#173.

LAB-086 transport was re-audited. `fetch_pr_file_patch` for PR #165 returned `strict_fence.py` as a complete `@@ -0,0 +1,949 @@` addition because the file is new relative to `main`. Therefore the exact 949-line predecessor source is available through an authoritative GitHub PR payload even though ordinary large file responses are display-truncated. The stored hidden-rowid patch was re-fetched unchanged as blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`.

Direct runtime network access still cannot resolve `raw.githubusercontent.com`. More importantly, the current tools still do not expose a byte-preserving composition/transfer operation from `complete PR payload + stored unified patch` into the Contents writer. Manual/model reserialization of a 949-line security-critical file remains outside the acceptance rule, so no LAB-086 branch mutation was attempted.

Durable note: `research/2026-08-29-lab086-pr-patch-byte-source-bridge.md`, main commit `b9b60be2964516acddc9d5c478539729992027ee`.

For LAB-091 fallback audit, rechecked the expected-name persisted-trigger hypothesis. `install_full_operation_guards()` drops/recreates legacy/v2 trigger names before adoption validation, while `validate_protected_trigger_surface()` requires the exact protected trigger-name set. A malicious preexisting v2 trigger under an expected v2 name is therefore overwritten before validation; no new reachable bypass was established and no speculative guard was added.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED->GREEN evidence retained; exact predecessor `d4a6a40f...` -> candidate `b78e7c98...` previously byte-rederived and focused mechanism-tested; publication/full gate still pending.
- Current runtime additionally proved the full 949-line predecessor is retrievable through PR per-file patch; missing capability is exact composition/transfer, not source retrieval.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption hardening combined focused gate remains 17/17 PASS over identity/index/collation + NOT NULL + weakened-watermark-CHECK logic.
- LAB-091 missing-singleton adoption-write regression 2/2 PASS on published source.
- LAB-091 persisted-trigger confused-deputy regression 3/3 PASS + compileall on exact published helper/test blobs.
- LAB-091 incoming-FK cascade generic mechanism reproduced with FK enforcement enabled, but current supported connection does not enable FKs; no current reachable bypass.
- LAB-091 expected-name v2 persisted-trigger substitution audited as currently overwritten by installer before surface validation; no bypass established.
- LAB-091 published real-stack timeout/UNKNOWN regression remains blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05e`; full execution still pending.
- LAB-091 real-stack process concurrency/crash regression remains blob `938877479d4c4b997ea52e8b5857bf89e5c3e246`; full final-ledger execution pending.

## Known blockers / constraints

- LAB-086 remains first priority. Current live security delta is rowid-only hardening; do not reapply alternate-UNIQUE or provider-receipt NULL patches as separate changes because current `d4a6a40f...` already contains those protections.
- LAB-086 source retrieval is available via complete PR per-file patch, but publication still requires byte-preserving composition of that exact predecessor with the stored hidden-rowid patch into the normal Contents writer. Do not manually/model-reserialize the whole 949-line file.
- PR #165 remains draft until exact rowid candidate publication/hash verification, focused rowid + existing receipt-NULL + alternate-UNIQUE regressions, complete strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- PR #173 remains draft. Timeout/UNKNOWN and process concurrency/crash real-stack tests still have not been behaviorally executed against an executable exact branch dependency closure.
- Do not repeat narrow LAB-091 adoption gates unless their pinned source blobs change.
- Do not add speculative SQLite schema guards without a reproduced reachable mutation path under the actual supported connection semantics.
- CHECK/type-affinity equivalence is not globally claimed. Only demonstrated behavior gaps should add constraints/guards.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: re-check `strict_fence.py` remains `d4a6a40f...`. If a supported byte-preserving composition/transfer bridge becomes available, combine the exact complete 949-line PR payload with only `research/2026-08-28-lab086-hidden-rowid-replace.patch`, require exact target blob `b78e7c98...`, predecessor conflict-check, publish through normal Contents API, then re-fetch/hash-verify and run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080->086 real-ledger gates.
2. If LAB-086 remains tool-limited, LAB-091: prioritize obtaining a supported branch-to-executable-FS path to execute exact published timeout/UNKNOWN blob `92133cdc...` and process concurrency/crash blob `93887747...`. Fix any real-stack defect; do not weaken either regression.
3. Only if execution transport remains unavailable, continue alternate-write/reentrancy audit for reachable SQLite mechanisms under the actual `_con()` configuration; do not add speculative FK/view/schema-object guards without an executable bypass.
4. After both real-stack tests are GREEN, retain/reconfirm LAB-087 restricted-worker composition before PR #173 can leave draft.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact rowid candidate previously re-derived + focused mechanism PASS, publication/full gate pending.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; real-stack timeout/UNKNOWN and process concurrency/crash full execution pending.
