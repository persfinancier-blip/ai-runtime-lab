import json
import tempfile
import unittest
from pathlib import Path

from experiments.namespace_reacquisition.protocol import issue_migration
from experiments.namespace_retirement.integration import RetirementIntegrationError
from experiments.signed_history_compaction.protocol import SignedPrunableHistory
from experiments.signed_history_compaction.tests.test_protocol import ChainBuilder


class AuthenticatedLineageTests(unittest.TestCase):
    def layer(self, builder, archive_dir):
        return SignedPrunableHistory(
            builder.store, archive_dir, checkpoint_key=b"cp-key", external_anchor_id="anchor-A"
        )

    def migrated(self, td):
        td = Path(td)
        builder = ChainBuilder(td / "db").append(4)
        old_dir = td / "v1"
        new_dir = td / "v2"
        new_dir.mkdir()
        layer = self.layer(builder, old_dir)
        layer.compact(layer.create_checkpoint())
        old = layer.require_namespace_authority()
        layer.migrate_archive_namespace(issue_migration(old, new_dir, 2, layer.key))
        return builder, layer, old_dir, new_dir, old

    def test_mutable_predecessor_column_cannot_redirect_retirement_authority(self):
        with tempfile.TemporaryDirectory() as td:
            builder, layer, old_dir, new_dir, old = self.migrated(td)
            q = builder.store._con()
            try:
                q.execute(
                    "UPDATE archive_namespace_records SET predecessor_record_id=? "
                    "WHERE generation=2",
                    ("0" * 64,),
                )
            finally:
                q.close()
            with self.assertRaises(RetirementIntegrationError):
                layer.issue_namespace_retirement_permit()
            self.assertTrue(any(old_dir.iterdir()))

    def test_migration_permit_tamper_invalidates_persisted_lineage(self):
        with tempfile.TemporaryDirectory() as td:
            builder, layer, old_dir, new_dir, old = self.migrated(td)
            q = builder.store._con()
            try:
                raw = json.loads(
                    q.execute(
                        "SELECT permit_json FROM archive_namespace_migration_intents "
                        "WHERE old_record_id=?",
                        (old.record_id,),
                    ).fetchone()[0]
                )
                raw["new_path"] = str(Path(td) / "attacker")
                q.execute(
                    "UPDATE archive_namespace_migration_intents SET permit_json=? "
                    "WHERE old_record_id=?",
                    (json.dumps(raw, sort_keys=True, separators=(",", ":")), old.record_id),
                )
            finally:
                q.close()
            with self.assertRaises(RetirementIntegrationError):
                layer.issue_namespace_retirement_permit()
            self.assertTrue(any(old_dir.iterdir()))

    def test_next_relocation_waits_for_predecessor_retirement(self):
        with tempfile.TemporaryDirectory() as td:
            builder, layer, old_dir, new_dir, old = self.migrated(td)
            v3 = Path(td) / "v3"
            v3.mkdir()
            current = layer.require_namespace_authority()
            with self.assertRaises(RetirementIntegrationError):
                layer.migrate_archive_namespace(
                    issue_migration(current, v3, current.namespace_generation + 1, layer.key)
                )
            layer.retire_superseded_namespace(layer.issue_namespace_retirement_permit())
            current = layer.require_namespace_authority()
            record = layer.migrate_archive_namespace(
                issue_migration(current, v3, current.namespace_generation + 1, layer.key)
            )
            self.assertEqual(record.namespace_generation, 3)


if __name__ == "__main__":
    unittest.main()
