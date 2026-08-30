# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the current allowed fallback while LAB-086 byte-preserving publication is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; regression commit `ac19c49226d9b31eed46646cd4ddb9ddd0dae507` adds the overlapping-rotation test candidate.
- LAB-091 / #170 remains IN_PROGRESS fallback on draft PR #173.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.

## Last completed step

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. Direct git transport was probed again and failed before repository-code execution with `Could not resolve host: github.com`, so no exact-head unittest/downstream PASS is claimed.

Resumed LAB-090 PR #175 and found a concrete concurrency defect. The current unresolved-activation guard is a SQLite trigger only on `shared_anchor_intents`; `rotate_provider()` itself does not reject a second provider-generation rotation while an earlier activation row remains `SQL_COMMITTED`.

Concrete schedule: rotation A durably advances generation head G1->G2 and leaves activation A `SQL_COMMITTED` because provider commit/acknowledgement is unavailable; before A is resolved, rotation B for G3 can prepare a different provider, obtain `BEGIN IMMEDIATE`, observe no PREPARED shared-anchor intent and the same tail, insert its own `SQL_COMMITTED` activation and advance durable head G2->G3. Activation A then becomes an older unresolved row; normal restart recovery only looks up the activation for the current durable generation and cannot repair the stranded G2 activation.

Published durable analysis: `research/2026-08-30-lab090-overlapping-rotation-audit.md`, main commit `6e0bde6456e480e0c58f359ff602c5a139f3e02a`. Published focused regression candidate on PR branch: `experiments/provider_generation_history/tests/test_activation_overlapping_rotation.py`, commit `ac19c49226d9b31eed46646cd4ddb9ddd0dae507`. Issue #169 updated in comment `5470428497`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact published signer-noise/core evidence remains 22/22 PASS + compileall; supported/downstream execution pending.
- LAB-091 accumulated adoption hardening/focused reproduced evidence retained; whole-branch timeout/UNKNOWN and process concurrency/crash gates pending.
- LAB-090 prior provider primitive focused mechanism gate 6/6 PASS is retained. Premature-release fail-closed correction is published. New overlapping-rotation regression is published but not yet executable-gated in this runtime.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, applying only the retained patch through a byte-preserving supported path, requiring exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`, then re-fetch/hash-verify and run the complete security gate.
- Direct git/network transport remains unavailable due DNS in this run; treat this as a per-run observation.
- PR #175 remains draft. The overlapping-rotation defect is unresolved in implementation and the new regression has not been executed.

## Exact next action

LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, publish and full-gate the exact hidden-rowid target. Otherwise resume LAB-090 PR #175 and make the minimal overlapping-rotation fix: inside the same `BEGIN IMMEDIATE` transaction, before inserting a new activation row, reject if any `provider_generation_activations` row has `status='SQL_COMMITTED'` with `PendingRotationBlocked("previous provider activation commit is unresolved")`; rely on the existing exception path to abort the second candidate's provider reservation. Then execute `test_activation_overlapping_rotation.py` plus `test_activation.py`, `test_activation_integration.py`, `test_activation_premature_release.py`, provider-generation integration, and downstream shared-anchor/provider-history suites as soon as exact-head execution is available. Do not widen the protocol or merge from source audit alone.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending on draft PR #172.
- #169 / LAB-090 — IN_PROGRESS; overlapping provider rotations can strand an older `SQL_COMMITTED` activation; regression published, minimal exclusion fix pending on draft PR #175.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; exact whole-branch/full behavioral gates pending.
