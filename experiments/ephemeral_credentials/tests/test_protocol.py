import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from experiments.ephemeral_credentials.protocol import (
    CredentialError, CredentialVault, EphemeralFile, StaleCredential,
    evidence, safe_child_env, validate_argv, validate_temp_mode,
)

SECRET = b"s3cr3t-low-entropy"


class EphemeralCredentialTests(unittest.TestCase):
    def test_argv_secret_rejected(self):
        with self.assertRaises(CredentialError):
            validate_argv(["tool", "--token", SECRET.decode()], SECRET)

    def test_ambient_environment_scrubbed(self):
        env = safe_child_env({"PATH": "/bin", "API_TOKEN": SECRET.decode(), "PASSWORD": "x"})
        self.assertEqual(env, {"PATH": "/bin"})

    def test_child_does_not_inherit_secret_environment(self):
        env = safe_child_env({**os.environ, "API_TOKEN": SECRET.decode()})
        out = subprocess.check_output(
            [sys.executable, "-c", "import os; print(os.getenv('API_TOKEN','missing'))"],
            env=env,
            text=True,
        ).strip()
        self.assertEqual(out, "missing")

    def test_ephemeral_file_is_0600_and_removed_on_success(self):
        with tempfile.TemporaryDirectory() as td:
            with EphemeralFile(SECRET, td) as path:
                validate_temp_mode(path)
                self.assertEqual(path.read_bytes(), SECRET)
            self.assertFalse(path.exists())

    def test_ephemeral_file_removed_on_failure(self):
        with tempfile.TemporaryDirectory() as td:
            path = None
            with self.assertRaises(RuntimeError):
                with EphemeralFile(SECRET, td) as path:
                    raise RuntimeError("boom")
            self.assertIsNotNone(path)
            self.assertFalse(path.exists())

    def test_bad_temp_permissions_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "cred"
            p.write_bytes(SECRET)
            p.chmod(0o644)
            with self.assertRaises(CredentialError):
                validate_temp_mode(p)

    @unittest.skipUnless(os.name == "posix", "POSIX fd inheritance semantics")
    def test_fd_not_inherited_by_default(self):
        r, w = os.pipe()
        try:
            self.assertFalse(os.get_inheritable(r))
            out = subprocess.check_output(
                [sys.executable, "-c", f"import os;\ntry: os.fstat({r}); print('open')\nexcept OSError: print('closed')"],
                close_fds=True,
                text=True,
            ).strip()
            self.assertEqual(out, "closed")
        finally:
            os.close(r); os.close(w)

    @unittest.skipUnless(os.name == "posix", "POSIX pass_fds semantics")
    def test_fd_explicit_allowlist(self):
        r, w = os.pipe()
        try:
            os.write(w, SECRET)
            os.close(w); w = -1
            out = subprocess.check_output(
                [sys.executable, "-c", f"import os; print(os.read({r}, 128).decode())"],
                pass_fds=(r,), close_fds=True, text=True,
            ).strip()
            self.assertEqual(out, SECRET.decode())
        finally:
            os.close(r)
            if w >= 0: os.close(w)

    def test_rotation_rejects_stale_generation(self):
        v = CredentialVault(b"audit-key")
        old = v.rotate("cred-A", "api.example", SECRET)
        v.rotate("cred-A", "api.example", b"new-secret")
        with self.assertRaises(StaleCredential):
            v.borrow(old)

    def test_evidence_contains_no_raw_secret(self):
        v = CredentialVault(b"audit-key")
        ref = v.rotate("cred-A", "api.example", SECRET)
        rendered = repr(evidence(ref)).encode()
        self.assertNotIn(SECRET, rendered)
        self.assertIn(b"cred-A", rendered)

    def test_unknown_retry_can_reuse_identity_not_secret_copy(self):
        v = CredentialVault(b"audit-key")
        ref = v.rotate("cred-A", "api.example", SECRET)
        first = evidence(ref)
        second = evidence(v.ref())
        self.assertEqual(first, second)
        self.assertNotIn(SECRET, repr(first).encode())

    def test_scope_change_invalidates_ref(self):
        v = CredentialVault(b"audit-key")
        old = v.rotate("cred-A", "api.example", SECRET)
        v.rotate("cred-A", "other.example", SECRET)
        with self.assertRaises(StaleCredential):
            v.borrow(old)


if __name__ == "__main__": unittest.main()
