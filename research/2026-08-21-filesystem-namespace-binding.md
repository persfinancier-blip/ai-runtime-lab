# LAB-065 — Filesystem namespace identity and symlink-swap conformance

## Question

LAB-064 binds durable receipts to an absolute pathname and content digest. Does that
also bind the operation to the same filesystem directory object if a pathname prefix
or symlink changes concurrently?

## Primary donors

- Linux `openat(2)` rationale: directory-FD APIs avoid path-prefix races and an open
  directory FD remains a stable reference even if the directory is renamed.
  https://man7.org/linux/man-pages/man2/openat.2.html
- Linux `openat2(2)`: `RESOLVE_BENEATH` rejects escapes from a starting dirfd;
  `RESOLVE_NO_SYMLINKS`/`RESOLVE_NO_MAGICLINKS` prevent link-based indirection;
  `RESOLVE_NO_XDEV` can optionally reject mount traversal.
  https://man7.org/linux/man-pages/man2/openat2.2.html
- Linux kernel pathname-lookup documentation explains the corresponding
  LOOKUP_BENEATH / NO_SYMLINKS / NO_XDEV restrictions and rename-race handling.
  https://www.kernel.org/doc/html/latest/filesystems/path-lookup.html

## Observed runtime probe

On the current x86_64 Linux runtime, syscall `openat2` succeeded for a real directory
beneath a trusted dirfd. A symlink path was rejected with `ELOOP`; a `..` escape under
`RESOLVE_BENEATH` was rejected with `EXDEV`.

## Reference contract

1. Open a trusted root directory FD.
2. Obtain the archive-directory FD with `openat2` and explicit resolution restrictions.
3. Treat the resulting FD/object identity, not the source pathname string, as authority.
4. Create/fsync/rename/fsync archive files relative to that FD.
5. Bind receipt to `(st_dev, st_ino, basename, SHA-256)`.
6. Immediately before consequential use, re-read content relative to the same held FD
   and compare namespace identity + digest.
7. Fail closed rather than silently falling back to lexical pathname authority when
   the required kernel primitive is unavailable.

## Negative baseline

A lexical absolute path through a symlink is planned while it targets an authorized
directory. The symlink is retargeted before publish. LAB-064's lexical receipt remains
the same path string, but the bytes are actually written into the attacker directory.
The namespace-FD design is unaffected by the path swap.

## Boundary

This is pathname/object-identity binding for a local Linux publication boundary. It
is not a sandbox, chroot, mount-namespace policy, distributed filesystem guarantee,
secure deletion mechanism, or proof against a compromised kernel/storage stack.
