from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

from experiments.archive_publication_durability.protocol import require_durable_pair
from .protocol import (
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
    """Strengthen archive publication with one held, symlink-free directory object.

    Authorization starts at the filesystem root and resolves the complete absolute
    archive-directory path with openat2 RESOLVE_BENEATH|RESOLVE_NO_SYMLINKS. This
    avoids treating `archive_dir.parent` as trusted when one of its own path-prefix
    components may have been substituted by a symlink. Consequential file I/O then
    remains relative to the held directory FD until SQL commit.
    """

    _active_namespace_handle = None

    def _absolute_archive_relative_to_root(self) -> str:
        archive_dir = Path(self.archive_dir)
        absolute = Path(os.path.abspath(os.fspath(archive_dir)))
        try:
            relative = absolute.relative_to(Path("/"))
        except ValueError as exc:
            raise NamespaceMismatch("archive directory must be an absolute POSIX path") from exc
        value = os.fspath(relative)
        if not value or value == ".":
            raise NamespaceMismatch("archive directory cannot be filesystem root")
        return value

    def _namespace_handle(self):
        return NamespaceHandle.authorize_beneath("/", self._absolute_archive_relative_to_root())

    def _assert_configured_namespace(self, handle: NamespaceHandle):
        """Re-resolve the full configured path without symlinks and compare identity."""
        try:
            current = NamespaceHandle.authorize_beneath(
                "/", self._absolute_archive_relative_to_root()
            )
        except Exception as exc:
            raise NamespaceMismatch("configured archive pathname changed") from exc
        try:
            if current.directory != handle.directory:
                raise NamespaceMismatch(
                    "configured archive pathname now resolves to another directory object"
                )
        finally:
            current.close()

    def _atomic_file(self, path, data):
        handle = self._active_namespace_handle
        if handle is None:
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
        self, handle, artifact_receipt, manifest_receipt, *,
        artifact_path, artifact_data, manifest_path, manifest_data,
    ):
        publication = require_durable_pair(
            artifact_receipt, manifest_receipt,
            artifact_path=artifact_path, artifact_data=artifact_data,
            manifest_path=manifest_path, manifest_data=manifest_data,
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
                    namespace, artifact_receipt, manifest_receipt,
                    artifact_path=artifact_path, artifact_data=artifact_bytes,
                    manifest_path=manifest_path, manifest_data=manifest_bytes,
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
                    self._assert_configured_namespace(namespace)
                    self._require_namespace_pair(
                        namespace, artifact_receipt, manifest_receipt,
                        artifact_path=artifact_path, artifact_data=artifact_bytes,
                        manifest_path=manifest_path, manifest_data=manifest_bytes,
                    )
                    self._verify_manifest_identity(q, manifest)
                    q.execute(
                        "INSERT INTO signed_archives VALUES(?,?,?)",
                        (manifest.archive_id, manifest.end_sequence, self._archive_manifest_json(manifest)),
                    )
                    if fail_before_commit:
                        raise self._unknown_outcome("simulated failure before prune commit")
                    q.execute(
                        "UPDATE signed_compaction_base SET base_sequence=?,root_id=?,recovery_id=?,"
                        "prefix_commitment=?,archive_id=?,checkpoint_id=? WHERE singleton=1",
                        (cp.sequence, cp.root_id, cp.recovery_id, cp.prefix_commitment,
                         manifest.archive_id, cp.checkpoint_id),
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
