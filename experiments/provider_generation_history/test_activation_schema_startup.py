from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.provider_generation_history.activation_schema_startup import (
    ActivationSchemaProvenanceStartupMixin,
    classify_activation_schema_provenance,
    require_complete_activation_schema_provenance_for_startup,
)
from experiments.provider_generation_history.activation_schema_provenance import (
    ActivationSchemaMigrationRequired,
)
from experiments.provider_generation_history.protocol import HistoricalVerificationError


class ActivationSchemaStartupTests(unittest.TestCase):
    def test_recoverable_states_require_explicit_migration(self):
        for state in (
            "LEGACY_ABSENT",
            "DDL_INSTALLED_UNMARKED",
            "DDL_INSTALLED_PREPARED",
        ):
            with self.subTest(state=state), patch(
                "experiments.provider_generation_history.activation_schema_startup."
                "classify_activation_schema_provenance",
                return_value=state,
            ):
                with self.assertRaises(ActivationSchemaMigrationRequired):
                    require_complete_activation_schema_provenance_for_startup("unused.db")

    def test_complete_allows_startup(self):
        with patch(
            "experiments.provider_generation_history.activation_schema_startup."
            "classify_activation_schema_provenance",
            return_value="COMPLETE",
        ):
            self.assertIsNone(
                require_complete_activation_schema_provenance_for_startup("unused.db")
            )

    def test_unknown_state_fails_closed(self):
        with patch(
            "experiments.provider_generation_history.activation_schema_startup."
            "classify_activation_schema_provenance",
            return_value="UNKNOWN",
        ):
            with self.assertRaises(HistoricalVerificationError):
                require_complete_activation_schema_provenance_for_startup("unused.db")

    def test_mixin_checks_before_inherited_constructor(self):
        calls = []

        class Base:
            def __init__(self, path, marker):
                calls.append((path, marker))

        class Surface(ActivationSchemaProvenanceStartupMixin, Base):
            pass

        with patch(
            "experiments.provider_generation_history.activation_schema_startup."
            "require_complete_activation_schema_provenance_for_startup",
            side_effect=ActivationSchemaMigrationRequired("explicit migration required"),
        ):
            with self.assertRaises(ActivationSchemaMigrationRequired):
                Surface("db-a", "side-effect")
        self.assertEqual(calls, [])

    def test_path_wrapper_is_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "startup.db"
            q = sqlite3.connect(path)
            q.execute("CREATE TABLE shared_anchor_intents(intent_id TEXT PRIMARY KEY)")
            q.commit()
            q.close()

            with patch(
                "experiments.provider_generation_history.activation_schema_startup."
                "classify_activation_schema_provenance_locked",
                return_value="LEGACY_ABSENT",
            ) as classifier:
                self.assertEqual(
                    classify_activation_schema_provenance(path), "LEGACY_ABSENT"
                )
                self.assertEqual(classifier.call_count, 1)

            q = sqlite3.connect(path)
            try:
                self.assertEqual(
                    q.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                    ).fetchall(),
                    [("shared_anchor_intents",)],
                )
            finally:
                q.close()


if __name__ == "__main__":
    unittest.main()
