# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity plus lifetime physical DB binding.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, current head `0fc0b5233607254424ec833476b0a1e077a4ff9c`, mergeable=true at last check. Keep draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, and inspected active PR #187. LAB-086 was re-probed first: direct clone again failed before repository execution with `Could not resolve host: github.com` / exit 128. No LAB-086 gate was weakened and no new LAB-086 PASS is claimed.

### LAB-095 public orphan-intent classifier consistency fix
The locked migration classifier had already been hardened so zero custody plus an existing exact LAB-095 `IDENTITY_INTENT_ID` is `CORRUPT`, but public read-only `database_identity.classify_identity_custody()` still returned `ABSENT` before checking the persisted intent.

Fixed on PR #187:
- zero custody rows + orphan PREPARED identity intent -> `CORRUPT`;
- zero custody rows + orphan CONFIRMED identity intent -> `CORRUPT`;
- orphan identity intent with no custody relation -> `CORRUPT`;
- genuine zero-custody/no-identity-intent remains `ABSENT`.

Production commit `c521e0f8cf49040faf2caac5e8a13d65cb4afea0`, blob `13d4b8cfb056d28969252e28905e9d20a30cb3c2`.
Regression file final commit `0fc0b5233607254424ec833476b0a1e077a4ff9c`, blob `86b4f19450c7486d5ba5a1b869c918c2a24ebbb1`.

Executed focused local SQLite semantic probe for those four states: 4/4 PASS; probe source also passed `py_compile`. This is narrow semantic evidence only. The exact repository regression/downstream suite is not claimed GREEN because the dependency closure remains unavailable through shell network transport.

Durable report: `research/2026-09-13-lab095-public-classifier-orphan-intent-fix.md`, main commit `c425230ccbabb16cbf4997606fb57dea9c14f885`; #180 comment `5655511043`.

Earlier LAB-095 production remains on PR #187: logical identity/custody classifier, explicit CSPRNG/BEGIN IMMEDIATE migration/recovery, same-request reconciliation, under-lock full provider-history verification, local confirmed finalization, construction-bound physical path binding with DB-A -> DB-B regression, and committed crash/concurrent/legacy recovery regressions.

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted because shell git transport cannot resolve `github.com`; do not manually reconstruct the 50+ file closure or weaken byte-exact evidence requirements.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 full DB-A/B regression and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates remain unexecuted.
- LAB-095 crash/concurrent/legacy repository regressions are committed but not exact-closure executed.
- LAB-090/LAB-095 supported.py conflict resolution is security-sensitive: binding MRO must not be dropped.
- LAB-094 bootstrap authority and LAB-096 provider-history strategy authority remain distinct follow-ups.
- LAB-099 migration/resume must not derive authority from `tests/lab095_*` or LAB-099 fixtures.

## Exact next action
LAB-086 first: re-probe for a supported byte-preserving materialization path. If available, reconstruct only executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, require local `git hash-object` match for every manifest/test/helper/transitive file, then run the full retained LAB-086 gate including unsafe expected-failure separately, compileall, security/reconciliation, and current-main conflict audit.

If exact LAB-086 materialization is still unavailable, continue LAB-095 on PR #187:
1. execute the already-committed crash-before-commit, partial-state, concurrent-installer, and legacy-prefix migration regressions on the smallest byte-exact closure that can be safely materialized; require one nonce/request and deterministic same-request recovery;
2. execute `test_database_path_binding.py` and LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates when exact closure is available;
3. run a fresh compare/conflict audit against current main and retained LAB-090 PR #175 before any integration; preserve `CanonicalDatabaseBinding` on both supported ledger/history MROs;
4. only after LAB-095 completion return to LAB-099 authenticated PREPARED authority.

Never use deterministic test vectors, caller-supplied nonce/digest, filesystem path hashes, or a same-DB self-asserted UUID as production authority.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #180 / LAB-095 — IN_PROGRESS on draft PR #187; public/locked orphan-intent classifiers now consistent; next is exact recovery/path-binding/downstream execution closure.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups with executable gates pending.
- #184 / LAB-099 — classifier/startup slice published; PREPARED authority waits on LAB-095 completion.
