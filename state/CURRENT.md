# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes. LAB-099 is the permitted fallback when the byte-exact LAB-086 execution closure cannot be materialized safely in the current runtime.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-099 fallback: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, now contains first production slice commit `d40aea8c48efe587b273650a3756ca782ba81472`, based on PR #177.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and PR state; resumed LAB-086 first.

### LAB-086 current-run evidence
- Exact executable pin remains `1f90830fca21e2f43fc241012cdd34fd187ba96d`; `1fa85a0...` is notes/evidence containing the manifest, not the executable snapshot.
- Reconstructed the pinned LAB-086 test inventory from Contents API: 29 ordinary `test_*.py` files plus `unsafe_legacy_promotion_expected_failure.py`.
- Fresh direct clone again failed before repository execution with `Could not resolve host: github.com` (exit 128).
- Connector reads exact pinned UTF-8 blobs and SHAs, including `strict_fence.py=d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` and NULL-receipt regression `a66d9ddef2d4a41db937222b875f697c7ff74b75`.
- Concrete current-runtime blocker: no supported programmatic byte-stream bridge exists from connector responses into the local execution filesystem. Manual transcription of the 50+ implementation/test/transitive closure would violate the byte-exact gate, so it was rejected. No new LAB-086 full unittest/security/compile/conflict PASS is claimed.
- Durable evidence: `research/2026-09-13-lab086-materialization-blocker-and-lab099-first-production-slice.md`, main commit `9e40de69f5e10b39bc095b09260f05cd28dbd3ed`; #163 comment `5652416167`.

### LAB-099 fallback completed slice
Prior retained evidence remains: 18-file frozen orchestration closure was byte-exact, compileall + fresh file-backed SQLite orchestration were GREEN, then exact six-case RED ran 6/6 failures solely because production `activation_reservation_provenance` was absent.

This run published the first production slice:
- branch commit `d40aea8c48efe587b273650a3756ca782ba81472`;
- new production file `experiments/provider_generation_history/activation_reservation_provenance.py`;
- GitHub blob `1e642016c7f3fec258f0e2b7671b763d758f2ff4`, exactly equal to local `git hash-object`; local `py_compile` PASS;
- production imports no `tests/lab099_*` authority;
- implements exact precursor relation identity/DDL digest checking, cutover evidence/cardinality and digest->intent cross-binding, shared-anchor marker checks, read-only classifier, and fail-closed startup gate;
- migration/resume API exists but intentionally remains fail-closed until authenticated PREPARED/CONFIRMED authority is derived from inherited LAB-092 state and existing production shared-anchor/provider-history primitives;
- narrow exact-source SQLite classifier execution with inert import stubs produced `ABSENT`, `ORPHAN_UNAUTHENTICATED_SCHEMA`, and `CORRUPT_RELATION` for the expected three cases. This is not the full six-case repository GREEN.
- #184 comment `5652416957`; PR #186 body updated to reflect production status.

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted because byte-exact connector->filesystem materialization is not available in this run; PR #165 remains draft.
- Do not manually reconstruct/reformat LAB-086 source as a substitute for exact Git blob identity.
- PRs #172/#173/#175/#177/#186 remain draft until their retained exact gates execute.
- LAB-099 migration/resume production authority is intentionally incomplete; test-only vectors, deterministic witness keys, prefix payloads, and historical synthetic `c0..df` head are not production authority.

## Exact next action
LAB-086 first on the next run: probe whether a supported byte-preserving connector/file materialization path exists. If it does, reconstruct only executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, require local `git hash-object` match for every manifest/test/helper/transitive file, then run all normal LAB-086 tests, unsafe expected-failure separately, downstream/helper tests, compileall, `*_for_test_only` source audit, security/reconciliation audit, and current-main conflict audit.

If that exact materialization path is still unavailable, do not repeat manual source-transfer attempts. Resume LAB-099 production: source-audit LAB-092 durable completion/provenance and existing shared-anchor/provider-history primitives, then implement the smallest independent authenticated PREPARED migration authority in `activation_reservation_provenance.py`. Do not import or derive production authority from `tests/lab099_*`. After publication, rerun the exact six-case RED as soon as byte-exact executable closure is available; fix only observed failures, including any fixture-side gaps that were previously masked by the missing module.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178..185 / LAB-093..100 — design/source follow-ups with executable gates pending.
- #184 / LAB-099 — first production classifier/startup slice published; authenticated migration/resume next after LAB-086 probe.
