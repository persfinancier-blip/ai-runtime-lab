# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, base LAB-090.
- LAB-099 RED-intent staging: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, latest write commit `b6f40cb6b76e84828dae9f25f51b995ac62a4c71`, based on PR #177 branch.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/PR #186; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive for the complete pinned LAB-086 closure is exposed;
- therefore no new LAB-086 behavioral/unsafe-seed/compileall/security/conflict PASS and no LAB-099 repository RED/GREEN PASS is claimed.

Completed LAB-099 source-audit + test-owned CONFIRMED read-back boundary on PR #186:
- audited pinned `experiments/shared_anchor_intent_ledger/protocol.py`: CONFIRMED authority already requires externally reauthenticated provider `RECONCILE`, exact provider generation, position/request identity and a stable 64-hex `receipt_binding`; LAB-099 must reuse this authority instead of adding another receipt mechanism;
- added `experiments/provider_generation_history/tests/lab099_confirmed_fixture_row_verifier.py`;
- verifier resolves exactly one materialization + matching shared-anchor row, requires CONFIRMED, preserves exact PREPARED ancestry through the existing PREPARED cross-binding oracle, requires externally supplied confirmed position/head authority, reauthenticates the stored receipt using existing RECONCILE semantics, and rejects head/event mismatch;
- narrow test-only tamper hooks cover receipt binding, position/predecessor and PREPARED digest ancestry;
- latest verifier blob: `b1324194ef0f9c251ccdc747394d63b7b0a9d68a`.

Audit finding / new frozen boundary:
- existing frozen CONFIRMED authority vector contains independent `RESULTING_PROVENANCE_HEAD_DIGEST = c0..df` and epoch `8`;
- `lab099_cutover_storage_reference.confirmed_head_digest(entry)` instead derives a digest from a concrete CONFIRMED shared-anchor entry including `receipt_binding`;
- no frozen reference CONFIRMED shared-anchor entry/receipt vector currently proves those two authority surfaces are the same, and `lab099_precursor_fixture_vectors.py` still has no `confirmed_event_plan()`;
- therefore `LAB099_CONFIRMED_LEDGER_REFERENCE_BRIDGE_REQUIRED_V1` is frozen: do not invent receipt/head/epoch bytes merely to make CONFIRMED fixtures executable.

Durable evidence:
- PR #186 verifier update commit `b6f40cb6b76e84828dae9f25f51b995ac62a4c71`;
- verifier blob `b1324194ef0f9c251ccdc747394d63b7b0a9d68a`;
- PR topology after write: ahead 19 / behind 0 relative to pinned PR #177 head; changed files remain entirely under `experiments/provider_generation_history/tests/`;
- `research/2026-09-13-lab099-confirmed-receipt-head-binding-audit.md` main commit `3e2b7bfc6478a512ad0df8c122e12296cae2bd6a`;
- #184 comment `5649057919`.

## Known failures / blockers
- LAB-086 remains priority #1; exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read/write pinned source but cannot byte-exactly materialize the whole LAB-086 closure into the executor in this run.
- Complete LAB-086 real-schema tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177/#186 draft until their retained exact gates execute.
- PR #186 remains RED-intent staging only; the new CONFIRMED verifier was not locally imported/compiled/executed in this run.
- The exact CONFIRMED ledger-entry/receipt -> frozen CONFIRMED provenance-head/epoch bridge is not yet frozen; `confirmed_event_plan()` must remain absent until that authority mapping is explicit.
- LAB-090..100 source/design evidence does not substitute for executable RED/GREEN proof.
- Whole-store rollback/deletion is not solved by another local table; LAB-099 composes with LAB-095/LAB-097 logical-database/provenance authority and must not claim SQLite can prove total deletion of its own history.
- Do not auto-upgrade existing unauthenticated LAB-090 rows; do not call provider prepare from an unauthenticated local recovery row; do not treat PR #177's LAB-092 V1 migration marker as proof of precursor governance.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against pinned blobs before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no supported exact materialization path exists, continue only PR #186 test-owned LAB-099 work: freeze one exact reference CONFIRMED shared-anchor `LedgerEntry` including a stable receipt vector derived under the existing RECONCILE receipt formula; freeze `confirmed_head_digest(entry)` and explicitly decide whether frozen CONFIRMED event field 7 equals that digest directly or uses a separate deterministic provenance-head transform; freeze the epoch mapping. Only after that bridge is byte-exact and independently self-checking, add `confirmed_event_plan()` plus a non-discoverable persisted CONFIRMED RED-intent suite with isolated receipt-binding, confirmed position/head and exact PREPARED-digest ancestry mutations. Do not add production `activation_reservation_provenance` until the exact repository RED-intent suite can execute and an actual RED is observed.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement/execute frozen LAB-090..100 RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending; V1 migration marker does not cover precursor semantics.
- #178 / LAB-093 — READY/design-frozen; exact RED/GREEN pending.
- #179..182 / LAB-094..097 — READY/design-frozen; exact executable gates pending.
- #183 / LAB-098 — READY; exact RED/GREEN pending.
- #184 / LAB-099 — READY + isolated RED-intent draft PR #186; PREPARED physical/storage/cross-binding layers plus persisted CONFIRMED reauthentication verifier are published; exact CONFIRMED ledger-reference -> provenance-head/epoch bridge is the next fallback slice.
- #185 / LAB-100 — READY/design-frozen; exact executable gates pending.
