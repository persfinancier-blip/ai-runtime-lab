# LAB-069 — path-compatible memfd credential transport

## Question

Can Linux path-only tools consume credentials without creating a persistent directory entry, while preserving explicit inheritance, immutable publication, credential-generation fencing, and non-secret evidence?

## Donor semantics

Linux `memfd_create()` creates an anonymous file descriptor with ordinary fork/exec descriptor semantics. `MFD_CLOEXEC` gives default non-inheritance and `MFD_ALLOW_SEALING` permits file seals. `/proc/self/fd/N` is a pathname-like reference to an already-open descriptor, subject to procfs/permission/namespace constraints.

## Experiment

The reference route keeps `MFD_CLOEXEC` by default and uses explicit `pass_fds` only for the intended child. The credential is written fully, rewound, and then sealed with write/grow/shrink/seal seals. A real Python subprocess then opens `/proc/self/fd/N` as a path and reads the exact bytes. The same path fails when the descriptor is not explicitly inherited. Closing the final owner reference removes the owner's procfd path.

Durable evidence contains only credential ID, generation, scope, keyed fingerprint, and transport type. Stale permits are rejected after rotation. Retry reuses the same non-secret permit/evidence identity rather than persisting another secret copy.

Capability/compatibility is observed, not assumed. If memfd creation or procfd path use is unavailable for a target runtime/tool, routing explicitly returns to the separately hardened LAB-068 named fallback.

## Boundary

Anonymous volatile-file lifetime is not forensic erasure and does not establish that pages never reach swap. `/proc/self/fd` access can be constrained by procfs mount options, ptrace-style permission checks, user/process namespaces, or tool behavior. This experiment therefore reduces the named-filesystem attack surface where compatibility is proven; it does not remove LAB-068 as the fail-closed compatibility fallback.
