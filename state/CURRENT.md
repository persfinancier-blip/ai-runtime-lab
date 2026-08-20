# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-064 — prove the filesystem durability boundary required before SQL may commit an authoritative reference to a newly published archive artifact/manifest.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-063.
- Issue #119 / LAB-064 — IN_PROGRESS.
- Active branch: `lab/064-archive-publication-durability`.
- Active draft PR: #120 at HEAD `14943e32c033e046596b5e356f5ce819cdc9bbbc`.

## Last completed step

The merge-blocking receipt-binding defect from the previous remote audit was fixed. `PublicationReceipt` now binds successful publication to a normalized absolute target path and SHA-256. `require_durable_pair()` requires the exact expected artifact path+bytes and manifest path+bytes and rejects any durable receipt whose path or content digest does not match. LAB-062 `compact()` now supplies those exact expected values before opening the authoritative prune transaction.

Regression tests were added for durable-but-wrong manifest path, wrong artifact digest, and wrong manifest digest; each requires SQL history to remain unpruned. A second remote patch audit of the corrected publication primitive, LAB-062 compaction boundary, and integration regressions found no new content defect.

Direct shell `git clone` was retried in this invocation and again failed because the runtime could not resolve `github.com`. Therefore exact published branch execution plus LAB-062/LAB-063 regressions remains deliberately unclaimed and is the only known merge gate.

## Evidence produced

- Corrected publication primitive blob: `135cbf1eb8085dc1067bf0485e0acd2995aa5eb0`.
- Corrected focused-test blob: `e2e9c9b8a0446d1f4ae8929f675b988ce9e58d0f`.
- Corrected LAB-062 archive blob: `dcd8a0c0ea90c9aa60d2252b460879e877dde105`.
- Corrected signed-compaction integration-test blob: `f23a58a49d17644c7e12149e6c180ed418cb0466`.
- PR #120 remote patch audit confirms the compaction call binds both receipts to exact expected path and bytes.
- Issue #119 acceptance checklist updated: receipt binding is complete; exact-source execution remains open.
- Shell clone failure observed again: `Could not resolve host: github.com`.

## Known blockers / constraints

- No known design/content blocker remains after the receipt-binding fix.
- Exact published LAB-064 tests plus LAB-062/LAB-063 regression suites still must be executed before merge.
- Direct shell GitHub DNS is unavailable in this runtime; use connector-retrieved exact bytes/local reconstruction if a future invocation can complete the dependency closure safely.
- Directory `fsync()` is an OS/filesystem/storage-stack durability contract, not a universal physical-media guarantee.
- Process-crash orphan cleanup remains LAB-063; whole-store rollback/freshness remains LAB-034–037.

## Exact next action

Resume PR #120. Obtain a complete exact-source runnable checkout of HEAD through a supported route (normal shell clone if DNS works; otherwise connector-reconstruct all dependency bytes and verify local `git hash-object` against GitHub blob IDs). Execute the LAB-064 focused suite, LAB-062 signed-compaction regression suite, LAB-063 scavenging regression suite, and compileall. If all pass, perform one final full PR patch audit, mark the draft ready, integrate, close Issue #119 as DONE, and select the next highest-value gap.

## Backlog

- #119 / LAB-064 — IN_PROGRESS; receipt-binding defect fixed; exact-source execution is the only known merge gate.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
