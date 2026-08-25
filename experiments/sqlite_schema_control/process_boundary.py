from __future__ import annotations

import os
import stat
import sqlite3
from dataclasses import dataclass
from pathlib import Path


class FilesystemBoundaryError(RuntimeError):
    pass


@dataclass(frozen=True)
class UnixReadOnlyWorkerBoundary:
    """Unix ownership boundary for a broker-owned SQLite database.

    The broker owns the database and parent directory.  A separate worker group
    receives traverse/read permission only: directory 0750, database 0640.
    Workers running under a different UID in that group can read the database,
    but cannot modify the database file or replace/delete names in its directory.

    This is a Unix discretionary-access-control experiment, not a same-UID/root
    sandbox.  A process with the broker UID, root, CAP_DAC_OVERRIDE, or authority
    to change permissions remains outside this boundary.
    """

    path: Path
    broker_uid: int
    worker_gid: int
    directory_mode: int = 0o750
    database_mode: int = 0o640

    @staticmethod
    def _journal_mode(db: Path) -> str:
        q = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        try:
            row = q.execute("PRAGMA journal_mode").fetchone()
        finally:
            q.close()
        if row is None or not isinstance(row[0], str):
            raise FilesystemBoundaryError("unable to determine SQLite journal mode")
        return row[0].lower()

    @classmethod
    def install(cls, path: str | Path, *, worker_gid: int) -> "UnixReadOnlyWorkerBoundary":
        db = Path(path).absolute()
        parent = db.parent
        if db.is_symlink() or parent.is_symlink():
            raise FilesystemBoundaryError("symlinked database namespace is not supported")
        if not db.is_file():
            raise FilesystemBoundaryError("database file must already exist")
        if type(worker_gid) is not int or worker_gid < 0:
            raise FilesystemBoundaryError("invalid worker gid")

        if cls._journal_mode(db) == "wal":
            raise FilesystemBoundaryError("WAL mode is not supported for a live read-only worker boundary")

        uid = os.geteuid()
        os.chown(parent, uid, worker_gid)
        os.chmod(parent, 0o750)
        os.chown(db, uid, worker_gid)
        os.chmod(db, 0o640)
        boundary = cls(db, uid, worker_gid)
        boundary.verify()
        return boundary

    def verify(self) -> bool:
        db = self.path
        parent = db.parent
        ds = os.lstat(db)
        ps = os.lstat(parent)
        if stat.S_ISLNK(ds.st_mode) or stat.S_ISLNK(ps.st_mode):
            raise FilesystemBoundaryError("namespace became symlinked")
        if not stat.S_ISREG(ds.st_mode) or not stat.S_ISDIR(ps.st_mode):
            raise FilesystemBoundaryError("unexpected filesystem object type")
        if (ps.st_uid, ps.st_gid, stat.S_IMODE(ps.st_mode)) != (
            self.broker_uid, self.worker_gid, self.directory_mode
        ):
            raise FilesystemBoundaryError("parent ownership/mode drift")
        if (ds.st_uid, ds.st_gid, stat.S_IMODE(ds.st_mode)) != (
            self.broker_uid, self.worker_gid, self.database_mode
        ):
            raise FilesystemBoundaryError("database ownership/mode drift")
        # Group may traverse/read, but never write either the directory or DB.
        if self.directory_mode & 0o020 or self.database_mode & 0o020:
            raise FilesystemBoundaryError("worker group has write permission")
        if not (self.directory_mode & 0o010 and self.database_mode & 0o040):
            raise FilesystemBoundaryError("worker group lacks required read/traverse access")
        if self._journal_mode(db) == "wal":
            raise FilesystemBoundaryError("WAL mode is not supported for a live read-only worker boundary")
        return True
