# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; atomic source fix head `d9a381dd4607a928cd1315adef6431e239995bc1`, `supported.py` blob `8140d6e180c3e97085830b872cea7d87f8433144`.
- LAB-092 / #176 is IN_PROGRESS on branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090. Current head `30b0ecfd92d15b84ee5565a92cb4304b581f1348`; current provenance blob `46b8edc72d76921d638c4efad35cba16777a8064`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and PR #177. LAB-086 remains first priority. Current GitHub operations still expose normal Contents reads/writes but no supported byte-preserving patch-composition operation; do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.

Re-probed exact source execution with a fresh clone of `lab-092-activation-schema-provenance`; transport again failed before repository execution with `Could not resolve host: github.com`. No branch-level RED/GREEN is claimed.

Advanced the allowed LAB-092 fallback. Exact activation DDL installation and deterministic PREPARED migration-marker reservation now occur in one SQLite `BEGIN IMMEDIATE` transaction, are re-read before one commit, and are externally confirmed only after that commit. Published implementation commit `6aaab4e72144ad7fc4309f1054b4881187c2c22d`; crash/concurrency-boundary regression commit `3590acee6e42685524e59ce123767003cba32cc6`.

A follow-up reservation-surface audit found and fixed two authority ambiguities in commit/current head `30b0ecfd92d15b84ee5565a92cb4304b581f1348`: `_reservation_surface` now requires exact `AttestedCatchup`, matching the supported historical ledger, and `_classify()` now fails closed when the shared-anchor ledger itself is absent instead of treating that as a legitimate activation-schema legacy state. LAB-092 must migrate an existing LAB-080/081 authority surface, not bootstrap one incidentally.

Executed standalone file-backed SQLite visibility probe: before atomic commit a concurrent reader observed `(DDL absent, marker absent)`; after commit it observed `(DDL present, marker PREPARED)`; it never observed DDL-present/marker-absent. This validates the SQLite visibility mechanism only, not exact branch behavior.

Durable evidence: `research/2026-09-01-lab092-atomic-ddl-prepared-boundary.md`, latest main commit `ea32192978567e5db208d5e14734d48e8b4d56f9`; #176 comment `5486110457`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; atomic installation fix published, exact branch behavioral/full-suite execution pending.
- LAB-092 earlier classifier `py_compile`/standalone state-machine evidence retained. New standalone atomic-visibility probe PASS; exact PR #177 regressions remain unexecuted because checkout transport still fails before code execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available, but no supported byte-preserving server-side patch-composition write is exposed.
- Direct git transport failed again before repository execution with `Could not resolve host: github.com`.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft. Atomic DDL+PREPARED candidate and reservation-surface hardening are published, but exact behavioral execution is still pending.
- Do not solve LAB-092 with unauthenticated local markers, marker confirmation before exact DDL, post-confirmation auto-repair, or any durable PREPARED-before-DDL state.
- Explicit branch/base conflict reconciliation is required before integration of #175/#177.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable and exact source execution becomes available, execute PR #175 `test_activation_schema_installation_race.py` first on source blob `8140d6e1...`, then remaining LAB-090 gates; then execute all PR #177 provenance tests on head `30b0ecfd...`, especially atomic boundary, unresolved activation, PREPARED recovery, deletion/mismatch, and legitimate legacy migration.

If execution remains unavailable, add a LAB-092 stale-runtime-provider regression at the atomic migration boundary. Required outcome: fail closed before DDL+marker commit, leaving the legitimate legacy state unchanged. Then audit whether `CoordinatorOnlyProviderHistory` construction performs any undesired initialization before the atomic migration lock; if so, replace it with a non-mutating verified history view rather than weakening migration preconditions.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; atomic installation source fix published; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; atomic DDL+PREPARED candidate and reservation-surface hardening published; stale-runtime regression plus exact regression gate pending.
