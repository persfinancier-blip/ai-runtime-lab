# LAB-087 — ancestor namespace stability

## Finding

A database file can be perfectly read-only to a worker while the *name of its protected directory* is still replaceable through a writable ancestor. The pre-fix process boundary protected the database (`0640`) and its immediate parent (`0750`) but did not verify the namespace above that parent.

Executable counterexample: place the protected directory under a broker-owned `0777` non-sticky container, run the worker as a distinct UID/GID, then rename the entire protected directory and create a replacement directory under the original name. The worker never writes inside the protected directory; it mutates the ancestor directory entry instead. The counterexample succeeded.

## Corrected boundary

`UnixReadOnlyWorkerBoundary` now verifies every lexical ancestor above the protected directory:

- it must be a real directory rather than a symlink;
- its owner must be root or the broker UID;
- group/world-writable ancestors are rejected unless sticky-bit semantics protect broker-owned child names (for example `/tmp`).

The same checks run at installation and re-verification. This preserves normal `/tmp`-based tests while rejecting a writable non-sticky deployment ancestor and detecting permission drift after installation.

## Evidence

Exact published implementation blob after the fix: `87456dfcbeac0c0e795fc0bcdeb3502cf57fcdd0`.

Exact published process-test blob: `eacffa649db7e848de6b17cbf734b4fbc7f6cae3`.

Full exact LAB-087 suite after publication: 14/14 PASS; compileall PASS.

## Boundary

This remains Unix discretionary-access-control evidence, not protection against broker UID, root, `CAP_DAC_OVERRIDE`, ACL/capability policy not represented by mode bits, mount-namespace replacement, or another privileged actor that can change ownership/permissions. SQLite `set_authorizer()` remains connection-scoped defense-in-depth; process separation plus writable filesystem/handle ownership is the outer authority boundary.
