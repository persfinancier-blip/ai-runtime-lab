# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; atomic source fix head `d9a381dd4607a928cd1315adef6431e239995bc1`, `supported.py` blob `8140d6e180c3e97085830b872cea7d87f8433144`.
- LAB-092 / #176 is IN_PROGRESS on branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090. Latest head `5f6d2beda547d4395f7c149b7bd5bbf9ce05f3d9`; implementation commit remains `ce6fcbedeb838473d68071321df449d339ede290`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs and issue #176. LAB-086 remains first priority, but the current GitHub interface still exposes no supported byte-preserving patch-composition/write bridge. Manual/model reserialization of the 949-line security-critical `strict_fence.py` remains prohibited.

Re-probed exact source execution with a fresh git clone of PR #177; transport failed before repository execution with `Could not resolve host: github.com`. No branch-level GREEN is claimed.

Advanced the allowed LAB-092 fallback without changing LAB-090. Added `test_activation_schema_provenance_recovery.py` on PR #177, current blob `f7e69087525f74bc7ed2a8e1d6acbb8bf30b5b40`, branch commit `5f6d2beda547d4395f7c149b7bd5bbf9ce05f3d9`, covering:
- unmarked same-name mismatched activation trigger -> startup and explicit migration fail closed, no repair;
- completed provenance followed by same-name mismatched trigger -> startup and explicit migration fail closed, no repair;
- deterministic completion marker left PREPARED -> ordinary startup raises specifically `ActivationSchemaMigrationRequired` and leaves it PREPARED; only explicit migration may resume it to CONFIRMED.

Durable evidence: `research/2026-09-01-lab092-mismatched-ddl-and-prepared-recovery.md`, main commit `343dd73caca8351723f654f89c9641d7d7aedcaa`; #176 comment `5484728877`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; atomic installation fix published, exact branch behavioral/full-suite execution pending.
- LAB-092 authored implementation `py_compile` PASS from prior run. Standalone file-backed SQLite classifier probe produced expected `LEGACY_ABSENT`, `DDL_INSTALLED_UNMARKED`, `DDL_INSTALLED_PREPARED`, `COMPLETE`, and post-completion-deletion `FAIL_CLOSED` states. Current mismatch/PREPARED recovery regressions are published but not branch-executed because checkout transport still fails before code execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available, but no supported byte-preserving server-side patch-composition write is exposed.
- Direct git transport was probed again in this run and failed before repository execution with `Could not resolve host: github.com`.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact LAB-092 behavioral tests execute; authored regressions and mechanism-level probes are not branch-level GREEN.
- Do not solve LAB-092 with unauthenticated local markers, marker-before-DDL ordering, post-confirmation auto-repair, or broad exception assertions that can mask unrelated failures.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable and exact source execution becomes available, execute PR #175 `test_activation_schema_installation_race.py` first on source blob `8140d6e1...`, then the remaining LAB-090 activation restart/tamper/integration/downstream gates; then execute all PR #177 provenance regressions on exact published head.

If execution remains unavailable, continue LAB-092 on PR #177 without changing LAB-090: add a concurrent-writer explicit-migration regression, then audit/regress explicit migration with an unresolved LAB-090 activation record. Require fail-closed behavior and no provenance confirmation when LAB-090's trigger blocks the migration marker intent. Keep all claims below branch-level GREEN until exact published-head execution succeeds.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; atomic installation source fix published; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; explicit provenance candidate in draft PR #177; deletion/partial/mismatch/PREPARED recovery regressions published; exact behavioral gate plus concurrency/unresolved-activation regressions pending.
