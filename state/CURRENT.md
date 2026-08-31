# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the allowed fallback; draft PR #175; branch `lab-090-provider-activation-fencing`; current head `5101eba17df411d194ef1194d23d2c3ec130d923`; `supported.py` blob `d80a6015df8b39a43a1d3674ff7fc65263f1de7b`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs.

LAB-086 remains first priority. No safe supported byte-preserving server-side composition/write bridge is exposed for exact predecessor `d4a6a40f...` + retained patch `61841b58...` -> required target `b78e7c98...`; do not manually/model-reserialize the 949-line security-critical `strict_fence.py`. LAB-086 was not mutated.

Resumed LAB-090 fallback. The previously published RED regression proved that same-name `CREATE TRIGGER IF NOT EXISTS` preserves a tampered/no-op `block_intent_during_provider_activation` trigger across restart. Implemented fail-closed persisted-trigger authentication in PR #175 commit `5101eba17df411d194ef1194d23d2c3ec130d923`.

The implementation now keeps one canonical `_ACTIVATION_TRIGGER_SQL`, derives the idempotent install statement from it, reads persisted `sqlite_master.sql`, normalizes whitespace only, and raises `HistoricalVerificationError` on absence or mismatch. It does not drop/recreate the trigger, avoiding a fence-removal concurrency window.

GitHub commit inspection confirms one source file changed: `experiments/provider_generation_history/supported.py`, 38 additions / 9 deletions; resulting blob `d80a6015df8b39a43a1d3674ff7fc65263f1de7b`.

A separate file-backed SQLite mechanism test executed PASS: fresh canonical install verifies; replacing the trigger with same-name `WHEN 0` survives `IF NOT EXISTS` but canonical verification detects the mismatch. Exact branch behavioral/full-suite GREEN is not claimed because direct repository execution transport remains unavailable.

Durable note: `research/2026-08-31-lab090-activation-trigger-canonical-verification-fix.md`, main commit `22824d0c4582d4c4d8ca3a7ffd75191adfd13d04`; issue #169 comment `5476289299`.

PR #175 is open/draft at head `5101eba17...`; GitHub currently reports mergeability as unknown/null rather than a resolved clean/conflict state.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall. Subsequent integration/restart/stale-runtime/verify-component/ticket-binding/numeric-type hardening is published. Trigger-tamper RED regression is published and canonical trigger-definition fix is now published; broader exact execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact blob fetch is available, but no supported byte-preserving server-side patch composition/write bridge is currently exposed.
- Direct Git/raw repository execution transport remains unavailable; GitHub connector read/write operations are available.
- PR #175 stays draft; do not claim behavioral GREEN for the trigger-tamper regression/fix without exact execution.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable, resume LAB-090 PR #175. First attempt exact published-head execution of `test_activation_trigger_tamper_restart.py`, activation restart/integration tests, and downstream gates using any newly available safe execution path. If execution remains unavailable, audit the activation-table/schema durability boundary next: determine whether persisted table/index/constraint tampering can weaken coordinator assumptions despite canonical trigger authentication, reproduce only a concrete defect before changing code, and avoid speculative protocol expansion.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; canonical trigger verification fix published; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
