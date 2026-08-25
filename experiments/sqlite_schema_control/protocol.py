from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Sequence


class RestrictedSQLViolation(RuntimeError):
    pass


# sqlite3_set_authorizer action classes that a restricted worker must never
# receive. This is defense-in-depth on one connection, not file-level security.
_READ_ONLY_PRAGMAS = {
    "table_info",
    "table_xinfo",
    "index_list",
    "index_info",
    "foreign_key_list",
}

_DENIED_ACTIONS = {
    sqlite3.SQLITE_INSERT,
    sqlite3.SQLITE_UPDATE,
    sqlite3.SQLITE_DELETE,
    sqlite3.SQLITE_CREATE_INDEX,
    sqlite3.SQLITE_CREATE_TABLE,
    sqlite3.SQLITE_CREATE_TEMP_INDEX,
    sqlite3.SQLITE_CREATE_TEMP_TABLE,
    sqlite3.SQLITE_CREATE_TEMP_TRIGGER,
    sqlite3.SQLITE_CREATE_TEMP_VIEW,
    sqlite3.SQLITE_CREATE_TRIGGER,
    sqlite3.SQLITE_CREATE_VIEW,
    sqlite3.SQLITE_DROP_INDEX,
    sqlite3.SQLITE_DROP_TABLE,
    sqlite3.SQLITE_DROP_TEMP_INDEX,
    sqlite3.SQLITE_DROP_TEMP_TABLE,
    sqlite3.SQLITE_DROP_TEMP_TRIGGER,
    sqlite3.SQLITE_DROP_TEMP_VIEW,
    sqlite3.SQLITE_DROP_TRIGGER,
    sqlite3.SQLITE_DROP_VIEW,
    sqlite3.SQLITE_ALTER_TABLE,
    sqlite3.SQLITE_ATTACH,
    sqlite3.SQLITE_DETACH,
    sqlite3.SQLITE_REINDEX,
    sqlite3.SQLITE_ANALYZE,
    sqlite3.SQLITE_CREATE_VTABLE,
    sqlite3.SQLITE_DROP_VTABLE,
}


class RestrictedConnection:
    """Read/query-only SQLite handle for an unprivileged worker.

    The underlying connection is opened read-only *and* carries an authorizer.
    The wrapper deliberately does not expose ``set_authorizer`` or the raw
    connection. This narrows accidental/stale-code authority inside a worker.

    It is not a same-process sandbox: code with arbitrary Python introspection,
    filesystem access, or permission to open another writable SQLite connection
    is outside this boundary. The broker/process owns the only writable handle.
    """

    __slots__ = ("__conn",)

    def __init__(self, path: str | Path):
        resolved = Path(path).absolute()
        uri = f"file:{resolved.as_posix()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.set_authorizer(self._authorize)
        object.__setattr__(self, "_RestrictedConnection__conn", conn)

    @staticmethod
    def _authorize(action, arg1, arg2, database, source):
        if action in _DENIED_ACTIONS:
            return sqlite3.SQLITE_DENY
        # PRAGMA callback arguments do not reliably encode read-vs-write:
        # table_info(authority), for example, passes "authority" as arg2.
        # Use an explicit read-only allowlist instead of guessing from arg2.
        if action == sqlite3.SQLITE_PRAGMA:
            return sqlite3.SQLITE_OK if str(arg1).lower() in _READ_ONLY_PRAGMAS else sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    def execute(self, sql: str, parameters: Sequence | None = None):
        conn = object.__getattribute__(self, "_RestrictedConnection__conn")
        try:
            if parameters is None:
                return conn.execute(sql)
            return conn.execute(sql, parameters)
        except sqlite3.DatabaseError as exc:
            text = str(exc).lower()
            if "not authorized" in text or "authorization denied" in text or "readonly" in text:
                raise RestrictedSQLViolation(str(exc)) from exc
            raise

    def query_all(self, sql: str, parameters: Sequence | None = None):
        return self.execute(sql, parameters).fetchall()

    def close(self):
        conn = object.__getattribute__(self, "_RestrictedConnection__conn")
        conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


class BrokerOwnedDatabase:
    """Explicit trust contract for the writable SQLite handle.

    The owner/broker creates and retains the writable connection. Workers are
    given only ``RestrictedConnection`` instances. File/process permissions must
    ensure workers cannot independently reopen the database writable.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path).absolute()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._owner = sqlite3.connect(str(self.path))

    @property
    def owner_connection(self) -> sqlite3.Connection:
        return self._owner

    def restricted(self) -> RestrictedConnection:
        # Make prior owner commits visible before handing out a reader.
        self._owner.commit()
        return RestrictedConnection(self.path)

    def close(self):
        self._owner.close()
