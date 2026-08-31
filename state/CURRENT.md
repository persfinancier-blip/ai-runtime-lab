# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the allowed fallback; draft PR #175; branch `lab-090-provider-activation-fencing`; current head `ae3a3cf089f7436ea74548ef9fa6cc5242e276e8`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues, and PR #175.

LAB-086 remains first priority. Direct git transport is still unavailable (`Could not resolve host: github.com`) and no safe supported byte-preserving server-side composition/write bridge is exposed for exact predecessor `d4a6a40f...` + retained patch `61841b58...` -> required target `b78e7c98...`. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`. LAB-086 was not mutated.

Resumed LAB-090 fallback and implemented the pending fail-closed activation relation-schema verification. PR #175 commit `ae3a3cf089f7436ea74548ef9fa6cc5242e276e8`, `experiments/provider_generation_history/supported.py` blob `76278dfceff78e2738d7dba73a5c8bcf2c4d3ef6`.

The implementation now canonicalizes `provider_generation_activations` DDL and, immediately after `CREATE TABLE IF NOT EXISTS`, requires `sqlite_master` to report the object as a real `table` whose normalized persisted SQL exactly matches the canonical PRIMARY KEY / UNIQUE / NOT NULL / CHECK contract. No drop/recreate or evidence-destructive repair is attempted; any mismatch raises `HistoricalVerificationError` before trigger verification/recovery.

GitHub commit diff inspection confirms only `experiments/provider_generation_history/supported.py` changed. A file-backed SQLite mechanism probe executed PASS: fresh canonical table passes exact DDL verification; same-name VIEW substitution survives SQLite `CREATE TABLE IF NOT EXISTS` but is rejected by the new `type='table'`/DDL check.

Exact published-branch behavioral/full-suite GREEN is not claimed because repository execution transport remains unavailable. Existing regression `test_activation_schema_tamper_restart.py` remains the required exact behavioral gate.

Durable note: `research/2026-08-31-lab090-activation-table-schema-verification-fix.md`, main commit `fef486875f511900e3274b156836393becf486aa`; issue #169 comment `5477562648`.

PR #175 remains open/draft at head `ae3a3cf...`; GitHub currently reports `mergeable=false`. Do not integrate until exact behavioral/full gate executes and branch integration state is resolved through supported high-level operations.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall. Subsequent integration/restart/stale-runtime/verify-component/ticket-binding/numeric-type hardening is published. Trigger-definition and activation-table schema fail-closed verification are now published. Broader exact execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact blob fetch is available, but no supported byte-preserving server-side patch composition/write bridge is currently exposed.
- Direct Git/raw repository execution transport remains unavailable; GitHub connector read/write operations are available.
- PR #175 stays draft and currently reports `mergeable=false`; do not claim behavioral GREEN for activation schema/trigger fixes without exact execution.

## Exact next action

LAB-086 first: probe again for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable, resume LAB-090 PR #175. First inspect why GitHub reports `mergeable=false` and determine whether divergence is only control-plane/docs or an actual source conflict. Use only supported high-level operations; do not use low-level ref/tree manipulation or force updates. If an exact-source execution path becomes available, run `test_activation_schema_tamper_restart.py`, trigger-tamper restart regression, activation restart/integration suite, and downstream gates on published head `ae3a3cf...`. If execution remains unavailable, continue only narrow byte-verifiable audits/fixes and record missing behavioral gates explicitly.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation-table schema-substitution fix published; exact behavioral/full gate + integration-state resolution pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
