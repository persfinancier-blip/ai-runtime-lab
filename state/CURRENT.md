# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity plus lifetime physical DB binding.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, current head `b1bfd7d54b568d3c3f1a935945550499e505fa05`, mergeable=true at last check. Keep draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, and inspected active PRs. LAB-086 was re-probed first: direct clone again failed before repository execution with `Could not resolve host: github.com` / exit 128. No LAB-086 gate was weakened and no new LAB-086 PASS is claimed.

### LAB-095 malformed anchor relation classifier hardening
A fail-closed audit found that public `database_identity.classify_identity_custody()` still returned `ABSENT` when custody was absent but `shared_anchor_intents` existed as a same-name non-table relation such as a VIEW. That malformed authority-bearing relation must not be indistinguishable from genuine legacy absence.

Fixed on PR #187:
- no custody + no anchor relation -> `ABSENT`;
- no custody + exact anchor table with no LAB-095 identity intent -> `ABSENT`;
- no custody + exact anchor table containing the LAB-095 identity intent -> `CORRUPT`;
- no custody + same-name non-table anchor relation -> `CORRUPT`.

Production commit `eb7ddca749eaa92f08af0211a23d2484b6644883`, blob `bac58a48c576001370144cc10cfab8e0cfd129e3`.
Regression commit/head `b1bfd7d54b568d3c3f1a935945550499e505fa05`, blob `4cfd6f6f8902cde415d86e37a3a25c1a7fdf960a`.

Executed a narrow local file-backed SQLite semantic probe for the exact new condition: genuine legacy absence -> `ABSENT`; same-name `shared_anchor_intents` VIEW -> `CORRUPT`; 2/2 PASS. This is narrow semantic evidence only, not exact-repository/downstream GREEN.

Durable report: `research/2026-09-13-lab095-malformed-anchor-relation-classifier-fail-closed.md`, main commit `0fd65da68e1bdd509195dd3d221940297ff80fe5`; #180 comment `5655854969`.

Earlier LAB-095 production remains on PR #187: logical identity/custody classifier, explicit CSPRNG/BEGIN IMMEDIATE migration/recovery, same-request reconciliation, under-lock full provider-history verification, local confirmed finalization, construction-bound physical path binding with DB-A -> DB-B regression, and committed crash/concurrent/legacy recovery regressions.

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted because shell git transport cannot resolve `github.com`; do not manually reconstruct the 50+ file closure or weaken byte-exact evidence requirements.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 full DB-A/B regression and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates remain unexecuted.
- LAB-095 crash/concurrent/legacy repository regressions are committed but not exact-closure executed.
- LAB-090/LAB-095 `supported.py` conflict resolution is security-sensitive: binding MRO must not be dropped.
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
- #180 / LAB-095 — IN_PROGRESS on draft PR #187; malformed same-name anchor relation now fails closed; next is exact recovery/path-binding/downstream execution closure.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups with executable gates pending.
- #184 / LAB-099 — classifier/startup slice published; PREPARED authority waits on LAB-095 completion.
