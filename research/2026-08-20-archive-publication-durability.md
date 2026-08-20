# LAB-064 — Filesystem archive-publication durability

Date: 2026-08-20
Issue: #119
Branch: `lab/064-archive-publication-durability`

## Problem

LAB-062 made archive content atomic at the process level by writing a temporary file, calling `fsync(file)`, and replacing the final pathname. LAB-063 then made orphan cleanup safe against concurrent compaction. The remaining gap is sudden host/power loss: a successfully returned rename does not by itself prove that the containing directory entry was durably persisted before SQL commits a reference to the new archive name.

## Primary donors

### Linux `fsync(2)`

The Linux man-pages explicitly separate file durability from directory-entry durability: syncing a file does not necessarily persist the containing directory entry; applications requiring that namespace update to survive a crash must explicitly `fsync()` a descriptor for the directory.

Source: https://man7.org/linux/man-pages/man2/fsync.2.html

### POSIX rename

`rename()` supplies atomic namespace replacement semantics, but atomicity of the operation is a different property from persistence across sudden host/power loss.

Source: https://man7.org/linux/man-pages/man3/rename.3p.html

### SQLite atomic commit

SQLite's atomic-commit documentation explicitly discusses syncing directories around journal namespace changes and records the dependence of power-loss safety on filesystem/storage behavior. This is a useful donor because LAB-062 similarly publishes filesystem state before committing an authoritative database reference.

Source: https://www.sqlite.org/atomiccommit.html

## Protocol decision

For the POSIX/Linux reference path, a file publication is considered eligible for an authoritative SQL reference only after this observed sequence succeeds:

`write temp -> flush -> fsync(temp file) -> atomic replace -> fsync(parent directory)`

Both the archive artifact and its manifest must independently cross this boundary. The compaction SQL transaction then re-verifies the published bytes and may commit the `signed_archives` / compaction-base reference only when both publication receipts are durable.

A failure after rename but before directory fsync may leave a filename visible to the running process. That visible name is debris, not proof of durable publication. A failure after directory fsync but before the caller receives the receipt is treated conservatively as unknown/safe-to-reconcile rather than fabricated success.

## Current implementation slice

`experiments/archive_publication_durability/protocol.py` introduces:

- `durable_publish()` for the explicit file + directory sync boundary;
- `PublicationReceipt` whose `durable` property requires both file and directory sync;
- `require_durable_pair()` for artifact+manifest gating;
- deterministic fault hooks around write, file fsync, rename, and directory fsync;
- an unsafe rename-only receipt retained as a negative baseline.

LAB-062 `ArchiveMixin._atomic_file()` now delegates to `durable_publish()`, and `compact()` refuses to start its authoritative write transaction unless both publication receipts are durable and the artifact digest matches the signed manifest.

## Boundary / non-claims

- This is not a claim of universal power-loss durability for every filesystem/device/virtual storage stack.
- `fsync()` returning successfully is an OS/filesystem/device contract whose strength depends on the platform and storage stack.
- Atomic rename is not treated as equivalent to durable rename.
- Process-crash orphan cleanup remains LAB-063's responsibility.
- Whole-database rollback/freshness remains LAB-034–037's external-anchor responsibility.
- Backup durability, secure deletion, forensic erasure, distributed filesystems and remote object stores are out of scope.

## Remaining acceptance work

Execute the exact published branch source for the focused failure matrix and LAB-062 integration tests, then rerun relevant LAB-062 and LAB-063 regressions. Perform a separate remote patch audit before integration. No success claim should be made from the code publication alone.
