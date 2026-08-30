# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` (949 lines); retained hidden-rowid patch `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the current allowed fallback while LAB-086 byte-preserving publication is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; current head `d0c4bb5f61f334aed7fc403e56529cf70982cf39`.
- LAB-091 / #170 remains IN_PROGRESS fallback on draft PR #173, branch `lab/091-mutable-shared-anchor-writer`, head last verified `aad64cc350b5fdef44f941d0d2cffd22adf5b0f5`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172; source audit clean, downstream execution pending.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected issue #169 and the actual LAB-036/LAB-081 provider abstraction. Direct `git clone` was probed and failed before execution with `Could not resolve host: github.com`, so exact branch transport is still unavailable. LAB-086 therefore remains blocked by the same byte-preserving composition/transfer constraint and was not mutated.

Advanced LAB-090 instead. Created branch `lab-090-provider-activation-fencing` and draft PR #175. Added `experiments/provider_generation_history/activation.py` with a provider-owned activation ticket, monotonic fence, exact-position prepare/CAS, idempotent commit/abort/status, UNKNOWN-after-commit reconciliation, restart model through provider-owned `ActivationState`, and rejection of ordinary provider increments while an activation is PREPARED. Added six focused regressions in `experiments/provider_generation_history/tests/test_activation.py`.

A local focused mechanism execution of the exact new primitive logic with dependency behavior matching the LAB-036 methods it calls passed 6/6: external advance fenced after prepare; stale N+1 candidate rejected; prepare idempotent; UNKNOWN commit reconciled COMMITTED; provider-owned state visible after coordinator reconstruction; abort released fence without advancing position. This is mechanism evidence, not byte-for-byte branch unittest execution. Re-fetched PR #175 patch and audited it as additive; existing `HistoricalSharedAnchorLedger.rotate_provider()` is intentionally not yet rewired because the coordinator must durably bind the exact activation ticket/fence before the SQL generation-head commit for correct restart/UNKNOWN recovery.

Durable evidence: `research/2026-08-30-lab090-provider-activation-primitive.md`, main commit `f81875f4711d0733044b97f9aca4f64b42907be2`; issue #169 comment `5468384693`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact published signer-noise/core evidence remains 22/22 PASS + compileall; fresh PR-diff semantic audit CLEAN; supported/downstream execution pending.
- LAB-091 accumulated adoption hardening and focused reproduced evidence remain retained; whole-branch timeout/UNKNOWN and process concurrency/crash gates pending.
- LAB-090 design note `research/2026-08-30-lab090-provider-activation-fencing-design.md` plus new provider primitive evidence above. Focused primitive mechanism gate: 6/6 PASS.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- Direct git/network transport is currently unavailable due DNS; treat this as a per-run observation.
- PR #175 remains draft. The primitive is not yet wired into coordinator rotation; exact branch tests are not claimed. Correct integration needs durable coordinator binding of activation_id/ticket/fence before SQL generation-head commit, then provider commit/reconcile and restart recovery.
- LAB-090 cannot be solved by SQLite locking or a second external read alone. The provider must own the atomic position precondition/reservation/fence, or the contract must mechanically enforce candidate-provider exclusivity/quiescence.
- Do not represent focused local mechanism execution or source audit as byte-for-byte full-branch behavioral execution.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, publish and full-gate the exact hidden-rowid target as already specified. Otherwise continue LAB-090 on PR #175: inspect the provider-generation SQLite schema and add the smallest durable activation record that binds `activation_id`, provider generation, expected position and fence to an in-progress rotation; then rewire `HistoricalSharedAnchorLedger.rotate_provider()` to `provider prepare -> durable ticket + SQL rotation -> provider commit/reconcile`, aborting the provider reservation on pre-commit SQL failure and reconciling the exact durable ticket after UNKNOWN/restart. Add regressions for `prepare -> attempted external advance -> SQL rotate`, stale candidate, SQL failure/abort, UNKNOWN-after-provider-commit, and restart. Do not substitute a second read.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending on draft PR #172.
- #169 / LAB-090 — IN_PROGRESS; provider primitive on draft PR #175; durable coordinator ticket integration next.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; exact whole-branch/full behavioral gates pending.
