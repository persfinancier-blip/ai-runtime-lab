# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the allowed fallback; draft PR #175; branch `lab-090-provider-activation-fencing`; current head `fcad18c938f732241c968229831e0fccd82a3f6b`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues, and PR #175.

LAB-086 remains first priority. No safe supported byte-preserving composition/write bridge is exposed for exact predecessor `d4a6a40f...` + retained patch `61841b58...` -> required target `b78e7c98...`; do not manually/model-reserialize the 949-line security-critical `strict_fence.py`. LAB-086 was not mutated.

Resumed LAB-090 fallback and audited the activation table/schema durability boundary after canonical trigger verification. Found a concrete restart defect: SQLite accepts `CREATE TABLE IF NOT EXISTS provider_generation_activations(...)` when a same-name VIEW already exists. A durable schema tamper can therefore replace the activation table with an empty compatible view and reinstall the exact canonical trigger text. Restart then preserves the substitution; trigger authentication passes, while `_recover_pending_activation()` and `_verify_activation_records()` see no activation rows.

Published deterministic regression in PR #175 commit `fcad18c938f732241c968229831e0fccd82a3f6b`: `experiments/provider_generation_history/tests/test_activation_schema_tamper_restart.py`, blob `b03e52c1cd512a104b70cbd9f5a91747ce901184`. Re-fetch/hash matched exactly; `py_compile` executed PASS. Exact branch behavioral RED/GREEN is not claimed because repository execution transport remains unavailable.

Independent file-backed SQLite mechanism probe confirmed same-name VIEW survives `CREATE TABLE IF NOT EXISTS` instead of being rejected/replaced.

Durable note: `research/2026-08-31-lab090-activation-table-schema-tamper-restart.md`, main commit `e16c29593b53222c36fd7862781e0b7774035b64`; issue #169 comment `5476925547`.

PR #175 remains open/draft. Last observed mergeability before the new regression was false; do not integrate until exact behavioral/full gate is available and branch divergence is resolved through supported high-level operations.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall. Subsequent integration/restart/stale-runtime/verify-component/ticket-binding/numeric-type hardening is published. Canonical trigger-definition verification is published. New activation-table schema-substitution regression is published; broader exact execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact blob fetch is available, but no supported byte-preserving server-side patch composition/write bridge is currently exposed.
- Direct Git/raw repository execution transport remains unavailable; GitHub connector read/write operations are available.
- PR #175 stays draft; do not claim behavioral GREEN for activation-schema tamper regression/fix without exact execution.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable, resume LAB-090 PR #175. Implement the smallest fail-closed activation relation-schema verification: before recovery, require `provider_generation_activations` to be a real table with the exact canonical schema/constraints (or an equivalently strict PRAGMA contract), without drop/recreate or evidence loss. Then execute `test_activation_schema_tamper_restart.py`, trigger-tamper restart regression, activation restart/integration suite, and downstream gates through any safe exact-source execution path that becomes available. If execution remains unavailable, publish only byte-verifiable code/tests and record the missing behavioral gate explicitly.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation-table schema-substitution RED regression published; fail-closed schema verification pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
