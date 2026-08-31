# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- LAB-086 exact predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the allowed fallback while LAB-086 exact byte-preserving publication/execution is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; current head `27b059fb1da8cd7f790daaa3e5603f0172c427c4`.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. LAB-086 remains first priority, but the available GitHub connector still exposes complete-file Contents writes rather than a safe server-side exact-blob-plus-retained-patch composition operation. No LAB-086 mutation was attempted because manually/model-reserializing the 949-line security-critical `strict_fence.py` remains prohibited.

Resumed the exact LAB-090 fallback target recorded in the previous handoff: `verify_component()` generation concurrency. Source audit confirmed the remaining TOCTOU window. Inherited LAB-080 `verify_component()` authenticates/checks the current provider before its final `BEGIN IMMEDIATE`, but the commit-boundary transaction only rechecks the ledger slice and watermark. A G1->G2 rotation can therefore commit after the initial provider check but before watermark DML, allowing already-authenticated G1 evidence to advance the watermark after G2 is durable current.

Published deterministic regression candidate in PR #175 commit/head `27b059fb1da8cd7f790daaa3e5603f0172c427c4`: `experiments/provider_generation_history/tests/test_activation_verify_component_rotation_race.py`, blob `359288e32e7df0ffd60bd359e326398b0bec276a`. The test rotates G1->G2 during reauthentication immediately before the inherited final watermark transaction and requires `CurrentGenerationRequired` plus an unchanged component watermark. Exact published test bytes were independently reconstructed and Git-blob hashed to the same SHA; `py_compile` PASS. Behavioral unittest PASS is not claimed because the production commit-boundary guard is not yet published.

Minimal fix design is recorded: add a no-op commit-boundary hook to LAB-080 `SharedAnchorLedger.verify_component()` immediately after final `BEGIN IMMEDIATE`; override it in provider-history integration to read `IntegratedProviderHistory._current_locked(q)` through that same connection and require the observed provider/generation to equal the durable current head before any watermark DML. This gives a cross-process linearization point with provider rotation; a post-write check is insufficient.

Issue #169 comment `5473245952`. Durable note: `research/2026-08-31-lab090-verify-component-generation-commit-race.md`, main commit `b4976b101bcd0e91b8afd3378c1b15741d0ce708`.

PR #175 recheck reports open, draft, and mergeable at head `27b059fb1...`; the earlier transient non-mergeable control-plane observation is no longer present.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED->GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact signer-noise/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-091 focused/adoption evidence retained; full real-stack gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice remains 10/10 PASS + compileall. Subsequent activation integration/restart/stale-runtime hardening is published but broader exact execution remains pending.
- New LAB-090 `verify_component` rotation-race regression blob `359288e3...` is byte-verified and `py_compile` PASS; behavioral RED/GREEN execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` plus retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Current GitHub connector provides normal complete-file Contents writes but no observed safe server-side patch/composition primitive for the LAB-086 exact predecessor+retained-patch operation.
- PR #175 stays draft. The new generation-commit race regression is exact-byte/syntax verified only, not yet behaviorally executed.
- Production fix for the LAB-090 race should not be published by casually reserializing shared protocol files; require exact replacement-byte verification and an exact diff, or a byte-preserving patch path.

## Exact next action

LAB-086 first: probe again for a supported byte-preserving composition/transfer bridge; if available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable, resume LAB-090 PR #175. Publish the `verify_component` commit-boundary generation guard through a byte-exact path: base no-op hook immediately after final `BEGIN IMMEDIATE`, provider-history override using the same connection/current-head read, and no watermark DML before that check. Then execute the new rotation-race regression and the activation integration/restart/downstream gate. If execution transport remains unavailable, independently reconstruct/hash-verify the changed production bytes and audit the exact commit diff before any claim of correctness.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; stable stale-runtime fix published; commit-boundary generation race regression now published; production guard + exact integration/restart/downstream gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
