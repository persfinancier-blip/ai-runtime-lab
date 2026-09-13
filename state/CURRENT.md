# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-099 fallback: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head `d810fae3b2c47d0f733bfb23d5cc1dcf4b20fcde`, based on PR #177.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open work; probed LAB-086 exact materialization first.

Current-run capability/evidence:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- no new LAB-086 behavioral/security/compile/conflict PASS and no LAB-099 repository RED/GREEN PASS is claimed.

Completed LAB-099 fallback slice:
- source-audited the pinned shared-anchor reserve/execute and historical durable-verification paths;
- confirmed `HistoricalSharedAnchorLedger.verify_durable()` requires a contiguous authenticated row history through the durable tail, so raw synthetic rows or merely setting `reserved_position=41` would fabricate history;
- added test-only `lab099_shared_anchor_prefix_witness.py` to PR #186;
- the witness installs the existing fixture-only provider-alpha g1..g8 history, starts g8 at position 0, executes 41 deterministic `archive_checkpoint` intents through `SupportedHistoricalSharedAnchorLedger.execute()`, then requires durable verification, tail=41, row count=41, zero PREPARED rows and authenticated provider position 41;
- prefix payloads are explicitly non-authoritative execution mechanics and do not derive LAB-099 PREPARED/CONFIRMED authority;
- local authored source passed `python -m py_compile`; local `git hash-object` `079d42b61836294d433170d4aace867e1c03b106` exactly matched the published GitHub blob.

Durable evidence:
- PR #186 branch commit `d810fae3b2c47d0f733bfb23d5cc1dcf4b20fcde`; prefix-witness blob `079d42b61836294d433170d4aace867e1c03b106`;
- research note `research/2026-09-13-lab099-legitimate-shared-anchor-prefix-witness.md`, main commit `ff7aa5f51f4858e80efa5db54d4690adab6b44ae`;
- #184 comment `5650694593`;
- PR #186 remains open/draft/mergeable with 24 commits and 16 changed files, all LAB-099 changes test-only.

## Known failures / blockers
- LAB-086 remains priority #1; complete real-ledger execution is unavailable in this run.
- PR #165 remains draft and must not be integrated without the exact gate and fresh conflict audit.
- PRs #172/#173/#175/#177/#186 remain draft until their retained exact gates execute.
- PR #186 is test-only staging; production `activation_reservation_provenance` is forbidden until actual executable RED is observed.
- historical synthetic CONFIRMED head `c0..df` remains non-authoritative.
- exact CONFIRMED bridge and dynamic PREPARED fixture remain intentionally distinct authority layers.
- deterministic execution-witness keys and prefix payloads are fixture mechanics only and must never become LAB-099 semantic authority.
- the legitimate prefix builder itself has only passed source compile/blob-identity checks; full import/execution is still unobserved because the exact repository closure is not locally materialized.

## Exact next action
LAB-086 first: probe once for a supported exact non-model materialization path for pinned executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize and hash-verify the manifest-listed closure plus all `test_*.py` and pinned LAB-085 helper; execute normal LAB-086 real-schema tests, the unsafe expected-failure seed separately, full compileall, then final security/reconciliation and current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no exact LAB-086 materialization path exists, stay test-only on PR #186: source-audit and, if mechanically clean, add one orchestration helper that composes the already-separated mechanisms without creating new authority: legitimate prefix positions 1..41 -> frozen `atomic_prepared_plan()` at position 42 -> existing provider increment/RECONCILE for the frozen request -> frozen `confirmed_event_plan()` -> persisted CONFIRMED verifier. It must require exact request id `shared-anchor:42:9fda50427f6b8a55b305cd4a8833413a1f20b349bc21332bfaf0eb4de7d01bdf`, stable receipt `ead923c6b9bcd68bc6e4276284fd72211544fcede9f06297b8bc074d898130b4`, and confirmed head `45c53da7909f826f6c8107fef542ba17bed551df8637f8a3185fe66a04410dda`, and refuse divergence rather than synthesize replacements. Execute persisted CONFIRMED end-to-end only if the complete exact import closure can be materialized; otherwise record the next missing prerequisite. Do not add production LAB-099 code.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178..185 / LAB-093..100 — design/source follow-ups with executable gates pending.
- #184 / LAB-099 — READY + isolated draft PR #186; semantic authority layers frozen; provider g1..g8 witness and legitimate shared-anchor prefix 1..41 are staged test-only; exact position-42 orchestration is the next safe fallback prerequisite before executable CONFIRMED evidence.
