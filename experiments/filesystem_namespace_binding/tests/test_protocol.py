import errno
import os
import tempfile
import unittest
from pathlib import Path

from experiments.filesystem_namespace_binding.protocol import (
    ContentMismatch,
    NamespaceHandle,
    NamespaceMismatch,
    NamespaceReceipt,
    PathEscape,
    UnsupportedNamespaceBoundary,
    UnsafeLexicalPublisher,
    verify_pair,
)


class NamespaceBindingTests(unittest.TestCase):
    def test_runtime_openat2_rejects_symlink_component(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "safe").mkdir()
            os.symlink(root / "safe", root / "alias")
            with self.assertRaises(PathEscape):
                NamespaceHandle.authorize_beneath(root, "alias")

    def test_runtime_openat2_rejects_dotdot_escape(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaises(PathEscape):
                NamespaceHandle.authorize_beneath(root, "../")

    def test_held_directory_fd_survives_rename_and_path_replacement(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            safe = root / "safe"
            safe.mkdir()
            with NamespaceHandle.authorize_beneath(root, "safe") as handle:
                safe.rename(root / "safe-original")
                (root / "safe").mkdir()
                receipt = handle.publish("artifact.json", b"trusted")
                self.assertEqual((root / "safe-original" / "artifact.json").read_bytes(), b"trusted")
                self.assertFalse((root / "safe" / "artifact.json").exists())
                self.assertTrue(handle.verify(receipt, expected_data=b"trusted")["durable"])

    def test_lexical_baseline_is_retargeted_by_symlink_swap(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            safe = root / "safe"
            attacker = root / "attacker"
            safe.mkdir(); attacker.mkdir()
            alias = root / "alias"
            os.symlink(safe, alias)
            unsafe = UnsafeLexicalPublisher()
            planned = unsafe.plan(alias / "artifact.json")
            alias.unlink()
            os.symlink(attacker, alias)
            receipt = unsafe.publish(planned, b"secret")
            self.assertEqual(receipt.path, planned)
            self.assertEqual((attacker / "artifact.json").read_bytes(), b"secret")
            self.assertFalse((safe / "artifact.json").exists())

    def test_receipt_for_other_directory_object_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a").mkdir(); (root / "b").mkdir()
            with NamespaceHandle.authorize_beneath(root, "a") as a, NamespaceHandle.authorize_beneath(root, "b") as b:
                receipt = a.publish("artifact.json", b"x")
                forged = NamespaceReceipt(b.directory, receipt.name, receipt.sha256, True, True)
                with self.assertRaises(NamespaceMismatch):
                    a.verify(forged, expected_data=b"x")

    def test_content_change_after_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / "safe").mkdir()
            with NamespaceHandle.authorize_beneath(root, "safe") as handle:
                receipt = handle.publish("artifact.json", b"x")
                fd = os.open("artifact.json", os.O_WRONLY | os.O_TRUNC, dir_fd=handle.fd)
                try:
                    os.write(fd, b"y")
                    os.fsync(fd)
                finally:
                    os.close(fd)
                with self.assertRaises(ContentMismatch):
                    handle.verify(receipt, expected_data=b"x")

    def test_artifact_manifest_pair_share_exact_namespace(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / "safe").mkdir()
            with NamespaceHandle.authorize_beneath(root, "safe") as handle:
                artifact = handle.publish("a.json", b"a")
                manifest = handle.publish("m.json", b"m")
                result = verify_pair(handle, artifact, manifest, artifact_data=b"a", manifest_data=b"m")
                self.assertTrue(result["namespace_bound"])
                self.assertEqual(result["directory"], handle.directory)

    def test_openat2_unavailable_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / "safe").mkdir()
            # A nonsense syscall number is expected to return ENOSYS on Linux.
            with self.assertRaises(UnsupportedNamespaceBoundary):
                NamespaceHandle.authorize_beneath(root, "safe", syscall=999999)

    def test_publication_name_cannot_escape_dirfd(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / "safe").mkdir()
            with NamespaceHandle.authorize_beneath(root, "safe") as handle:
                for name in ("../escape", "/tmp/escape", "..", "sub/name"):
                    with self.assertRaises(PathEscape):
                        handle.publish(name, b"x")


if __name__ == "__main__":
    unittest.main()
