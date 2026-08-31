# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the allowed fallback; draft PR #175; branch `lab-090-provider-activation-fencing`; latest production commit remains `71c22a2054b983839b760edf21ceedc77ad0bc6b`, `supported.py` blob `fb2bab4a262f295ef6a9b87cee459547038a0da9`; latest regression commit `23087e48fbc99229e194e15620fa35d13f8a1e86`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs.

LAB-086 was checked first. The GitHub connector can now fetch exact blobs by SHA and successfully returned predecessor `d4a6a40f...` plus retained patch `61841b58...`. Conflict check also confirmed branch `lab/086-asymmetric-break-glass-history` still has exact predecessor blob `d4a6a40f...` at `strict_fence.py`. However, no supported high-level server-side apply-patch/composition operation is exposed. The Contents API requires full replacement UTF-8 content, so using it would still require prohibited manual/model reserialization of the 949-line security-critical file. LAB-086 was not mutated.

Resumed LAB-090 fallback and audited the durable activation intent fence. Found that `_init_activation_schema()` uses `CREATE TRIGGER IF NOT EXISTS block_intent_during_provider_activation`; an already-persisted same-name no-op/tampered trigger therefore survives restart unchanged, while `_verify_activation_records()` does not authenticate the trigger definition. This can remove the durable fence that must block new intents while an activation remains `SQL_COMMITTED`.

Published deterministic RED regression:
- commit `23087e48fbc99229e194e15620fa35d13f8a1e86`;
- `experiments/provider_generation_history/tests/test_activation_trigger_tamper_restart.py`;
- exact remotely re-fetched blob `3b6efe53d3cef505ef78a4fadf9d283aa88deac7`;
- independent `py_compile` PASS.

A separate file-backed SQLite mechanism check confirmed that same-name `CREATE TRIGGER IF NOT EXISTS` preserves a tampered `WHEN 0` trigger and admits an intent insert despite a persisted unresolved activation. Exact branch behavioral RED/GREEN is not claimed because direct repository execution transport remains unavailable.

Durable note: `research/2026-08-31-lab090-activation-trigger-tamper-restart.md`, main commit `9b4fa16d0da0c40d813a40a2a59c2ca2cc2d4ddc`; issue #169 comment `5475758883`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall. Subsequent integration/restart/stale-runtime/verify-component/ticket-binding/numeric-type hardening is published. Trigger-tamper RED regression is now published; broader exact execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact blob fetch is available, but no supported byte-preserving server-side patch composition/write bridge is currently exposed.
- Direct Git/raw repository execution transport remains unavailable; GitHub connector read/write operations are available.
- PR #175 stays draft; do not claim behavioral GREEN for newly published LAB-090 regressions/guards without exact execution.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable, resume LAB-090 PR #175. Implement fail-closed authentication of the persisted `block_intent_during_provider_activation` enforcement trigger, preferably from one canonical trigger definition used for both install and verification, without introducing a drop/recreate concurrency window. Run `test_activation_trigger_tamper_restart.py` plus activation restart/integration/downstream gates when exact repository execution is available. If execution remains unavailable, continue only narrow durability/provider-coordinator audit work and retain explicit RED/mechanism evidence without claiming behavioral GREEN.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation-trigger tamper RED published; canonical trigger verification fix and exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
