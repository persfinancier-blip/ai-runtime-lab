# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-099 fallback: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head `766434563a5ad82a88156687c84de9c9e17b14c6`, based on PR #177.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open work; kept LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- GitHub connector can read exact pinned blobs/trees;
- supported byte-preserving archive/raw transfer into the local execution filesystem was probed but unavailable in this runtime;
- therefore no new LAB-086 behavioral/security/compile/conflict PASS and no LAB-099 branch import/SQLite end-to-end PASS is claimed.

Completed LAB-099 fallback slice:
- source-audited the minimal exact import closure for `lab099_confirmed_orchestration_witness.py` at PR #186 head;
- froze `LAB099_EXACT_ORCHESTRATION_IMPORT_CLOSURE_V1_FROZEN` containing 18 exact Python paths/blob SHAs covering the orchestration helpers plus anchor-attestation/provider-history/shared-anchor substrate;
- recorded audited import edges and the exact executable procedure required on the first runtime that can materialize those bytes;
- no production LAB-099 code was added.

Durable evidence:
- `research/2026-09-13-lab099-exact-orchestration-import-closure.md`, main commit `5d1b1cbdc9175b1c01ff2720a7917c202356e92c`;
- #184 comment `5651348933`;
- PR #186 remains draft/test-only at head `766434563a5ad82a88156687c84de9c9e17b14c6`.

## Known failures / blockers
- LAB-086 remains priority #1; exact complete real-ledger execution is unavailable in this run.
- PR #165 remains draft and must not be integrated without the exact gate and fresh conflict audit.
- PRs #172/#173/#175/#177/#186 remain draft until their retained exact gates execute.
- PR #186 is test-only staging; production `activation_reservation_provenance` is forbidden until actual executable RED is observed.
- historical synthetic CONFIRMED head `c0..df` remains non-authoritative.
- exact CONFIRMED bridge and dynamic PREPARED fixture remain intentionally distinct authority layers.
- deterministic witness keys/prefix payloads are execution mechanics only and must never become LAB-099 semantic authority.
- exact LAB-099 orchestration closure is now frozen, but materialization/import/execution remains unobserved.

## Exact next action
LAB-086 first: probe once for a supported exact non-model materialization path for pinned executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize and hash-verify the manifest-listed closure plus all `test_*.py` and pinned LAB-085 helper; execute normal LAB-086 real-schema tests, unsafe expected-failure seed separately, full compileall, then final security/reconciliation and current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no exact LAB-086 materialization path exists, use `research/2026-09-13-lab099-exact-orchestration-import-closure.md` as the authoritative LAB-099 execution manifest. Materialize every listed blob exactly, verify all Git blob SHAs, run compileall, import `lab099_confirmed_orchestration_witness`, then execute a fresh file-backed SQLite `execute_frozen_confirmed_orchestration()` and require exact frozen request `shared-anchor:42:9fda50427f6b8a55b305cd4a8833413a1f20b349bc21332bfaf0eb4de7d01bdf`, receipt `ead923c6b9bcd68bc6e4276284fd72211544fcede9f06297b8bc074d898130b4`, position 42, confirmed head `45c53da7909f826f6c8107fef542ba17bed551df8637f8a3185fe66a04410dda`, and final durable verification. Do not add production LAB-099 code before observed executable RED.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178..185 / LAB-093..100 — design/source follow-ups with executable gates pending.
- #184 / LAB-099 — READY + isolated draft PR #186; exact orchestration import closure is frozen; byte-exact closure execution is the next safe prerequisite before any production implementation.
