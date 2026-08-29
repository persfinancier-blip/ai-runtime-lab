# Current Lab State

Last updated: 2026-08-29

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Live LAB-086 `strict_fence.py` blob remains `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` (re-fetched this run).
- Durable hidden-rowid patch is `research/2026-08-28-lab086-hidden-rowid-replace.patch`; prior exact derived candidate was `b78e7c98e35138719f77c482c7f1aab36b702de7` from the same live predecessor. Do not publish unless the whole replacement is byte-preserved and returned/re-fetched blob matches the tested target.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current branch HEAD `2e83e6b12e4e40f42df890f964f134c2d397ec7b`; fallback only while LAB-086 exact publication/execution is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected open issues/PRs and fresh LAB-086 issue comments. Re-fetched LAB-086 `strict_fence.py`; live runtime is still exact blob `d4a6a40f...`. The durable rowid patch is present on the branch and still describes the intended narrow delta, but executable shell DNS to `github.com`, `api.github.com` and `raw.githubusercontent.com` still fails and connector branch bytes are not mounted into executable FS. No low-level ref/tree bypass or manual lossy whole-file rewrite was used.

For the allowed LAB-091 fallback, published `experiments/mutable_shared_anchor_writer/tests/test_real_stack_process_concurrency_and_crash.py` at commit `2e83e6b12e4e40f42df890f964f134c2d397ec7b`; post-write blob `938877479d4c4b997ea52e8b5857bf89e5c3e246`. Unlike the older stubbed process test, this imports the real final `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` and real LAB-080/LAB-082 verifier/history types. It defines (1) identical two-process execution against the same ledger and a process-shareable external provider-state DB and (2) process death after durable signed-receipt persistence but before final intent confirmation, followed by restart convergence.

Executed a focused two-process probe of the new SQLite-backed provider fixture in the current runtime: two `fork` workers raced on one request ID, both returned position 1, both exited 0, durable provider position remained 1, and the provider recorded two increment invocations. Result: PASS for provider request-id idempotency/process-sharing mechanism only. The full published final-ledger unittest was not executed and must not be counted as behavioural PASS because the branch dependency closure is still unavailable in executable FS.

Durable note: `research/2026-08-29-lab091-real-stack-process-concurrency-crash-regression.md`, main commit `bf91ba049fc6cb369e111115f4f7e27abb430a37`; Issue #170 comment `5460797825`; PR #173 comment `5460798320`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED->GREEN evidence retained; exact predecessor `d4a6a40f...` -> candidate `b78e7c98...` was previously byte-rederived and focused mechanism-tested; publication/full gate still pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption hardening combined focused gate remains 17/17 PASS over identity/index/collation + NOT NULL + weakened-watermark-CHECK logic.
- LAB-091 published real-stack timeout/UNKNOWN regression remains blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05e`; full execution still pending. Focused provider timeout mechanism PASS is retained separately and is not a substitute for the full gate.
- LAB-091 real-stack process concurrency/crash regression is now published as blob `938877479d4c4b997ea52e8b5857bf89e5c3e246`; focused shared-provider process/idempotency probe PASS, full final-ledger execution pending.

## Known blockers / constraints

- LAB-086 remains first priority. Current live security delta is rowid-only hardening; do not reapply alternate-UNIQUE or provider-receipt NULL patches as separate changes because current `d4a6a40f...` already contains those protections.
- LAB-086 publication remains blocked by byte-preserving data-plane separation for the exact whole-file candidate. Do not use low-level blob/tree/ref manipulation, force updates, or manual lossy rewrites.
- PR #165 remains draft until exact rowid candidate publication/hash verification, focused rowid + existing receipt-NULL + alternate-UNIQUE regressions, complete strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- PR #173 remains draft. Both real-stack regression definitions now exist, but neither the timeout/UNKNOWN test nor the new process concurrency/crash test has been behaviorally executed against an executable exact branch dependency closure.
- Do not repeat the narrow LAB-091 combined adoption gate unless one of its pinned source blobs changes.
- CHECK/type-affinity equivalence is not globally claimed. Only demonstrated behavior gaps should add constraints/guards.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: re-check `strict_fence.py` remains `d4a6a40f...`. If a supported byte-preserving bridge to the normal Contents writer becomes available, reconstruct/apply only `research/2026-08-28-lab086-hidden-rowid-replace.patch`, require the exact tested target blob on a temporary/non-runtime check or equivalent byte-safe path, then publish the runtime replacement only after predecessor conflict-check; re-fetch/hash-verify and run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080->086 real-ledger gates.
2. If LAB-086 publication remains tool-limited, LAB-091: obtain a supported branch-to-executable-FS path and execute exact published timeout/UNKNOWN blob `92133cdc...` and real process concurrency/crash blob `93887747...` against their real dependency closure. Fix any real-stack defect; do not weaken either regression.
3. After both real-stack tests are GREEN, retain/reconfirm LAB-087 restricted-worker composition and audit alternate write surfaces/reentrancy before PR #173 can leave draft.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact rowid candidate previously re-derived + focused mechanism PASS, publication/full gate pending.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; combined adoption gate 17/17 PASS; real-stack timeout/UNKNOWN and process concurrency/crash regressions both published but full execution pending.
