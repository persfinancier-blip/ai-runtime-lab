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
Mandatory LAB-086 probe was executed first. Direct shell Git materialization again failed before repository execution with `Could not resolve host: github.com`, exit 128. No byte-exact LAB-086 requirement was weakened and no new complete-gate PASS is claimed. The authoritative complete-gate pin remains `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`.

Permitted LAB-095 fallback resolved the prior exact reconstruction mismatch for the three remaining focused tests. In an isolated `/dev/shm/lab095-exact` tree, local `git hash-object` matched all three authoritative PR #187 blobs exactly:

- recovery -> `363ab95f1aad425fc89f146ae8fba35d9169950d`
- confirmed-finalize reauth -> `7dcd20dfd24a9439583595bf433f9f696bd870e7`
- locked-custody tamper -> `443e84f65e1d7f58c9b0ae284d700d4ec0f77cc6`

Combined with the five exact files established in the prior run, authoritative exact content is now known for all eight entries of the focused no-stub manifest. No no-stub behavioral GREEN is claimed yet because all eight files were not reassembled simultaneously and executed together in this run.

Durable report: `research/2026-09-14-lab095-three-test-blob-exact-reconstruction.md`, main commit `dc43a591dda914c094133e9374b756eeeca17dbe`.

Previously established evidence remains valid: cross-generation COMPLETE reauth exact closure passed 1/1; object.__new__ binding exact regression passed 1/1; recovery/tamper behavior passed 6/6 previously with exact LAB-095 production/test blobs but protocol stubs.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell/raw GitHub transport cannot resolve GitHub and no safe automatic byte-preserving bulk connector -> executable-filesystem mount is exposed.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` is observed working.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 focused manifest now has authoritative exact content known for all 8/8 files, but the complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-090/LAB-095 `supported.py` conflict resolution is security-sensitive: preserve `CanonicalDatabaseBinding` on both supported ledger/history MROs.

## Exact next action
LAB-086 first: attempt the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`.

If LAB-086 remains blocked, reconstruct all eight focused LAB-095 files from PR #187 head `835a81914c5234e68ef436e30c9837331d262432` into one isolated `/dev/shm` tree. Require 8/8 `git hash-object` matches in the same run, run `compileall`, then execute the recovery/confirmed-finalize/locked-custody suite with no protocol stubs under `TMPDIR=/dev/shm`. Only observed execution counts as GREEN. After that, execute full DB-A -> DB-B and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates plus a fresh conflict/security audit.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; all 8 focused manifest blobs now have exact authoritative content established across runs; same-run 8/8 no-stub reconstruction and behavioral execution next.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091, #176 / LAB-092 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
