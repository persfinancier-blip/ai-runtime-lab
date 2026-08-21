# LAB-069 — path-compatible memfd credential transport

## Question

Can Linux path-only tools consume credentials without creating a persistent directory entry, while preserving explicit inheritance, immutable publication, credential-generation fencing, and non-secret evidence?

## Donor semantics

Linux `memfd_create()` creates an anonymous file descriptor with ordinary fork/exec descriptor semantics. `MFD_CLOEXEC` gives default non-inheritance and `MFD_ALLOW_SEALING` permits file seals. `/proc/self/fd/N` is a pathname-like reference to an already-open descriptor, subject to procfs/permission/namespace constraints.

## Experiment

The reference route keeps `MFD_CLOEXEC` by default and uses explicit `pass_fds` only for the intended child. The credential is written fully, rewound, and then sealed with write/grow/shrink/seal seals. A real Python subprocess then opens `/proc/self/fd/N` as a path and reads the exact bytes. The same path fails when the descriptor is not explicitly inherited. Closing the final owner reference removes the owner's procfd path.

Durable evidence contains only credential ID, generation, scope, keyed fingerprint, and transport type. Stale permits are rejected after rotation. Retry reuses the same non-secret permit/evidence identity rather than persisting another secret copy.

## Audit findings

A generic runtime probe is not enough to authorize an arbitrary path-only tool: Python may accept `/proc/self/fd/N` while another target rejects it or runs in a different procfs/namespace context. The corrected router therefore requires a caller-supplied **target-specific compatibility probe**. Missing, false, or failing target probes route explicitly to LAB-068. The memfd route also requires the complete sealing primitive set; partial kernel/runtime support fails closed rather than producing an unsealed transport.

## Boundary

Anonymous volatile-file lifetime is not forensic erasure and does not establish that pages never reach swap. `/proc/self/fd` access can be constrained by procfs mount options, ptrace-style permission checks, user/process namespaces, or tool behavior. This experiment reduces the named-filesystem attack surface only where compatibility of the actual target tool is proven; it does not remove LAB-068 as the fail-closed compatibility fallback.
