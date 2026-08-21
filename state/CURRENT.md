# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-065 — bind durable archive publication to the exact authorized filesystem directory object so symlink/path-prefix substitution cannot redirect publication between authorization and SQL commit.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-064.
- Active Issue #121 / LAB-065 — IN_PROGRESS.
- Active branch: `lab/065-filesystem-namespace-binding`.
- Active draft PR: #122.
- Current audited PR HEAD: `bfed3746d81aa4030ec69f46761d00dfb09b9e51`.

## Last completed step

LAB-065 is now wired into the real LAB-062 `SignedPrunableHistory` compaction path rather than remaining an isolated primitive. Artifact and manifest publication are performed relative to one held archive-directory FD; LAB-064 path/digest/file-fsync/directory-fsync receipt checks are preserved; LAB-065 additionally verifies `(st_dev, st_ino, basename, SHA-256)` through the same handle. Immediately before the SQL prune transaction makes an archive authoritative, the exact bytes are re-read through that held namespace object and the configured archive pathname is checked to still resolve to the same object.

Real integration regressions were added for: archive-directory symlink substitution at authorization, pathname retarget immediately after namespace authorization, pathname retarget after durable publication receipt, and stable dirfd identity across rename.

A separate remote patch audit found a concurrency defect in the first integration slice: active namespace authority was ordinary mutable instance state, so concurrent compactions on one object could overwrite each other's handle. `SignedPrunableHistory` now initializes a `threading.local()` namespace slot and exposes the mixin's active-handle field through a thread-local property, preventing cross-thread authority consumption.

Normal draft PR creation, which had been blocked in the previous run, succeeded as PR #122. The PR is currently mergeable and intentionally remains draft.

## Evidence produced

Earlier isolated LAB-065 evidence remains valid:
- namespace protocol blob from the isolated slice: `d7b3ea96631e5b1fdf312953db23d55f0dbfc52a`;
- isolated corrected suite: 11/11 passed;
- unsafe lexical symlink-retarget seed failed as expected;
- isolated compileall passed;
- runtime probe: `openat2` available on x86_64, symlink rejected with `ELOOP`, `..` beneath escape rejected with `EXDEV`.

Current integration evidence:
- PR #122 exists and is mergeable/draft at HEAD `bfed3746d81aa4030ec69f46761d00dfb09b9e51`.
- New `experiments/filesystem_namespace_binding/integration.py` binds the real SignedPrunableHistory publication and pre-commit boundary to a held dirfd.
- `experiments/signed_history_compaction/protocol.py` now composes `NamespaceBoundArchiveMixin` and uses thread-local active namespace authority.
- Real SignedPrunableHistory path-swap regression file is present on the branch.
- Remote patch audit found and fixed the shared-handle concurrency defect; no merge has been attempted after the fix.

## Known blockers / constraints

- The newly integrated current PR HEAD has **not yet been executed exactly**. A fresh direct shell `git clone` in this runtime failed before checkout because DNS could not resolve `github.com`. Do not claim the integration tests passed until exact-source execution is observed.
- PR #122 must remain draft until exact-source validation and final remote patch audit complete.
- Branch is currently ahead of and slightly behind main; no low-level ref update/force bypass should be used. Re-check compare state before integration.
- The x86_64 syscall mapping intentionally fails closed on other architectures.
- The trusted root used to acquire the directory FD is itself an authority boundary; this experiment does not claim chroot/mount-namespace isolation.
- Directory `fsync()` is an OS/filesystem/storage-stack durability contract, not a universal physical-media guarantee.
- Path relocation after a failed/non-authoritative publication can leave bytes in the held renamed directory; restart reacquisition/cleanup of such namespace-detached artifacts is a separate follow-up concern.
- Whole-store rollback/freshness remains LAB-034–037.

## Exact next action

Resume Issue #121 / draft PR #122. Obtain the exact current PR HEAD source using the safest available route; if direct clone still lacks DNS, reconstruct the dependency closure through the GitHub connector and verify each executable file with local `git hash-object` against its GitHub blob ID before running it. Execute: LAB-065 isolated tests, LAB-065 SignedPrunableHistory integration tests, LAB-064 focused and signed-compaction integration regressions, LAB-062 signed-history suite, LAB-063 unit and real signed integration regressions, and compileall. Fix any failure, then re-fetch PR #122 at the same audited HEAD, perform a final remote patch audit, mark ready and integrate only if all exact-source evidence is clean. Close #121 only after that.

## Backlog

- #121 / LAB-065 — filesystem namespace identity and symlink-swap conformance — IN_PROGRESS.
- Candidate after LAB-065: persisted namespace identity/reacquisition and cleanup of namespace-detached non-authoritative archive artifacts after restart/path relocation.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
