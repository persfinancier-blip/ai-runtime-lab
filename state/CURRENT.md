# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the current allowed fallback while LAB-086 byte-preserving publication is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; head last observed `5f680da36733a54b6d79d554a083276a1643a0ce`.
- LAB-091 / #170 remains IN_PROGRESS fallback on draft PR #173.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.

## Last completed step

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues and PR #175. Direct branch transport was probed again with `git clone --depth 1 --branch lab-090-provider-activation-fencing ...` and failed before repository execution with `Could not resolve host: github.com`. No whole-branch unittest result is claimed.

Fresh source audit of PR #175 found a concrete remaining LAB-090 race in the `provider commit -> coordinator durable acknowledgement` window. Current `FencedActivationProvider.commit_activation()` records the ticket COMMITTED and immediately clears `activation_state.pending`; `increment()` fences only while `pending` is non-null. Before coordinator `_mark_activation_committed()` changes SQLite from `SQL_COMMITTED` to `COMMITTED`, an external actor can therefore advance the provider from N to N+1. The SQLite unresolved-activation trigger blocks coordinator intent inserts but cannot fence this external writer.

Durable evidence/design note: `research/2026-08-30-lab090-post-provider-commit-fence-release-race.md`, main commit `831088e3d69b7336f2295b1e5715f8adba089599`; issue #169 comment `5468910303`. PR #175 remains draft.

## Required LAB-090 protocol correction

Provider commit must remain externally fenced until the coordinator durably acknowledges the exact ticket. Implement an explicit provider state equivalent to `COMMITTED_FENCED` and an idempotent exact-ticket `release_activation()` / `finalize_activation()` after the SQLite activation row is durably `COMMITTED`. Restart must reconcile both directions: SQLite `SQL_COMMITTED` with provider `PREPARED`/`COMMITTED_FENCED`, and SQLite `COMMITTED` with provider still fenced. A stale or different ticket must never release the fence.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact published signer-noise/core evidence remains 22/22 PASS + compileall; supported/downstream execution pending.
- LAB-091 accumulated adoption hardening/focused reproduced evidence retained; whole-branch timeout/UNKNOWN and process concurrency/crash gates pending.
- LAB-090 provider primitive prior focused mechanism gate 6/6 PASS; coordinator integration source audit had a focused SQLite trigger PASS, but the new post-provider-commit fence-release race means PR #175 is not yet behaviorally complete.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- Direct git/network transport is currently unavailable due DNS; treat this as a per-run observation.
- PR #175 remains draft until the post-provider-commit fence-release race is fixed and exact published branch/downstream suites execute.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, publish and full-gate the exact hidden-rowid target. Otherwise resume LAB-090 PR #175: implement the minimal provider `COMMITTED_FENCED -> RELEASED` acknowledgement protocol, keep increments fenced through coordinator durable `COMMITTED`, add regressions for external advance between provider commit and SQL acknowledgement plus crash/restart after SQL COMMITTED but before provider release, then execute exact branch/downstream tests if transport becomes available. Do not add unrelated speculative guards.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending on draft PR #172.
- #169 / LAB-090 — IN_PROGRESS; post-provider-commit fence-release race discovered on draft PR #175; acknowledgement/finalization protocol required.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; exact whole-branch/full behavioral gates pending.
