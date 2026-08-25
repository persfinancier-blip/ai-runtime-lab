# LAB-087 — SQLite authorizer boundary

Date: 2026-08-25
Issue: #166

## Question

Can SQLite connection-level authorization turn LAB-086 trigger fences into a real boundary against arbitrary same-process SQL/DDL, or is a broker/process boundary still required?

## Primary-source findings

SQLite documents `sqlite3_set_authorizer()` as a callback installed on one database connection. It is invoked while SQL is compiled/prepared and may return `SQLITE_DENY` to reject an operation. SQLite exposes action codes including `SQLITE_DROP_TRIGGER`, `SQLITE_INSERT`, `SQLITE_UPDATE`, `SQLITE_DELETE`, `SQLITE_ALTER_TABLE`, `SQLITE_ATTACH`, `SQLITE_DETACH`, and `SQLITE_PRAGMA`.

SQLite also documents three constraints that matter here:

1. authorization is connection-scoped, not database-file-scoped;
2. only one authorizer is installed per connection, and another `sqlite3_set_authorizer()` call replaces it (or NULL disables it);
3. the authorizer runs during statement preparation, not as an independent durable policy stored in the database.

Python's stdlib exposes the same mechanism as `sqlite3.Connection.set_authorizer()`.

Primary references:
- https://www.sqlite.org/c3ref/set_authorizer.html
- https://www.sqlite.org/c3ref/c_alter_table.html
- https://www.sqlite.org/security.html
- https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.set_authorizer

## Security conclusion

`set_authorizer()` is useful defense-in-depth for a **broker-owned connection** or for deliberately restricted worker connections. It can reject `DROP TRIGGER`, arbitrary DDL, and unauthorized DML before SQLite prepares those statements.

It is **not** a security boundary against an actor that can open its own unrestricted connection to the same writable SQLite file or can replace/disable the authorizer on the privileged connection. Therefore LAB-086 triggers plus per-connection authorizers cannot honestly claim protection against arbitrary same-privilege database-file writers.

The actual authority boundary should be process/handle ownership:

- one broker process owns the writable SQLite database handle and consequential authority writes;
- workers receive RPC/capability operations, not a writable database path/handle;
- worker-side SQLite handles, if any, are read-only and have an authorizer that denies schema changes and consequential DML;
- filesystem permissions/process isolation prevent workers from opening an independent writable connection to the authority DB;
- LAB-086 SQL triggers remain a durable stale-code/invariant guard inside the broker, not the outer security perimeter.

## Recommended LAB-087 implementation slice

1. Add a small connection-authorizer policy for restricted/read-only worker handles that denies schema mutation (`CREATE/DROP/ALTER`, ATTACH/DETACH, writable PRAGMAs) and authority-table INSERT/UPDATE/DELETE.
2. Add executable regressions showing `DROP TRIGGER` and direct authority DML fail on a restricted connection while SELECT remains usable.
3. Add an explicit negative control showing a separately opened unrestricted writable connection can bypass a connection authorizer. This proves why filesystem/process ownership is required.
4. Define the broker-owned writable-handle contract in code/docs and ensure normal workers are never handed the authority DB writable path/handle.
5. Keep LAB-086 claims scoped to stale/supported writers and ordinary DML under the broker-owned connection model.

## Decision

Do not attempt to make SQLite triggers or `set_authorizer()` alone the outer security boundary. Use `set_authorizer()` as defense-in-depth under a broker/process/file-permission boundary. This preserves one durable authority store while making the trust model explicit and testable.
