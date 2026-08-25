# LAB-087 — SQLite schema-control boundary

This experiment makes the trust boundary behind LAB-086 explicit.

- The broker/process owns the only writable SQLite handle and database-file authority.
- Workers receive `RestrictedConnection`: a read-only URI connection plus a connection-scoped SQLite authorizer that denies DDL, ATTACH/DETACH, write PRAGMAs, and INSERT/UPDATE/DELETE.
- LAB-086 triggers remain durable stale-code/invariant guards inside the broker.
- The authorizer is defense-in-depth, **not** a database-file security boundary. The negative-control test opens another unrestricted writable connection and successfully drops a trigger and changes authority state.

Therefore deployment must enforce the outer boundary with process separation and filesystem/handle ownership so a worker cannot simply reopen the database writable or replace the broker connection's authorizer.

Run:

```bash
python -m unittest experiments.sqlite_schema_control.tests.test_protocol -v
```
