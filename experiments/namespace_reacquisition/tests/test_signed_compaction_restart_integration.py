import os
import shutil
import tempfile
import unittest
from pathlib import Path

from experiments.filesystem_namespace_binding.protocol import NamespaceMismatch
from experiments.namespace_reacquisition.integration import NamespaceAuthorityUnavailable
from experiments.namespace_reacquisition.protocol import issue_migration
from experiments.signed_history_compaction.protocol import SignedPrunableHistory
from experiments.signed_history_compaction.tests.test_protocol import ChainBuilder


class SignedCompactionRestartContinuityTests(unittest.TestCase):
    def layer(self, builder, archive_dir, cls=SignedPrunableHistory):
        return cls(
            builder.store, archive_dir, checkpoint_key=b"cp-key", external_anchor_id="anchor-A"
        )

    def test_unchanged_restart_reacquires_before_compaction(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(4)
            archive = td / "archives"
            first = self.layer(builder, archive)
            self.assertEqual(first.namespace_reacquisition_status["status"], "REACQUIRED")
            del first
            restarted = self.layer(builder, archive)
            self.assertEqual(restarted.namespace_reacquisition_status["status"], "REACQUIRED")
            manifest = restarted.compact(restarted.create_checkpoint())
            self.assertEqual(restarted.audit_archive(manifest.archive_id)["end_sequence"], 4)

    def test_missing_directory_restart_does_not_recreate_authority(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(4)
            archive = td / "archives"
            first = self.layer(builder, archive)
            detached = td / "detached"
            archive.rename(detached)
            self.assertFalse(archive.exists())
            restarted = self.layer(builder, archive)
            self.assertFalse(archive.exists(), "restart silently recreated detached namespace")
            self.assertNotEqual(restarted.namespace_reacquisition_status["status"], "REACQUIRED")
            with self.assertRaises(NamespaceAuthorityUnavailable):
                restarted.compact(restarted.create_checkpoint())

    def test_byte_identical_directory_replacement_blocks_compaction(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(4)
            archive = td / "archives"
            first = self.layer(builder, archive)
            (archive / "copied.bin").write_bytes(b"same bytes")
            old = td / "old-archive-object"
            archive.rename(old)
            shutil.copytree(old, archive)
            restarted = self.layer(builder, archive)
            self.assertNotEqual(restarted.namespace_reacquisition_status["status"], "REACQUIRED")
            with self.assertRaises(NamespaceAuthorityUnavailable):
                restarted.compact(restarted.create_checkpoint())
            self.assertEqual(restarted.live_transition_count(), 4)

    def test_replacement_after_successful_restart_is_rechecked(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(4)
            archive = td / "archives"
            layer = self.layer(builder, archive)
            self.assertEqual(layer.require_namespace_authority().namespace_generation, 1)
            old = td / "old"
            archive.rename(old)
            shutil.copytree(old, archive)
            with self.assertRaises(NamespaceAuthorityUnavailable):
                layer.require_namespace_authority()
            with self.assertRaises(NamespaceAuthorityUnavailable):
                layer.compact(layer.create_checkpoint())

    def test_symlink_replacement_cannot_be_reopened_as_authority(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(4)
            archive = td / "archives"
            first = self.layer(builder, archive)
            old = td / "old-archive-object"
            attacker = td / "attacker"
            attacker.mkdir()
            archive.rename(old)
            os.symlink(attacker, archive, target_is_directory=True)
            with self.assertRaises(Exception):
                self.layer(builder, archive)
            self.assertEqual(list(attacker.iterdir()), [])

    def test_authenticated_relocation_advances_generation_and_compacts(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(4)
            archive = td / "archives"
            new_archive = td / "archives-v2"
            new_archive.mkdir()
            layer = self.layer(builder, archive)
            old = layer.require_namespace_authority()
            permit = issue_migration(old, new_archive, 2, layer.key)
            record = layer.migrate_archive_namespace(permit)
            self.assertEqual(record.namespace_generation, 2)
            self.assertEqual(layer.namespace_generation, 2)
            self.assertEqual(Path(record.archive_path), new_archive)
            manifest = layer.compact(layer.create_checkpoint())
            self.assertTrue(all(path.exists() for path in layer._archive_paths(manifest.archive_id)))

    def test_generation_change_after_publication_rejects_stale_receipts(self):
        class MigratingLayer(SignedPrunableHistory):
            migrated = False

            def _after_namespace_published(self, handle, manifest):
                if self.migrated:
                    return
                target = Path(self.archive_dir).parent / "archives-v2"
                target.mkdir(exist_ok=True)
                old = self.require_namespace_authority()
                permit = issue_migration(old, target, old.namespace_generation + 1, self.key)
                self.migrate_archive_namespace(permit)
                self.migrated = True

        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(4)
            layer = self.layer(builder, td / "archives", cls=MigratingLayer)
            with self.assertRaises((NamespaceMismatch, NamespaceAuthorityUnavailable)):
                layer.compact(layer.create_checkpoint())
            self.assertEqual(layer.namespace_generation, 2)
            self.assertEqual(layer.live_transition_count(), 4)


if __name__ == "__main__":
    unittest.main()
