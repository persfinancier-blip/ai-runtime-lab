import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.archive_publication_durability.protocol import (
    FaultPlan,
    InjectedPublicationFailure,
    PublicationError,
    PublicationReceipt,
    UnsafeRenameReceipt,
    durable_publish,
    require_durable_pair,
)


class PublicationTests(unittest.TestCase):
    def test_success_requires_file_and_directory_sync(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "archive.json"
            receipt = durable_publish(path, b"payload")
            self.assertTrue(receipt.file_synced)
            self.assertTrue(receipt.directory_synced)
            self.assertTrue(receipt.durable)
            self.assertEqual(path.read_bytes(), b"payload")
            self.assertEqual(receipt.path, os.path.abspath(path))

    def test_failure_before_file_sync_produces_no_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            fault = FaultPlan("after_write")
            with self.assertRaises(InjectedPublicationFailure):
                durable_publish(Path(td) / "archive.json", b"payload", fault=fault)
            self.assertEqual(fault.events, ["after_write"])

    def test_failure_after_file_sync_before_rename_produces_no_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "archive.json"
            fault = FaultPlan("after_file_fsync")
            with self.assertRaises(InjectedPublicationFailure):
                durable_publish(path, b"payload", fault=fault)
            self.assertFalse(path.exists())

    def test_failure_after_rename_before_directory_sync_is_not_durable_success(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "archive.json"
            fault = FaultPlan("after_rename")
            with self.assertRaises(InjectedPublicationFailure):
                durable_publish(path, b"payload", fault=fault)
            self.assertTrue(path.exists())
            self.assertNotIn("after_directory_fsync", fault.events)

    def test_failure_after_directory_sync_is_conservatively_unknown(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "archive.json"
            fault = FaultPlan("after_directory_fsync")
            with self.assertRaises(InjectedPublicationFailure):
                durable_publish(path, b"payload", fault=fault)
            self.assertTrue(path.exists())
            self.assertIn("after_directory_fsync", fault.events)

    def test_fsync_error_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with patch(
                "experiments.archive_publication_durability.protocol.os.fsync",
                side_effect=OSError("EIO"),
            ):
                with self.assertRaises(PublicationError):
                    durable_publish(Path(td) / "archive.json", b"payload")

    def test_unsafe_rename_receipt_is_rejected_by_pair_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            artifact_path = root / "artifact.json"
            manifest_path = root / "manifest.json"
            unsafe = UnsafeRenameReceipt().publish(artifact_path, b"a")
            safe = durable_publish(manifest_path, b"m")
            self.assertFalse(unsafe.durable)
            with self.assertRaises(PublicationError):
                require_durable_pair(
                    unsafe,
                    safe,
                    artifact_path=artifact_path,
                    artifact_data=b"a",
                    manifest_path=manifest_path,
                    manifest_data=b"m",
                )

    def test_pair_gate_accepts_only_exact_durable_receipts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            artifact_path = root / "artifact.json"
            manifest_path = root / "manifest.json"
            artifact = durable_publish(artifact_path, b"a")
            manifest = durable_publish(manifest_path, b"m")
            result = require_durable_pair(
                artifact,
                manifest,
                artifact_path=artifact_path,
                artifact_data=b"a",
                manifest_path=manifest_path,
                manifest_data=b"m",
            )
            self.assertTrue(result["publication_durable"])
            self.assertEqual(result["artifact_path"], os.path.abspath(artifact_path))
            self.assertEqual(result["manifest_path"], os.path.abspath(manifest_path))

    def test_pair_gate_rejects_durable_receipt_for_wrong_path(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            artifact_path = root / "artifact.json"
            manifest_path = root / "manifest.json"
            artifact = durable_publish(artifact_path, b"a")
            manifest = durable_publish(manifest_path, b"m")
            substituted = PublicationReceipt(
                path=os.path.abspath(root / "other.manifest.json"),
                sha256=manifest.sha256,
                file_synced=True,
                directory_synced=True,
            )
            with self.assertRaises(PublicationError):
                require_durable_pair(
                    artifact,
                    substituted,
                    artifact_path=artifact_path,
                    artifact_data=b"a",
                    manifest_path=manifest_path,
                    manifest_data=b"m",
                )

    def test_pair_gate_rejects_durable_receipt_for_wrong_digest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            artifact_path = root / "artifact.json"
            manifest_path = root / "manifest.json"
            artifact = durable_publish(artifact_path, b"a")
            manifest = durable_publish(manifest_path, b"m")
            substituted = PublicationReceipt(
                path=artifact.path,
                sha256=hashlib.sha256(b"different").hexdigest(),
                file_synced=True,
                directory_synced=True,
            )
            with self.assertRaises(PublicationError):
                require_durable_pair(
                    substituted,
                    manifest,
                    artifact_path=artifact_path,
                    artifact_data=b"a",
                    manifest_path=manifest_path,
                    manifest_data=b"m",
                )


if __name__ == "__main__":
    unittest.main()
