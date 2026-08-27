from __future__ import annotations


class RestartSchemaError(RuntimeError):
    pass


def initialize_shared_anchor_schema(q) -> None:
    """Initialize LAB-080 tables without replaying a guarded singleton INSERT.

    LAB-080's historical initializer uses ``INSERT OR IGNORE`` for the metadata
    singleton. Once LAB-091 persistent ``BEFORE INSERT`` guards exist, SQLite
    executes that trigger before conflict resolution, so an otherwise harmless
    reopen aborts. The final LAB-091 surface instead creates the schema under one
    write lock, observes the singleton first, and inserts it only for a genuinely
    fresh database.

    If the singleton is missing from an already guarded database, the attempted
    insertion is intentionally left to the persistent guard and fails closed.
    """
    if q.in_transaction:
        raise RestartSchemaError("restart-safe schema initialization requires no active transaction")

    q.execute("BEGIN IMMEDIATE")
    try:
        q.execute(
            """CREATE TABLE IF NOT EXISTS shared_anchor_meta(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              reserved_position INTEGER NOT NULL CHECK(reserved_position>=0)
            )"""
        )
        q.execute(
            """CREATE TABLE IF NOT EXISTS shared_anchor_intents(
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
            )"""
        )
        q.execute(
            """CREATE TABLE IF NOT EXISTS component_anchor_watermarks(
              component_id TEXT PRIMARY KEY,
              position INTEGER NOT NULL CHECK(position>=0)
            )"""
        )

        row = q.execute(
            "SELECT singleton FROM shared_anchor_meta WHERE singleton=1"
        ).fetchone()
        if row is None:
            q.execute("INSERT INTO shared_anchor_meta VALUES(1,0)")
        q.commit()
    except Exception:
        if q.in_transaction:
            q.rollback()
        raise
