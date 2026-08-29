# Current Lab State

Last updated: 2026-08-29

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Live LAB-086 `strict_fence.py` blob remains `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Durable hidden-rowid patch is `research/2026-08-28-lab086-hidden-rowid-replace.patch`; prior exact derived candidate is `b78e7c98e35138719f77c482c7f1aab36b702de7`. Do not publish unless the whole replacement is byte-preserved and re-fetched blob matches that tested target.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact publication/execution is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`. This run exposed a normal GitHub `fetch_file` + Contents `update_file` capability, but the wrappers still do not provide a supported server-side way to compose the large fetched LAB-086 source with the stored patch; no manual lossy whole-file rewrite or low-level ref/tree manipulation was used.

For the allowed LAB-091 fallback, audited alternate write surfaces and reproduced a real first-adoption defect in `restart_safe_schema.initialize_shared_anchor_schema()`: a preexisting canonical mutable shared-anchor schema with a missing metadata singleton was silently mutated to add `(1,0)` before adoption verification. Published fail-closed fix at branch commit `736434d0430bfae40d5726b0e63c310b0e98f8b8`, blob `5b1ff616d9ddefbf82742e79d3b547eb02b8754b`, plus regression commit `fac191b8daba8754b3fe004576dfd31904e0ae83`, blob `60b4c33a9edf6b2405cd861b89b69037b2f89a37`.

Executed the exact published focused regression in the current Python runtime: fresh database initialization succeeds with `(1,0)` and preexisting mutable schema missing the singleton fails closed without inserting it. Result: 2/2 PASS. Durable note: `research/2026-08-29-lab091-missing-singleton-adoption-write-gap.md`, main commit `ab4e98f32a34436173b2c92bf9826753206e0ffc`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED->GREEN evidence retained; exact predecessor `d4a6a40f...` -> candidate `b78e7c98...` previously byte-rederived and focused mechanism-tested; publication/full gate still pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption hardening combined focused gate remains 17/17 PASS over identity/index/collation + NOT NULL + weakened-watermark-CHECK logic.
- LAB-091 missing-singleton adoption-write regression 2/2 PASS on published source; preexisting mutable schema is no longer auto-healed before validation.
- LAB-091 published real-stack timeout/UNKNOWN regression remains blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05e`; full execution still pending.
- LAB-091 real-stack process concurrency/crash regression remains blob `938877479d4c4b997ea52e8b5857bf89e5c3e246`; full final-ledger execution pending.

## Known blockers / constraints

- LAB-086 remains first priority. Current live security delta is rowid-only hardening; do not reapply alternate-UNIQUE or provider-receipt NULL patches as separate changes because current `d4a6a40f...` already contains those protections.
- LAB-086 publication still requires a byte-preserving composition path from exact predecessor + stored patch into the normal Contents writer. Current fetch/update wrappers are individually available but not safely composable for the 39 KB replacement without manual reserialization.
- PR #165 remains draft until exact rowid candidate publication/hash verification, focused rowid + existing receipt-NULL + alternate-UNIQUE regressions, complete strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- PR #173 remains draft. A newly found adoption write gap is fixed and tested, but timeout/UNKNOWN and process concurrency/crash real-stack tests still have not been behaviorally executed against an executable exact branch dependency closure.
- Do not repeat the narrow LAB-091 combined adoption gate unless one of its pinned source blobs changes.
- CHECK/type-affinity equivalence is not globally claimed. Only demonstrated behavior gaps should add constraints/guards.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: re-check `strict_fence.py` remains `d4a6a40f...`. If a supported byte-preserving composition bridge becomes available, apply only `research/2026-08-28-lab086-hidden-rowid-replace.patch`, require exact target blob `b78e7c98...`, predecessor conflict-check, publish through normal Contents API, then re-fetch/hash-verify and run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080->086 real-ledger gates.
2. If LAB-086 remains tool-limited, LAB-091: extend the alternate-write/reentrancy audit from the newly fixed initializer path, then obtain a supported branch-to-executable-FS path and execute exact published timeout/UNKNOWN blob `92133cdc...` and process concurrency/crash blob `93887747...`. Fix any real-stack defect; do not weaken either regression.
3. After both real-stack tests are GREEN, retain/reconfirm LAB-087 restricted-worker composition before PR #173 can leave draft.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact rowid candidate previously re-derived + focused mechanism PASS, publication/full gate pending.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; adoption hardening expanded with missing-singleton fail-closed regression; real-stack timeout/UNKNOWN and process concurrency/crash full execution pending.
