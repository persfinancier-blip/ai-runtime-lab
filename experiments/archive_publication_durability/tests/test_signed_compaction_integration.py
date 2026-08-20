import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from experiments.archive_publication_durability.protocol import (
    PublicationError,
    PublicationReceipt,
)
from experiments.signed_history_compaction.protocol import SignedPrunableHistory
from experiments.signed_history_compaction.tests.test_protocol import ChainBuilder


class SignedCompactionDurabilityIntegrationTests(unittest.TestCase):
    def layer(self, builder, archive_dir):
        return SignedPrunableHistory(
            builder.store,
            archive_dir,
            checkpoint_key=b"cp-key",
            external_anchor_id="anchor-A",
        )

    def assert_uncompacted(self, layer, sequence=4):
        self.assertEqual(layer.live_transition_count(), sequence)
        self.assertEqual(layer.verify_restart()["sequence"], sequence)

    def test_normal_compaction_requires_and_obtains_durable_publication(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(4)
            layer = self.layer(builder, td / "archives")
            manifest = layer.compact(layer.create_checkpoint())
            self.assertEqual(layer.live_transition_count(), 0)
            self.assertEqual(layer.verify_restart()["sequence"], 4)
            self.assertEqual(layer.audit_archive(manifest.archive_id)["end_sequence"], 4)

    def test_sql_commit_is_blocked_if_manifest_lacks_directory_sync(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(4)
            layer = self.layer(builder, td / "archives")
            checkpoint = layer.create_checkpoint()
            original = layer._atomic_file
            calls = {"count": 0}

            def incomplete(path, data):
                calls["count"] += 1
                receipt = original(path, data)
                if calls["count"] == 2:
                    return PublicationReceipt(
                        path=receipt.path,
                        sha256=receipt.sha256,
                        file_synced=True,
                        directory_synced=False,
                    )
                return receipt

            layer._atomic_file = incomplete
            with self.assertRaises(PublicationError):
                layer.compact(checkpoint)
            self.assert_uncompacted(layer)

    def test_sql_commit_is_blocked_if_artifact_lacks_directory_sync(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(4)
            layer = self.layer(builder, td / "archives")
            checkpoint = layer.create_checkpoint()
            original = layer._atomic_file
            calls = {"count": 0}

            def incomplete(path, data):
                calls["count"] += 1
                receipt = original(path, data)
                if calls["count"] == 1:
                    return PublicationReceipt(
                        path=receipt.path,
                        sha256=receipt.sha256,
                        file_synced=True,
                        directory_synced=False,
                    )
                return receipt

            layer._atomic_file = incomplete
            with self.assertRaises(PublicationError):
                layer.compact(checkpoint)
            self.assert_uncompacted(layer)

    def test_sql_commit_is_blocked_by_durable_manifest_receipt_for_wrong_path(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(4)
            layer = self.layer(builder, td / "archives")
            checkpoint = layer.create_checkpoint()
            original = layer._atomic_file
            calls = {"count": 0}

            def substituted(path, data):
                calls["count"] += 1
                receipt = original(path, data)
                if calls["count"] == 2:
                    return PublicationReceipt(
                        path=os.path.abspath(Path(path).with_name("other.manifest.json")),
                        sha256=receipt.sha256,
                        file_synced=True,
                        directory_synced=True,
                    )
                return receipt

            layer._atomic_file = substituted
            with self.assertRaises(PublicationError):
                layer.compact(checkpoint)
            self.assert_uncompacted(layer)

    def test_sql_commit_is_blocked_by_durable_artifact_receipt_for_wrong_digest(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(4)
            layer = self.layer(builder, td / "archives")
            checkpoint = layer.create_checkpoint()
            original = layer._atomic_file
            calls = {"count": 0}

            def substituted(path, data):
                calls["count"] += 1
                receipt = original(path, data)
                if calls["count"] == 1:
                    return PublicationReceipt(
                        path=receipt.path,
                        sha256=hashlib.sha256(b"wrong artifact bytes").hexdigest(),
                        file_synced=True,
                        directory_synced=True,
                    )
                return receipt

            layer._atomic_file = substituted
            with self.assertRaises(PublicationError):
                layer.compact(checkpoint)
            self.assert_uncompacted(layer)

    def test_sql_commit_is_blocked_by_durable_manifest_receipt_for_wrong_digest(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(4)
            layer = self.layer(builder, td / "archives")
            checkpoint = layer.create_checkpoint()
            original = layer._atomic_file
            calls = {"count": 0}

            def substituted(path, data):
                calls["count"] += 1
                receipt = original(path, data)
                if calls["count"] == 2:
                    return PublicationReceipt(
                        path=receipt.path,
                        sha256=hashlib.sha256(b"wrong manifest bytes").hexdigest(),
                        file_synced=True,
                        directory_synced=True,
                    )
                return receipt

            layer._atomic_file = substituted
            with self.assertRaises(PublicationError):
                layer.compact(checkpoint)
            self.assert_uncompacted(layer)


if __name__ == "__main__":
    unittest.main()
