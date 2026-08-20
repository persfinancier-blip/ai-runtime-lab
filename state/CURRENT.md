# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-065 — bind durable archive publication to the exact authorized filesystem directory object so symlink/path-prefix substitution cannot redirect the same lexical path between authorization, publication, and SQL commit.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-064.
- Completed Issue #119 / LAB-064.
- PR #120 closed as manually integrated after normal squash merge returned a real conflict caused only by stale `state/CURRENT.md` divergence.
- Active Issue #121 / LAB-065 — IN_PROGRESS.
- Active branch: `lab/065-filesystem-namespace-binding`.
- Active PR: none; draft PR creation was blocked by an external safety-status gate before execution in the latest run.

## Last completed step

LAB-064's final merge gate was closed by exact-source execution. Direct shell clone still could not resolve `github.com`, so the PR HEAD dependency closure was reconstructed through the GitHub connector and every executable file was checked with local `git hash-object` against its GitHub blob ID before tests ran.

Observed exact-source results: LAB-064 focused 10/10, LAB-064 signed-compaction integration 6/6, LAB-062 regressions 15/15, LAB-063 unit 9/9, LAB-063 signed integration 4/4, compileall passed. The normal squash merge of PR #120 was then attempted at exact HEAD `643aee0e764f70f73f3612d8cb2be035332c34bc` and GitHub returned a merge conflict. `compare_commits` showed main had diverged from the PR merge base only in this CURRENT file; code/research paths did not overlap. The exact audited 7 code/research changes were therefore integrated with the repository-approved file-scoped Contents API fallback, excluding the stale branch CURRENT copy. Issue #119 is DONE and PR #120 is closed as manually integrated.

LAB-065 then started. Current x86_64 runtime probing observed `openat2` support: a real directory beneath a trusted dirfd opened; a symlink component was rejected with `ELOOP`; a `..` escape under `RESOLVE_BENEATH` was rejected with `EXDEV`.

An isolated reference implementation is now on `lab/065-filesystem-namespace-binding`: held directory FD is authority, publication/verification are dirfd-relative, receipts bind `(st_dev, st_ino, basename, SHA-256)`, unsupported architecture/openat2 fails closed, and final reread rejects non-regular-file substitution. Corrected local namespace suite passed 11/11; unsafe lexical-path baseline failed as expected after symlink retarget redirected publication into an attacker directory; compileall passed. A separate audit found and fixed unknown-architecture syscall use and special-file blocking risk before handoff.

## Evidence produced

LAB-064:
- Main publication protocol blob: `135cbf1eb8085dc1067bf0485e0acd2995aa5eb0`.
- Main LAB-062 archive integration blob: `dcd8a0c0ea90c9aa60d2252b460879e877dde105`.
- Exact validation counts: 10/10 + 6/6 + 15/15 + 9/9 + 4/4; compileall passed.
- Issue #119 closed DONE; PR #120 closed after exact file-scoped integration fallback.

LAB-065 current branch:
- Corrected namespace protocol blob: `d7b3ea96631e5b1fdf312953db23d55f0dbfc52a`.
- Corrected namespace tests blob: `bab566d9d14e6c845b6c79d4720d74d5dc2d7805`.
- Corrected isolated suite: 11/11 passed.
- Unsafe lexical symlink-retarget seed: failed as expected.
- Runtime `openat2` probe: symlink `ELOOP`, beneath escape `EXDEV`.
- Research note: `research/2026-08-21-filesystem-namespace-binding.md`.

## Known blockers / constraints

- No LAB-064 correctness blocker remains.
- LAB-065 isolated primitive is not yet wired into the real LAB-062 `SignedPrunableHistory` archive publication/pre-SQL-commit path, so LAB-065 is not DONE.
- Draft PR creation for LAB-065 was blocked by an external safety-status gate before execution; branch/issue state is durable, so retry normal PR creation later rather than bypassing the gate.
- The LAB-065 reference syscall mapping intentionally fails closed outside x86_64 instead of guessing another architecture's syscall ABI.
- The trusted-root directory passed into LAB-065 is an authority boundary; this experiment does not claim sandbox/chroot/mount-namespace isolation.
- Directory `fsync()` remains an OS/filesystem/storage-stack durability contract, not a universal physical-media guarantee.
- Whole-store rollback/freshness remains LAB-034–037.

## Exact next action

Resume Issue #121 / branch `lab/065-filesystem-namespace-binding`. First retry normal draft PR creation if the connector allows it. Then integrate the namespace-bound handle into the actual LAB-062 `SignedPrunableHistory` publication boundary: artifact and manifest must be created/fsynced/renamed and pre-commit reverified relative to the same authorized directory FD/object identity, while preserving LAB-064 durability receipts. Add real integration regressions that retarget/replace the archive pathname after authorization and after publication receipt and prove SQL either commits against the same held namespace object or fails closed. Execute exact branch source plus LAB-065 focused tests and LAB-064/LAB-062/LAB-063 regressions, perform a separate remote patch audit, and only then integrate/close LAB-065.

## Backlog

- #121 / LAB-065 — filesystem namespace identity and symlink-swap conformance — IN_PROGRESS.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
