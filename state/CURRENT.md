# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current PR #165 HEAD: `3cc63c2133507fd8d468471e1fe0fe5b3680e12c`; GitHub reports mergeable=false.
- Last fully executed published LAB-086 runtime/test pin before the hidden-rowid blocker: `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; published `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Hidden-rowid candidate remains `b78e7c98e35138719f77c482c7f1aab36b702de7`; runtime is intentionally still unpatched until byte-safe publication is possible.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current HEAD `4c1718384778f7a9122fd87fbe67183f50b989ab`, mergeable=true, draft. Use only as fallback while LAB-086 exact work is concretely tool-limited.

## Last completed step

Probed LAB-086 first. The connector can fetch the exact predecessor `strict_fence.py` blob `d4a6a40f...` and the exact saved hidden-rowid patch, but candidate blob `b78e7c98...` is not already present in GitHub (`fetch_blob` returned 404) and the normal Contents writer still requires complete replacement text rather than a local exact-file reference. Two historical helper branches, `lab086-byte-transfer-20260826` and `lab086-bytegate-20260826-1715`, were inspected; both carry older `strict_fence.py` blob `5da01e28...`, not the hidden-rowid candidate. No unsafe/manual whole-file publication was attempted and no new LAB-086 PASS was claimed.

Used the allowed LAB-091 fallback and found a first-adoption TOCTOU not covered by the prior failed-adoption regression. The inherited LAB-082 constructor performs a complete `verify_durable()` before LAB-091 `_install_guards()`. LAB-091 then installs v2/v3/v4 guards and runs `validate_existing_mutable_state_locked()` in a separate `BEGIN IMMEDIATE` transaction, commits the triggers, and only afterward the legacy `SupportedMutableAsymmetricSharedAnchorLedger.__init__()` calls full `verify_durable()` again. A lower/legacy writer can therefore corrupt authenticated LAB-082 history after the first verification but before guard installation; the LAB-091 adoption validator intentionally does not verify LAB-082 cryptographic receipt/provider-history semantics. The post-commit verifier then rejects construction while persistent `lab091_%` guards can remain.

Added deterministic regression `experiments/mutable_shared_anchor_writer/tests/test_adoption_toctou_guard_persistence_regression.py` on PR #173, commit `a569b4ed132f4148816548bcc0d10f11324de621`, published blob `262834c34b6b7be182427e86f78963fc5caafa42`. It corrupts the LAB-082 receipt immediately after the first successful inherited verification, then requires failed construction to leave zero LAB-091 triggers. Added design note `research/2026-08-28-lab091-first-adoption-toctou.md`, commit `4c1718384778f7a9122fd87fbe67183f50b989ab`, and Issue #170 comment `5449642830`.

Source audit confirmed a partial fix is insufficient: LAB-082 `AsymmetricHistoricalSharedAnchorLedger.verify_durable()` atomically checks provider history/signatures, shared-anchor tail continuity, PREPARED/CONFIRMED receipt binding, and component watermarks. Only `provider_history._verify_durable_locked(q)` is already factored; using that alone inside adoption would leave lower durable invariants outside the atomic boundary. No runtime fix or test PASS is claimed yet.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Previous repinned LAB-086 strict/thaw exact subgate: 31/31 PASS + compileall on pin `1fa85a0e...`; not sufficient for merge because hidden-rowid conflict was not covered.
- Hidden-rowid exact RED→GREEN retained: predecessor RED 3/3, candidate `b78e7c98...` GREEN 3/3 + compileall; runtime publication still pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption-state/domain gate: 23/23 PASS + compileall.
- LAB-091 alternate lower/legacy connection persistence regression: exact published 2/2 PASS + compileall, blob `365688e0...`.
- LAB-091 prior failed-adoption regression is published as blob `a81c3937...`; it covers corruption before the first inherited verifier, not the newly found inter-verification race.
- LAB-091 adoption-TOCTOU regression is published as blob `262834c3...`; no PASS is claimed. Source ordering predicts current RED with persisted guards after constructor failure.

## Known blockers / constraints

- LAB-086 remains first priority. Hidden-rowid fix must be published byte-exact before the full real-ledger gate resumes.
- Direct shell/raw GitHub transport remains unavailable in this runtime; connector reads do not mount repository files into the executor.
- The available Contents write cannot consume the exact local LAB-086 candidate file by filesystem reference; manually transcribing/reformatting the large security-critical file would weaken the exact-blob discipline.
- PR #165 must remain draft until rowid fix publication, repinned strict/thaw subgate, complete real-ledger gate, unsafe seed, compileall and final audit are all clean.
- PR #173 must remain draft. New adoption TOCTOU is a merge blocker until the complete LAB-082 durable verifier can run inside the same LAB-091 `BEGIN IMMEDIATE` adoption/guard-install transaction and the new regression is GREEN on exact real dependencies.
- Do not fix the TOCTOU by calling only `provider_history._verify_durable_locked(q)`; that omits ledger/receipt/watermark validity currently owned by the full LAB-082 verifier.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: obtain a byte-safe supported transfer path for exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` into `experiments/asymmetric_break_glass_history/strict_fence.py` on PR #165. Publish only if branch predecessor remains `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` and GitHub returns exactly `b78e7c98...`.
2. Re-fetch/hash-verify the published LAB-086 runtime, execute exact `test_thaw_rowid_collision_regression.py` plus the complete strict/thaw conflict subgate and compileall, then repin only after green evidence; resume the complete LAB-080→086 real-ledger gate afterward.
3. If LAB-086 publication remains concretely tool-limited, LAB-091 fallback: refactor the complete body of `AsymmetricHistoricalSharedAnchorLedger.verify_durable()` into a transaction-accepting locked helper without changing its semantics; keep public `verify_durable()` as a wrapper over that helper.
4. Invoke that complete locked LAB-082 verifier inside final LAB-091 `_install_guards()` under the same `BEGIN IMMEDIATE`, after LAB-091 retroactive validation and before commit. Then execute `test_adoption_toctou_guard_persistence_regression.py` and the prior `test_failed_adoption_no_guard_persistence.py` on exact real LAB-080/LAB-082 dependencies. Only GREEN evidence permits continuing the two-worker/crash/timeout-UNKNOWN/reentrancy/legacy-write gate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; hidden-rowid blocker has exact RED→GREEN candidate evidence; byte-exact runtime publication is next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173 HEAD `4c171838...`; first-adoption TOCTOU regression/design recorded, full atomic-adoption fix + real-stack execution next when LAB-086 remains tool-limited.
