# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the allowed fallback; draft PR #175; branch `lab-090-provider-activation-fencing`; current head `96d7ad17836174c94c668d00e8608e498b1c5254`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issue #169, PR #175, and the current LAB-090 activation coordinator/provider code.

LAB-086 remains first priority. The GitHub write surface still exposes complete UTF-8 Contents replacement, not a supported byte-preserving server-side composition/write bridge for exact predecessor `d4a6a40f...` + retained patch `61841b58...` -> required target `b78e7c98...`. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`. LAB-086 was not mutated.

Fresh direct execution transport remains unavailable, so exact published-head behavioral/full-suite GREEN is still not claimed.

Narrow LAB-090 restart audit found a new writer window in `_init_activation_schema()`: activation table creation/verification and blocking-trigger creation/verification are two separate autocommit `executescript()` steps. If the trigger is missing while a `SQL_COMMITTED` activation exists, a concurrent live/older writer can insert after the table step and before trigger installation.

Published deterministic RED candidate on PR #175: `experiments/provider_generation_history/tests/test_activation_schema_installation_race.py`, commit `96d7ad17836174c94c668d00e8608e498b1c5254`, blob `cfd5c24107a9582bef91cbeeec28a8bc9b6f83c5`. Independent `py_compile` PASS; GitHub re-fetch exactly matches the computed blob. A separate file-backed SQLite mechanism probe reproduced the current two-autocommit-step ordering and admitted one writer in the gap despite an unresolved activation row.

Durable note: `research/2026-08-31-lab090-activation-schema-installation-race.md`, main commit `fec7a6ef0269cc2974f919ac5eb98bc7004b6a10`; issue #169 comment `5479151189`.

PR #175 remains open/draft. Do not claim the new regression behavioral RED/GREEN until exact repository execution is available.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall. Subsequent integration/restart/stale-runtime/verify-component/ticket-binding/numeric-type hardening is published. Trigger-definition and activation-table schema fail-closed verification are published. New schema-installation writer-race regression is published; broader exact execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact blob fetch is available, but no supported byte-preserving server-side patch composition/write bridge is currently exposed.
- Direct Git/raw repository execution transport remains unavailable; GitHub connector read/write operations are available.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute. Do not use a large multi-file Contents-API integration fallback before those gates.

## Exact next action

LAB-086 first: probe again for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable and exact source execution becomes available, run PR #175 published head beginning with `test_activation_schema_installation_race.py`, then `test_activation_schema_tamper_restart.py`, `test_activation_trigger_tamper_restart.py`, activation restart/integration and downstream gates. Expected current result for the new installation-race regression is RED. After reproducing it, fix `_init_activation_schema()` by holding one `BEGIN IMMEDIATE` transaction across table create/verify and trigger create/verify, using single-statement `execute()` rather than `executescript()`, then require GREEN and rerun downstream gates.

If execution remains unavailable, continue only narrow byte-verifiable LAB-090 provider/coordinator/restart audits; keep #175 draft and do not claim behavioral GREEN.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation schema-installation writer-race regression published; transactional install fix + exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
