import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from experiments.mutable_shared_anchor_writer.operation_permit import (
    PermitConnection,
    install_operation_permit_udf,
    one_shot_permit,
)
from experiments.sqlite_schema_control.process_boundary import UnixReadOnlyWorkerBoundary


WORKER_UID = 65534
WORKER_GID = 65534


class Lab087Lab091CompositionTests(unittest.TestCase):
    def make_broker_db(self, root: Path):
        db = root / "authority.db"
        q = sqlite3.connect(str(db), isolation_level=None, factory=PermitConnection)
        install_operation_permit_udf(q)
        q.executescript(
            """
            PRAGMA journal_mode=DELETE;
            CREATE TABLE shared_anchor_meta(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              reserved_position INTEGER NOT NULL
            );
            INSERT INTO shared_anchor_meta VALUES(1,0);
            CREATE TRIGGER lab091_v2_meta_exact_update
            BEFORE UPDATE ON shared_anchor_meta
            WHEN NEW.singleton IS NOT OLD.singleton
              OR NEW.reserved_position!=OLD.reserved_position+1
              OR lab091_consume_permit(
                'meta-update',CAST(OLD.singleton AS TEXT),
                CAST(OLD.reserved_position AS TEXT),CAST(NEW.reserved_position AS TEXT)
              )!=1
            BEGIN SELECT RAISE(ABORT,'LAB-091 exact meta permit required'); END;
            """
        )
        return db, q

    @staticmethod
    def run_worker(db: Path, code: str):
        env = dict(os.environ)
        env["PYTHONPATH"] = "/mnt/data/lab091_lab087_comp"

        def demote():
            os.setgroups([])
            os.setgid(WORKER_GID)
            os.setuid(WORKER_UID)

        return subprocess.run(
            [sys.executable, "-c", code, str(db)],
            env=env,
            preexec_fn=demote,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_restricted_worker_can_read_but_not_mutate_or_replace_namespace(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as td:
            root = Path(td)
            db, broker = self.make_broker_db(root)
            boundary = UnixReadOnlyWorkerBoundary.install(db, worker_gid=WORKER_GID)
            self.assertTrue(boundary.verify())

            worker = self.run_worker(
                db,
                r'''
import json, os, sqlite3, sys
from pathlib import Path
from experiments.sqlite_schema_control.protocol import RestrictedConnection, RestrictedSQLViolation

db=Path(sys.argv[1])
out={}
with RestrictedConnection(db) as q:
    out["read"] = q.query_all("SELECT reserved_position FROM shared_anchor_meta")[0][0]
    try:
        q.execute("UPDATE shared_anchor_meta SET reserved_position=999 WHERE singleton=1")
        out["restricted_update"] = "unexpected-success"
    except Exception as exc:
        out["restricted_update"] = type(exc).__name__
try:
    raw=sqlite3.connect(str(db), timeout=1)
    raw.execute("UPDATE shared_anchor_meta SET reserved_position=999 WHERE singleton=1")
    raw.commit()
    out["raw_update"] = "unexpected-success"
except Exception as exc:
    out["raw_update"] = type(exc).__name__
try:
    os.rename(db.parent, db.parent.with_name(db.parent.name+"-attacker"))
    out["rename_parent"] = "unexpected-success"
except Exception as exc:
    out["rename_parent"] = type(exc).__name__
print(json.dumps(out, sort_keys=True))
''',
            )
            self.assertEqual(worker.returncode, 0, worker.stderr)
            out = json.loads(worker.stdout)
            self.assertEqual(out["read"], 0)
            self.assertEqual(out["restricted_update"], "RestrictedSQLViolation")
            self.assertNotEqual(out["raw_update"], "unexpected-success")
            self.assertNotEqual(out["rename_parent"], "unexpected-success")

            self.assertEqual(
                broker.execute("SELECT reserved_position FROM shared_anchor_meta").fetchone()[0],
                0,
            )
            broker.close()

    def test_broker_existing_writable_handle_still_requires_exact_one_shot_permit(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as td:
            root = Path(td)
            db, broker = self.make_broker_db(root)
            UnixReadOnlyWorkerBoundary.install(db, worker_gid=WORKER_GID)

            broker.execute("BEGIN IMMEDIATE")
            with self.assertRaises(sqlite3.IntegrityError):
                broker.execute(
                    "UPDATE shared_anchor_meta SET reserved_position=1 WHERE singleton=1"
                )
            broker.rollback()

            broker.execute("BEGIN IMMEDIATE")
            with one_shot_permit(
                broker,
                kind="meta-update",
                identity="1",
                old_value="0",
                new_value="1",
            ):
                broker.execute(
                    "UPDATE shared_anchor_meta SET reserved_position=1 "
                    "WHERE singleton=1 AND reserved_position=0"
                )
            broker.commit()
            self.assertEqual(
                broker.execute("SELECT reserved_position FROM shared_anchor_meta").fetchone()[0],
                1,
            )
            broker.close()


if __name__ == "__main__":
    unittest.main()
