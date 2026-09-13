# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-099 fallback: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head `57bee50daa9bdcf00f2620713acf0435bc96eae9`, based on PR #177.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; probed LAB-086 exact materialization first.

Current-run capability/evidence:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available, but no supported exact connector-to-local materialization path for the complete LAB-086 closure was observed;
- therefore no new LAB-086 behavioral/security/compile/conflict PASS and no LAB-099 repository RED/GREEN PASS is claimed.

Completed LAB-099 fallback slice:
- source-audited provider-history generation/transition verification and anchor-attestation increment/reconcile mechanics;
- proved the frozen historical receipt stable binding is independent of fixture key/signature/challenge/kind and hashes only provider id, generation, position and request id;
- added test-only non-authoritative `lab099_confirmed_execution_witness.py` to PR #186;
- witness deterministically constructs provider-alpha generations 1..8 with fixture-only keys, can install/verify that history through normal `DurableProviderHistory.rotate()`, instantiates g8 provider state at position 41, executes the frozen request through existing increment+RECONCILE mechanics, and requires exact equality to frozen receipt/head identities;
- local authored source passed `python -m py_compile`; local `git hash-object` `454e76cb3059353d041ba83f81dc11b9eec45b5c` exactly matched the published GitHub blob;
- independent local stable-receipt calculation reproduced `ead923c6b9bcd68bc6e4276284fd72211544fcede9f06297b8bc074d898130b4`.

New prerequisite discovered:
- provider execution mechanics are now witnessable without synthesizing LAB-099 semantic authority;
- however a full `HistoricalSharedAnchorLedger.verify_durable()` reference DB at predecessor position 41 also requires legitimate contiguous shared-anchor rows 1..41; setting only `shared_anchor_meta.reserved_position=41` would violate `len(rows) == reserved` and fabricate history.

Durable evidence:
- PR #186 branch commit `57bee50daa9bdcf00f2620713acf0435bc96eae9`; witness blob `454e76cb3059353d041ba83f81dc11b9eec45b5c`;
- research note `research/2026-09-13-lab099-confirmed-execution-witness.md`, main commit `79b4ff775d6881d1e61a022098f6d94e14367fb2`;
- #184 comment `5650179735`;
- PR #186 remains open/draft/mergeable, ahead 23 / behind 0 relative to pinned PR #177, exactly 15 changed files, all under `experiments/provider_generation_history/tests/`.

## Known failures / blockers
- LAB-086 remains priority #1; complete real-ledger execution is unavailable in this run.
- PR #165 remains draft and must not be integrated without the exact gate and fresh conflict audit.
- PRs #172/#173/#175/#177/#186 remain draft until their retained exact gates execute.
- PR #186 is test-only staging; production `activation_reservation_provenance` is forbidden until actual executable RED is observed.
- historical synthetic CONFIRMED head `c0..df` remains non-authoritative.
- exact CONFIRMED bridge and dynamic PREPARED fixture are intentionally not interchangeable.
- deterministic execution-witness keys are fixture mechanics only and must never become LAB-099 semantic authority.
- exact end-to-end CONFIRMED reference execution still lacks a legitimate contiguous shared-anchor prefix for positions 1..41.

## Exact next action
LAB-086 first: probe once for a supported exact non-model materialization path for pinned executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize and hash-verify the manifest-listed closure plus all `test_*.py` and pinned LAB-085 helper; execute normal LAB-086 real-schema tests, the unsafe expected-failure seed separately, full compileall, then final security/reconciliation and current-main conflict audit. Fix every observed blocker before changing draft/merge status.

If no exact LAB-086 materialization path exists, stay test-only on PR #186: source-audit a minimal **legitimate shared-anchor prefix builder** for positions 1..41 using the existing supported ledger execution path under the non-authoritative provider-alpha/g8 execution witness. Do not insert synthetic prefix rows or merely set the tail metadata. The builder must leave the provider and durable ledger both at exact position 41 with no PREPARED row, then allow the frozen LAB-099 PREPARED/CONFIRMED position-42 contract to reproduce exact request id `shared-anchor:42:9fda50427f6b8a55b305cd4a8833413a1f20b349bc21332bfaf0eb4de7d01bdf`, stable receipt `ead923c6b9bcd68bc6e4276284fd72211544fcede9f06297b8bc074d898130b4`, and confirmed head `45c53da7909f826f6c8107fef542ba17bed551df8637f8a3185fe66a04410dda`. Add code only if prefix generation remains mechanically separate from LAB-099 semantic authority. Execute persisted CONFIRMED contract only if the complete exact import closure can be materialized; otherwise record the next missing prerequisite. Do not add production LAB-099 code.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178..185 / LAB-093..100 — design/source follow-ups with executable gates pending.
- #184 / LAB-099 — READY + isolated draft PR #186; semantic authority layers frozen; non-authoritative g1..g8 provider execution witness now staged; legitimate shared-anchor prefix 1..41 is the next safe fallback prerequisite before exact seeded CONFIRMED execution.
