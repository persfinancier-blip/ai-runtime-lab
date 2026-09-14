# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 plus its composed LAB-096/#181 provider-history binding prerequisite is the permitted fallback. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095/#180 + LAB-096/#181 composition: branch `lab-095-database-identity-red-intent`, draft PR #187, current head `c3ce17f160ad157213fc931bd4fe1fec290353e5`. Keep draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
LAB-086 direct execution was probed first. `git clone` again failed before repository execution with `Could not resolve host: github.com` / exit 128, so no LAB-086 PASS is claimed and the complete gate was not weakened.

The LAB-095/LAB-096 fallback then audited every currently visible authority-changing surface exposed through the new construction-bound provider-history strategy. A concrete remaining LAB-096 bypass was found: `SupportedHistoricalSharedAnchorLedger.provider_history` still returns the exact live `CoordinatorOnlyProviderHistory`. Its public `rotate()` is blocked, but inherited `_rotate_locked()` remains reachable. A caller delegated only the supported ledger can combine `ledger.provider_history._rotate_locked(...)` with `ledger._con()` and bypass `rotate_provider()` coordinator checks.

A regression-first contract was added on PR #187: `experiments/provider_generation_history/tests/test_provider_history_capability_surface.py`, branch commit `c3ce17f160ad157213fc931bd4fe1fec290353e5`. It requires the public alias to be unable to drive locked rotation and requires durable/runtime generation to remain unchanged. The authored test file passed local `py_compile`; exact repository RED execution is NOT claimed because the branch closure is still unavailable byte-for-byte in the executable filesystem.

Durable report: `research/2026-09-14-lab096-public-history-alias-capability-leak.md`, main commit `3c4bfb8f055efb2702be627c4845fb0ff4ff0a06`.

Previously established evidence remains valid: LAB-086 authoritative complete-gate pin is `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; all eight focused LAB-095 manifest blobs have authoritative exact content known across runs; cross-generation COMPLETE reauth exact closure passed 1/1; object.__new__ binding exact regression passed 1/1; recovery/tamper behavior passed 6/6 previously with exact LAB-095 production/test blobs but protocol stubs. The earlier whole-object DB-B provider-history replacement path remains patched on PR #187.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted. Direct executable-runtime GitHub transport is blocked; no supported byte-preserving connector -> filesystem bridge is exposed in this run.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` is observed working.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 focused manifest has authoritative exact content known for all 8/8 files, but the complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 whole-object strategy replacement is patched, but the public `provider_history` compatibility alias still leaks the live strategy's `_rotate_locked()` capability and therefore remains an acceptance blocker.
- LAB-090/LAB-095 `supported.py` conflict resolution remains security-sensitive: preserve LAB-090 activation semantics, `CanonicalDatabaseBinding`, construction-bound provider-history strategy, and the eventual least-capability public history view.

## Exact next action
LAB-086 first: execute the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` if a newly exposed supported byte-preserving materialization path can place exact repository bytes into an executable filesystem. Do not weaken or manually reserialize the large security-critical closure.

If no such LAB-086 bridge exists, continue PR #187 from head `c3ce17f160ad157213fc931bd4fe1fec290353e5`: refactor provider-history access so ledger internals use the private construction-bound strategy while public `provider_history` exposes only a least-capability read-only inspection surface. Because inherited `HistoricalSharedAnchorLedger` methods currently dispatch through `self.provider_history`, prefer a small internal-access helper/refactor in `integration.py` over a superficial wrapper that still exposes mutation helpers. Then update the new regression to GREEN by construction; do not fold LAB-093 caller-owned external-provider capability work into this patch unless a concrete bypass requires it.

If a safe byte-preserving execution bridge becomes available, reconstruct the exact PR #187 head, run `compileall`, execute `test_provider_history_capability_surface.py`, `test_database_path_binding.py`, then run the retained no-stub LAB-095 recovery/confirmed-finalize/locked-custody suite under `TMPDIR=/dev/shm`. After that run LAB-081 and conflict-resolved LAB-090/LAB-092 downstream gates while preserving activation fencing + canonical DB binding + construction-bound history strategy + least-capability public history inspection.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; path binding implemented; exact/downstream gates pending.
- #181 / LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; whole-object replacement patched; public live-strategy alias capability leak now has committed RED regression and requires production least-capability refactor.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091, #176 / LAB-092 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
