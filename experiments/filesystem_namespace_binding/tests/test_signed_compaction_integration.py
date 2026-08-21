import os
import tempfile
import unittest
from pathlib import Path

from experiments.filesystem_namespace_binding.protocol import NamespaceMismatch, PathEscape
from experiments.namespace_reacquisition.integration import NamespaceAuthorityUnavailable
from experiments.signed_history_compaction.protocol import SignedPrunableHistory
from experiments.signed_history_compaction.tests.test_protocol import ChainBuilder


class SignedCompactionNamespaceIntegrationTests(unittest.TestCase):
    def layer(self, builder, archive_dir):
        return SignedPrunableHistory(builder.store, archive_dir, checkpoint_key=b"cp-key", external_anchor_id="anchor-A")

    def assert_uncompacted(self, layer, sequence=4):
        self.assertEqual(layer.live_transition_count(), sequence)
        self.assertEqual(layer.verify_restart()["sequence"], sequence)

    def test_normal_compaction_is_namespace_bound_and_auditable(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); builder = ChainBuilder(td / "db").append(4); layer = self.layer(builder, td / "archives")
            manifest = layer.compact(layer.create_checkpoint())
            self.assertEqual(layer.live_transition_count(), 0)
            self.assertEqual(layer.verify_restart()["sequence"], 4)
            self.assertEqual(layer.audit_archive(manifest.archive_id)["end_sequence"], 4)

    def test_archive_directory_symlink_is_rejected_at_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); builder = ChainBuilder(td / "db").append(4); attacker = td / "attacker"; attacker.mkdir(); archive = td / "archives"
            os.symlink(attacker, archive, target_is_directory=True)
            with self.assertRaises((PathEscape, NamespaceMismatch)):
                self.layer(builder, archive)
            self.assertEqual(list(attacker.iterdir()), [])

    def test_constructor_does_not_create_through_intermediate_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); builder = ChainBuilder(td / "db").append(4)
            real_parent = td / "real-parent"; real_parent.mkdir()
            alias_parent = td / "alias-parent"; os.symlink(real_parent, alias_parent, target_is_directory=True)
            with self.assertRaises(NamespaceMismatch):
                self.layer(builder, alias_parent / "archives")
            self.assertFalse((real_parent / "archives").exists())

    def test_intermediate_path_symlink_is_rejected_at_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); builder = ChainBuilder(td / "db").append(4)
            real_parent = td / "real-parent"; real_parent.mkdir(); (real_parent / "archives").mkdir()
            alias_parent = td / "alias-parent"; os.symlink(real_parent, alias_parent, target_is_directory=True)
            with self.assertRaises((PathEscape, NamespaceMismatch)):
                self.layer(builder, alias_parent / "archives")

    def test_swap_after_authorization_cannot_redirect_and_blocks_sql_commit(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); builder = ChainBuilder(td / "db").append(4); archive = td / "archives"; layer = self.layer(builder, archive); checkpoint = layer.create_checkpoint()
            original = td / "authorized-object"; attacker = td / "attacker"; attacker.mkdir()
            def swap(_handle):
                archive.rename(original); os.symlink(attacker, archive, target_is_directory=True)
            layer._after_namespace_authorized = swap
            with self.assertRaises((NamespaceMismatch, NamespaceAuthorityUnavailable)): layer.compact(checkpoint)
            self.assert_uncompacted(layer); self.assertEqual(list(attacker.iterdir()), []); self.assertTrue(original.is_dir())

    def test_swap_after_publication_receipt_fails_before_sql_commit(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); builder = ChainBuilder(td / "db").append(4); archive = td / "archives"; layer = self.layer(builder, archive); checkpoint = layer.create_checkpoint()
            original = td / "authorized-object"; attacker = td / "attacker"; attacker.mkdir(); published = {"archive_id": None}
            def swap(_handle, manifest):
                published["archive_id"] = manifest.archive_id; archive.rename(original); os.symlink(attacker, archive, target_is_directory=True)
            layer._after_namespace_published = swap
            with self.assertRaises((NamespaceMismatch, NamespaceAuthorityUnavailable)): layer.compact(checkpoint)
            self.assert_uncompacted(layer); aid = published["archive_id"]; self.assertIsNotNone(aid)
            self.assertTrue((original / f"{aid}.json").exists()); self.assertTrue((original / f"{aid}.manifest.json").exists()); self.assertEqual(list(attacker.iterdir()), [])

    def test_relative_archive_path_is_bound_at_construction_across_chdir(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); original_cwd = Path.cwd(); creator = td / "creator"; later = td / "later"
            creator.mkdir(); later.mkdir()
            try:
                os.chdir(creator)
                builder = ChainBuilder(td / "db").append(4)
                layer = self.layer(builder, Path("archives"))
                expected_archive_dir = creator / "archives"
                os.chdir(later)
                (later / "archives").mkdir()
                manifest = layer.compact(layer.create_checkpoint())
                self.assertTrue((expected_archive_dir / f"{manifest.archive_id}.json").exists())
                self.assertTrue((expected_archive_dir / f"{manifest.archive_id}.manifest.json").exists())
                self.assertEqual(list((later / "archives").iterdir()), [])
            finally:
                os.chdir(original_cwd)

    def test_directory_identity_is_stable_across_rename_without_path_retarget(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); archive = td / "archives"; archive.mkdir()
            from experiments.filesystem_namespace_binding.protocol import NamespaceHandle
            handle = NamespaceHandle.authorize_beneath(td, "archives")
            try:
                before = handle.directory; archive.rename(td / "renamed"); self.assertEqual(handle.directory, before)
                receipt = handle.publish("probe.bin", b"probe"); self.assertTrue(receipt.durable); self.assertTrue((td / "renamed" / "probe.bin").exists())
            finally: handle.close()


if __name__ == "__main__": unittest.main()
