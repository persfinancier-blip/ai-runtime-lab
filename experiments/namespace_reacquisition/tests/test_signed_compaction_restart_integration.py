import os
import shutil
import tempfile
import unittest
from pathlib import Path

from experiments.namespace_reacquisition.integration import NamespaceAuthorityUnavailable
from experiments.signed_history_compaction.protocol import SignedPrunableHistory
from experiments.signed_history_compaction.tests.test_protocol import ChainBuilder


class SignedCompactionRestartContinuityTests(unittest.TestCase):
    def layer(self, builder, archive_dir):
        return SignedPrunableHistory(
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


if __name__ == "__main__":
    unittest.main()
