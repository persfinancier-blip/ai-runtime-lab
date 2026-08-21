from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

from experiments.archive_publication_durability.protocol import require_durable_pair
from .protocol import (
    DirectoryIdentity,
    NamespaceHandle,
    NamespaceMismatch,
    NamespaceReceipt,
    verify_pair,
)


@dataclass(frozen=True)
class BoundPublicationReceipt:
    """LAB-064-compatible receipt with LAB-065 namespace evidence attached."""

    path: str
    sha256: str
    file_synced: bool
    directory_synced: bool
    namespace_receipt: NamespaceReceipt

    @property
    def durable(self):
        return self.file_synced and self.directory_synced


class NamespaceBoundArchiveMixin:
    """Strengthens SignedPrunableHistory's publication boundary with a held dirfd.

    The lexical archive path is used to acquire and later continuity-check the
    configured directory, but archive bytes are created, fsynced, renamed, and
    re-read relative to one held directory FD until the SQL commit completes.
    """

    _active_namespace_handle = None

    def _namespace_handle(self):
        archive_dir = Path(self.archive_dir)
        parent = archive_dir.parent
        name = archive_dir.name
        if not name:
            raise NamespaceMismatch("archive directory must have a basename")
        return NamespaceHandle.authorize_beneath(parent, name)

    def _assert_configured_namespace(self, handle: NamespaceHandle):
        """Fail closed if the configured pathname stops naming the held object."""
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(self.archive_dir, flags)
        except OSError as exc:
            raise NamespaceMismatch("configured archive pathname changed") from exc
        try:
            st = os.fstat(fd)
            current = DirectoryIdentity(st.st_dev, st.st_ino)
        finally:
            os.close(fd)
        if current != handle.directory:
            raise NamespaceMismatch("configured archive pathname now resolves to another directory object")

    def _atomic_file(self, path, data):
        handle = self._active_namespace_handle
        if handle is None:
            # This should not occur on the consequential compaction path. Keep a
            # fail-closed error instead of silently falling back to lexical I/O.
            raise NamespaceMismatch("namespace handle not active")
        path = Path(path)
        receipt = handle.publish(path.name, data)
        return BoundPublicationReceipt(
            path=os.path.abspath(os.fspath(path)),
            sha256=receipt.sha256,
            file_synced=receipt.file_synced,
            directory_synced=receipt.directory_synced,
            namespace_receipt=receipt,
        )

    def _require_namespace_pair(
        self,
        handle,
        artifact_receipt,
        manifest_receipt,
        *,
        artifact_path,
        artifact_data,
        manifest_path,
        manifest_data,
    ):
        # Preserve LAB-064's exact path/digest/fsync gate first. This also keeps
        # its fault-injection tests authoritative.
        publication = require_durable_pair(
            artifact_receipt,
            manifest_receipt,
            artifact_path=artifact_path,
            artifact_data=artifact_data,
            manifest_path=manifest_path,
            manifest_data=manifest_data,
        )
        if not isinstance(artifact_receipt, BoundPublicationReceipt) or not isinstance(
            manifest_receipt, BoundPublicationReceipt
        ):
            raise NamespaceMismatch("durable receipt lacks namespace-object binding")
        bound = verify_pair(
            handle,
            artifact_receipt.namespace_receipt,
            manifest_receipt.namespace_receipt,
            artifact_data=artifact_data,
            manifest_data=manifest_data,
        )
        if not bound.get("namespace_bound"):
            raise NamespaceMismatch("namespace verification missing")
        if bound["artifact_sha256"] != publication["artifact_sha256"]:
            raise NamespaceMismatch("LAB-064/LAB-065 artifact digest disagreement")
        return {**publication, **bound}

    def _after_namespace_authorized(self, handle):
        """Fault-injection hook used only by deterministic integration tests."""

    def _after_namespace_published(self, handle, manifest):
        """Fault-injection hook used only by deterministic integration tests."""

    def compact(self, cp, *, fail_after_archive=False, fail_before_commit=False, timeout_after_commit=False):
        # The preparation transaction remains unchanged from LAB-062/064.
        q = self.store._con()
        try:
            q.execute("BEGIN")
            base = self._base(q)
            if base[5] == cp.checkpoint_id and base[0] == cp.sequence:
                row = q.execute(
                    "SELECT manifest_json FROM signed_archives WHERE archive_id=?", (base[4],)
                ).fetchone()
                if not row:
                    raise self._archive_error("committed compaction missing manifest")
                manifest = self._verify_manifest_identity(q, self._archive_manifest_parse(row[0]))
                q.commit()
                return manifest
            cp = self._verify_current_checkpoint_locked(q, cp)
            artifact_bytes, manifest = self._build_archive(q, cp)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

        artifact_path, manifest_path = self._archive_paths(manifest.archive_id)
        manifest_bytes = self._archive_manifest_bytes(manifest)

        with self._namespace_handle() as namespace:
            self._active_namespace_handle = namespace
            try:
                self._after_namespace_authorized(namespace)
                artifact_receipt = self._atomic_file(artifact_path, artifact_bytes)
                manifest_receipt = self._atomic_file(manifest_path, manifest_bytes)
                publication = self._require_namespace_pair(
                    namespace,
                    artifact_receipt,
                    manifest_receipt,
                    artifact_path=artifact_path,
                    artifact_data=artifact_bytes,
                    manifest_path=manifest_path,
                    manifest_data=manifest_bytes,
                )
                self._after_namespace_published(namespace, manifest)
                if publication["artifact_sha256"] != manifest.artifact_sha256:
                    raise self._archive_error("durable artifact receipt digest mismatch")
                if fail_after_archive:
                    raise self._unknown_outcome(
                        "durably published archive exported before live-store commit"
                    )

                q = self.store._con()
                try:
                    q.execute("BEGIN IMMEDIATE")
                    cp = self._verify_current_checkpoint_locked(q, cp)
                    artifact2, manifest2 = self._build_archive(q, cp)
                    if manifest2 != manifest or hashlib.sha256(artifact2).hexdigest() != manifest.artifact_sha256:
                        raise self._archive_error("archive changed before commit")
                    if not publication.get("publication_durable"):
                        raise self._archive_error("archive publication durability not established")

                    # Re-check both the current configuration and the exact bytes
                    # using the same held namespace object immediately before SQL
                    # makes the archive authoritative.
                    self._assert_configured_namespace(namespace)
                    self._require_namespace_pair(
                        namespace,
                        artifact_receipt,
                        manifest_receipt,
                        artifact_path=artifact_path,
                        artifact_data=artifact_bytes,
                        manifest_path=manifest_path,
                        manifest_data=manifest_bytes,
                    )
                    self._verify_manifest_identity(q, manifest)
                    q.execute(
                        "INSERT INTO signed_archives VALUES(?,?,?)",
                        (
                            manifest.archive_id,
                            manifest.end_sequence,
                            self._archive_manifest_json(manifest),
                        ),
                    )
                    if fail_before_commit:
                        raise self._unknown_outcome("simulated failure before prune commit")
                    q.execute(
                        "UPDATE signed_compaction_base SET base_sequence=?,root_id=?,recovery_id=?,"
                        "prefix_commitment=?,archive_id=?,checkpoint_id=? WHERE singleton=1",
                        (
                            cp.sequence,
                            cp.root_id,
                            cp.recovery_id,
                            cp.prefix_commitment,
                            manifest.archive_id,
                            cp.checkpoint_id,
                        ),
                    )
                    q.execute("DELETE FROM transitions WHERE sequence<=?", (cp.sequence,))
                    q.commit()
                    if timeout_after_commit:
                        raise self._unknown_outcome("commit outcome unknown")
                    return manifest
                except:
                    if q.in_transaction:
                        q.rollback()
                    raise
                finally:
                    q.close()
            finally:
                self._active_namespace_handle = None

    # Small adapters keep this mixin independent of star-import details in
    # signed_history_compaction.archive while still using the exact LAB-062 types.
    def _archive_manifest_parse(self, raw):
        from experiments.signed_history_compaction.core import ArchiveManifest

        return ArchiveManifest.parse(raw)

    def _archive_manifest_bytes(self, manifest):
        from dataclasses import asdict
        from experiments.signed_history_compaction.core import canon

        return canon(asdict(manifest))

    def _archive_manifest_json(self, manifest):
        import json
        from dataclasses import asdict

        return json.dumps(asdict(manifest), sort_keys=True, separators=(",", ":"))

    def _archive_error(self, message):
        from experiments.signed_history_compaction.core import ArchiveError

        return ArchiveError(message)

    def _unknown_outcome(self, message):
        from experiments.signed_history_compaction.core import UnknownOutcome

        return UnknownOutcome(message)
