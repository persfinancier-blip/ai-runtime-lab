# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the allowed fallback; draft PR #175; branch `lab-090-provider-activation-fencing`; atomic installation source fix is now published at commit `d9a381dd4607a928cd1315adef6431e239995bc1`, `supported.py` blob `8140d6e180c3e97085830b872cea7d87f8433144`.
- LAB-092 / #176 is a READY follow-up for migration-safe activation-schema installation provenance/post-install deletion detection; do not fold it speculatively into LAB-090.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PR state. LAB-086 remained first priority. The current GitHub connector still exposes exact blob reads and complete UTF-8 Contents replacement but no supported byte-preserving server-side patch composition/write bridge for exact predecessor `d4a6a40f...` + retained patch `61841b58...` -> required target `b78e7c98...`. LAB-086 was not mutated; do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.

Used the allowed LAB-090 fallback. Re-fetched PR #175 `experiments/provider_generation_history/supported.py` at blob `76278dfceff78e2738d7dba73a5c8bcf2c4d3ef6` and the retained patch `research/patches/lab090-activation-schema-installation-transaction.patch`. The old hunk matched the current method. Applied the already-audited narrow change through the normal GitHub Contents API using the exact current blob as conflict guard.

Published source commit `d9a381dd4607a928cd1315adef6431e239995bc1`; resulting `supported.py` blob `8140d6e180c3e97085830b872cea7d87f8433144`. GitHub commit inspection confirms exactly one source-file hunk: add `BEGIN IMMEDIATE`, replace the two `executescript(... + ';')` calls with single-statement `execute()` calls, and preserve exact table/trigger definition checks, commit, rollback and close behavior. Branch re-fetch confirms the new method/blob.

Ran an independent file-backed two-connection SQLite mechanism probe for the security-relevant restart state: canonical activation table already contains `SQL_COMMITTED`, trigger initially absent, installer holds `BEGIN IMMEDIATE` while installing trigger, concurrent writer attempts an intent. The writer resumed only after installer commit and failed with `IntegrityError: provider activation unresolved`; zero intents persisted. This validates the intended locking mechanism, but is not an exact published-branch behavioral suite.

Durable note: `research/2026-08-31-lab090-activation-schema-atomic-install-applied.md`, main commit `446a8f41c17194760e37314a2828051140dc37cd`; #169 comment `5481243321`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall. Integration/restart/stale-runtime/verify-component/ticket-binding/numeric-type hardening, trigger-definition verification, activation-table schema verification, and schema-installation writer-race regression are published. Atomic schema installation source fix is now published at `d9a381dd...` / blob `8140d6e1...`; exact branch behavioral/full-suite execution remains pending.
- LAB-092 provenance/deletion-detection gap is documented and tracked separately; no speculative implementation was made.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact blob fetch is available, but no supported byte-preserving server-side patch composition/write bridge is currently exposed for LAB-086.
- Direct Git/raw repository execution transport is not currently available; GitHub connector read/write operations are available.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute. Do not upgrade mechanism-level SQLite evidence into branch-level GREEN.
- Do not solve LAB-092 by simply requiring the activation table to pre-exist: that would break legitimate pre-LAB-090 migration. Installation provenance needs an explicit durable/migration contract.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable and exact source execution becomes available, execute PR #175 `test_activation_schema_installation_race.py` first on source blob `8140d6e1...`, then `test_activation_schema_tamper_restart.py`, `test_activation_trigger_tamper_restart.py`, activation restart/integration and downstream gates. Require GREEN before moving PR #175 out of draft.

If execution remains unavailable, continue only narrow byte-verifiable LAB-090 provider/coordinator/restart audits. LAB-092 may be researched for a migration-safe provenance contract, but do not expand LAB-090 protocol scope speculatively.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; atomic installation source fix published; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — READY; define activation-schema installation provenance and post-install deletion detection without breaking legacy migration.
