# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the allowed fallback; draft PR #175; branch `lab-090-provider-activation-fencing`; latest production commit `71c22a2054b983839b760edf21ceedc77ad0bc6b`, `supported.py` blob `fb2bab4a262f295ef6a9b87cee459547038a0da9`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs.

LAB-086 was checked first again. Its exact predecessor/retained-patch/required-target publication contract is unchanged. No supported byte-preserving server-side composition path was observed, so the 949-line security-critical `strict_fence.py` was not reserialized or mutated.

Resumed LAB-090 fallback and audited durable activation-record verification. Found that SQLite INTEGER affinity can persist non-integral REAL values and the historical verifier accepted them: `expected_position` was normalized through `int()` for activation ID reconstruction and `fence` was only checked with `< 1`. Historical `COMMITTED` rows for older generations are not reconciled against a live provider, so this could let restart accept a record that cannot represent an exact integer provider ticket.

Published deterministic regression:
- commit `c39bb4f89042f3c8171e534f3c389716f80da5f8`;
- `experiments/provider_generation_history/tests/test_activation_historical_numeric_types.py`.

Published minimal production guard:
- commit `71c22a2054b983839b760edf21ceedc77ad0bc6b`;
- `supported.py` blob `fb2bab4a262f295ef6a9b87cee459547038a0da9`;
- verifier now requires exact `int` `expected_position >= 0` and exact `int` `fence >= 1`.

GitHub commit diff confirms only those verifier checks changed. A local file-backed SQLite mechanism check confirmed `INTEGER NOT NULL` stores `0.5`/`1.5` as storage class REAL. Exact branch behavioral/full downstream unittest GREEN is not claimed because direct repository execution transport remains unavailable.

Durable note: `research/2026-08-31-lab090-historical-activation-numeric-type-verification.md`, main commit `e10e200146f88abcfe207de59a043b55e6f42bf2`; issue #169 comment `5475130297`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall. Subsequent integration/restart/stale-runtime/verify-component/ticket-binding/numeric-type hardening is published; broader exact execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Direct Git/raw repository execution transport remains unavailable; GitHub connector read/write operations are available.
- PR #175 stays draft; do not claim behavioral GREEN for newly published LAB-090 regressions/guards without exact execution.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable, resume LAB-090 PR #175. Re-fetch/hash-audit head `supported.py` and execute `test_activation_historical_numeric_types.py`, `test_activation_ticket_binding.py`, activation integration/restart regressions, and downstream gates when exact repository execution becomes available. If execution remains unavailable, continue only the narrow activation durability/provider-coordinator audit and publish deterministic regressions plus minimal fail-closed fixes.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; historical numeric-type verifier guard published; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
