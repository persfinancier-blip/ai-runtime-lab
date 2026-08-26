# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `95fa5da3c457e3431cd596ec969d5939b0a1d925`; mergeable=false; full current-head LAB-080→086 real-ledger execution gate remains outstanding.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current PR #173 HEAD `57648107966baba58fccbc4191cb9bb401aba7d6`, mergeable=true, draft.

## Last completed step

Re-read AGENTS.md, CURRENT and SELF_RESUME, re-inspected PR #165/#173 and resumed LAB-086 first. The exact full LAB-080→086 dependency closure was still not safely reconstructed in this runtime, so no new LAB-086 PASS or merge claim was made.

Per the recorded fallback, audited LAB-091 operation-scoped concurrency. Found a real fail-closed convergence bug: two identical workers can share the same exact request and authenticated provider receipt, but if one commits `PREPARED→CONFIRMED` first, the loser previously observed `current != entry` and raised `IntentSubstitution` instead of converging on the durable winner.

Published additive candidate `SupportedConvergentOperationScopedAsymmetricSharedAnchorLedger`. `_commit_confirmation()` now accepts an already-CONFIRMED winner only when exact request identity and exact authenticated receipt binding match; a different request or receipt remains fail-closed. The first writer still uses the one-shot `intent-confirm` permit; a loser performs no second mutation.

Published/exact evidence:
- `convergent_operation_scoped.py` blob `84a84df633fbaaca7f424f4db5bd3fd20403263b`;
- byte-aligned focused regression `test_confirmation_convergence.py` blob `faae1a75d5448737f51c850d4cbec289e83c4697`;
- focused harness actually executed **4/4 PASS**: normal confirm, identical-worker convergence, receipt substitution rejection, request substitution rejection;
- research note `research/2026-08-26-lab091-identical-worker-confirmation-convergence.md` published at PR HEAD `57648107966baba58fccbc4191cb9bb401aba7d6`.

This 4/4 result is focused evidence only, not the final LAB-080/LAB-082 concurrent-worker/restart/UNKNOWN gate.

## Evidence retained

- LAB-086 lower-stack exact evidence remains LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as expected.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-087 is merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 reference layer exact 11/11 PASS + compileall; unsafe raw-DML seed failed as intended.
- LAB-091 one-shot permit primitive exact 6/6 PASS + compileall.
- LAB-091 full mutable-row guards exact 12/12 PASS including legacy-surface persistence.
- LAB-091 identical-worker confirmation convergence focused exact-byte candidate: 4/4 PASS.

## Known blockers / constraints

- LAB-086 remains first priority. Merge gate is exact current-head execution on one LAB-080→086 closure: own/lower cardinality + migration + suffix + final-supported/security suites, unsafe seed, compileall and final audit. PR #165 reports mergeable=false; do not reconcile/integrate before that gate is clean.
- Direct shell GitHub transport is not assumed; connector reconstruction works but full closure assembly remains expensive.
- LAB-091 `operation_scoped_integration.py` plus the new convergence candidate still need exact real LAB-080/LAB-082 execution: restart, real concurrent workers, crash rollback, timeout/UNKNOWN reconciliation and LAB-087 restricted-worker composition.
- The convergence wrapper is additive/focused; do not treat it as the final supported surface until the real-stack gate validates it and alternate/legacy surfaces are re-audited.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: connector-reconstruct exact current PR #165 `migration_guard.py`, `suffix.py`, `final_supported.py` and their real-schema tests on the proven LAB-080→085 closure; execute own/lower cardinality, migration, suffix, final-supported, cross-binding/history, inherited/direct-surface, strict-fence/thaw, restart/concurrency tests; then unsafe seed + full compileall + final audit.
2. If that exact closure remains tool-limited, continue LAB-091 from PR #173: run the new convergence surface against real LAB-080/LAB-082 with two actual worker processes/threads sharing one intent/request, proving exactly one durable confirmation and identical receipt convergence.
3. Add exact restart, crash rollback, timeout-after-commit/UNKNOWN reconciliation and LAB-087 restricted-worker composition tests. Keep PR #173 draft until that complete gate is clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; full current-head real-ledger execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; one-shot primitive/guards exact-tested, legacy downgrade fixed, focused identical-worker convergence fixed, but real-stack restart/concurrency/crash/UNKNOWN/LAB-087 gate remains.
