# LAB-068 — credential-file scavenging

Named `0600` credential files are fallback transport only. Secret bytes are never written before durable non-secret authority exists.

Creation order is:

`PREPARED lease -> empty 0600 file + fsync -> opaque Linux file-handle identity -> ALLOCATED lease -> secret write + fsync -> READY`.

`ALLOCATED` is intentionally cleanup-authoritative even if a crash left zero, partial, or complete secret bytes: the durable opaque file handle identifies the exact allocated object. `READY/HANDED_OFF` additionally require the keyed content fingerprint to match. A live process proven through LAB-032 PID/starttime/fresh-pidfd authority blocks cleanup even after credential rotation.

Cleanup binds the exact directory object, opaque file handle, cleanup generation, task/process authority, and content state before unlink; `UNKNOWN` after unlink is reconciled idempotently. If strong opaque file identity is unavailable, named-file fallback fails closed rather than downgrading to pathname or `(st_dev, st_ino)` authority.

Filesystem deletion is lifetime/storage reclamation, not forensic erasure.
