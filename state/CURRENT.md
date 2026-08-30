# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the current allowed fallback while LAB-086 byte-preserving publication is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; overlapping-rotation fix commit `960e847c4309626d86fee756bb304cfb240a0f4f`.
- LAB-091 / #170 remains IN_PROGRESS fallback on draft PR #173.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.

## Last completed step

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. Direct git transport was probed again and failed before repository-code execution with `Could not resolve host: github.com`, so no exact-head unittest/downstream PASS is claimed.

Resumed LAB-090 PR #175 and implemented the previously identified overlapping-provider-rotation exclusion. Inside the existing `BEGIN IMMEDIATE` in `rotate_provider()`, before PREPARED-intent validation and before inserting a candidate activation, the coordinator now rejects any existing `provider_generation_activations` row with `status='SQL_COMMITTED'` using `PendingRotationBlocked("previous provider activation commit is unresolved")`. The existing exception path rolls back and aborts the second candidate provider reservation.

GitHub commit inspection confirms commit `960e847c4309626d86fee756bb304cfb240a0f4f` changes only the intended five lines in `experiments/provider_generation_history/supported.py`. Existing focused regression `test_activation_overlapping_rotation.py` already asserts the required G2-unresolved/G3-blocked behavior. Issue #169 updated in comment `5470731974`.

Durable analysis: `research/2026-08-30-lab090-overlapping-rotation-fix.md`, main commit `57cadba2a64799c8a2bc12dd59f6c2927ae14ea4`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact published signer-noise/core evidence remains 22/22 PASS + compileall; supported/downstream execution pending.
- LAB-091 accumulated adoption hardening/focused reproduced evidence retained; whole-branch timeout/UNKNOWN and process concurrency/crash gates pending.
- LAB-090 prior provider primitive focused mechanism gate 6/6 PASS is retained. Premature-release fail-closed correction is published. Overlapping-rotation regression and minimal exclusion fix are now published but not yet executable-gated in this runtime.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- Direct git/network transport remains unavailable due DNS in this run; treat this as a per-run observation.
- PR #175 remains draft. The overlapping-rotation implementation fix is published, but exact-head focused/integration/downstream execution is still pending.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, publish and full-gate the exact hidden-rowid target. Otherwise resume LAB-090 PR #175 and attempt exact-head execution of `test_activation_overlapping_rotation.py`, `test_activation.py`, `test_activation_integration.py`, `test_activation_premature_release.py`, provider-generation integration, and downstream shared-anchor/provider-history suites. If direct execution remains unavailable, perform one narrow fresh audit of restart/concurrency handling around unresolved activation rows and current-generation recovery; make no speculative protocol expansion and do not merge from source audit alone.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending on draft PR #172.
- #169 / LAB-090 — IN_PROGRESS; overlapping provider rotations now fail closed in implementation; exact-head executable gate pending on draft PR #175.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; exact whole-branch/full behavioral gates pending.
