# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-065 — bind durable archive publication to the exact authorized filesystem directory object so symlink/path-prefix substitution cannot redirect publication between authorization and SQL commit.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-064.
- Active Issue #121 / LAB-065 — IN_PROGRESS.
- Active branch: `lab/065-filesystem-namespace-binding`.
- Active draft PR: #122.
- Latest branch commits in this run: `547ecd9b560db261a5484faa72d32d2b71d789e3`, `afe0f6fafc63b3550ff6abc5a2d36a7fcd86cc15`.

## Last completed step

A fresh remote audit found a namespace-authority defect in the integrated slice: `_namespace_handle()` treated `archive_dir.parent` as a trusted root and opened it lexically with `O_NOFOLLOW`, which protects only the final parent component and can still follow an intermediate symlink. Therefore the prior implementation did not actually prove the advertised path-prefix substitution property.

The branch was corrected so authorization starts from filesystem root `/` and resolves the complete absolute archive-directory path using the existing `openat2` `RESOLVE_BENEATH|RESOLVE_NO_SYMLINKS|RESOLVE_NO_MAGICLINKS` boundary. The pre-SQL-commit configured-path continuity check now re-authorizes that complete path through the same symlink-free mechanism and compares directory `(st_dev, st_ino)` with the held handle. A real SignedPrunableHistory regression was added where an intermediate parent component is a symlink; it must fail before compaction.

The earlier thread-local fix remains: concurrent compactions cannot overwrite each other's active namespace handle.

## Evidence produced

- Direct shell clone was retried in this run and still failed with `Could not resolve host: github.com`.
- Remote audit evidence: prior integration authorized only `archive_dir.parent + basename`, leaving symlink traversal possible in ancestors of `archive_dir.parent`.
- Corrected integration blob after commit `547ecd9b...`: GitHub Contents API accepted the full-root openat2 authorization change.
- Corrected integration regression blob after commit `afe0f6fa...`: intermediate path-component symlink test added.
- Earlier isolated LAB-065 evidence remains: 11/11 corrected tests passed, unsafe lexical seed failed as expected, compileall passed, runtime openat2 probe succeeded on x86_64.

## Known blockers / constraints

- The newly corrected PR #122 HEAD has not yet been executed exactly; do not merge or close #121 until exact-source execution is observed.
- Direct shell GitHub DNS remains unavailable in this runtime. Connector reconstruction remains the supported fallback, but the complete runnable dependency closure was not reconstructed before this run ended.
- PR #122 must remain draft until exact-source LAB-065 + LAB-064 + LAB-062 + LAB-063 regressions and final patch audit pass.
- The x86_64 syscall mapping intentionally fails closed on other architectures.
- Starting resolution at `/` removes untrusted intermediate symlink components from the configured absolute path, but does not claim mount-namespace/chroot/bind-mount immutability.
- Directory `fsync()` remains an OS/filesystem/storage-stack durability contract, not a universal physical-media guarantee.
- Namespace-detached non-authoritative bytes after relocation remain a follow-up cleanup/reacquisition concern.
- Whole-store rollback/freshness remains LAB-034–037.

## Exact next action

Resume Issue #121 / draft PR #122 at its new HEAD. Reconstruct the exact runnable dependency closure through the GitHub connector (or normal clone if DNS recovers), verify every reconstructed executable file with `git hash-object` against its GitHub blob ID, and execute: LAB-065 isolated tests; LAB-065 SignedPrunableHistory integration tests including the new intermediate-prefix-symlink regression; LAB-064 focused + signed-compaction integration regressions; LAB-062 signed-history suite; LAB-063 unit + real signed integration regressions; compileall. Fix any failure. Then re-fetch the unchanged tested PR HEAD, perform a final remote patch audit, and only after a clean result mark ready/integrate and close #121 DONE.

## Backlog

- #121 / LAB-065 — filesystem namespace identity and symlink-swap conformance — IN_PROGRESS.
- Candidate after LAB-065: persisted namespace identity/reacquisition and cleanup of namespace-detached non-authoritative archive artifacts after restart/path relocation.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
