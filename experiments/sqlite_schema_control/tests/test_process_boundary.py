import json
import os
import pwd
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from experiments.sqlite_schema_control.process_boundary import UnixReadOnlyWorkerBoundary


WORKER_SCRIPT = r'''
import json, os, sqlite3, sys
from pathlib import Path
p = Path(sys.argv[1])
out = {}
try:
    q = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    out["read"] = q.execute("SELECT value FROM authority WHERE id=1").fetchone()[0]
    q.close()
except Exception as exc:
    out["read"] = f"ERROR:{type(exc).__name__}:{exc}"
for name, action in (
    ("open_rw", lambda: os.close(os.open(p, os.O_RDWR))),
    ("unlink", lambda: os.unlink(p)),
    ("rename", lambda: os.rename(p, p.with_name("attacker.db"))),
    ("chmod", lambda: os.chmod(p, 0o660)),
):
    try:
        action(); out[name] = "ALLOWED"
    except Exception as exc:
        out[name] = f"DENIED:{type(exc).__name__}"
try:
    q = sqlite3.connect(str(p))
    q.execute("UPDATE authority SET value='evil' WHERE id=1")
    q.commit(); q.close(); out["sqlite_write"] = "ALLOWED"
except Exception as exc:
    out["sqlite_write"] = f"DENIED:{type(exc).__name__}"
print(json.dumps(out, sort_keys=True))
'''


@unittest.skipUnless(os.name == "posix" and os.geteuid() == 0, "requires root Unix test principal setup")
class ProcessBoundaryTests(unittest.TestCase):
    def test_distinct_worker_principal_can_read_but_cannot_mutate_canonical_db(self):
        worker = pwd.getpwnam("nobody")
        with tempfile.TemporaryDirectory(dir="/tmp") as td:
            path = Path(td) / "authority.db"
            q = sqlite3.connect(path)
            q.execute("CREATE TABLE authority(id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
            q.execute("INSERT INTO authority VALUES(1,'trusted')")
            q.commit(); q.close()

            boundary = UnixReadOnlyWorkerBoundary.install(path, worker_gid=worker.pw_gid)
            self.assertTrue(boundary.verify())
            proc = subprocess.run(
                [sys.executable, "-c", WORKER_SCRIPT, str(path)],
                user=worker.pw_uid,
                group=worker.pw_gid,
                extra_groups=[],
                capture_output=True,
                text=True,
                check=True,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(result["read"], "trusted")
            for operation in ("open_rw", "sqlite_write", "unlink", "rename", "chmod"):
                self.assertTrue(result[operation].startswith("DENIED:"), (operation, result))

            q = sqlite3.connect(path)
            try:
                self.assertEqual(q.execute("SELECT value FROM authority WHERE id=1").fetchone()[0], "trusted")
            finally:
                q.close()
            self.assertTrue(path.exists())
            self.assertFalse(path.with_name("attacker.db").exists())

    def test_broker_uid_remains_writable_negative_control(self):
        worker = pwd.getpwnam("nobody")
        with tempfile.TemporaryDirectory(dir="/tmp") as td:
            path = Path(td) / "authority.db"
            q = sqlite3.connect(path)
            q.execute("CREATE TABLE authority(id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
            q.execute("INSERT INTO authority VALUES(1,'trusted')")
            q.commit(); q.close()
            UnixReadOnlyWorkerBoundary.install(path, worker_gid=worker.pw_gid)

            q = sqlite3.connect(path)
            q.execute("UPDATE authority SET value='broker-write' WHERE id=1")
            q.commit()
            self.assertEqual(q.execute("SELECT value FROM authority WHERE id=1").fetchone()[0], "broker-write")
            q.close()

    def test_wal_mode_is_rejected_because_worker_sidecars_are_not_owned_by_boundary(self):
        worker = pwd.getpwnam("nobody")
        with tempfile.TemporaryDirectory(dir="/tmp") as td:
            path = Path(td) / "authority.db"
            q = sqlite3.connect(path)
            self.assertEqual(q.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower(), "wal")
            q.execute("CREATE TABLE authority(id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
            q.execute("INSERT INTO authority VALUES(1,'trusted')")
            q.commit()
            q.close()

            with self.assertRaisesRegex(RuntimeError, "WAL mode is not supported"):
                UnixReadOnlyWorkerBoundary.install(path, worker_gid=worker.pw_gid)

    def test_verify_detects_broker_switch_to_wal_after_install(self):
        worker = pwd.getpwnam("nobody")
        with tempfile.TemporaryDirectory(dir="/tmp") as td:
            path = Path(td) / "authority.db"
            q = sqlite3.connect(path)
            q.execute("CREATE TABLE authority(id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
            q.execute("INSERT INTO authority VALUES(1,'trusted')")
            q.commit()
            q.close()
            boundary = UnixReadOnlyWorkerBoundary.install(path, worker_gid=worker.pw_gid)

            q = sqlite3.connect(path)
            self.assertEqual(q.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower(), "wal")
            q.close()
            with self.assertRaisesRegex(RuntimeError, "WAL mode is not supported"):
                boundary.verify()

    def test_shared_parent_directory_is_rejected_before_permission_changes(self):
        worker = pwd.getpwnam("nobody")
        with tempfile.TemporaryDirectory(dir="/tmp") as td:
            parent = Path(td)
            path = parent / "authority.db"
            sibling = parent / "unrelated.txt"
            q = sqlite3.connect(path)
            q.execute("CREATE TABLE authority(id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
            q.execute("INSERT INTO authority VALUES(1,'trusted')")
            q.commit()
            q.close()
            sibling.write_text("unrelated")
            before = parent.stat()

            with self.assertRaisesRegex(RuntimeError, "directory must be dedicated"):
                UnixReadOnlyWorkerBoundary.install(path, worker_gid=worker.pw_gid)

            after = parent.stat()
            self.assertEqual((before.st_uid, before.st_gid, before.st_mode & 0o777),
                             (after.st_uid, after.st_gid, after.st_mode & 0o777))
            self.assertEqual(sibling.read_text(), "unrelated")


if __name__ == "__main__":
    unittest.main()
