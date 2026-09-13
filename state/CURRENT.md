# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity plus lifetime physical DB binding.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, current head `74d4acf0a7fb819cef574c841cdf9d7ee31d2476`, mergeable=true at last check. Keep draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues/PRs, and re-probed LAB-086 first. Direct clone again failed before repository execution with `Could not resolve host: github.com` / exit 128. No LAB-086 gate was weakened and no new LAB-086 PASS is claimed.

### LAB-095 under-lock full-history fix
Closed the identified migration TOCTOU on draft PR #187.

`prepare_database_identity()` now:
- acquires `BEGIN IMMEDIATE`;
- invokes the existing full `history._verify_durable_locked(q)` on that SAME connection before any custody DDL/DML, nonce generation, shared-anchor reservation, or tail mutation;
- requires locked verified `(provider_id, generation)` to match both the pre-lock durable current descriptor and runtime ledger authority;
- sources the PREPARED reservation provider fields from the locked verified descriptor.

This also moves `install_custody_schema()` behind full under-lock verification, so already-corrupt provider history leaves zero LAB-095 migration mutation.

Published production blob: `eef3277def1443ea880e64240ef314f731825a98`.
The existing migration regression fake was aligned with `_verify_durable_locked()`; branch head is `74d4acf0a7fb819cef574c841cdf9d7ee31d2476`.

Focused file-backed SQLite semantic execution against the exact published migration module plus minimal dependency stubs: 4/4 PASS:
1. corrupt under-lock full verifier -> exception, zero shared-anchor rows, no custody table persisted;
2. PREPARED retry -> same nonce/request reused;
3. provider-head race between precheck and writer lock -> rejected before custody creation;
4. externally CONFIRMED restart -> same custody finalized locally.

This is focused semantic evidence only; complete repository/downstream GREEN is NOT claimed.

Durable report: `research/2026-09-13-lab095-under-lock-history-verification-fix.md`, main commit `9fb64fec7fb831a95c74b312919aab07ae4e4b87`; #180 comment `5654823742`.

Earlier LAB-095 production remains on PR #187: logical identity/custody classifier, explicit CSPRNG/BEGIN IMMEDIATE migration/recovery, same-request reconciliation, local confirmed finalization, and construction-bound physical path binding with DB-A -> DB-B regression committed.

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted because shell git transport cannot resolve `github.com`; do not manually reconstruct the 50+ file closure or weaken byte-exact evidence requirements.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 full DB-A/B regression and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates remain unexecuted.
- LAB-095 under-lock fix is published and focused-semantically tested, but exact repository RED/GREEN remains unexecuted because the full closure is not safely materialized.
- LAB-095 still needs crash-before-commit, partial-state, concurrent-installer, and legacy-history migration regressions.
- LAB-090/LAB-095 supported.py conflict resolution is security-sensitive: binding MRO must not be dropped.
- LAB-094 bootstrap authority and LAB-096 provider-history strategy authority remain distinct follow-ups.
- LAB-099 migration/resume must not derive authority from `tests/lab095_*` or LAB-099 fixtures.

## Exact next action
LAB-086 first: re-probe for a supported byte-preserving materialization path. If available, reconstruct only executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, require local `git hash-object` match for every manifest/test/helper/transitive file, then run the full retained LAB-086 gate including unsafe expected-failure separately, compileall, security/reconciliation, and current-main conflict audit.

If exact LAB-086 materialization is still unavailable, continue LAB-095 on PR #187:
1. add and execute focused regressions for crash-before-commit, partial-state, concurrent-installer, and legacy-history migration; require zero duplicate nonce/request and deterministic same-request recovery;
2. execute the committed under-lock RED plus existing migration tests on the smallest exact closure that can be safely materialized; do not claim broader GREEN;
3. execute `test_database_path_binding.py` and LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates when exact closure is available;
4. run a fresh compare/conflict audit against current main and retained LAB-090 PR #175 before any integration; preserve `CanonicalDatabaseBinding` on both supported ledger/history MROs;
5. only after LAB-095 completion return to LAB-099 authenticated PREPARED authority.

Never use deterministic test vectors, caller-supplied nonce/digest, filesystem path hashes, or a same-DB self-asserted UUID as production authority.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #180 / LAB-095 — IN_PROGRESS on draft PR #187; under-lock full-history fix published; next is crash/partial/concurrent/legacy migration regression closure.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups with executable gates pending.
- #184 / LAB-099 — classifier/startup slice published; PREPARED authority waits on LAB-095 completion.
