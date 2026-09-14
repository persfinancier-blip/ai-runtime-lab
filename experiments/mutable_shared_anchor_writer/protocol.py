from __future__ import annotations

import contextlib
import sqlite3
from pathlib import Path


class WriterAuthorizationError(RuntimeError):
    pass


class InvalidLedgerMutation(WriterAuthorizationError):
    pass


class MutableLedgerWriter:
    """Reference LAB-091 broker-owned writable connection.

    The connection-local SQL function is not a standalone security boundary. The
    trusted broker/process owns the only writable handle (LAB-087 boundary) and
    does not expose arbitrary function registration or raw DML to workers. These
    triggers are defense-in-depth against accidental/stale DML on that handle.
    """

    def __init__(self, path: str | Path):
        self.path = str(path)
        self._authorized = False
        self._con = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        self._con.execute("PRAGMA busy_timeout=5000")
        self._con.create_function(
            "lab091_writer_authorized", 0, lambda: 1 if self._authorized else 0
        )
        self._install_schema_and_guards()

    @property
    def connection(self):
        """Reference-only inspection hook; production broker must not expose it."""
        return self._con

    def close(self):
        self._con.close()

    def _install_schema_and_guards(self):
        q = self._con
        q.executescript(
            """
            CREATE TABLE IF NOT EXISTS shared_anchor_meta(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              reserved_position INTEGER NOT NULL CHECK(reserved_position>=0)
            );
            INSERT OR IGNORE INTO shared_anchor_meta VALUES(1,0);
            CREATE TABLE IF NOT EXISTS shared_anchor_intents(
              intent_id TEXT PRIMARY KEY,
              component_id TEXT NOT NULL,
              intent_type TEXT NOT NULL,
              payload_digest TEXT NOT NULL,
              provider_id TEXT NOT NULL,
              provider_generation INTEGER NOT NULL,
              predecessor_position INTEGER NOT NULL,
              position INTEGER NOT NULL UNIQUE,
              request_id TEXT NOT NULL UNIQUE,
              status TEXT NOT NULL CHECK(status IN ('PREPARED','CONFIRMED')),
              receipt_binding TEXT
            );
            CREATE TABLE IF NOT EXISTS component_anchor_watermarks(
              component_id TEXT PRIMARY KEY,
              position INTEGER NOT NULL CHECK(position>=0)
            );
            CREATE TABLE IF NOT EXISTS asymmetric_provider_receipts(
              request_id TEXT PRIMARY KEY,
              provider_id TEXT NOT NULL,
              generation INTEGER NOT NULL,
              position INTEGER NOT NULL,
              kind TEXT NOT NULL,
              stable_binding TEXT NOT NULL
            );
            """
        )
        for name in (
            "lab091_meta_no_insert", "lab091_meta_authorized_update", "lab091_meta_no_delete",
            "lab091_intent_authorized_insert", "lab091_intent_authorized_update", "lab091_intent_no_delete",
            "lab091_watermark_authorized_insert", "lab091_watermark_authorized_update", "lab091_watermark_no_delete",
            "lab091_receipt_authorized_insert", "lab091_receipt_no_update", "lab091_receipt_no_delete",
        ):
            q.execute(f"DROP TRIGGER IF EXISTS {name}")
        q.executescript(
            """
            CREATE TRIGGER lab091_meta_no_insert BEFORE INSERT ON shared_anchor_meta
            BEGIN SELECT RAISE(ABORT,'LAB-091 meta singleton already initialized'); END;
            CREATE TRIGGER lab091_meta_authorized_update BEFORE UPDATE ON shared_anchor_meta
            WHEN lab091_writer_authorized()!=1
            BEGIN SELECT RAISE(ABORT,'LAB-091 meta update requires broker writer'); END;
            CREATE TRIGGER lab091_meta_no_delete BEFORE DELETE ON shared_anchor_meta
            BEGIN SELECT RAISE(ABORT,'LAB-091 meta cannot be deleted'); END;

            CREATE TRIGGER lab091_intent_authorized_insert BEFORE INSERT ON shared_anchor_intents
            WHEN lab091_writer_authorized()!=1
              OR EXISTS(SELECT 1 FROM shared_anchor_intents WHERE intent_id=NEW.intent_id OR request_id=NEW.request_id OR position=NEW.position)
            BEGIN SELECT RAISE(ABORT,'LAB-091 intent creation requires a fresh broker-authorized identity'); END;
            CREATE TRIGGER lab091_intent_authorized_update BEFORE UPDATE ON shared_anchor_intents
            WHEN lab091_writer_authorized()!=1
              OR OLD.status!='PREPARED' OR NEW.status!='CONFIRMED'
              OR NEW.intent_id IS NOT OLD.intent_id
              OR NEW.component_id IS NOT OLD.component_id
              OR NEW.intent_type IS NOT OLD.intent_type
              OR NEW.payload_digest IS NOT OLD.payload_digest
              OR NEW.provider_id IS NOT OLD.provider_id
              OR NEW.provider_generation IS NOT OLD.provider_generation
              OR NEW.predecessor_position IS NOT OLD.predecessor_position
              OR NEW.position IS NOT OLD.position
              OR NEW.request_id IS NOT OLD.request_id
              OR OLD.receipt_binding IS NOT NULL
              OR NEW.receipt_binding IS NULL
            BEGIN SELECT RAISE(ABORT,'LAB-091 invalid intent transition'); END;
            CREATE TRIGGER lab091_intent_no_delete BEFORE DELETE ON shared_anchor_intents
            BEGIN SELECT RAISE(ABORT,'LAB-091 intent history cannot be deleted'); END;

            CREATE TRIGGER lab091_watermark_authorized_insert BEFORE INSERT ON component_anchor_watermarks
            WHEN lab091_writer_authorized()!=1
              OR EXISTS(SELECT 1 FROM component_anchor_watermarks WHERE component_id=NEW.component_id)
            BEGIN SELECT RAISE(ABORT,'LAB-091 watermark creation requires a fresh broker-authorized component'); END;
            CREATE TRIGGER lab091_watermark_authorized_update BEFORE UPDATE ON component_anchor_watermarks
            WHEN lab091_writer_authorized()!=1 OR NEW.component_id IS NOT OLD.component_id OR NEW.position<OLD.position
            BEGIN SELECT RAISE(ABORT,'LAB-091 invalid watermark transition'); END;
            CREATE TRIGGER lab091_watermark_no_delete BEFORE DELETE ON component_anchor_watermarks
            BEGIN SELECT RAISE(ABORT,'LAB-091 watermark cannot be deleted'); END;

            CREATE TRIGGER lab091_receipt_authorized_insert BEFORE INSERT ON asymmetric_provider_receipts
            WHEN lab091_writer_authorized()!=1
              OR EXISTS(SELECT 1 FROM asymmetric_provider_receipts WHERE request_id=NEW.request_id)
            BEGIN SELECT RAISE(ABORT,'LAB-091 provider receipt creation requires a fresh broker-authorized request'); END;
            CREATE TRIGGER lab091_receipt_no_update BEFORE UPDATE ON asymmetric_provider_receipts
            BEGIN SELECT RAISE(ABORT,'LAB-091 provider receipt is immutable'); END;
            CREATE TRIGGER lab091_receipt_no_delete BEFORE DELETE ON asymmetric_provider_receipts
            BEGIN SELECT RAISE(ABORT,'LAB-091 provider receipt cannot be deleted'); END;
            """
        )

    @contextlib.contextmanager
    def _write_txn(self):
        if self._authorized:
            raise WriterAuthorizationError("nested writer authorization")
        q = self._con
        q.execute("BEGIN IMMEDIATE")
        self._authorized = True
        try:
            yield q
            self._authorized = False
            q.commit()
        except Exception:
            self._authorized = False
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            self._authorized = False

    def reserve(self, row):
        with self._write_txn() as q:
            q.execute("INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'PREPARED',NULL)", row)
            predecessor, position = row[6], row[7]
            changed = q.execute(
                "UPDATE shared_anchor_meta SET reserved_position=? WHERE singleton=1 AND reserved_position=?",
                (position, predecessor),
            ).rowcount
            if changed != 1:
                raise InvalidLedgerMutation("reserved tail changed")

    def confirm(self, intent_id, receipt_binding):
        with self._write_txn() as q:
            changed = q.execute(
                "UPDATE shared_anchor_intents SET status='CONFIRMED',receipt_binding=? WHERE intent_id=?",
                (receipt_binding, intent_id),
            ).rowcount
            if changed != 1:
                raise InvalidLedgerMutation("intent absent")

    def advance_watermark(self, component_id, old_position, new_position):
        if new_position < old_position:
            raise InvalidLedgerMutation("watermark rollback")
        with self._write_txn() as q:
            row = q.execute(
                "SELECT position FROM component_anchor_watermarks WHERE component_id=?", (component_id,)
            ).fetchone()
            if row is None:
                if old_position != 0:
                    raise InvalidLedgerMutation("watermark predecessor absent")
                q.execute("INSERT INTO component_anchor_watermarks VALUES(?,?)", (component_id, new_position))
            else:
                if row[0] != old_position:
                    raise InvalidLedgerMutation("watermark changed")
                q.execute(
                    "UPDATE component_anchor_watermarks SET position=? WHERE component_id=? AND position=?",
                    (new_position, component_id, old_position),
                )

    def record_receipt(self, row):
        with self._write_txn() as q:
            q.execute("INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?)", row)
