# LAB-068 — credential-file scavenging

Named 0600 credential files are fallback transport only. A durable non-secret lease binds task, credential generation, HMAC fingerprint, exact directory/file identities and optional child process identity. Cleanup rechecks process liveness and exact namespace/object identity before unlink. Raw secret bytes never enter durable evidence. `UNKNOWN` after unlink is reconciled idempotently.

Filesystem deletion is lifetime/storage reclamation, not forensic erasure.
