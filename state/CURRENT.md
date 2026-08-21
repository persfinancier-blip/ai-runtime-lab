# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-066 — reconstruct archive namespace authority after process restart without silently trusting a pathname, recycled inode/mount identifier, or byte-identical replacement directory; safely classify detached artifacts and intentional relocation.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-065.
- Completed Issue #121 / LAB-065.
- Merged PR #122 / LAB-065 as `ff5fb48f2971ff50859607584bd309e9f3d515c1`.
- Active Issue #123 / LAB-066 — IN_PROGRESS.
- Active branch: `lab/066-namespace-reacquisition`.
- Active PR: none yet.

## Last completed step

LAB-065 exact-source validation was completed after reconstructing the current PR HEAD through the GitHub connector because direct shell checkout still could not resolve `github.com`. Executable source/test files were verified with `git hash-object` against GitHub blob IDs.

A final audit found one additional pre-authorization side effect: `Path.mkdir(parents=True)` in `SignedPrunableHistory.__init__` could create a missing archive directory through an intermediate symlink before the later openat2 boundary rejected the path. It was replaced with component-by-component directory creation from `/` using held dirfds plus `O_NOFOLLOW`, and a regression proves no directory is created under the symlink target.

Observed current-HEAD results: LAB-065 isolated 11/11; LAB-065 real SignedPrunableHistory integration 8/8; LAB-062 signed compaction 15/15; LAB-064 publication core 10/10; LAB-064 signed integration 6/6; LAB-063 scavenging core 9/9; LAB-063 real signed integration 4/4; relevant compileall passed. Exact unsafe lexical-path baseline failed as expected after retargeting to an attacker directory. `main` had advanced only in this state file, with no code overlap. PR #122 was marked ready and squash-merged normally.

LAB-066 was then selected as the next correctness bottleneck. Primary-source research confirms that Linux opaque file handles can cross processes but are filesystem-dependent, can become stale, and `open_by_handle_at` requires `CAP_DAC_READ_SEARCH`; mount IDs are not universal persistent filesystem identities.

A real runtime probe observed:
- Linux 6.18.35 x86_64;
- libc exposes `name_to_handle_at` and `open_by_handle_at`;
- `name_to_handle_at` succeeded for a real directory with an 8-byte type-1 handle and mount id 50;
- `open_by_handle_at` failed `EPERM` because the runtime lacks `CAP_DAC_READ_SEARCH`;
- `/proc/sys/kernel/random/boot_id` is available for explicit same-boot classification.

## Evidence produced

- LAB-065 merge: `ff5fb48f2971ff50859607584bd309e9f3d515c1`.
- LAB-065 tested PR HEAD: `bb05c9dfee2c470748e4327c437445dcb9e861dd`.
- Key exact blobs included namespace protocol `d7b3ea96631e5b1fdf312953db23d55f0dbfc52a`, integration `0aca43fc493d8041d2538b9d53c1ada992494da6`, signed-compaction protocol `02d9277e35bef52021bff039196fb55719dfb6d2`, and constructor/integration tests `8e38d5a8c3b9ae8cf4ad83f80dddd7429c7be4ee`.
- Issue #121 closed DONE; completion evidence recorded in its comment thread.
- Issue #123 / LAB-066 created and moved to IN_PROGRESS.
- Branch `lab/066-namespace-reacquisition` created from current main.
- LAB-066 capability probe recorded in Issue #123.

## Known blockers / constraints

- No owner-level blocker.
- Direct shell GitHub DNS remains unavailable in this runtime; GitHub connector reconstruction is the supported fallback when exact source is needed.
- `open_by_handle_at` is not currently usable because `CAP_DAC_READ_SEARCH` is absent even though `name_to_handle_at` succeeds. LAB-066 must treat this as an observed capability limitation, not silently weaken authority to pathname-only trust.
- `st_dev/st_ino` and mount IDs must not be described as universal cross-reboot identities.
- Opaque handles may be unsupported or stale depending on filesystem/runtime.
- Intentional archive relocation must be an authenticated namespace-generation transition, not automatic path rebinding.
- Whole-store rollback/freshness remains LAB-034–037.
- Local cleanup is not forensic secure erasure.

## Exact next action

Resume Issue #123 on branch `lab/066-namespace-reacquisition`. First implement the minimal authenticated namespace-continuity record and capability/identity-strength model. Use real LAB-065 openat2 path reauthorization on restart. Build deterministic cases for unchanged object, symlink/path replacement with copied valid archive bytes, missing/detached directory, unavailable/stale strong handle, tampered continuity record, and explicit migration/rebind that advances a namespace generation and fences stale evidence. Keep `open_by_handle_at` optional and capability-gated; the current runtime should produce an explicit `UNSUPPORTED_STRONG_REACQUISITION` path where elevated reopen cannot be demonstrated. Integrate with real SignedPrunableHistory and LAB-063 before declaring DONE.

## Backlog

- #123 / LAB-066 — restart namespace reacquisition and detached-artifact reconciliation — IN_PROGRESS.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
