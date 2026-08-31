# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; atomic source fix head `d9a381dd4607a928cd1315adef6431e239995bc1`, `supported.py` blob `8140d6e180c3e97085830b872cea7d87f8433144`.
- LAB-092 / #176 is IN_PROGRESS on branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090. Current head `3590acee6e42685524e59ce123767003cba32cc6`; atomic DDL+PREPARED implementation commit `6aaab4e72144ad7fc4309f1054b4881187c2c22d`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and PR #177. LAB-086 remains first priority. The current GitHub interface still exposes normal Contents writes/reads but no supported byte-preserving patch-composition operation; do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.

Re-probed exact source execution with a fresh clone of `lab-092-activation-schema-provenance`; transport again failed before repository execution with `Could not resolve host: github.com`. No branch-level RED/GREEN is claimed.

Advanced the allowed LAB-092 fallback. The previously proven DDL→marker writer-admission gap is now addressed: exact activation DDL installation and deterministic PREPARED migration-marker reservation are performed in one SQLite `BEGIN IMMEDIATE` transaction, re-read before one commit, and only then externally confirmed through the inherited shared-anchor ledger. The implementation reuses LAB-081/LAB-080 identity/serialization primitives (`_current_locked`, `_descriptor_from_attested`, `_request_id`, reserved-position CAS) rather than introducing a second authority marker.

Published on PR #177:
- implementation commit `6aaab4e72144ad7fc4309f1054b4881187c2c22d`, `activation_schema_provenance.py` blob `83d790edbfdf0ac05c39f7f5e37d0e36453b3a29`;
- crash/concurrency-boundary regression commit/current head `3590acee6e42685524e59ce123767003cba32cc6`, test blob `fc51685da555306326e6313182bdf1c1d0a2ebd4`.

The regression models a crash immediately after the atomic SQLite commit: both exact DDL objects and exactly one PREPARED marker must already be durable; a different writer must fail under `PendingIntent`; explicit migration then resumes that same marker to CONFIRMED.

Executed a standalone file-backed SQLite visibility probe for the chosen transaction mechanism: before commit a concurrent reader observed `(DDL absent, marker absent)`; after commit it observed `(DDL present, marker PREPARED)`; it never observed DDL-present/marker-absent. This is mechanism evidence, not exact-branch GREEN.

Durable evidence: `research/2026-09-01-lab092-atomic-ddl-prepared-boundary.md`, main commit `fc1376a8f436e5b72d487231e59fa492567d29b8`; #176 comment `5486110457`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; atomic installation fix published, exact branch behavioral/full-suite execution pending.
- LAB-092 earlier classifier `py_compile`/standalone state-machine evidence retained. New standalone SQLite atomic-visibility probe PASS for the DDL+PREPARED commit boundary. Exact PR #177 regressions remain unexecuted because checkout transport still fails before code execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available, but no supported byte-preserving server-side patch-composition write is exposed.
- Direct git transport was probed again in this run and failed before repository execution with `Could not resolve host: github.com`.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft. The known DDL→marker admission gap now has a candidate atomic fix, but exact behavioral execution is still pending.
- Do not solve LAB-092 with unauthenticated local markers, marker confirmation before exact DDL, post-confirmation auto-repair, or any durable PREPARED-before-DDL state.
- Current GitHub metadata still requires explicit branch/base conflict reconciliation before integration of #175/#177.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable and exact source execution becomes available, execute PR #175 `test_activation_schema_installation_race.py` first on source blob `8140d6e1...`, then remaining LAB-090 gates; then execute all PR #177 provenance tests on head `3590acee...`, especially atomic boundary, unresolved activation, PREPARED recovery, deletion/mismatch, and legitimate legacy migration.

If execution remains unavailable, audit/tighten LAB-092 `_reservation_surface` construction against inherited LAB-081 initialization/type/runtime invariants and add a regression for stale runtime provider identity at the atomic migration boundary. Do not expand scope beyond this until that audit is complete.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; atomic installation source fix published; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; atomic DDL+PREPARED candidate published; exact regression gate and small reservation-surface audit pending.
