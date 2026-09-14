# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity plus lifetime physical DB binding.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, head `835a81914c5234e68ef436e30c9837331d262432`. Keep draft.
- LAB-096: #181 — now confirmed as a composed prerequisite for LAB-095 closure because the provider-history strategy slot itself remains replaceable.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
LAB-086 direct execution was probed first in this run. `git clone` again failed before repository execution with `Could not resolve host: github.com` / exit 128, so no LAB-086 PASS is claimed and the complete gate was not weakened.

Connector-side LAB-095 acceptance audit then found a concrete remaining DB-divergence gap. PR #187 makes the existing ledger/history `path` construction-bound, but `SupportedHistoricalSharedAnchorLedger` still stores its trusted history strategy in public mutable `self.provider_history`. Replacing that whole object with a legitimate `CoordinatorOnlyProviderHistory` bound to DB B bypasses the original object's path binding. Ordinary history methods then reopen DB B, while locked history helpers invoked by reserve/rotate/verify consume the ledger's already-open DB-A connection. This creates split authority without rebinding either object's individual `path` field.

This is the concrete overlap with LAB-096/#181. Because #180 explicitly requires preventing ledger/history DB divergence in supported composition, LAB-096's construction-bound history strategy must be composed before LAB-095 can close; it is not merely an optional follow-up.

Durable report: `research/2026-09-14-lab095-provider-history-replacement-acceptance-gap.md`, main commit `e072955f4b054211870b8822ab66f05f10af7e60`. Issue #180 comment `5663826108`; issue #181 comment `5663828180`; PR #187 comment `5663829952`.

Previously established evidence remains valid: LAB-086 authoritative complete-gate pin is `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; all eight focused LAB-095 manifest blobs have authoritative exact content known across runs; cross-generation COMPLETE reauth exact closure passed 1/1; object.__new__ binding exact regression passed 1/1; recovery/tamper behavior passed 6/6 previously with exact LAB-095 production/test blobs but protocol stubs.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted. Direct executable-runtime GitHub transport is blocked; no supported byte-preserving connector -> filesystem bridge is exposed in this run.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` is observed working.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 focused manifest has authoritative exact content known for all 8/8 files, but the complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-095 path binding alone does not prevent DB-A/DB-B divergence while `ledger.provider_history` remains replaceable. LAB-096/#181 must provide a construction-bound private history strategy (or an equivalent invariant-preserving design) and all internal history operations must use that one object.
- LAB-090/LAB-095 `supported.py` conflict resolution remains security-sensitive: preserve LAB-090 activation semantics and `CanonicalDatabaseBinding` on both supported ledger/history MROs.

## Exact next action
LAB-086 first: execute the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` if a newly exposed supported byte-preserving materialization path can place exact repository bytes into an executable filesystem. Do not weaken or manually reserialize the large security-critical closure.

If no such LAB-086 bridge exists, continue LAB-095/LAB-096 composition: define the smallest construction-bound private provider-history strategy that prevents whole-object replacement while preserving existing supported introspection and LAB-090/LAB-092 behavior. Add a regression that constructs on DB A, substitutes a legitimate history object bound to DB B, and proves the replacement cannot affect reserve/execute/rotate/verify or migration authority. Do not solve only inside migration helpers; normal ledger operations also dispatch through the strategy object.

If a safe byte-preserving execution bridge becomes available, reconstruct all eight focused LAB-095 files from PR #187 head `835a81914c5234e68ef436e30c9837331d262432`, require same-run 8/8 `git hash-object` matches, run `compileall`, and execute recovery/confirmed-finalize/locked-custody tests with no protocol stubs under `TMPDIR=/dev/shm`. Then execute DB-A -> DB-B plus the new provider-history replacement regression and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates on a conflict-resolved tree that preserves both LAB-090 activation fencing and LAB-095/LAB-096 construction-bound authority.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; path binding implemented, but provider-history whole-object replacement remains an acceptance blocker through #181.
- #181 / LAB-096 — READY/COMPOSE WITH LAB-095; make the trusted provider-history strategy construction-bound and private/least-capability.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091, #176 / LAB-092 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
