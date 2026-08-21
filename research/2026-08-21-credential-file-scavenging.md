# LAB-068 — crash-resilient credential-file scavenging

LAB-027 leaves a narrow gap: SIGKILL/power loss can strand a named `0600` fallback file. The corrected model composes existing authority instead of trusting pathnames: LAB-032 PID+starttime+fresh-pidfd liveness, LAB-065 directory-FD/no-symlink namespace authority, and LAB-066 Linux opaque file-handle identity.

## Critical creation-order finding

The first published slice wrote and `fsync`ed the secret before the lease INSERT. A crash in that interval could leave plaintext bytes with no durable authority record. `(st_dev, st_ino)` was also experimentally insufficient because immediate unlink/recreate reused an inode; `ctime` cannot be durable pre-write identity because writing the secret changes it.

The corrected protocol is therefore:

1. commit a non-secret `PREPARED` lease containing task, credential generation, scope, HMAC fingerprint, exact directory identity, and random basename;
2. create an empty `0600` regular file relative to the held directory FD, `fsync` file + directory;
3. capture a Linux opaque `name_to_handle_at` identity and commit it as `ALLOCATED`;
4. only then write the secret, handling partial writes, and `fsync` it;
5. transition `ALLOCATED -> READY` only after the complete secret bytes are durable.

A crash during a partial or complete secret write leaves an `ALLOCATED` lease. Cleanup may remove any bytes from that exact opaque-handle object because object authority was durably established before secret bytes existed. Once `READY/HANDED_OFF`, keyed content identity is additionally required. If strong opaque file identity is unavailable, named-file fallback fails closed rather than degrading to pathname/dev+ino authority.

A live old-generation child remains authoritative after credential rotation and blocks cleanup. Cleanup also requires the exact cleanup generation and exact directory object. An unlink whose acknowledgement is lost becomes `UNKNOWN` and is reconciled idempotently from durable lease state plus exact-file absence.

## Boundary

Raw secret bytes never enter the lease DB or evidence. HMAC is correlation/identity evidence, not secret storage. File unlink is lifetime/storage reclamation, not forensic erasure. This experiment is not an OS keyring, secrets manager, distributed lease system, backup policy, secure-erasure mechanism, or replacement for LAB-066/067 namespace lineage across restarts/migration.
