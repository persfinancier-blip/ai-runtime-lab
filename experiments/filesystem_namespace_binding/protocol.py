from __future__ import annotations

import ctypes
import errno
import hashlib
import os
import secrets
from dataclasses import dataclass
from pathlib import Path


SYS_OPENAT2 = 437  # Linux x86_64/aarch64/generic syscall number.
RESOLVE_NO_XDEV = 0x01
RESOLVE_NO_MAGICLINKS = 0x02
RESOLVE_NO_SYMLINKS = 0x04
RESOLVE_BENEATH = 0x08


class NamespaceError(RuntimeError):
    pass


class UnsupportedNamespaceBoundary(NamespaceError):
    pass


class PathEscape(NamespaceError):
    pass


class NamespaceMismatch(NamespaceError):
    pass


class ContentMismatch(NamespaceError):
    pass


class OpenHow(ctypes.Structure):
    _fields_ = [
        ("flags", ctypes.c_uint64),
        ("mode", ctypes.c_uint64),
        ("resolve", ctypes.c_uint64),
    ]


@dataclass(frozen=True)
class DirectoryIdentity:
    st_dev: int
    st_ino: int


@dataclass(frozen=True)
class NamespaceReceipt:
    directory: DirectoryIdentity
    name: str
    sha256: str
    file_synced: bool
    directory_synced: bool

    @property
    def durable(self):
        return self.file_synced and self.directory_synced


def _identity(fd: int) -> DirectoryIdentity:
    st = os.fstat(fd)
    return DirectoryIdentity(st.st_dev, st.st_ino)


def _validate_name(name: str) -> str:
    if type(name) is not str or not name or name in {".", ".."} or "/" in name or "\x00" in name:
        raise PathEscape("publication name must be one relative basename")
    return name


def _openat2(dirfd: int, relative: str, *, no_xdev=False, syscall=SYS_OPENAT2) -> int:
    if os.name != "posix" or not hasattr(os, "O_DIRECTORY"):
        raise UnsupportedNamespaceBoundary("Linux/POSIX directory-FD reference required")
    if type(relative) is not str or not relative or relative.startswith("/"):
        raise PathEscape("authorized path must be relative")
    resolve = RESOLVE_BENEATH | RESOLVE_NO_SYMLINKS | RESOLVE_NO_MAGICLINKS
    if no_xdev:
        resolve |= RESOLVE_NO_XDEV
    how = OpenHow(
        os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC,
        0,
        resolve,
    )
    libc = ctypes.CDLL(None, use_errno=True)
    result = libc.syscall(
        syscall,
        dirfd,
        os.fsencode(relative),
        ctypes.byref(how),
        ctypes.sizeof(how),
    )
    if result < 0:
        error = ctypes.get_errno()
        if error == errno.ENOSYS:
            raise UnsupportedNamespaceBoundary("openat2 unavailable")
        if error in {errno.EXDEV, errno.ELOOP}:
            raise PathEscape(os.strerror(error))
        raise NamespaceError(os.strerror(error))
    return int(result)


class NamespaceHandle:
    """Stable authority for one archive directory object.

    The path used to obtain the handle is diagnostic only after acquisition.
    All consequential operations are relative to the held directory FD.
    """

    def __init__(self, fd: int, *, diagnostic_path: str):
        self.fd = fd
        self.diagnostic_path = diagnostic_path
        self.directory = _identity(fd)
        self.closed = False

    @classmethod
    def authorize_beneath(
        cls,
        trusted_root,
        relative: str,
        *,
        no_xdev=False,
        syscall=SYS_OPENAT2,
    ):
        root_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | getattr(os, "O_NOFOLLOW", 0)
        try:
            rootfd = os.open(trusted_root, root_flags)
        except OSError as exc:
            raise NamespaceError(str(exc)) from exc
        try:
            fd = _openat2(rootfd, relative, no_xdev=no_xdev, syscall=syscall)
        finally:
            os.close(rootfd)
        return cls(
            fd,
            diagnostic_path=os.path.abspath(os.path.join(os.fspath(trusted_root), relative)),
        )

    def close(self):
        if not self.closed:
            os.close(self.fd)
            self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def _check_open(self):
        if self.closed:
            raise NamespaceError("namespace handle is closed")
        if _identity(self.fd) != self.directory:
            raise NamespaceMismatch("directory FD identity changed")

    def publish(self, name: str, data: bytes) -> NamespaceReceipt:
        self._check_open()
        name = _validate_name(name)
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        temp_name = f".{name}.{secrets.token_hex(8)}.tmp"
        descriptor = None
        temp_exists = False
        try:
            descriptor = os.open(
                temp_name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC,
                0o600,
                dir_fd=self.fd,
            )
            temp_exists = True
            with os.fdopen(descriptor, "wb", closefd=True) as handle:
                descriptor = None
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.rename(temp_name, name, src_dir_fd=self.fd, dst_dir_fd=self.fd)
            temp_exists = False
            os.fsync(self.fd)
            receipt = NamespaceReceipt(
                directory=self.directory,
                name=name,
                sha256=hashlib.sha256(data).hexdigest(),
                file_synced=True,
                directory_synced=True,
            )
            self.verify(receipt, expected_data=data)
            return receipt
        except OSError as exc:
            raise NamespaceError(str(exc)) from exc
        finally:
            if descriptor is not None:
                os.close(descriptor)
            if temp_exists:
                try:
                    os.unlink(temp_name, dir_fd=self.fd)
                except FileNotFoundError:
                    pass

    def verify(self, receipt: NamespaceReceipt, *, expected_data: bytes) -> dict:
        self._check_open()
        if receipt.directory != self.directory:
            raise NamespaceMismatch("receipt is for a different directory object")
        if not receipt.durable:
            raise NamespaceMismatch("receipt is not durably published")
        name = _validate_name(receipt.name)
        expected_sha = hashlib.sha256(expected_data).hexdigest()
        if receipt.sha256 != expected_sha:
            raise ContentMismatch("receipt digest mismatch")
        flags = os.O_RDONLY | os.O_CLOEXEC | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(name, flags, dir_fd=self.fd)
        except OSError as exc:
            raise ContentMismatch(str(exc)) from exc
        try:
            chunks = []
            while True:
                chunk = os.read(fd, 65536)
                if not chunk:
                    break
                chunks.append(chunk)
            actual = b"".join(chunks)
        finally:
            os.close(fd)
        if hashlib.sha256(actual).hexdigest() != expected_sha:
            raise ContentMismatch("published bytes changed")
        return {
            "directory": self.directory,
            "name": name,
            "sha256": expected_sha,
            "durable": True,
        }


def verify_pair(
    handle: NamespaceHandle,
    artifact: NamespaceReceipt,
    manifest: NamespaceReceipt,
    *,
    artifact_data: bytes,
    manifest_data: bytes,
):
    a = handle.verify(artifact, expected_data=artifact_data)
    m = handle.verify(manifest, expected_data=manifest_data)
    if a["directory"] != m["directory"]:
        raise NamespaceMismatch("artifact and manifest namespace mismatch")
    return {
        "directory": a["directory"],
        "artifact_sha256": a["sha256"],
        "manifest_sha256": m["sha256"],
        "namespace_bound": True,
    }


class UnsafeLexicalPublisher:
    """Negative baseline: authority is a path string that can be retargeted."""

    def plan(self, path):
        return os.path.abspath(os.fspath(path))

    def publish(self, planned_path: str, data: bytes):
        from experiments.archive_publication_durability.protocol import durable_publish
        return durable_publish(planned_path, data)
