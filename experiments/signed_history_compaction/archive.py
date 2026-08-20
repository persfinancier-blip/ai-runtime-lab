from .core import *
from experiments.archive_publication_durability.protocol import durable_publish, require_durable_pair

class ArchiveMixin:
    def _build_archive(self, q, cp):
            base = self._base(q)
            rows = self._rows(q, base[0], cp.sequence)
            if len(rows) != cp.sequence - base[0]:
                raise ArchiveError("archive range gap")
            verified = self._verify_signed_rows(
                q,
                start_sequence=base[0],
                start_root_id=base[1],
                start_recovery_id=base[2],
                start_commitment=base[3],
                rows=rows,
            )
            if (
                verified["root_id"], verified["recovery_id"], verified["prefix_commitment"]
            ) != (cp.root_id, cp.recovery_id, cp.prefix_commitment):
                raise ArchiveError("archive terminal/checkpoint mismatch")
            artifact = {
                "schema_version": SCHEMA,
                "protocol_version": PROTOCOL,
                "history_id": cp.history_id,
                "previous_archive_id": base[4],
                "start_sequence": base[0] + 1,
                "end_sequence": cp.sequence,
                "rows": [row_obj(row) for row in rows],
            }
            artifact_bytes = canon(artifact)
            provisional = {
                "schema_version": SCHEMA,
                "protocol_version": PROTOCOL,
                "history_id": cp.history_id,
                "previous_archive_id": base[4],
                "start_sequence": base[0] + 1,
                "end_sequence": cp.sequence,
                "start_root_id": base[1],
                "start_recovery_id": base[2],
                "start_commitment": base[3],
                "end_root_id": cp.root_id,
                "end_recovery_id": cp.recovery_id,
                "end_commitment": cp.prefix_commitment,
                "checkpoint_id": cp.checkpoint_id,
                "artifact_sha256": sha(artifact_bytes),
                "row_count": len(rows),
            }
            archive_id = sha(canon(provisional))
            return artifact_bytes, ArchiveManifest(archive_id=archive_id, **provisional)

    def _archive_paths(self, archive_id):
            return (
                self.archive_dir / f"{archive_id}.json",
                self.archive_dir / f"{archive_id}.manifest.json",
            )

    def _atomic_file(self, path, data):
            # LAB-064: a successful publication receipt requires both the file
            # contents and the containing directory entry to have crossed an
            # explicit fsync boundary. Atomic rename alone is not treated as
            # power-loss durability.
            return durable_publish(path, data)

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
                        raise ArchiveError("committed compaction missing manifest")
                    manifest = self._verify_manifest_identity(q, ArchiveManifest.parse(row[0]))
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
            manifest_bytes = canon(asdict(manifest))
            artifact_receipt = self._atomic_file(artifact_path, artifact_bytes)
            manifest_receipt = self._atomic_file(manifest_path, manifest_bytes)
            publication = require_durable_pair(
                artifact_receipt,
                manifest_receipt,
                artifact_path=artifact_path,
                artifact_data=artifact_bytes,
                manifest_path=manifest_path,
                manifest_data=manifest_bytes,
            )
            if publication["artifact_sha256"] != manifest.artifact_sha256:
                raise ArchiveError("durable artifact receipt digest mismatch")
            if fail_after_archive:
                raise UnknownOutcome("durably published archive exported before live-store commit")

            q = self.store._con()
            try:
                q.execute("BEGIN IMMEDIATE")
                cp = self._verify_current_checkpoint_locked(q, cp)
                artifact2, manifest2 = self._build_archive(q, cp)
                if manifest2 != manifest or sha(artifact2) != manifest.artifact_sha256:
                    raise ArchiveError("archive changed before commit")
                if not publication.get("publication_durable"):
                    raise ArchiveError("archive publication durability not established")
                if not artifact_path.exists() or not manifest_path.exists():
                    raise ArchiveError("archive files missing")
                if sha(artifact_path.read_bytes()) != manifest.artifact_sha256:
                    raise ArchiveError("archive artifact tampered before commit")
                if ArchiveManifest.parse(manifest_path.read_text()) != manifest:
                    raise ArchiveError("archive manifest tampered before commit")
                self._verify_manifest_identity(q, manifest)
                q.execute(
                    "INSERT INTO signed_archives VALUES(?,?,?)",
                    (
                        manifest.archive_id,
                        manifest.end_sequence,
                        json.dumps(asdict(manifest), sort_keys=True, separators=(",", ":")),
                    ),
                )
                if fail_before_commit:
                    raise UnknownOutcome("simulated failure before prune commit")
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
                    raise UnknownOutcome("commit outcome unknown")
                return manifest
            except:
                if q.in_transaction:
                    q.rollback()
                raise
            finally:
                q.close()

    def audit_archive(self, archive_id=None):
            q = self.store._con()
            try:
                base = self._base(q)
                selected = archive_id or base[4]
                if selected is None:
                    raise ArchiveError("no archive")
                row = q.execute(
                    "SELECT manifest_json FROM signed_archives WHERE archive_id=?", (selected,)
                ).fetchone()
                if not row:
                    raise ArchiveError("archive manifest missing")
                manifest = self._verify_manifest_identity(q, ArchiveManifest.parse(row[0]))
                if selected not in self._reachable_archive_ids(q):
                    raise ArchiveError("archive is not on the authenticated compaction chain")
                checkpoint_row = q.execute(
                    "SELECT body_json FROM signed_compact_checkpoints WHERE checkpoint_id=?",
                    (manifest.checkpoint_id,),
                ).fetchone()
                if not checkpoint_row:
                    raise ArchiveError("archive checkpoint missing")
                checkpoint = SignedCheckpoint.parse(checkpoint_row[0])
                self._verify_checkpoint_signature(q, checkpoint)
                self._verify_manifest_start_binding(q, manifest, checkpoint)
                if (
                    manifest.end_sequence, manifest.end_root_id, manifest.end_recovery_id,
                    manifest.end_commitment
                ) != (
                    checkpoint.sequence, checkpoint.root_id, checkpoint.recovery_id,
                    checkpoint.prefix_commitment
                ):
                    raise ArchiveError("archive/checkpoint terminal mismatch")
                artifact_path, manifest_path = self._archive_paths(selected)
                if not artifact_path.exists() or not manifest_path.exists():
                    raise ArchiveError("archive files missing")
                if ArchiveManifest.parse(manifest_path.read_text()) != manifest:
                    raise ArchiveError("archive manifest substitution")
                data = artifact_path.read_bytes()
                if sha(data) != manifest.artifact_sha256:
                    raise ArchiveError("archive artifact digest")
                artifact = json.loads(data)
                if (
                    artifact.get("history_id") != manifest.history_id
                    or artifact.get("previous_archive_id") != manifest.previous_archive_id
                    or artifact.get("start_sequence") != manifest.start_sequence
                    or artifact.get("end_sequence") != manifest.end_sequence
                ):
                    raise ArchiveError("archive artifact identity")
                rows_raw = artifact.get("rows")
                if not isinstance(rows_raw, list) or len(rows_raw) != manifest.row_count:
                    raise ArchiveError("archive row count")
                names = (
                    "sequence", "proposal_id", "transition_digest", "kind", "predecessor_root_id",
                    "predecessor_recovery_id", "successor_root_id", "successor_recovery_id", "proof_json",
                )
                rows = []
                for obj in rows_raw:
                    if not isinstance(obj, dict) or set(obj) != set(names):
                        raise ArchiveError("archive row schema")
                    rows.append(tuple(obj[name] for name in names))
                verified = self._verify_signed_rows(
                    q,
                    start_sequence=manifest.start_sequence - 1,
                    start_root_id=manifest.start_root_id,
                    start_recovery_id=manifest.start_recovery_id,
                    start_commitment=manifest.start_commitment,
                    rows=rows,
                )
                if (
                    verified["sequence"], verified["root_id"], verified["recovery_id"], verified["prefix_commitment"]
                ) != (
                    manifest.end_sequence, manifest.end_root_id, manifest.end_recovery_id, manifest.end_commitment
                ):
                    raise ArchiveError("archive terminal mismatch")
                return {"archive_id": selected, "rows_verified": verified["rows_verified"], "end_sequence": verified["sequence"]}
            finally:
                q.close()

    def live_transition_count(self):
            q = self.store._con()
            try:
                return q.execute("SELECT COUNT(*) FROM transitions").fetchone()[0]
            finally:
                q.close()
