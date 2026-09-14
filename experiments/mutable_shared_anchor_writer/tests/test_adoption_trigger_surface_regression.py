import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.adoption_trigger_surface import (
    AdoptionTriggerSurfaceError,
    _EXPECTED_TRIGGERS_BY_TABLE,
    validate_protected_trigger_surface,
)


class AdoptionTriggerSurfaceRegressionTests(unittest.TestCase):
    def make_schema(self):
        q = sqlite3.connect(":memory:", isolation_level=None)
        q.executescript(
            """
            CREATE TABLE shared_anchor_meta(singleton INTEGER PRIMARY KEY, reserved_position INTEGER NOT NULL);
            CREATE TABLE shared_anchor_intents(intent_id TEXT PRIMARY KEY, status TEXT NOT NULL);
            CREATE TABLE component_anchor_watermarks(component_id TEXT PRIMARY KEY, position INTEGER NOT NULL);
            CREATE TABLE asymmetric_provider_receipts(request_id TEXT PRIMARY KEY);
            CREATE TABLE asymmetric_provider_head(singleton INTEGER PRIMARY KEY, generation INTEGER NOT NULL);
            INSERT INTO asymmetric_provider_head VALUES(1,1);
            """
        )
        return q

    def install_expected_names(self, q):
        for table, names in _EXPECTED_TRIGGERS_BY_TABLE.items():
            for name in names:
                q.execute(
                    f"CREATE TRIGGER {name} BEFORE DELETE ON {table} "
                    "BEGIN SELECT 1; END"
                )

    def test_exact_known_surface_is_accepted(self):
        q = self.make_schema()
        self.install_expected_names(q)
        q.execute("BEGIN IMMEDIATE")
        self.assertTrue(validate_protected_trigger_surface(q))
        q.rollback()

    def test_unknown_persisted_trigger_is_rejected(self):
        q = self.make_schema()
        self.install_expected_names(q)
        q.execute(
            """CREATE TRIGGER legacy_confused_deputy
               AFTER INSERT ON shared_anchor_intents
               BEGIN
                 UPDATE asymmetric_provider_head
                 SET generation=generation+100 WHERE singleton=1;
               END"""
        )
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaisesRegex(
            AdoptionTriggerSurfaceError,
            "unexpected=legacy_confused_deputy",
        ):
            validate_protected_trigger_surface(q)
        q.rollback()

    def test_missing_supported_trigger_is_rejected(self):
        q = self.make_schema()
        self.install_expected_names(q)
        q.execute("DROP TRIGGER lab091_v4_confirmation_requires_matching_receipt")
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaisesRegex(
            AdoptionTriggerSurfaceError,
            "missing=lab091_v4_confirmation_requires_matching_receipt",
        ):
            validate_protected_trigger_surface(q)
        q.rollback()


if __name__ == "__main__":
    unittest.main()
