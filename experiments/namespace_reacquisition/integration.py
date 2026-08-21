from __future__ import annotations

import json
from dataclasses import asdict

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
        """Acquire LAB-065 dirfd and bind it to the authenticated continuity object.

        This closes the gap between a successful pathname reacquisition and a later
        directory-FD acquisition: even if the path is swapped and swapped back during
        that interval, the held FD must name the exact `(st_dev, st_ino)` recorded in
        the authenticated continuity record.
        """
        record = self.require_namespace_authority()
        handle = super()._namespace_handle()
        if (handle.directory.st_dev, handle.directory.st_ino) != (record.st_dev, record.st_ino):
            handle.close()
            raise NamespaceAuthorityUnavailable("acquired directory FD does not match continuity record")
        return handle

    def migrate_archive_namespace(self, permit: MigrationPermit):
        old = self._namespace_continuity_record
        new = migrate(old, permit, self.key)
        q = self.store._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            row = q.execute(
                "SELECT record_id,generation FROM archive_namespace_continuity WHERE singleton=1"
            ).fetchone()
            if row != (old.record_id, old.namespace_generation):
                raise AuthenticationError("stale namespace generation")
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
