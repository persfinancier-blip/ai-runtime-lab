# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` (949 lines).
- Retained hidden-rowid patch: `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact previously derived target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-091 / #170 is the allowed fallback while LAB-086 publication/execution is concretely tool-limited; draft PR #173, branch `lab/091-mutable-shared-anchor-writer`; current head `aad64cc350b5fdef44f941d0d2cffd22adf5b0f5`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172; fresh semantic patch audit is clean, downstream execution still pending.
- LAB-090 / #169 remains READY but now has a concrete provider-activation fencing design and regression matrix.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open PRs/issues. LAB-086 remains first priority. The connector can fetch the exact predecessor blob and retained patch and can perform normal Contents API writes, but there is still no supported operation in this runtime that byte-preservingly composes the fetched 949-line security-critical source with the patch and transfers that exact composed payload into `update_file` without model/manual whole-file reserialization. Direct raw/archive web fetch remains unavailable. No LAB-086 mutation was attempted.

Because neither exact branch execution nor the required LAB-086 composition bridge appeared, advanced LAB-090 rather than adding speculative LAB-091 guards. Reviewed current primary-source conditional-write mechanisms (Google Cloud Storage generation-match preconditions; Amazon S3 If-Match) and derived the transferable requirement: the external provider, not SQLite, must own compare-and-swap/reservation/fencing over the exact observed provider state.

Executed a minimal local provider state-machine mechanism check. With an atomic `prepare_activation(expected_position)` returning a monotonically fenced activation ticket: a concurrent provider advance after prepare was rejected as `fenced`; timeout/UNKNOWN after activation commit reconciled from durable epoch+position; and a candidate provider already at N+1 rejected `prepare_activation(N)` as stale. This is mechanism evidence only, not exact repository/full-provider execution.

Durable LAB-090 design: `research/2026-08-30-lab090-provider-activation-fencing-design.md`, main commit `cc4240c20a706be5903340a267707ee5a1555b0d`; issue #169 comment `5468092407`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED→GREEN evidence retained; exact predecessor -> exact candidate target previously byte-rederived and mechanism-tested; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact published signer-noise/core evidence remains 22/22 PASS + compileall; fresh PR-diff semantic audit is CLEAN. Remaining readiness work is supported-integration plus downstream LAB-084/085/086 compatibility execution.
- LAB-091 accumulated adoption hardening includes receipt affinity/collation, identity lookup collation, constructor ordering, restrictive UNIQUE/CHECK, required/generated extra columns, function-valued extra defaults, inherited foreign-key rejection, secondary-index collation/expression/partial rejection, and unavailable persisted canonical-column collation rejection, each with focused reproduced evidence.
- LAB-091 table-options negative audit: canonical, STRICT, WITHOUT ROWID, status NOCASE, and PK ON CONFLICT REPLACE preserved the tested canonical supported write shape; no hardening added.
- LAB-091 timeout/UNKNOWN and process concurrency/crash regressions remain pending full final-surface execution.
- LAB-090 provider-activation design now has primary-source CAS/precondition donors, explicit fencing-ticket protocol, UNKNOWN/restart reconciliation rules, and a 10-case regression matrix; minimal mechanism simulation passed the race/stale/UNKNOWN cases described above.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft. Exact whole-branch regressions and full timeout/UNKNOWN + process concurrency/crash behavior remain pending executable transport.
- PR #172 remains draft. Its source audit is clean, but supported LAB-083 integration and downstream LAB-084/085/086 compatibility have not been freshly executed on that branch.
- Do not represent focused local mechanism execution or source audit as byte-for-byte full-branch behavioral execution.
- Do not add speculative SQLite guards without a reproduced reachable supported compatibility/security failure.
- LAB-090 cannot be solved by SQLite locking or a second external read alone; either the provider abstraction must supply atomic reservation/CAS/fencing, or the contract must explicitly require mechanically enforced candidate-provider exclusivity/quiescence.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, apply only retained hidden-rowid patch, require exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, publish through normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates. If executable branch transport appears but publication remains unavailable, prioritize exact behavioral execution of LAB-091 final-surface regressions and LAB-088 supported/downstream compatibility gates. If neither transport appears, inspect the actual LAB-036/LAB-082 external-provider abstraction for LAB-090 and implement the smallest provider-owned activation-ticket/CAS/fencing interface plus regressions for `read/prepare -> external advance -> SQL rotate`, stale candidate, timeout/UNKNOWN and restart; do not substitute a second read for an external atomic precondition.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; fresh patch audit CLEAN; supported/downstream execution pending on draft PR #172.
- #169 / LAB-090 — READY; provider-owned activation fencing design complete; implementation/protocol integration next fallback step.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; exact whole-branch/full behavioral gates pending.
