# LAB-087 — SQLite schema-control boundary

This experiment makes the trust boundary behind LAB-086 explicit.

- The broker/process owns the only writable SQLite handle and database-file authority.
- Workers receive `RestrictedConnection`: a read-only URI connection plus a connection-scoped SQLite authorizer that denies DDL, ATTACH/DETACH, write PRAGMAs, and INSERT/UPDATE/DELETE.
- LAB-086 triggers remain durable stale-code/invariant guards inside the broker.
- The authorizer is defense-in-depth, **not** a database-file security boundary. The negative-control test opens another unrestricted writable connection and successfully drops a trigger and changes authority state.
- On Unix, `UnixReadOnlyWorkerBoundary` makes the outer file boundary concrete: a broker-owned directory is `0750` and the database is `0640`, with a distinct worker group receiving only traverse/read permission.
- A process-level regression runs a worker under a distinct UID/GID. The worker can read the canonical database but cannot open it `O_RDWR`, commit a SQLite write, unlink/rename the database name, or change its mode. The broker UID remains writable as the explicit negative control.
- The protected directory's lexical ancestor chain is verified too. Every ancestor must be root/broker-owned; group/world-writable ancestors are rejected unless sticky-bit semantics protect broker-owned child names (for example `/tmp`). This closes directory-replacement attacks through a writable non-sticky ancestor.
- This slice deliberately rejects SQLite WAL mode at install and re-verification. A live read-only WAL database depends on `-wal`/`-shm` sidecars being readable/creatable (or on the database being declared immutable). The boundary does not grant the worker directory write authority and must not mark a live mutable authority database `immutable`, so rollback-journal mode is the supported deployment contract for this slice.

Therefore deployment must enforce the outer boundary with process separation and filesystem/handle ownership so a worker cannot simply reopen the database writable or replace the broker connection's authorizer. The database must live in a **dedicated broker-owned directory**: `install()` changes that parent directory's ownership/mode, and sharing it with unrelated files would broaden worker visibility and create unrelated permission side effects. This Unix DAC slice is not a same-UID/root/ACL/capability/mount-namespace sandbox: broker UID, root, `CAP_DAC_OVERRIDE`, permission-changing authority, privileged namespace replacement, and unrelated privileged processes remain outside the claim.

Run:

```bash
python -m unittest experiments.sqlite_schema_control.tests.test_protocol -v
python -m unittest experiments.sqlite_schema_control.tests.test_process_boundary -v
```
