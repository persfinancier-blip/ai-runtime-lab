# LAB-087 — SQLite schema-control boundary

This experiment makes the trust boundary behind LAB-086 explicit.

- The broker/process owns the only writable SQLite handle and database-file authority.
- Workers receive `RestrictedConnection`: a read-only URI connection plus a connection-scoped SQLite authorizer that denies DDL, ATTACH/DETACH, write PRAGMAs, and INSERT/UPDATE/DELETE.
- LAB-086 triggers remain durable stale-code/invariant guards inside the broker.
- The authorizer is defense-in-depth, **not** a database-file security boundary. The negative-control test opens another unrestricted writable connection and successfully drops a trigger and changes authority state.
- On Unix, `UnixReadOnlyWorkerBoundary` makes the outer file boundary concrete: a broker-owned directory is `0750` and the database is `0640`, with a distinct worker group receiving only traverse/read permission.
- A process-level regression runs a worker under a distinct UID/GID. The worker can read the canonical database but cannot open it `O_RDWR`, commit a SQLite write, unlink/rename the database name, or change its mode. The broker UID remains writable as the explicit negative control.

Therefore deployment must enforce the outer boundary with process separation and filesystem/handle ownership so a worker cannot simply reopen the database writable or replace the broker connection's authorizer. This Unix DAC slice is not a same-UID/root/capability sandbox: broker UID, root, `CAP_DAC_OVERRIDE`, permission-changing authority, and namespace-replacement authority remain outside the claim.

Run:

```bash
python -m unittest experiments.sqlite_schema_control.tests.test_protocol -v
python -m unittest experiments.sqlite_schema_control.tests.test_process_boundary -v
```
