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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and PR #186; probed LAB-086 exact materialization first.

Current-run capability/evidence:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available, but no supported exact connector-to-local materialization path for the complete LAB-086 closure was observed;
- therefore no new LAB-086 behavioral/security/compile/conflict PASS and no LAB-099 repository RED/GREEN PASS is claimed.

Completed LAB-099 fallback slice:
- source-audited the minimal exact seeded SQLite/reference fixture required for the frozen `provider-alpha` / generation 8 / `41 -> 42` CONFIRMED bridge;
- inspected pinned provider-history, shared-anchor and anchor-attestation source contracts;
- provider-history `verify_durable()` requires an exact bootstrap plus complete g1..g8 descriptor/key/transition chain; a lone g8 row is not a valid exact seed;
- CONFIRMED reauthentication requires provider-side retained `_request_results[request_id]` state and a matching current generation verification key; the frozen stable receipt cannot reconstruct either;
- repository code search found no existing default-branch `provider-alpha` fixture/authority chain to reuse;
- therefore no exact seeded reference DB was added: generating keys/history/request-result evidence inside the seed now would synthesize execution authority rather than derive it from the frozen bridge.

Decision:
- freeze the missing layer separately as an explicitly test-only, non-authoritative execution witness before persisted CONFIRMED execution;
- that witness may supply deterministic provider-alpha g1..g8 fixture keys/transitions and generation-8 provider request-result mechanics only if it reproduces the already frozen request id, positions, stable receipt and confirmed head exactly;
- it must never become a second LAB-099 semantic authority source.

Durable evidence:
- research note `research/2026-09-13-lab099-confirmed-seed-prerequisite-audit.md`, main commit `9c024c3ba1a5042ca632c3e8f12f8c79ea554487`;
- #184 comment `5649893814`;
- PR #186 remains open/draft/mergeable and unchanged: head `4d8db37bfa2818931a20337934bd3501a76d6ba9`, ahead 22 / behind 0 relative to pinned PR #177, exactly 14 changed files, all under `experiments/provider_generation_history/tests/`.

## Known failures / blockers
- LAB-086 remains priority #1; complete real-ledger execution is unavailable in this run.
- PR #165 remains draft and must not be integrated without the exact gate and fresh conflict audit.
- PRs #172/#173/#175/#177/#186 remain draft until their retained exact gates execute.
- PR #186 is test-only staging; production `activation_reservation_provenance` is forbidden until actual executable RED is observed.
- historical synthetic CONFIRMED head `c0..df` remains non-authoritative.
- exact CONFIRMED bridge and dynamic PREPARED fixture are intentionally not interchangeable.
- frozen CONFIRMED semantic vectors do not currently include the executable provider-history key chain or provider-side request-result state needed for authenticated end-to-end reauthentication.

## Exact next action
LAB-086 first: probe once for a supported exact non-model materialization path for pinned executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize and hash-verify the manifest-listed closure plus all `test_*.py` and pinned LAB-085 helper; execute normal LAB-086 real-schema tests, the unsafe expected-failure seed separately, full compileall, then final security/reconciliation and current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no exact LAB-086 materialization path exists, stay test-only on PR #186: define and source-audit a minimal **execution-witness contract** separate from LAB-099 semantic authority. It must deterministically construct provider-alpha generations 1..8 through the existing `GenerationDescriptor`/transition contract, instantiate generation-8 provider state at position 41, execute the already frozen request id through the existing provider increment/reconcile mechanics to position 42, and assert the resulting stable receipt equals `ead923c6b9bcd68bc6e4276284fd72211544fcede9f06297b8bc074d898130b4` and the existing confirmed-entry digest remains `45c53da7909f826f6c8107fef542ba17bed551df8637f8a3185fe66a04410dda`. Add code only if this witness is mechanically separated from semantic authority and introduces no generalized production behavior. Execute persisted CONFIRMED contract only if the complete exact import closure can be materialized; otherwise record the next missing prerequisite. Do not add production LAB-099 code.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178..185 / LAB-093..100 — design/source follow-ups with executable gates pending.
- #184 / LAB-099 — READY + isolated draft PR #186; PREPARED/CONFIRMED semantic authority layers frozen; test-only execution witness is the next safe fallback prerequisite before exact seeded CONFIRMED execution.
