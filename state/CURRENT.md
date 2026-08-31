# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the allowed fallback; draft PR #175; branch `lab-090-provider-activation-fencing`; current head `91b54bc3440c2e13dcc60a3138b7793afc58d85e`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs.

LAB-086 was probed first. `fetch_pr_file_patch` now returns the complete 949-line `strict_fence.py` PR addition and the retained hidden-rowid patch remains byte-identified as `61841b58...`. However, no supported operation observed in this run can server-side apply that unified patch to the exact predecessor payload and pass the composed bytes directly into a normal Contents write. Manual/model reserialization of the security-critical whole file remains prohibited. No LAB-086 mutation was attempted.

Resumed LAB-090 fallback and found a new activation-ticket binding defect: `rotate_provider()` trusts the `ActivationTicket` returned by candidate `prepare_activation()` and persists its fields before checking exact binding to the requested `GenerationDescriptor`, expected tail, and activation ID. A malformed provider response can therefore durably rotate the generation head and persist an inconsistent activation row before commit/restart verification fails.

Published deterministic regression on PR #175:
- commit `91b54bc3440c2e13dcc60a3138b7793afc58d85e`;
- `experiments/provider_generation_history/tests/test_activation_ticket_binding.py`;
- expected/locally recomputed Git blob `05b11e7549a051ee5c09d77b3571aa8123e95e3d`;
- local `py_compile` PASS.

Behavioral RED/GREEN execution is not claimed because direct repository transport remains unavailable. Durable note: `research/2026-08-31-lab090-activation-ticket-binding.md`, main commit `b77feac00c35818799b346dd3e0278b317c4997c`; issue #169 comment `5474068145`.

PR #175 is open, draft, and currently reports mergeable=true at head `91b54bc...`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall. Subsequent integration/restart/stale-runtime/verify-component hardening is published; broader exact execution remains pending.
- LAB-090 activation-ticket binding regression source hash/`py_compile` PASS; behavioral result pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Direct Git/raw network transport remains unavailable in this run; GitHub connector operations are available.
- PR #175 stays draft; do not claim behavioral GREEN for the new activation-ticket regression without execution.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable, resume LAB-090 PR #175. Add the smallest pre-SQL activation-ticket validation in `rotate_provider()`: require returned provider_id/generation/expected_position/activation_id/fence to bind exactly to the requested candidate and require the exact ticket to be provider-`PREPARED` before any coordinator SQL mutation. Then execute the new regression and activation integration/restart/downstream gate when exact repository execution is available. If execution remains unavailable, audit the resulting diff and persist only claims actually observed.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation-ticket binding regression published; pre-SQL production guard + behavioral gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
