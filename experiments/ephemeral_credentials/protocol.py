from __future__ import annotations

import hashlib
import hmac
import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path


class CredentialError(RuntimeError):
    pass


class StaleCredential(CredentialError):
    pass


@dataclass(frozen=True)
class CredentialRef:
    credential_id: str
    generation: int
    scope: str
    fingerprint: str


class CredentialVault:
    def __init__(self, audit_key: bytes):
        self._audit_key = audit_key
        self._secret: bytes | None = None
        self._generation = 0
        self._scope = ""
        self._credential_id = ""

    def rotate(self, credential_id: str, scope: str, secret: bytes) -> CredentialRef:
        self._generation += 1
        self._credential_id = credential_id
        self._scope = scope
        self._secret = bytes(secret)
        return self.ref()

    def ref(self) -> CredentialRef:
        if self._secret is None:
            raise CredentialError("no active credential")
        fp = hmac.new(self._audit_key, self._secret, hashlib.sha256).hexdigest()
        return CredentialRef(self._credential_id, self._generation, self._scope, fp)

    def borrow(self, ref: CredentialRef) -> bytes:
        current = self.ref()
        if ref != current:
            raise StaleCredential("credential reference is stale or scope changed")
        assert self._secret is not None
        return self._secret


class EphemeralFile:
    def __init__(self, secret: bytes, directory: str | Path):
        self.secret = secret
        self.directory = str(directory)
        self.path: Path | None = None

    def __enter__(self) -> Path:
        fd, name = tempfile.mkstemp(prefix="cred-", dir=self.directory)
        os.fchmod(fd, stat.S_IRUSR | stat.S_IWUSR)
        with os.fdopen(fd, "wb", closefd=True) as fh:
            fh.write(self.secret)
            fh.flush()
            os.fsync(fh.fileno())
        self.path = Path(name)
        return self.path

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.path and self.path.exists():
            try:
                self.path.write_bytes(b"\x00" * self.path.stat().st_size)
            finally:
                self.path.unlink(missing_ok=True)


def safe_child_env(base: dict[str, str] | None = None) -> dict[str, str]:
    src = dict(base or {})
    deny = ("TOKEN", "SECRET", "PASSWORD", "API_KEY", "AUTHORIZATION", "CREDENTIAL")
    return {k: v for k, v in src.items() if not any(mark in k.upper() for mark in deny)}


def validate_argv(argv: list[str], secret: bytes) -> None:
    needle = secret.decode("utf-8", errors="ignore")
    if needle and any(needle in arg for arg in argv):
        raise CredentialError("raw credential present in argv")


def validate_temp_mode(path: Path) -> None:
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode != 0o600:
        raise CredentialError(f"credential file mode {oct(mode)} is not 0600")


def evidence(ref: CredentialRef) -> dict[str, object]:
    return {
        "credential_id": ref.credential_id,
        "generation": ref.generation,
        "scope": ref.scope,
        "fingerprint": ref.fingerprint,
    }


def unsafe_argv(command: str, secret: str) -> list[str]:
    return [command, "--token", secret]


def unsafe_env(secret: str) -> dict[str, str]:
    return {"API_TOKEN": secret}
