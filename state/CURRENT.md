# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; atomic source fix head `d9a381dd4607a928cd1315adef6431e239995bc1`, `supported.py` blob `8140d6e180c3e97085830b872cea7d87f8433144`.
- LAB-092 / #176 is IN_PROGRESS on branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090. Current head `3abc53067d3e549a677f740c6a7b09c299acfaa2`; current provenance blob `52be0d1ae8365f3c8ffbfdfdb94c972dc082b74e`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and PR #177. LAB-086 remains first priority. Current GitHub operations still expose normal Contents reads/writes but no supported byte-preserving patch-composition operation; do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.

Re-probed exact source execution with a fresh clone of `lab-092-activation-schema-provenance`; transport again failed before repository execution with `Could not resolve host: github.com`. No branch-level RED/GREEN is claimed.

Advanced the allowed LAB-092 fallback. Source audit found that `_reservation_surface()` constructed `CoordinatorOnlyProviderHistory(path, bootstrap)` before acquiring the migration writer lock. Its inherited `DurableProviderHistory.__init__` executes `CREATE TABLE IF NOT EXISTS` for provider-history objects and may bootstrap empty history, creating an undesired pre-lock mutation surface.

Published stale-runtime regression commit `bc129f7d829486ff7a82fd88e260a872684374e2`: after valid durable provider history advances from generation 1 to generation 2, a generation-1 runtime attempting legacy activation-schema migration must raise `CurrentGenerationRequired` and leave activation table absent, trigger absent, provenance marker absent, and durable head unchanged.

Published implementation/current head `3abc53067d3e549a677f740c6a7b09c299acfaa2`: `_reservation_surface()` now builds a non-mutating provider-history view with `object.__new__` and only sets `path`/`bootstrap`; inside the same `BEGIN IMMEDIATE`, `_install_and_reserve_prepared()` now calls full inherited `_verify_durable_locked(q)` before runtime-current comparison and before any activation DDL creation. GitHub re-fetch confirms provenance blob `52be0d1ae8365f3c8ffbfdfdb94c972dc082b74e` and PR #177 remains open/draft/mergeable against LAB-090.

Durable evidence: `research/2026-09-01-lab092-stale-runtime-nonmutating-history-view.md`, main commit `723f963f5801add79b7c8f25994f3b6416c5eaf1`; #176 comment `5486620443`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; atomic installation fix published, exact branch behavioral/full-suite execution pending.
- LAB-092 earlier classifier `py_compile`/standalone state-machine and atomic-visibility evidence retained. Stale-runtime regression and non-mutating provider-history view are now published; exact PR #177 regressions remain unexecuted because checkout transport still fails before code execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available, but no supported byte-preserving server-side patch-composition write is exposed.
- Direct git transport failed again before repository execution with `Could not resolve host: github.com`.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft. Atomic DDL+PREPARED candidate, reservation-surface hardening, and stale-runtime fail-closed source are published, but exact behavioral execution is still pending.
- Do not solve LAB-092 with unauthenticated local markers, marker confirmation before exact DDL, post-confirmation auto-repair, durable PREPARED-before-DDL state, or provider-history bootstrap as a migration side effect.
- Explicit branch/base conflict reconciliation is required before integration of #175/#177.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable and exact source execution becomes available, execute PR #175 `test_activation_schema_installation_race.py` first on source blob `8140d6e1...`, then remaining LAB-090 gates; then execute all PR #177 provenance tests on head `3abc5306...`, including stale-runtime, atomic boundary, unresolved activation, PREPARED recovery, deletion/mismatch, and legitimate legacy migration.

If execution remains unavailable, audit LAB-092's recovery paths for existing migration markers. In `_install_and_reserve_prepared()`, PREPARED/CONFIRMED marker branches currently return before the newly added full durable-history/runtime-current verification. Determine whether this permits any recovery/confirmation side effect to proceed from stale or corrupted inherited provider history. Add regressions first, then move the non-mutating `_verify_durable_locked(q)` + runtime-current check ahead of those early returns if required, preserving the existing post-marker DDL tamper checks.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; atomic installation source fix published; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; atomic DDL+PREPARED candidate, non-mutating migration history view, and stale-runtime regression published; marker-recovery audit plus exact regression gate pending.
