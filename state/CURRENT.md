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
- direct local `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com` (exit 128);
- raw/archive download fallback was also unavailable through the supported web/download path;
- however, a new safe byte-exact connector-to-filesystem path was demonstrated: fetch an exact GitHub blob through the connector, write that returned UTF-8 content into an isolated execution tree, and accept it only when local `git hash-object` equals the frozen Git blob SHA;
- this transport was proven on all 18 frozen LAB-099 orchestration blobs: 18/18 local Git hashes matched exactly;
- therefore connector-based exact materialization is no longer categorically blocked and should be applied to the priority LAB-086 pinned snapshot before further LAB-099 production work;
- no new LAB-086 behavioral/security/compile/conflict PASS is claimed yet because its full pinned execution closure has not yet been materialized and executed.

Completed LAB-099 executable fallback slice:
- materialized all 18 files from `LAB099_EXACT_ORCHESTRATION_IMPORT_CLOSURE_V1_FROZEN` byte-exact, with every local `git hash-object` equal to the frozen manifest;
- `python -m compileall` over the exact closure returned 0;
- imported `lab099_confirmed_orchestration_witness`, validated its contract shape, and executed a fresh file-backed SQLite orchestration;
- the orchestration returned 0 with exact frozen request `shared-anchor:42:9fda50427f6b8a55b305cd4a8833413a1f20b349bc21332bfaf0eb4de7d01bdf`, receipt `ead923c6b9bcd68bc6e4276284fd72211544fcede9f06297b8bc074d898130b4`, confirmed position 42, and confirmed head `45c53da7909f826f6c8107fef542ba17bed551df8637f8a3185fe66a04410dda`; final `HistoricalSharedAnchorLedger.verify_durable()` succeeded inside the orchestration;
- then materialized exact PR #186 `red_intent_lab099_precursor_cutover.py` (blob `0a96b07196189add888df6e59ce5eb2f869138ef`) plus its exact LAB-092 dependency `activation_schema_provenance.py` (blob `396b67a46686f6df23584b1b366824c1b7ac1886`);
- explicit unittest execution produced the first observed LAB-099 production RED: 6 tests run / 6 failures / exit 1, all because production module `experiments.provider_generation_history.activation_reservation_provenance` does not yet exist;
- the old prohibition on beginning LAB-099 production solely because executable RED was unobserved is therefore removed, but priority remains LAB-086 and LAB-099 production authority must still be derived independently from test-only vectors/witnesses.

Durable evidence:
- `research/2026-09-13-lab099-byte-exact-closure-execution-red.md`, main commit `b303c3ec2c13e053bf877f5fda6a6657b0acba2b`;
- #163 comments include the current-run LAB-086 DNS/materialization observation;
- #184 comment `5652421646` records the 18/18 exact execution and observed six-case RED;
- PR #186 remains draft/test-only at head `766434563a5ad82a88156687c84de9c9e17b14c6`.

## Known failures / blockers
- LAB-086 remains priority #1; its exact complete real-ledger gate has not yet executed in this run.
- Direct clone/network materialization is still unavailable, but the GitHub connector + local `git hash-object` fallback is now a demonstrated safe exact-transfer path and must be tried for LAB-086 before declaring materialization blocked.
- PR #165 remains draft and must not be integrated without the exact gate and fresh conflict audit.
- PRs #172/#173/#175/#177/#186 remain draft until their retained exact gates execute.
- LAB-099 now has observed executable RED, but production `activation_reservation_provenance` must not import or treat test-only canonical vectors, deterministic witness keys, prefix payloads, or fixture mutation helpers as production authority.
- historical synthetic CONFIRMED head `c0..df` remains non-authoritative.
- exact CONFIRMED bridge and dynamic PREPARED fixture remain intentionally distinct authority layers.

## Exact next action
LAB-086 first. Use the newly demonstrated connector-to-filesystem exact-transfer method against pinned executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`: enumerate the exact LAB-086 execution closure from `research/2026-08-27-lab086-exact-gate-manifest.md`, including the manifest-listed implementation files, every relevant `test_*.py`, the pinned LAB-085 `experiments/anchor_attestation/tests/test_protocol.py` helper, and every transitive `experiments/**/protocol.py` dependency reached by those tests. Fetch each exact pinned blob through the GitHub connector, write it into an isolated local tree, and accept no file unless local `git hash-object` matches the pinned Git blob SHA. Only after the complete closure is byte-exact may the runtime execute the manifest gate: normal LAB-086 real-schema unittest path, unsafe expected-failure seed separately, discovery/full downstream helper path, full compileall, source audit for `*_for_test_only`, then final security/reconciliation and current-main conflict audit. Fix every observed blocker before changing PR #165 draft/merge status.

If a genuine connector/API inconsistency prevents completion of the LAB-086 pinned closure after reasonable per-file fallbacks, persist the exact missing path/blob instead of weakening the gate, then return to LAB-099. For LAB-099, source-audit/freeze the smallest production authority model required by the observed six-case RED, independently of `tests/lab099_*`, implement the minimum `activation_reservation_provenance` surface, and rerun the exact RED after each minimal slice so the next observed failure drives implementation.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; byte-exact connector fallback now demonstrated, exact complete real-ledger gate still pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178..185 / LAB-093..100 — design/source follow-ups with executable gates pending.
- #184 / LAB-099 — executable orchestration GREEN and first production RED observed; production implementation is now allowed by the RED gate but remains behind LAB-086 priority and must derive authority independently from test-only fixtures.
