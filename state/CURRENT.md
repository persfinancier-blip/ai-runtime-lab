# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-064 — prove the filesystem durability boundary required before SQL may commit an authoritative reference to a newly published archive artifact/manifest.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-063.
- Issue #119 / LAB-064 — IN_PROGRESS.
- Active branch: `lab/064-archive-publication-durability`.
- Active draft PR: #120 at audited HEAD `118da6f0bd195d34d4806f71744ebee5d0609881`.

## Last completed step

The unfinished LAB-064 branch and draft PR were reconstructed from GitHub. PR #120 is mergeable, ahead of main by 9 commits and behind by 0, with eight changed paths. Exact branch source for the new durable publication primitive, its tests, signed-compaction integration tests, and modified LAB-062 `archive.py` was retrieved through the connector because shell `git clone` could not resolve github.com in this runtime.

A separate remote audit found a correctness gap that blocks merge: `SignedPrunableHistory.compact()` currently requires two durable receipts and validates the artifact receipt digest, but does not bind the manifest receipt to the exact expected manifest path/content. A buggy or substituted publication adapter could therefore return a durable receipt for a different file/directory while the expected manifest is only visible, allowing SQL authority to outrun the intended namespace-durability proof.

Issue #119 has been updated with this defect and PR #120 remains draft/not merge-authorized.

## Evidence produced

- PR #120 metadata: mergeable, draft, HEAD `118da6f0bd195d34d4806f71744ebee5d0609881`.
- Branch is `ahead 9 / behind 0` relative to main.
- New publisher Git blob: `e698c0fa0150a15b6dafe8bd71a67f5d27745c9a`.
- Focused test blob: `93b3758684681eac8bb13d4769d8bd4b9e6415c7`.
- Signed-compaction integration test blob: `d7baf121a4a06e62cc0bc3b4d376b9db3dcab8bb`.
- Modified LAB-062 archive blob: `263cdcde0d4ea89aa8b6c777a7894de7db9c222a`.
- Shell clone attempt failed before execution of tests because the runtime could not resolve `github.com`; connector retrieval remained available.

## Known blockers / constraints

- No design blocker; there is one known implementation defect that must be fixed before merge.
- Bind both artifact and manifest durable receipts to exact expected path + content digest before SQL commit.
- Add wrong-path and wrong-digest durable-receipt regression tests.
- Exact published LAB-064 tests plus LAB-062/LAB-063 regressions still must be executed after the fix.
- Direct shell GitHub DNS is unavailable in this runtime; use connector-retrieved exact bytes/local reconstruction if needed.
- Directory `fsync()` is an OS/filesystem/storage-stack contract, not a universal physical-media guarantee.

## Exact next action

Resume PR #120. Fix receipt binding at the LAB-062 compaction boundary so both durable receipts are checked against the exact expected artifact/manifest paths and bytes; add regression tests that supply durable-but-wrong path/digest receipts and prove SQL remains unchanged. Then execute exact published source for LAB-064 plus relevant LAB-062/LAB-063 regression suites and compileall, perform another remote patch audit, and only if clean mark PR ready and integrate.

## Backlog

- #119 / LAB-064 — IN_PROGRESS; draft PR #120 blocked on receipt-binding fix + exact-source regression execution.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
