# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; atomic source fix head `d9a381dd4607a928cd1315adef6431e239995bc1`, `supported.py` blob `8140d6e180c3e97085830b872cea7d87f8433144`.
- LAB-092 / #176 is now IN_PROGRESS on branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090. Candidate head `ce6fcbedeb838473d68071321df449d339ede290`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. LAB-086 remains first priority, but no supported byte-preserving patch-composition/write bridge is exposed. Manual/model reserialization of the 949-line security-critical `strict_fence.py` remains prohibited.

Advanced the explicitly allowed LAB-092 fallback without changing LAB-090. Created branch `lab-092-activation-schema-provenance` from exact LAB-090 head `d9a381dd...`. Published regressions first at commit `5dc92792fd3dc6bcbd5cec14c8b2b6d1cf5f6bd1`, then implementation at `ce6fcbedeb838473d68071321df449d339ede290`. Opened draft PR #177 against `lab-090-provider-activation-fencing`.

LAB-092 candidate introduces `ProvenancedHistoricalSharedAnchorLedger` with explicit `migrate_activation_schema_v1()`. Contract is DDL-first using inherited LAB-090 atomic canonical table+trigger installation, then one deterministic authenticated shared-anchor `migration` completion intent. Ordinary startup requires exact DDL + CONFIRMED marker and re-authenticates that marker. Legacy absent DDL and exact DDL with absent/PREPARED marker are recoverable only through explicit migration. Any partial/mismatched DDL, especially PREPARED/CONFIRMED marker plus missing/mismatched activation objects, fails closed and is never automatically repaired.

Durable evidence: `research/2026-08-31-lab092-explicit-activation-schema-provenance-slice.md`, main commit `fea65ac697b6e1dc61abb69a0b5ebd396b4088d9`; #176 comment `5483311593`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; atomic installation fix published, exact branch behavioral/full-suite execution pending.
- LAB-092 authored implementation `py_compile` PASS in this run. Standalone file-backed SQLite classifier probe produced expected `LEGACY_ABSENT`, `DDL_INSTALLED_UNMARKED`, `DDL_INSTALLED_PREPARED`, `COMPLETE`, and post-completion-deletion `FAIL_CLOSED` states. Exact branch unit tests are not yet GREEN because repository checkout transport failed before execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available, but no supported byte-preserving server-side patch-composition write is exposed.
- Direct git transport was probed again in this run and failed before repository execution with `Could not resolve host: github.com`.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact LAB-092 behavioral tests execute; mechanism-level classifier evidence is not branch-level GREEN.
- Do not solve LAB-092 with unauthenticated local markers, marker-before-DDL ordering, or post-confirmation auto-repair.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable and exact source execution becomes available, execute PR #175 `test_activation_schema_installation_race.py` first on source blob `8140d6e1...`, then the remaining LAB-090 activation restart/tamper/integration/downstream gates.

If execution remains unavailable, continue LAB-092 on PR #177 with the remaining regression matrix without changing LAB-090: add trigger-only deletion after confirmed migration; partial/mismatched DDL with absent/PREPARED marker; PREPARED marker recovery; and a concurrent-writer explicit-migration test. Audit whether explicit migration can coexist safely with any unresolved LAB-090 activation record. Keep all claims below branch-level GREEN until exact published-head execution succeeds.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; atomic installation source fix published; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; isolated explicit provenance candidate in draft PR #177; exact behavioral gate and remaining regressions pending.
