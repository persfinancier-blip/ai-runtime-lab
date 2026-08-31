# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; atomic source fix head `d9a381dd4607a928cd1315adef6431e239995bc1`, `supported.py` blob `8140d6e180c3e97085830b872cea7d87f8433144`.
- LAB-092 / #176 is IN_PROGRESS on branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090. Current head `6244f5a43d7544b34c35f04f96b19fe2ca1dfd9d`; implementation commit remains `ce6fcbedeb838473d68071321df449d339ede290`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/PRs. LAB-086 remains first priority. The current GitHub interface still exposes normal Contents writes and exact ranged reads but no supported byte-preserving patch-composition operation; do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.

Re-probed exact source execution with a fresh git clone of PR #177; transport again failed before repository execution with `Could not resolve host: github.com`. No branch-level RED/GREEN is claimed.

Advanced the allowed LAB-092 fallback and found a concrete migration admission gap: current `migrate_activation_schema_v1()` commits inherited LAB-090 activation DDL before reserving the authenticated completion marker. In the observable DDL-committed / marker-ABSENT interval, with no unresolved activation, an unrelated legitimate shared-anchor writer can reserve first. A file-backed SQLite two-thread mechanism probe reproduced `admitted_before_marker=True`.

Published two regressions on PR #177:
- `test_activation_schema_migration_concurrency.py`, commit `b36b4a334dc1a8dea49342c758424ed3cc00a8ea`: deterministic pause after DDL commit/before marker reservation; desired contract forbids concurrent writer admission;
- `test_activation_schema_migration_unresolved_activation.py`, commit/current head `6244f5a43d7544b34c35f04f96b19fe2ca1dfd9d`: leaves a valid `SQL_COMMITTED` activation unresolved through a test-only no-recovery surface and requires LAB-090's trigger to block marker insertion with no provenance row created and activation still unresolved.

Durable evidence: `research/2026-09-01-lab092-ddl-to-marker-concurrency-gap.md`, main commit `9903f5d16342e321cccfcd2520fb63ddd1ba8c43`; #176 comment `5485477498`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; atomic installation fix published, exact branch behavioral/full-suite execution pending.
- LAB-092 implementation `py_compile` PASS from prior run. Standalone classifier probe produced expected `LEGACY_ABSENT`, `DDL_INSTALLED_UNMARKED`, `DDL_INSTALLED_PREPARED`, `COMPLETE`, and post-completion-deletion `FAIL_CLOSED`; new DDL→marker two-thread mechanism probe proves the admission gap exists. Published LAB-092 regressions remain unexecuted on exact branch bytes because checkout transport still fails before code execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available, but no supported byte-preserving server-side patch-composition write is exposed.
- Direct git transport was probed again in this run and failed before repository execution with `Could not resolve host: github.com`.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft. Current implementation now has a known DDL→marker writer-admission gap in addition to pending exact behavioral execution.
- Do not solve LAB-092 with unauthenticated local markers, marker confirmation before exact DDL, post-confirmation auto-repair, or a PREPARED-before-DDL rule that can launder local DB tamper into a fresh authenticated migration.
- Current GitHub PR metadata reports PR #175 and #177 `mergeable=false`; do not integrate either until their branch/base conflict state is explicitly reconciled in addition to the behavioral gates.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable and exact source execution becomes available, execute PR #175 `test_activation_schema_installation_race.py` first on source blob `8140d6e1...`, then remaining LAB-090 activation restart/tamper/integration/downstream gates; then execute all PR #177 provenance regressions on exact published head.

If execution remains unavailable, continue LAB-092 design/implementation without weakening LAB-090: make exact activation DDL installation and deterministic PREPARED migration-marker reservation become visible atomically under one SQLite writer transaction, then confirm the marker externally after commit. Reuse/refactor LAB-080 reservation semantics rather than duplicating authority logic blindly. Preserve `CONFIRMED marker + missing/mismatched DDL => fail closed`. Add crash-state regressions for the atomic DDL+PREPARED boundary before changing the implementation.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; atomic installation source fix published; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; explicit provenance candidate has known DDL→marker admission gap; concurrency and unresolved-activation regressions published; atomic DDL+PREPARED design/fix and exact behavioral gate pending.
