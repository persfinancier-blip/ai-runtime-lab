# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, base LAB-090.
- LAB-099 RED-intent staging: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, latest write commit `3d64249bdaf0c587e72096a751c3edbef971c3a5`, based on PR #177 branch.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open work plus PRs #165/#186; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive for the complete pinned LAB-086 closure is exposed;
- therefore no new LAB-086 behavioral/unsafe-seed/compileall/security/conflict PASS and no LAB-099 repository RED/GREEN PASS is claimed.

Completed LAB-099 fallback slice on draft PR #186:
- source-audited the pinned shared-anchor `RECONCILE` request/receipt formulas;
- added test-only `experiments/provider_generation_history/tests/lab099_confirmed_ledger_reference.py`;
- froze one exact CONFIRMED shared-anchor reference entry: provider `provider-alpha`, generation 8, predecessor 41, position 42;
- exact request id: `shared-anchor:42:9fda50427f6b8a55b305cd4a8833413a1f20b349bc21332bfaf0eb4de7d01bdf`;
- exact stable RECONCILE receipt: `ead923c6b9bcd68bc6e4276284fd72211544fcede9f06297b8bc074d898130b4`;
- exact `confirmed_head_digest(entry)`: `45c53da7909f826f6c8107fef542ba17bed551df8637f8a3185fe66a04410dda`;
- froze `LAB099_CONFIRMED_LEDGER_REFERENCE_BRIDGE_V1_FROZEN`: CONFIRMED provenance field 7 equals that authenticated ledger-entry digest directly; no second provenance-head transform;
- epoch mapping is predecessor epoch + 1; reference `7 -> 8`;
- bridged CONFIRMED canonical digest: `e7f7083876141f73cc7e8adc88b39c5e6da7f9c10a83433d2a067588c54ae157`;
- the prior `c0..df` field-7 value in the historical authority vector is explicitly synthetic/non-authoritative and must not be used by the executable CONFIRMED fixture layer.

Observed validation:
- local `python -m py_compile` for the new reference module: PASS;
- local byte/digest calculations for request id, receipt, confirmed-head and bridged CONFIRMED canonical digest: PASS;
- local `git hash-object` of exact authored module = `69b1bfeda67c43fbf2a7ed3361c08495a94a8a5e`, matching the published GitHub blob;
- PR #186 topology after write: ahead 20 / behind 0 relative to pinned PR #177; all 13 changed files remain under `experiments/provider_generation_history/tests/`.

Durable evidence:
- PR #186 branch commit `3d64249bdaf0c587e72096a751c3edbef971c3a5`;
- new reference blob `69b1bfeda67c43fbf2a7ed3361c08495a94a8a5e`;
- `research/2026-09-13-lab099-confirmed-ledger-reference-bridge.md` main commit `6d8f5c37f74fa7d2a0283a0b6d3a206bf72c4e79`;
- #184 comment `5649365280`.

## Known failures / blockers
- LAB-086 remains priority #1; exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Complete LAB-086 real-schema tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 is still open/draft and currently reports `mergeable=false`; do not infer cause or attempt integration before the exact gate and fresh conflict audit.
- Keep PRs #165/#172/#173/#175/#177/#186 draft until their retained exact gates execute.
- PR #186 remains RED-intent staging only; the complete branch cannot be imported/executed locally in this run.
- Historical synthetic CONFIRMED head `c0..df` must be superseded by the frozen bridged head in the executable CONFIRMED fixture/event layer, not silently reinterpreted.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- Whole-store rollback/deletion is not solved by another local table; LAB-099 composes with LAB-095/LAB-097 logical-database/provenance authority.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and pinned LAB-085 fixture helper; verify every file with `git hash-object` against pinned blobs before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no supported exact materialization path exists, continue only PR #186 test-owned LAB-099 work: add `confirmed_event_plan()` that uses `lab099_confirmed_ledger_reference.py` as the sole CONFIRMED head/receipt/epoch bridge; do not consume the historical synthetic `c0..df` head. Then add a non-discoverable persisted CONFIRMED RED-intent suite with isolated mutations for receipt binding, confirmed position, confirmed head and exact PREPARED-digest ancestry. Keep all work test-only. Do not add production `activation_reservation_provenance` until exact repository execution is available and an actual RED is observed.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178..185 / LAB-093..100 — design/source follow-ups with exact executable gates pending.
- #184 / LAB-099 — READY + isolated draft PR #186; PREPARED physical/storage/cross-binding and persisted CONFIRMED reauthentication layers published; exact CONFIRMED ledger-reference bridge is now frozen; `confirmed_event_plan()` + persisted CONFIRMED RED-intent is next fallback slice.
