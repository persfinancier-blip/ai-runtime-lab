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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/PRs; probed LAB-086 exact materialization first.

Current-run LAB-086 capability/evidence:
- pinned executable commit `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` is readable through the GitHub connector;
- no supported byte-preserving path in this runtime materialized the complete exact manifest/dependency closure into the local filesystem for execution;
- no new LAB-086 behavioral/security/compile/conflict PASS is claimed.

Completed LAB-099 fallback slice:
- added test-only `lab099_confirmed_orchestration_witness.py` to PR #186;
- it composes only already-frozen mechanisms: legitimate shared-anchor prefix 1..41 -> atomic frozen PREPARED at position 42 -> existing provider increment/RECONCILE using the frozen request -> existing provider-history receipt persistence -> frozen CONFIRMED plan -> persisted CONFIRMED verifier -> final historical-ledger durable verification;
- it refuses divergence from frozen request `shared-anchor:42:9fda50427f6b8a55b305cd4a8833413a1f20b349bc21332bfaf0eb4de7d01bdf`, receipt `ead923c6b9bcd68bc6e4276284fd72211544fcede9f06297b8bc074d898130b4`, position 42 and confirmed head `45c53da7909f826f6c8107fef542ba17bed551df8637f8a3185fe66a04410dda`;
- audit found the first authored helper reauthenticated but did not persist the position-42 historical receipt; corrected it to use existing `provider_history.store_receipt()` and added final `ledger.verify_durable()`;
- local authored helper passed `python -m py_compile`; local Git blob `71a50df5b5d8c3cece33274d5263f1c4fe0ec27a` exactly matched the published GitHub content blob;
- full exact branch import/orchestration execution remains unobserved; no LAB-099 repository RED/GREEN PASS is claimed.

Durable evidence:
- PR #186 corrected branch commit `766434563a5ad82a88156687c84de9c9e17b14c6`; orchestration blob `71a50df5b5d8c3cece33274d5263f1c4fe0ec27a`;
- research note `research/2026-09-13-lab099-confirmed-orchestration-witness.md`, main commit `76c826f9bfedcc736c72fff0e6eecd29228700f2`;
- #184 comment `5651109289`;
- PR #186 remains open/draft/mergeable, ahead 26 / behind 0 from pinned PR #177, 17 changed files, all under `experiments/provider_generation_history/tests/`.

## Known failures / blockers
- LAB-086 remains priority #1; exact complete real-ledger execution is unavailable in this run.
- PR #165 remains draft and must not be integrated without the exact gate and fresh conflict audit.
- PRs #172/#173/#175/#177/#186 remain draft until their retained exact gates execute.
- PR #186 is test-only staging; production `activation_reservation_provenance` is forbidden until actual executable RED is observed.
- historical synthetic CONFIRMED head `c0..df` remains non-authoritative.
- exact CONFIRMED bridge and dynamic PREPARED fixture remain intentionally distinct authority layers.
- deterministic witness keys/prefix payloads are execution mechanics only and must never become LAB-099 semantic authority.
- the complete orchestration helper has only passed authored-source compile/blob-identity checks; exact dependency-closure import/execution is still unobserved.

## Exact next action
LAB-086 first: probe once for a supported exact non-model materialization path for pinned executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize and hash-verify the manifest-listed closure plus all `test_*.py` and pinned LAB-085 helper; execute normal LAB-086 real-schema tests, unsafe expected-failure seed separately, full compileall, then final security/reconciliation and current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no exact LAB-086 materialization path exists, stay test-only on PR #186. Attempt exact byte-verified materialization of the minimal import closure for `lab099_confirmed_orchestration_witness.py`; if the complete closure is available, execute `execute_frozen_confirmed_orchestration()` against a fresh file-backed SQLite DB and require exact frozen request/receipt/head plus final durable verification. If closure materialization is still unavailable, source-audit and persist the exact minimal closure manifest so the next executable runtime can reproduce the gate. Do not add production LAB-099 code.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178..185 / LAB-093..100 — design/source follow-ups with executable gates pending.
- #184 / LAB-099 — READY + isolated draft PR #186; frozen position-42 orchestration is staged test-only; exact dependency-closure execution is the next safe prerequisite before any production implementation.
