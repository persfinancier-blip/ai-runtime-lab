# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 plus its composed LAB-096/#181 provider-history binding prerequisite is the permitted fallback. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095/#180 + LAB-096/#181 composition: branch `lab-095-database-identity-red-intent`, draft PR #187, current head includes `0a14492c280c0fa6ed60ae20c8ea9f04144ade7a`. Keep draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
LAB-086 was probed first. Direct `git clone` again failed before repository execution with `Could not resolve host: github.com` / exit 128. No LAB-086 PASS is claimed and the complete gate was not weakened.

The LAB-096 public live-strategy alias capability leak was then patched on draft PR #187. `HistoricalSharedAnchorLedger` now has an internal `_history()` accessor; all inspected security-sensitive history/head/receipt/rotation/verification call sites dispatch through it. Supported ledgers resolve `_history()` to the construction-bound private `_provider_history` strategy, while the LAB-081 base class retains its historical public strategy behavior.

`SupportedHistoricalSharedAnchorLedger.provider_history` now returns a separate immutable `ProviderHistoryInspectionView` rather than the live `CoordinatorOnlyProviderHistory`. The public view exposes read-only `current()`, `verify_durable()`, `load_receipt()`, `verify_receipt()`, `require_current()`, and pure `make_transition()`. It intentionally omits `rotate`, locked helpers, `_con`, `store_receipt`, `path`, and `bootstrap`. Supported receipt paths were also moved to `_history()`.

The delegated-ledger regression `test_provider_history_capability_surface.py` was strengthened to require those capabilities to be absent, to reject attribute assignment on the view, and to preserve durable/runtime generation after an attempted locked rotation using a separately obtained ledger connection.

Branch commits from this run:
- `939c0f5de2ea0787165e5816c4f1bba2c31f02ed` — internal history accessor/refactor.
- `be494e1afa5f09cc4e04b5d133e44a43bd27dbb3` — least-capability inspection view.
- `0a14492c280c0fa6ed60ae20c8ea9f04144ade7a` — strengthened capability-surface regression.

Durable report: `research/2026-09-14-lab096-least-capability-provider-history-view.md`, main commit `bb3f3e361730fb8af43caffd83bcff40d589c117`.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted. Direct executable-runtime GitHub transport is blocked; no supported byte-preserving connector -> filesystem bridge is exposed in this run.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` is observed working.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 focused manifest has authoritative exact content known for all 8/8 files, but the complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 source-level whole-object replacement and public live-strategy alias leaks are now patched on PR #187, but exact repository behavioral GREEN and downstream LAB-081/LAB-090/LAB-092 gates remain pending.
- Python reflection can still intentionally pierce name-mangled/private implementation state; this patch enforces the supported/public API capability boundary, not process-grade isolation.
- LAB-090/LAB-095 `supported.py` conflict resolution remains security-sensitive: preserve LAB-090 activation semantics, `CanonicalDatabaseBinding`, construction-bound provider-history strategy, and the least-capability public history view.

## Exact next action
LAB-086 first: execute the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` if a newly exposed supported byte-preserving materialization path can place exact repository bytes into an executable filesystem. Do not weaken or manually reserialize the large security-critical closure.

If no such LAB-086 bridge exists, continue auditing PR #187 from current head. Inspect the exact branch diff for any remaining direct `self.provider_history` use in supported/internal security-sensitive paths and any public route that recovers receipt mutation, connection, locked verification, or rotation authority. Fix concrete bypasses only; do not fold LAB-093 caller-owned external-provider capability work into this patch unless required by an observed bypass.

If a safe byte-preserving execution bridge becomes available, materialize exact PR #187 head, run `compileall`, execute `test_provider_history_capability_surface.py` and `test_database_path_binding.py`, then the retained no-stub LAB-095 recovery/confirmed-finalize/locked-custody suite under `TMPDIR=/dev/shm`. After that run LAB-081 and conflict-resolved LAB-090/LAB-092 downstream gates while preserving activation fencing + canonical DB binding + construction-bound history strategy + least-capability public history inspection.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; path binding implemented; exact/downstream gates pending.
- #181 / LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; strategy replacement + public live-strategy alias patched; exact/downstream validation pending.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091, #176 / LAB-092 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
