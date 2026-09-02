# Current Lab State

Last updated: 2026-09-03

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175 observed head `d9a381dd4607a928cd1315adef6431e239995bc1`; constructor ordering, post-prepare cleanup, concurrent duplicate idempotency, activation-record integrity, and activation-provider authority defects remain pending exact RED/GREEN.
- LAB-092 / #176 draft PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-093 / #178 READY; LAB-094 / #179 READY; LAB-095 / #180 READY; LAB-096 / #181 READY; LAB-097 / #182 READY; LAB-098 / #183 READY; LAB-099 / #184 READY; LAB-100 / #185 READY.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues/PRs, PR #165 metadata, and PR #175 exact GitHub-fetched activation/coordinator source. Direct Git was reprobed first and still failed before repository access with `Could not resolve host: github.com`; no LAB-086 source mutation was attempted and no new LAB-086 behavioral PASS is claimed.

Fallback-audited PR #175 / LAB-090 and found a same-generation concurrent duplicate-rotation idempotency race. Two coordinators can both see no activation row and obtain the same PREPARED ticket. If winner A completes SQL rotation, provider commit, durable `COMMITTED`, and provider `RELEASED` before loser B reaches its INSERT, B gets the duplicate-row SQL conflict, re-reads the exact row as `COMMITTED`, treats the SQL outcome as already committed, then falls through to `_commit_or_reconcile_activation()`. Exact `FencedActivationProvider.commit_activation()` correctly returns `RELEASED`, but `_commit_or_reconcile_activation()` accepts only `COMMITTED_FENCED` and raises `HistoricalVerificationError`. Durable/provider state is already correct, so the duplicate supported operation fails instead of converging idempotently. This extends #169 rather than creating a duplicate issue.

No production code was staged and no exact repository behavioral PASS is claimed.

## Evidence produced

- `research/2026-09-03-lab090-concurrent-duplicate-rotation-released-race.md` — commit `91ceccbb51c0c1ca312fadd551fe9f179be7b6b6`; #169 comment `5516599326`.
- Retained recent evidence: LAB-100 nonmonotonic reconstruction `fc0bc0fe...`; LAB-090 COMMITTED-before-release audit `6e1e69b0...`; cleanup secondary DB dependency `7c2dc24f...`; post-prepare connection leak `4c488991...`; LAB-100 caller-owned state `ee7b6ae0...`; inherited provider rotate `25297f0b...`; provider subclass authority `8b1abf6f...`; LAB-086 rowid semantics probe `04bdef2f...`; LAB-098 surplus bootstrap row `6ac5525c...`; LAB-099 ticket rebinding `3b6e311b...`.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and patch bytes are connector-readable, but this run still lacks a supported machine transformation bridge from connector payload -> patch application -> candidate Git blob verification -> Contents write. Direct Git transport is transiently unavailable by DNS.
- Exact checkout/source execution remains unavailable in this run; no fresh repository behavioral PASS is claimed.
- Keep PRs #175/#177 draft until exact focused/integration/downstream gates execute.
- LAB-090 constructor: reject runtime-head mismatch before activation-schema mutation; verify complete activation history before any recovery mutation.
- LAB-090 fresh activation: once this attempt owns a newly-created valid PREPARED reservation, every subsequent fallible coordinator step must be inside exact-ticket cleanup scope. Cleanup must not depend on a secondary fallible DB read before abort and must never abort unrelated prior/idempotently returned activation state; if ownership cannot be inferred, add explicit provider attempt/provenance identity.
- LAB-090 duplicate same-generation rotation: if a competing winner has already durably marked the exact ticket `COMMITTED` and released it, the loser must converge idempotently. `RELEASED` must remain invalid for durable `SQL_COMMITTED`, conflicting ticket/generation, or premature-release evidence.
- LAB-090 `COMMITTED -> release` interval is not a standalone supported-surface bypass under current runtime-generation/construction checks, but integration tests must prove LAB-093/LAB-100 capability rebinding cannot turn it into one.
- LAB-098: derive required activation records from authenticated transitions and require a bijection.
- LAB-099: bind exact historical activation ticket contents into independent authenticated evidence.
- LAB-100: exact-type acceptance alone is insufficient. Bind provider implementation, identity/key/state-machine authority, activation-state ownership, and monotonic fencing cursor/history for the lifetime of activation state. Reject generic inherited identity rotation while state is non-quiescent or define a proven activation-aware transition. Reconstructed state must fail closed unless its next fence is strictly consistent with all trusted historical/pending tickets; do not canonicalize from arbitrary caller-owned mutable state.
- Do not stage LAB-093/094/095/096/097/098/099/100 production code before their pre-fix REDs execute or an equivalently strong auditable execution path exists.

## Exact next action

LAB-086 first: probe for a supported byte-preserving machine composition operation for predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` + retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`. If available, compose only that patch, require candidate Git blob `b78e7c98e35138719f77c482c7f1aab36b702de7`, conflict-check PR #165 still contains the predecessor, publish through normal Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run LAB-090 pre-fix REDs before PR #175 production changes: constructor ordering; malformed/failed prepare cleanup; first post-prepare `_con()` failure; exception-handler `_activation_row()` failure; deterministic same-generation two-coordinator duplicate where A reaches durable `COMMITTED` + provider `RELEASED` before B's duplicate INSERT; LAB-100 fake subclass/inherited rotation/caller-owned ActivationState/non-monotonic reconstructed fence cases; and `COMMITTED` durable acknowledgement with provider still `COMMITTED_FENCED` proving no supported writer path can create/execute a new intent before exact-ticket release. Then run LAB-098/099 REDs and PR #175/#177 full gates, followed by LAB-093/094/095/096/097 REDs.

If neither becomes available, continue audit only for concrete distinct trust/capability/fail-closed violations not subsumed by existing issues; strengthen an existing issue rather than creating a duplicate when the finding shares the same authority boundary.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending; cleanup, concurrent-idempotency and composition regressions expanded.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending.
- #178 / LAB-093 — READY.
- #179 / LAB-094 — READY.
- #180 / LAB-095 — READY.
- #181 / LAB-096 — READY.
- #182 / LAB-097 — READY.
- #183 / LAB-098 — READY.
- #184 / LAB-099 — READY.
- #185 / LAB-100 — READY; provider implementation/capability/state ownership/monotonic-fence reconstruction RED/GREEN pending.
