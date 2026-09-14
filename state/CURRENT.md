# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 plus its composed LAB-096/#181 provider-history binding prerequisite is the permitted fallback. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095/#180 + LAB-096/#181 composition: branch `lab-095-database-identity-red-intent`, draft PR #187, current head `af0ed4cfafc830628ee80905ca2809158f546965`. Keep draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
LAB-086 direct execution was probed first. `git clone` again failed before repository execution with `Could not resolve host: github.com` / exit 128, so no LAB-086 PASS is claimed and the complete gate was not weakened.

The LAB-095/LAB-096 fallback then implemented the previously identified provider-history whole-object replacement fix on PR #187. `SupportedHistoricalSharedAnchorLedger` now construction-binds the exact `CoordinatorOnlyProviderHistory` instance into private `_provider_history`; the public `provider_history` alias remains readable for compatibility, while post-construction assignment to either `provider_history` or `_provider_history` raises `AttributeError`.

`test_database_path_binding.py` now contains a legitimate DB-B strategy replacement regression: construct the ledger/history on DB A, independently construct a legitimate history object on DB B, require public and private strategy replacement to fail, require the original DB-A strategy identity to remain installed, execute a supported intent, and require DB B to remain unmodified.

PR #187 commits for this slice: `2d2794f3a9703324f3bb7e91f94767ee467d19f5` (production binding) and `af0ed4cfafc830628ee80905ca2809158f546965` (regression). Authored `supported.py` compiled locally before publication; an isolated construction-bound strategy micro-regression passed public/private replacement rejection and original-object retention. The full repository regression is NOT yet counted GREEN because the exact branch closure is still unavailable in the executable filesystem.

Durable report: `research/2026-09-14-lab096-construction-bound-provider-history-strategy.md`, main commit `543ea7a924bdedd9a3edab49ac6061e53c15218f`.

Previously established evidence remains valid: LAB-086 authoritative complete-gate pin is `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; all eight focused LAB-095 manifest blobs have authoritative exact content known across runs; cross-generation COMPLETE reauth exact closure passed 1/1; object.__new__ binding exact regression passed 1/1; recovery/tamper behavior passed 6/6 previously with exact LAB-095 production/test blobs but protocol stubs.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted. Direct executable-runtime GitHub transport is blocked; no supported byte-preserving connector -> filesystem bridge is exposed in this run.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` is observed working.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 focused manifest has authoritative exact content known for all 8/8 files, but the complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- The specific LAB-096 whole-object replacement path is now patched on PR #187, but exact repository execution and downstream LAB-081/LAB-090/LAB-092 compatibility are still pending. The public read-only alias still exposes the underlying history object, so LAB-093/094 least-capability/bootstrap concerns remain separate follow-ups.
- LAB-090/LAB-095 `supported.py` conflict resolution remains security-sensitive: preserve LAB-090 activation semantics, `CanonicalDatabaseBinding`, and the new construction-bound provider-history strategy.

## Exact next action
LAB-086 first: execute the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` if a newly exposed supported byte-preserving materialization path can place exact repository bytes into an executable filesystem. Do not weaken or manually reserialize the large security-critical closure.

If no such LAB-086 bridge exists, continue PR #187 from head `af0ed4cfafc830628ee80905ca2809158f546965`: audit every inherited/internal access to `provider_history` and determine whether the read-only compatibility alias can remain without exposing an authority-changing surface. Do not fold LAB-093/094 into this patch unless a concrete bypass requires it.

If a safe byte-preserving execution bridge becomes available, reconstruct the exact PR #187 head, run `compileall`, execute `test_database_path_binding.py` including the legitimate DB-B strategy replacement case, then run the retained no-stub LAB-095 recovery/confirmed-finalize/locked-custody suite under `TMPDIR=/dev/shm`. After that run LAB-081 and conflict-resolved LAB-090/LAB-092 downstream gates while preserving activation fencing + canonical DB binding + construction-bound history strategy.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; path binding implemented; LAB-096 whole-object strategy replacement now patched on PR #187, exact/downstream gates pending.
- #181 / LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; production construction-bound strategy + legitimate DB-B regression committed, exact execution pending.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091, #176 / LAB-092 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
