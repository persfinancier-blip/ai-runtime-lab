from __future__ import annotations

import hashlib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


class PublicationError(RuntimeError):
    pass


class UnsupportedDurabilityBoundary(PublicationError):
    pass


class InjectedPublicationFailure(PublicationError):
    pass


@dataclass(frozen=True)
class PublicationReceipt:
    path: str
    sha256: str
    file_synced: bool
    directory_synced: bool

    @property
    def durable(self):
        return self.file_synced and self.directory_synced


class FaultPlan:
    """Deterministic fault injector used by the LAB-064 reference tests."""

    def __init__(self, fail_at=None):
        self.fail_at = fail_at
        self.events = []

    def hit(self, event):
        self.events.append(event)
        if self.fail_at == event:
            raise InjectedPublicationFailure(event)


def _normalized_path(path) -> str:
    """Return the lexical absolute publication target used for receipt binding."""

    return os.path.abspath(os.fspath(path))


def _fsync_directory(directory: Path, *, fault: FaultPlan):
    if os.name != "posix":
        raise UnsupportedDurabilityBoundary("directory fsync reference path requires POSIX")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(directory, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    fault.hit("after_directory_fsync")


def durable_publish(path, data: bytes, *, fault: FaultPlan | None = None):
    """Publish bytes with an explicit durable namespace barrier.

    The successful receipt means this process observed:
      write -> flush -> fsync(file) -> replace -> fsync(parent directory).

    It deliberately does not claim guarantees stronger than the host OS,
    filesystem, mount/storage stack, and device implementation provide.
    """

    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fault = fault or FaultPlan()
    descriptor, temp_name = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    temp_exists = True
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            fault.hit("after_write")
            handle.flush()
            os.fsync(handle.fileno())
            fault.hit("after_file_fsync")
        os.replace(temp_name, path)
        temp_exists = False
        fault.hit("after_rename")
        _fsync_directory(path.parent, fault=fault)
        return PublicationReceipt(
            path=_normalized_path(path),
            sha256=hashlib.sha256(data).hexdigest(),
            file_synced=True,
            directory_synced=True,
        )
    except OSError as exc:
        raise PublicationError(str(exc)) from exc
    finally:
        if temp_exists and os.path.exists(temp_name):
            os.unlink(temp_name)


def require_durable_receipt(
    receipt: PublicationReceipt,
    *,
    expected_path,
    expected_data: bytes,
    label: str,
):
    """Bind a durability claim to the exact target namespace and content bytes."""

    if not isinstance(expected_data, bytes):
        raise TypeError("expected_data must be bytes")
    if not receipt.durable:
        raise PublicationError(f"{label} has not crossed durable publication boundary")
    expected_path_value = _normalized_path(expected_path)
    if receipt.path != expected_path_value:
        raise PublicationError(
            f"{label} durable receipt path mismatch: expected={expected_path_value!r} actual={receipt.path!r}"
        )
    expected_sha256 = hashlib.sha256(expected_data).hexdigest()
    if receipt.sha256 != expected_sha256:
        raise PublicationError(
            f"{label} durable receipt digest mismatch: expected={expected_sha256} actual={receipt.sha256}"
        )
    return {
        "path": expected_path_value,
        "sha256": expected_sha256,
        "durable": True,
    }


def require_durable_pair(
    artifact: PublicationReceipt,
    manifest: PublicationReceipt,
    *,
    artifact_path,
    artifact_data: bytes,
    manifest_path,
    manifest_data: bytes,
):
    artifact_bound = require_durable_receipt(
        artifact,
        expected_path=artifact_path,
        expected_data=artifact_data,
        label="artifact",
    )
    manifest_bound = require_durable_receipt(
        manifest,
        expected_path=manifest_path,
        expected_data=manifest_data,
        label="manifest",
    )
    return {
        "artifact_path": artifact_bound["path"],
        "artifact_sha256": artifact_bound["sha256"],
        "manifest_path": manifest_bound["path"],
        "manifest_sha256": manifest_bound["sha256"],
        "publication_durable": True,
    }


class UnsafeRenameReceipt:
    """Deliberately unsafe: treats rename as durable without syncing the directory."""

    def publish(self, path, data: bytes):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temp_name = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
        return PublicationReceipt(
            path=_normalized_path(path),
            sha256=hashlib.sha256(data).hexdigest(),
            file_synced=True,
            directory_synced=False,
        )
