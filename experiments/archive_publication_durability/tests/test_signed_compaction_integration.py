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
            self.assertEqual(layer.live_transition_count(), 4)
            self.assertEqual(layer.verify_restart()["sequence"], 4)

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
            self.assertEqual(layer.live_transition_count(), 4)
            self.assertEqual(layer.verify_restart()["sequence"], 4)


if __name__ == "__main__":
    unittest.main()
