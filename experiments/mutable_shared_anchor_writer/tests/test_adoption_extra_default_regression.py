from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.mutable_shared_anchor_writer.adoption_extra_columns import (
    AdoptionExtraColumnError,
    validate_no_required_extra_columns,
)


def _create_legacy_schema(path: Path, extra_sql: str, register_legacy_function: bool = False):
    q = sqlite3.connect(path)
    try:
        if register_legacy_function:
            q.create_function("legacy_only", 0, lambda: "legacy", deterministic=True)
        q.execute(
            "CREATE TABLE shared_anchor_meta("
            "singleton INTEGER PRIMARY KEY, reserved_position INTEGER NOT NULL)"
        )
        q.execute(
            """CREATE TABLE shared_anchor_intents(
              intent_id TEXT PRIMARY KEY,
              component_id TEXT NOT NULL,
              intent_type TEXT NOT NULL,
              payload_digest TEXT NOT NULL,
              provider_id TEXT NOT NULL,
              provider_generation INTEGER NOT NULL,
              predecessor_position INTEGER NOT NULL,
              position INTEGER NOT NULL UNIQUE,
              request_id TEXT NOT NULL UNIQUE,
              status TEXT NOT NULL,
              receipt_binding TEXT,
              %s
            )""" % extra_sql
        )
        q.execute(
            "CREATE TABLE component_anchor_watermarks("
            "component_id TEXT PRIMARY KEY, position INTEGER NOT NULL)"
        )
        q.execute(
            """CREATE TABLE asymmetric_provider_receipts(
              request_id TEXT PRIMARY KEY,
              provider_id TEXT NOT NULL,
              generation INTEGER NOT NULL,
              position INTEGER NOT NULL,
              kind TEXT NOT NULL,
              challenge TEXT NOT NULL,
              signature TEXT NOT NULL,
              stable_binding TEXT NOT NULL
            )"""
        )
        q.commit()
    finally:
        q.close()


class AdoptionExtraDefaultRegressionTests(unittest.TestCase):
    def _validate(self, path: Path):
        q = sqlite3.connect(path)
        try:
            q.execute("BEGIN IMMEDIATE")
            return validate_no_required_extra_columns(q)
        finally:
            if q.in_transaction:
                q.rollback()
            q.close()

    def test_literal_and_builtin_keyword_defaults_remain_accepted(self):
        for extra_sql in (
            "legacy_note TEXT DEFAULT 'ok'",
            "legacy_counter INTEGER DEFAULT 42",
            "legacy_stamp TEXT DEFAULT CURRENT_TIMESTAMP",
        ):
            with self.subTest(extra_sql=extra_sql), tempfile.TemporaryDirectory() as td:
                path = Path(td) / "ledger.sqlite"
                _create_legacy_schema(path, extra_sql)
                self.assertTrue(self._validate(path))

    def test_legacy_only_function_default_is_rejected_before_supported_write(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.sqlite"
            _create_legacy_schema(
                path,
                "legacy_note TEXT DEFAULT (legacy_only())",
                register_legacy_function=True,
            )

            q = sqlite3.connect(path)
            try:
                with self.assertRaisesRegex(sqlite3.OperationalError, "unknown function"):
                    q.execute(
                        """INSERT INTO shared_anchor_intents(
                          intent_id,component_id,intent_type,payload_digest,provider_id,
                          provider_generation,predecessor_position,position,request_id,
                          status,receipt_binding
                        ) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                        (
                            "i-1",
                            "component-a",
                            "ANCHOR",
                            "0" * 64,
                            "provider-a",
                            1,
                            0,
                            1,
                            "r-1",
                            "PREPARED",
                            None,
                        ),
                    )
            finally:
                q.close()

            with self.assertRaisesRegex(
                AdoptionExtraColumnError, "function-valued extra default"
            ):
                self._validate(path)


if __name__ == "__main__":
    unittest.main()
