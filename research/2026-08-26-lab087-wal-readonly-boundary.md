# LAB-087 — WAL sidecars and the read-only worker boundary

## Question

Can the distinct-UID/GID worker boundary safely promise that a worker can read a live SQLite database while the broker retains all filesystem write authority if the database uses WAL mode?

## Primary-source constraint

SQLite's WAL documentation states that a read-only WAL database is openable only when at least one of these is true: the `-wal` and `-shm` files already exist and are readable; the process may create them in the database directory; or the connection uses the `immutable` query parameter. SQLite also documents `-wal` and `-shm` as quasi-persistent sidecars used by WAL clients. `immutable` is not an acceptable claim for a live authority database that the broker may continue to modify.

Sources:
- https://www.sqlite.org/wal.html#readonly
- https://www.sqlite.org/walformat.html

## Executed counterexample

Using the exact published pre-fix `UnixReadOnlyWorkerBoundary`, the broker created a WAL-mode database under umask `077` and kept its writable connection open. After installing the boundary:

- main DB: `0640`, broker UID, worker GID;
- `authority.db-wal`: `0600`, broker UID/GID;
- `authority.db-shm`: `0600`, broker UID/GID;
- `boundary.verify()` returned true;
- the distinct `nobody` worker failed to open the database read-only with `OperationalError: unable to open database file`.

So the old contract could claim a readable worker boundary while WAL sidecar permissions made the database unreadable.

## Decision

This LAB-087 slice fails closed on WAL rather than granting the worker directory write authority, weakening the outer filesystem boundary, or marking a live mutable authority database immutable. `UnixReadOnlyWorkerBoundary.install()` and `verify()` now reject `journal_mode=wal`. The supported deployment for this slice uses rollback-journal mode.

A future WAL-specific design would need its own explicit sidecar lifecycle, permissions, broker-open/close behavior, and concurrent-reader semantics; it is not inferred from the main DB permissions.

## Evidence

Exact published branch bytes after the fix:
- `process_boundary.py` blob `0bca65f9aa1505960d818405fb1a6f5f8d8fd4f7`;
- `tests/test_process_boundary.py` blob `e4217d8ca016713e380c7631c7d1fc042163a8b8`.

Combined exact PR slice executed locally:
- authorizer tests: 7/7 PASS;
- process/filesystem/WAL tests: 4/4 PASS;
- total: 11/11 PASS;
- compileall: PASS.

The database directory is also an explicit deployment boundary: it should be a dedicated broker-owned directory because installation changes parent ownership/mode. Shared-parent deployment is outside the supported contract.
