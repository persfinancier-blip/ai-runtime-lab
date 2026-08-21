# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-065 — bind durable archive publication to the exact authorized filesystem directory object so symlink/path-prefix/CWD substitution cannot redirect publication between configuration, authorization, receipt validation, and SQL commit.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-064.
- Active Issue #121 / LAB-065 — IN_PROGRESS.
- Active branch: `lab/065-filesystem-namespace-binding`.
- Active draft PR: #122.
- Current tested/audited target HEAD after this run: `e61b6a707b1319477d37526dcc4232d73df9ac7a` (not yet exact-source regression executed).

## Last completed step

A fresh audit resumed PR #122 and re-probed direct checkout. Shell `git clone` still failed with `Could not resolve host: github.com`, so connector reconstruction remains the supported fallback.

The audit then found a new namespace-authority defect: `SignedPrunableHistory.__init__` retained `archive_dir` as a relative `Path`. If the process changed cwd after object construction, both authorization and `_archive_paths()` could silently retarget the same history object to a different directory. This violated LAB-065's stable namespace-authority goal even without a symlink attack.

The branch now binds the configured archive directory lexically to an absolute path at construction using `os.path.abspath(os.fspath(archive_dir))`; it deliberately does not use `Path.resolve()` and therefore does not bless symlink traversal. A real SignedPrunableHistory regression changes cwd after construction, creates a competing relative `archives` directory under the new cwd, performs compaction, and requires bytes to appear only under the original construction-time directory.

The earlier full-root `openat2` path-prefix fix and thread-local namespace-handle fix remain in place.

## Evidence produced

- Direct shell clone retried: failed before checkout due DNS resolution of `github.com`.
- PR #122 current HEAD after fixes: `e61b6a707b1319477d37526dcc4232d73df9ac7a`; GitHub reports it mergeable and still draft.
- `experiments/signed_history_compaction/protocol.py` audit fix commit: `5252b619decad734794239d2c1c376db0cd01add`.
- Relative-path/CWD regression commit: `e61b6a707b1319477d37526dcc4232d73df9ac7a`.
- Earlier isolated LAB-065 evidence remains: 11/11 corrected tests passed, unsafe lexical seed failed as expected, compileall passed, runtime openat2 probe succeeded on x86_64.
- Exact connector bytes for current LAB-065 protocol/integration and key LAB-062/LAB-064 dependencies were inspected in this run, but the complete updated dependency closure has not yet been executed; do not claim the current HEAD validated.

## Known blockers / constraints

- PR #122 must remain draft until exact-source execution of current HEAD is observed.
- Direct shell GitHub DNS is unavailable in this runtime; connector reconstruction is the safe supported fallback.
- Required merge gate remains: LAB-065 isolated + SignedPrunableHistory integration, LAB-064 focused + integration regressions, LAB-062 suite, LAB-063 unit + real signed integration regressions, compileall, then final unchanged-HEAD remote patch audit.
- x86_64 openat2 syscall mapping intentionally fails closed on unsupported architectures.
- Full-root openat2 removes symlink components from configured absolute path authorization but does not claim mount-namespace/chroot/bind-mount immutability.
- Directory fsync remains an OS/filesystem/storage-stack durability contract, not a universal physical-media guarantee.
- Namespace-detached non-authoritative bytes after relocation remain a follow-up cleanup/reacquisition concern.
- Whole-store rollback/freshness remains LAB-034–037.

## Exact next action

Resume Issue #121 / draft PR #122 at HEAD `e61b6a707b1319477d37526dcc4232d73df9ac7a`. First retry normal checkout; if DNS still fails, finish reconstructing the exact runnable dependency closure through GitHub connector and verify every executable file with `git hash-object` against GitHub blob IDs. Execute the full LAB-065/064/062/063 regression matrix and compileall, including the new cwd-retarget regression. Fix any failure. Then re-fetch the unchanged tested PR HEAD, perform a final remote patch audit, and only after a clean result mark ready/integrate and close #121 DONE.

## Backlog

- #121 / LAB-065 — filesystem namespace identity and symlink/CWD-swap conformance — IN_PROGRESS.
- Candidate after LAB-065: persisted namespace identity/reacquisition and cleanup of namespace-detached non-authoritative archive artifacts after restart/path relocation.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
