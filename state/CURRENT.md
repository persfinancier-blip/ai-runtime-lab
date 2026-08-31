# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the allowed fallback; draft PR #175; branch `lab-090-provider-activation-fencing`; current head `8aa12d35e3dc397543193e098ab51017cf09ffc8`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs.

LAB-086 was probed first again. The exact predecessor/retained-patch/required-target contract is unchanged. No supported operation observed can server-side compose the retained unified patch with the exact predecessor bytes and feed that result directly into a normal Contents write. Manual/model reserialization of the 949-line security-critical `strict_fence.py` remains prohibited. No LAB-086 mutation was attempted.

Resumed LAB-090 fallback. The previously published deterministic regression `test_activation_ticket_binding.py` showed that `rotate_provider()` trusted the candidate provider's returned `ActivationTicket` before proving exact binding.

Published the minimal production guard on PR #175:
- commit `8aa12d35e3dc397543193e098ab51017cf09ffc8`;
- `experiments/provider_generation_history/supported.py` blob `f9f4975001fa691b415cbbd488897d8c44499c49`;
- optimistic-concurrency predecessor blob `6aee4eaec6d34563ea82c2a3216a82fb1d157c00`.

Immediately after `prepare_activation()` and before coordinator `BEGIN IMMEDIATE`, the returned ticket must now be exact `ActivationTicket`, bind provider/generation/observed tail/deterministic activation ID, carry a positive integer fence, and be provider-`PREPARED` for that exact ticket. Binding failures raise `HistoricalVerificationError` before coordinator SQL mutation.

GitHub commit diff confirms the guard is inserted before SQL mutation. The only incidental change is newline-at-EOF normalization. Direct Git/raw transport was probed again and remains unavailable due DNS resolution failure, so no exact branch behavioral GREEN/full downstream unittest gate is claimed.

Durable note: `research/2026-08-31-lab090-pre-sql-activation-ticket-validation.md`, main commit `35d404291f397938bc32377d5b4f4446b3d9974a`; issue #169 comment `5474563697`.

PR #175 is open, draft, and reports mergeable=true at head `8aa12d35...`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall. Subsequent integration/restart/stale-runtime/verify-component hardening is published; broader exact execution remains pending.
- LAB-090 activation-ticket binding regression source hash/`py_compile` PASS from the prior run; pre-SQL production guard is now published; behavioral result for the guard remains pending exact execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Direct Git/raw network transport remains unavailable in this run; GitHub connector read/write operations are available.
- PR #175 stays draft; do not claim behavioral GREEN for activation-ticket binding without exact execution.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable, resume LAB-090 PR #175. Re-fetch/hash-audit the new `supported.py` head and execute `test_activation_ticket_binding.py` plus activation integration/restart/downstream gates when exact repository execution becomes available. If execution remains unavailable, continue the narrow provider/coordinator boundary audit and persist only defects with deterministic regressions; do not expand protocol scope speculatively.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; pre-SQL activation-ticket guard published; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
