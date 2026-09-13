# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-099 fallback: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head `4d8db37bfa2818931a20337934bd3501a76d6ba9`, based on PR #177.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open work and PR #186; probed LAB-086 materialization first.

Current-run capability/evidence:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available, but no supported exact connector-to-local materialization path for the complete LAB-086 closure was observed;
- therefore no new LAB-086 behavioral/security/compile/conflict PASS and no LAB-099 repository RED/GREEN PASS is claimed.

Completed LAB-099 fallback slice on PR #186:
- updated test-only `lab099_precursor_fixture_vectors.py` with `confirmed_event_plan()`;
- the plan uses `lab099_confirmed_ledger_reference.py` as the sole CONFIRMED receipt/head/epoch bridge;
- it accepts only frozen PREPARED digest `77ffdf5f657510a285d75e866d3418a85d1aeb0ca0f2c830617c850a5277b53e`;
- it updates PREPARED->CONFIRMED only when every frozen authority-relevant shared-anchor field plus matching cutover materialization still matches; adapter `expected_rowcount=1` semantics make stale/substituted state roll back;
- it deliberately refuses arbitrary sibling PREPARED digests rather than synthesizing receipt/head/epoch authority;
- added non-discoverable `red_intent_lab099_confirmed_row_cross_binding.py` freezing persisted negative cases for receipt binding, confirmed position, external confirmed-head authority and PREPARED-digest ancestry;
- locally authored versions of both changed/new files passed `python -m py_compile` before publication; exact published branch bytes were not imported/executed.

Audit finding retained:
- the frozen CONFIRMED bridge is one exact provider/tail reference (`provider-alpha`, generation 8, predecessor 41, position 42), while `atomic_prepared_plan()` intentionally derives provider/tail dynamically from the fixture database;
- do not silently generalize the exact bridge. A broader executable fixture requires a separately authenticated derivation contract or an exact seeded reference database.

Durable evidence:
- PR #186 commits `8d628b3c799e071171265e2b0386679a1a8f6746` and `4d8db37bfa2818931a20337934bd3501a76d6ba9`;
- updated fixture-vector blob `73406169990849327774fc46682747a14222bd9d`;
- PR #186 topology: ahead 22 / behind 0 relative to pinned PR #177; exactly 14 changed files, all under `experiments/provider_generation_history/tests/`; PR remains open/draft/mergeable;
- research note `research/2026-09-13-lab099-confirmed-event-plan-and-persisted-tamper-contract.md`, main commit `71d9bf21175c8ca85f4c3fbfe7874f91c9849495`;
- #184 comment `5649652394`.

## Known failures / blockers
- LAB-086 remains priority #1; complete real-ledger execution is unavailable in this run.
- PR #165 remains draft and must not be integrated without the exact gate and fresh conflict audit.
- PRs #172/#173/#175/#177/#186 remain draft until their retained exact gates execute.
- PR #186 is test-only staging; production `activation_reservation_provenance` is forbidden until actual executable RED is observed.
- historical synthetic CONFIRMED head `c0..df` remains non-authoritative.
- exact CONFIRMED bridge and dynamic PREPARED fixture are intentionally not interchangeable.

## Exact next action
LAB-086 first: probe once for a supported exact non-model materialization path for pinned executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize and hash-verify the manifest-listed closure plus all `test_*.py` and pinned LAB-085 helper; execute normal LAB-086 real-schema tests, the unsafe expected-failure seed separately, full compileall, then final security/reconciliation and current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no exact LAB-086 materialization path exists, stay test-only on PR #186: source-audit the minimal exact seeded SQLite/reference fixture needed to make the frozen provider-alpha/g8/41->42 CONFIRMED bridge mechanically executable end-to-end without adapting or synthesizing authority. Add that exact seed only if every provider-generation/shared-anchor prerequisite can be derived from existing frozen source contracts. Then wire `confirmed_event_plan()` through the fixture adapter and execute the persisted CONFIRMED contract only if the complete exact import closure can be materialized. Otherwise record the missing prerequisite; do not add production LAB-099 code.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178..185 / LAB-093..100 — design/source follow-ups with executable gates pending.
- #184 / LAB-099 — READY + isolated draft PR #186; PREPARED and CONFIRMED test authority layers frozen; exact seeded CONFIRMED fixture execution is the next safe fallback slice.
