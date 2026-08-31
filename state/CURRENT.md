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

LAB-086 remains first priority. No supported byte-preserving server-side composition/write bridge is exposed for exact predecessor `d4a6a40f...` + retained patch `61841b58...` -> required target `b78e7c98...`. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`. LAB-086 was not mutated.

Reconciled PR #175 integration state. The earlier `mergeable=false` observation is not evidence of a source conflict: two-way compare from merge base `6cc7a044...` shows main-side divergence only in research/state paths and branch-side divergence in LAB-090 source/tests. A direct GitHub REST PR fetch now reports `mergeable=true`, `rebaseable=true`, `mergeable_state=clean`.

Fresh direct execution transport probe still fails before repository execution: `git ls-remote ...` -> `Could not resolve host: github.com`. Therefore exact published-head LAB-090 behavioral/full-suite GREEN is still not claimed.

Durable note: `research/2026-08-31-lab090-pr175-mergeability-reconciliation.md`, main commit `1f1b3b27d92f960ad81993af0899b9f22e85aef9`; issue #169 comment `5478529592`.

PR #175 remains open/draft because exact focused/integration/downstream behavioral gates are pending, not because of a demonstrated merge conflict.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall. Subsequent integration/restart/stale-runtime/verify-component/ticket-binding/numeric-type hardening is published. Trigger-definition and activation-table schema fail-closed verification are published. Broader exact execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact blob fetch is available, but no supported byte-preserving server-side patch composition/write bridge is currently exposed.
- Direct Git/raw repository execution transport remains unavailable; GitHub connector read/write operations are available.
- PR #175 is currently cleanly mergeable according to direct REST, but stays draft until exact behavioral/integration/downstream gates execute. Do not use the large multi-file Contents-API integration fallback before those gates.

## Exact next action

LAB-086 first: probe again for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable and exact source execution becomes available, run PR #175 published head regressions beginning with `test_activation_schema_tamper_restart.py` and `test_activation_trigger_tamper_restart.py`, then activation restart/integration and downstream gates. If execution remains unavailable, continue only narrow byte-verifiable LAB-090 provider/coordinator/restart audits; keep #175 draft and do not claim behavioral GREEN.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation-table schema-substitution fix published; exact behavioral/full gate pending; merge-conflict concern reconciled as clean.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
