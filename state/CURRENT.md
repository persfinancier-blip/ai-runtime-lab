# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity plus lifetime physical DB binding.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, head `835a81914c5234e68ef436e30c9837331d262432`. Keep draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
Mandatory LAB-086 probe was executed first. Ordinary direct Git again failed before repository execution because `github.com` could not resolve. A stronger diagnostic supplied current public A records explicitly: `github.com -> 20.200.245.247` via `git http.curloptResolve`, and `raw.githubusercontent.com -> 185.199.111.133` via `curl --resolve`. Both TCP/443 connections were refused immediately before content transfer. The current executable-runtime blocker is therefore stronger than DNS alone; direct GitHub egress is unavailable even with explicit name resolution. No byte-exact LAB-086 requirement was weakened and no new complete-gate PASS is claimed. The authoritative complete-gate pin remains `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`.

Permitted LAB-095 fallback performed a fresh static/security audit of the committed DB-A -> DB-B lifetime-binding regression on PR #187. The regression preserves a superficially matching generation-2 head in DB B while corrupting its provider-transition continuity, requires public/private rebinding attempts on both ledger and provider history to fail, then proves supported execution remains on DB A only. Composition audit confirmed the ledger retains `CanonicalDatabaseBinding` transitively through `HistoricalSharedAnchorLedger -> SupportedSharedAnchorLedger`, while `CoordinatorOnlyProviderHistory` independently binds its canonical path. No new path-binding defect was identified statically. This is not behavioral GREEN.

Durable report: `research/2026-09-14-lab086-direct-ip-egress-probe-and-lab095-binding-audit.md`, main commit `f1616f9ea93cc42202d746d140ab88025d3f68cc`.

Previously established evidence remains valid: all eight focused LAB-095 manifest blobs have authoritative exact content known across runs; cross-generation COMPLETE reauth exact closure passed 1/1; object.__new__ binding exact regression passed 1/1; recovery/tamper behavior passed 6/6 previously with exact LAB-095 production/test blobs but protocol stubs.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted. Direct executable-runtime GitHub transport is blocked at both local DNS and direct TCP/443 even when current A records are supplied explicitly.
- No supported automatic byte-preserving connector -> executable-filesystem bulk mount is currently exposed in this run.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` is observed working.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 focused manifest has authoritative exact content known for all 8/8 files, but the complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-090/LAB-095 `supported.py` conflict resolution is security-sensitive: preserve `CanonicalDatabaseBinding` on both supported ledger/history MROs.

## Exact next action
LAB-086 first: attempt the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` if a new supported byte-preserving materialization path is available. Do not spend repeated runs treating DNS alone as the blocker; direct TCP/443 refusal has now been demonstrated.

If direct transport remains unavailable, probe for any newly exposed supported connector/file materialization path that can preserve exact bytes into `/dev/shm`. If one exists, reconstruct all eight focused LAB-095 files from PR #187 head `835a81914c5234e68ef436e30c9837331d262432`, require same-run 8/8 `git hash-object` matches, run `compileall`, and execute the recovery/confirmed-finalize/locked-custody suite with no protocol stubs under `TMPDIR=/dev/shm`. Then execute the full DB-A -> DB-B regression and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates plus a fresh conflict/security audit.

If no safe byte-preserving execution bridge is exposed, continue only with auditable connector-side research/static security work and record the exact blocker; do not fabricate executable evidence or manually reserialize large security-critical sources as a substitute for byte-exact materialization.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; 8 focused manifest blobs have exact authoritative content established across runs; same-run 8/8 no-stub reconstruction and behavioral execution pending; DB-A -> DB-B regression statically audited clean.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091, #176 / LAB-092 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
