from __future__ import annotations

import hashlib
import json
import os
import stat
from dataclasses import asdict
from pathlib import Path

from experiments.filesystem_namespace_binding.protocol import NamespaceHandle

from .protocol import (
    AuthenticationError,
    ContinuityRecord,
    HandleEvidence,
    MigrationPermit,
    ReacquisitionError,
    capture,
    migrate,
    reacquire,
    verify_record,
)


class NamespaceAuthorityUnavailable(ReacquisitionError):
    pass


def _parse_record(raw: str) -> ContinuityRecord:
    body = json.loads(raw)
    handle = body.get("handle")
    if handle is not None:
        body["handle"] = HandleEvidence(**handle)
    return ContinuityRecord(**body)


def _read_regular_at(directory_fd: int, name: str) -> bytes:
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(name, flags, dir_fd=directory_fd)
    except OSError as exc:
        raise NamespaceAuthorityUnavailable(f"cannot read migration source {name!r}: {exc}") from exc
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise NamespaceAuthorityUnavailable(f"migration source {name!r} is not a regular file")
        chunks = []
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


class RestartNamespaceContinuityMixin:
    """Persist and reacquire LAB-065 archive namespace authority across restart.

    The continuity row is authority evidence, not a cache. On first initialization
    the current namespace is captured and authenticated. On later construction the
    saved record is verified and must strongly reacquire before consequential
    compaction is allowed. A failed reacquisition is retained as an explicit status;
    callers may inspect it or perform an authenticated generation-advancing migration,
    but may not silently fall back to pathname trust.
    """

    def _init_restart_namespace_continuity(self):
        q = self.store._con()
        try:
            q.execute(
                "CREATE TABLE IF NOT EXISTS archive_namespace_continuity("
                "singleton INTEGER PRIMARY KEY CHECK(singleton=1),"
                "record_id TEXT NOT NULL, generation INTEGER NOT NULL, body_json TEXT NOT NULL)"
            )
            row = q.execute(
                "SELECT record_id,generation,body_json FROM archive_namespace_continuity WHERE singleton=1"
            ).fetchone()
            if row is None:
                record = capture(self.archive_dir, self.key, 1)
                q.execute(
                    "INSERT INTO archive_namespace_continuity VALUES(1,?,?,?)",
                    (record.record_id, record.namespace_generation,
                     json.dumps(asdict(record), sort_keys=True, separators=(",", ":"))),
                )
                self._namespace_continuity_record = record
                self._namespace_reacquisition = {
                    "status": "REACQUIRED",
                    "strength": "INITIAL_AUTHENTICATED_CAPTURE",
                    "namespace_generation": 1,
                }
            else:
                record = _parse_record(row[2])
                verify_record(record, self.key)
                if row[0] != record.record_id or row[1] != record.namespace_generation:
                    raise AuthenticationError("durable continuity row/record mismatch")
                self._namespace_continuity_record = record
                self._namespace_reacquisition = reacquire(record, self.key, require_strong=True)
        finally:
            q.close()

    @property
    def namespace_reacquisition_status(self):
        return dict(self._namespace_reacquisition)

    @property
    def namespace_generation(self):
        return self._namespace_continuity_record.namespace_generation

    def require_namespace_authority(self):
        """Re-prove current namespace identity at each consequential boundary.

        A successful restart-time observation is not a lease. The pathname can be
        replaced after construction, so compaction, publication and GC must refresh
        strong reacquisition immediately before use rather than trusting cached status.
        """
        record = self._namespace_continuity_record
        status = reacquire(record, self.key, require_strong=True)
        self._namespace_reacquisition = status
        if status.get("status") != "REACQUIRED":
            raise NamespaceAuthorityUnavailable(
                "archive namespace authority unavailable: " + status.get("status", "UNKNOWN")
            )
        if status.get("namespace_generation") != record.namespace_generation:
            raise NamespaceAuthorityUnavailable("archive namespace generation mismatch")
        return record

    def _namespace_handle(self):
        """Acquire LAB-065 dirfd and bind it to the authenticated continuity object."""
        record = self.require_namespace_authority()
        handle = super()._namespace_handle()
        if (handle.directory.st_dev, handle.directory.st_ino) != (record.st_dev, record.st_ino):
            handle.close()
            raise NamespaceAuthorityUnavailable("acquired directory FD does not match continuity record")
        return handle

    @staticmethod
    def _new_namespace_handle(record: ContinuityRecord):
        relative = os.fspath(Path(record.archive_path).relative_to(Path("/")))
        handle = NamespaceHandle.authorize_beneath("/", relative)
        if (handle.directory.st_dev, handle.directory.st_ino) != (record.st_dev, record.st_ino):
            handle.close()
            raise NamespaceAuthorityUnavailable("migration target directory identity changed")
        return handle

    def _copy_reachable_archives_for_migration(self, q, old_handle, new_handle):
        if not hasattr(self, "_reachable_archive_ids"):
            return 0
        copied = 0
        for archive_id in sorted(self._reachable_archive_ids(q)):
            row = q.execute(
                "SELECT manifest_json FROM signed_archives WHERE archive_id=?", (archive_id,)
            ).fetchone()
            if not row:
                raise NamespaceAuthorityUnavailable("reachable archive manifest missing during migration")
            manifest = self._verify_manifest_identity(q, self._archive_manifest_parse(row[0]))
            artifact_name = f"{archive_id}.json"
            manifest_name = f"{archive_id}.manifest.json"
            artifact_bytes = _read_regular_at(old_handle.fd, artifact_name)
            manifest_bytes = _read_regular_at(old_handle.fd, manifest_name)
            if hashlib.sha256(artifact_bytes).hexdigest() != manifest.artifact_sha256:
                raise NamespaceAuthorityUnavailable("migration source artifact digest mismatch")
            parsed_source_manifest = self._archive_manifest_parse(manifest_bytes.decode())
            if parsed_source_manifest != manifest:
                raise NamespaceAuthorityUnavailable("migration source manifest mismatch")
            artifact_receipt = new_handle.publish(artifact_name, artifact_bytes)
            manifest_receipt = new_handle.publish(manifest_name, manifest_bytes)
            new_handle.verify(artifact_receipt, expected_data=artifact_bytes)
            new_handle.verify(manifest_receipt, expected_data=manifest_bytes)
            copied += 1
        return copied

    def migrate_archive_namespace(self, permit: MigrationPermit):
        old = self.require_namespace_authority()
        new = migrate(old, permit, self.key)
        with self._namespace_handle() as old_handle, self._new_namespace_handle(new) as new_handle:
            q = self.store._con()
            try:
                # Hold the same write-serialization boundary used by compaction commit.
                # New namespace bytes are published before the continuity CAS, so a
                # crash leaves only duplicate/unreferenced copies, never a half-moved
                # authoritative archive chain.
                q.execute("BEGIN IMMEDIATE")
                row = q.execute(
                    "SELECT record_id,generation FROM archive_namespace_continuity WHERE singleton=1"
                ).fetchone()
                if row != (old.record_id, old.namespace_generation):
                    raise AuthenticationError("stale namespace generation")
                self._copy_reachable_archives_for_migration(q, old_handle, new_handle)
                q.execute(
                    "UPDATE archive_namespace_continuity SET record_id=?,generation=?,body_json=? "
                    "WHERE singleton=1 AND record_id=? AND generation=?",
                    (new.record_id, new.namespace_generation,
                     json.dumps(asdict(new), sort_keys=True, separators=(",", ":")),
                     old.record_id, old.namespace_generation),
                )
                if q.total_changes != 1:
                    raise AuthenticationError("namespace migration CAS failed")
                q.commit()
            except:
                if q.in_transaction:
                    q.rollback()
                raise
            finally:
                q.close()
        self.archive_dir = type(self.archive_dir)(new.archive_path)
        self._namespace_continuity_record = new
        self._namespace_reacquisition = reacquire(new, self.key, require_strong=True)
        self.require_namespace_authority()
        return new

    def compact(self, *args, **kwargs):
        self.require_namespace_authority()
        return super().compact(*args, **kwargs)
