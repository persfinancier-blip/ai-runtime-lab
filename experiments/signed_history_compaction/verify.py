from .core import *

class VerifyMixin:
    def _base(self, q):
            row = q.execute(
                "SELECT base_sequence,root_id,recovery_id,prefix_commitment,archive_id,checkpoint_id "
                "FROM signed_compaction_base WHERE singleton=1"
            ).fetchone()
            if not row:
                raise AuthenticationError("missing compaction base")
            return row

    def history_id(self, q):
            root_id, recovery_id = q.execute(
                "SELECT root_id,recovery_id FROM bootstrap WHERE singleton=1"
            ).fetchone()
            return digest(
                {
                    "kind": "lab062-history",
                    "bootstrap_root_id": root_id,
                    "bootstrap_recovery_id": recovery_id,
                    "protocol_version": PROTOCOL,
                    "external_anchor_id": self.anchor,
                }
            )

    def _rows(self, q, start_exclusive, end_inclusive=None):
            sql = (
                "SELECT sequence,proposal_id,transition_digest,kind,predecessor_root_id,"
                "predecessor_recovery_id,successor_root_id,successor_recovery_id,proof_json "
                "FROM transitions WHERE sequence>?"
            )
            args = [start_exclusive]
            if end_inclusive is not None:
                sql += " AND sequence<=?"
                args.append(end_inclusive)
            sql += " ORDER BY sequence"
            return q.execute(sql, args).fetchall()

    def _verify_signed_rows(self, q, *, start_sequence, start_root_id, start_recovery_id, start_commitment, rows):
            """Apply LAB-059's authority/payload/threshold/digest proof rules to an explicit row sequence."""
            root = self.store._get(q, start_root_id)
            recovery = self.store._get(q, start_recovery_id)
            commitment = start_commitment
            expected = start_sequence + 1
            count = 0
            for row in rows:
                seq, pid, td, kind, r0, c0, r1, c1, proof_json = row
                if seq != expected:
                    raise HistoryIntegrityError("transition sequence gap")
                if (r0, c0) != (root.authority_id, recovery.authority_id):
                    raise HistoryIntegrityError("historical predecessor mismatch")
                proof = json.loads(proof_json)
                if (
                    proof.get("proposal_id") != pid
                    or proof.get("transition_digest") != td
                    or proof.get("kind") != kind
                ):
                    raise HistoryIntegrityError("proof identity mismatch")
                if kind == "rotate_recovery":
                    new_recovery = self.store._get(q, c1)
                    if r1 != root.authority_id:
                        raise HistoryIntegrityError("unexpected root successor")
                    payload = rotation_payload(root, recovery, new_recovery)
                    if proof.get("payload") != payload:
                        raise HistoryIntegrityError("payload mismatch")
                    verify_threshold(recovery, payload, proof.get("sig1", []))
                    verify_threshold(new_recovery, payload, proof.get("sig2", []))
                    verify_threshold(root, payload, proof.get("sig3", []))
                    expected_td = digest(
                        {
                            "proposal_id": pid,
                            "kind": kind,
                            "predecessor_root_id": r0,
                            "predecessor_recovery_id": c0,
                            "successor": new_recovery.descriptor,
                        }
                    )
                    recovery = new_recovery
                elif kind == "recover_root":
                    new_root = self.store._get(q, r1)
                    if c1 != recovery.authority_id:
                        raise HistoryIntegrityError("unexpected recovery successor")
                    payload = recovery_payload(root, new_root, recovery)
                    if proof.get("payload") != payload:
                        raise HistoryIntegrityError("payload mismatch")
                    verify_threshold(recovery, payload, proof.get("sig1", []))
                    expected_td = digest(
                        {
                            "proposal_id": pid,
                            "kind": kind,
                            "predecessor_root_id": r0,
                            "predecessor_recovery_id": c0,
                            "successor": new_root.descriptor,
                        }
                    )
                    root = new_root
                else:
                    raise HistoryIntegrityError("unknown historical kind")
                if td != expected_td:
                    raise HistoryIntegrityError("transition digest mismatch")
                commitment = advance_commitment(commitment, row)
                expected += 1
                count += 1
            return {
                "root_id": root.authority_id,
                "recovery_id": recovery.authority_id,
                "sequence": expected - 1,
                "prefix_commitment": commitment,
                "rows_verified": count,
            }

    def _verify_base_checkpoint(self, q, base):
            base_sequence, root_id, recovery_id, commitment, archive_id, checkpoint_id = base
            if base_sequence == 0:
                if archive_id is not None or checkpoint_id is not None:
                    raise AuthenticationError("bootstrap base has archive/checkpoint")
                return
            row = q.execute(
                "SELECT body_json FROM signed_compact_checkpoints WHERE checkpoint_id=?",
                (checkpoint_id,),
            ).fetchone()
            if not row:
                raise AuthenticationError("base checkpoint missing")
            cp = SignedCheckpoint.parse(row[0])
            if cp.checkpoint_id != checkpoint_id:
                raise AuthenticationError("checkpoint content identity")
            self._verify_checkpoint_signature(q, cp)
            if (cp.sequence, cp.root_id, cp.recovery_id, cp.prefix_commitment) != (
                base_sequence, root_id, recovery_id, commitment
            ):
                raise AuthenticationError("base/checkpoint mismatch")
            manifest_row = q.execute(
                "SELECT manifest_json FROM signed_archives WHERE archive_id=?", (archive_id,)
            ).fetchone()
            if not manifest_row:
                raise ArchiveError("base archive manifest missing")
            manifest = ArchiveManifest.parse(manifest_row[0])
            self._verify_manifest_identity(q, manifest)
            self._verify_manifest_start_binding(q, manifest, cp)
            if (
                manifest.archive_id,
                manifest.end_sequence,
                manifest.end_root_id,
                manifest.end_recovery_id,
                manifest.end_commitment,
                manifest.checkpoint_id,
            ) != (archive_id, base_sequence, root_id, recovery_id, commitment, checkpoint_id):
                raise ArchiveError("base/archive mismatch")

    def _archive_manifest_row(self, q, archive_id):
            row = q.execute(
                "SELECT manifest_json FROM signed_archives WHERE archive_id=?", (archive_id,)
            ).fetchone()
            if not row:
                raise ArchiveError("archive manifest missing")
            manifest = ArchiveManifest.parse(row[0])
            return self._verify_manifest_identity(q, manifest)

    def _verify_manifest_start_binding(self, q, manifest, checkpoint):
            if (manifest.start_sequence - 1, manifest.previous_archive_id) != (
                checkpoint.base_sequence, checkpoint.base_archive_id
            ):
                raise ArchiveError("archive start/checkpoint-base mismatch")
            if checkpoint.base_sequence == 0:
                bootstrap = q.execute(
                    "SELECT root_id,recovery_id FROM bootstrap WHERE singleton=1"
                ).fetchone()
                expected = (
                    bootstrap[0], bootstrap[1], seed_commitment(bootstrap[0], bootstrap[1])
                )
            else:
                previous = self._archive_manifest_row(q, checkpoint.base_archive_id)
                if previous.end_sequence != checkpoint.base_sequence:
                    raise ArchiveError("previous archive sequence mismatch")
                expected = (
                    previous.end_root_id, previous.end_recovery_id, previous.end_commitment
                )
            if (
                manifest.start_root_id, manifest.start_recovery_id, manifest.start_commitment
            ) != expected:
                raise ArchiveError("archive start-state substitution")

    def _reachable_archive_ids(self, q):
            current = self._base(q)[4]
            reachable = set()
            while current is not None:
                if current in reachable:
                    raise ArchiveError("archive chain cycle")
                reachable.add(current)
                manifest = self._archive_manifest_row(q, current)
                current = manifest.previous_archive_id
            return reachable

    def _verify_checkpoint_signature(self, q, cp):
            cp = SignedCheckpoint.parse(asdict(cp))
            if cp.schema_version != SCHEMA or cp.protocol_version != PROTOCOL:
                raise AuthenticationError("checkpoint version")
            if cp.history_id != self.history_id(q) or cp.external_anchor_id != self.anchor:
                raise AuthenticationError("checkpoint history/anchor")
            if cp.signer_id != self.signer_id or not hmac.compare_digest(
                mac(self.key, cp.unsigned), cp.signature
            ):
                raise AuthenticationError("checkpoint signature")
            return cp

    def _verify_current_checkpoint_locked(self, q, cp):
            cp = self._verify_checkpoint_signature(q, cp)
            wm = q.execute(
                "SELECT sequence,checkpoint_id FROM signed_checkpoint_watermark WHERE singleton=1"
            ).fetchone()
            if not wm:
                raise AuthenticationError("missing checkpoint watermark")
            if cp.sequence < wm[0]:
                raise StaleCheckpoint("checkpoint behind watermark")
            if (cp.sequence, cp.checkpoint_id) != wm:
                raise AuthenticationError("checkpoint watermark mismatch")
            row = q.execute(
                "SELECT body_json FROM signed_compact_checkpoints WHERE checkpoint_id=?",
                (cp.checkpoint_id,),
            ).fetchone()
            if not row or SignedCheckpoint.parse(row[0]) != cp:
                raise AuthenticationError("checkpoint persistence")
            base = self._base(q)
            if (cp.base_sequence, cp.base_archive_id) != (base[0], base[4]):
                raise StaleCheckpoint("checkpoint base changed")
            derived = self._verify_live_locked(q, through_sequence=cp.sequence)
            if (
                derived["root_id"], derived["recovery_id"], derived["prefix_commitment"]
            ) != (cp.root_id, cp.recovery_id, cp.prefix_commitment):
                raise AuthenticationError("checkpoint derived state")
            return cp

    def _verify_live_locked(self, q, through_sequence=None):
            base = self._base(q)
            self._verify_base_checkpoint(q, base)
            head = q.execute(
                "SELECT root_id,recovery_id,sequence FROM head WHERE singleton=1"
            ).fetchone()
            if not head:
                raise HeadMismatch("missing head")
            end = head[2] if through_sequence is None else through_sequence
            if end < base[0] or end > head[2]:
                raise HistoryIntegrityError("verification range")
            rows = self._rows(q, base[0], end)
            result = self._verify_signed_rows(
                q,
                start_sequence=base[0],
                start_root_id=base[1],
                start_recovery_id=base[2],
                start_commitment=base[3],
                rows=rows,
            )
            if result["sequence"] != end:
                raise HistoryIntegrityError("suffix missing tail")
            if through_sequence is None and head != (
                result["root_id"], result["recovery_id"], result["sequence"]
            ):
                raise HeadMismatch("head/suffix mismatch")
            return result

    def verify_restart(self):
            q = self.store._con()
            try:
                q.execute("BEGIN")
                result = self._verify_live_locked(q)
                q.commit()
                return result
            except:
                if q.in_transaction:
                    q.rollback()
                raise
            finally:
                q.close()

    def create_checkpoint(self):
            q = self.store._con()
            try:
                q.execute("BEGIN IMMEDIATE")
                verified = self._verify_live_locked(q)
                base = self._base(q)
                unsigned = {
                    "schema_version": SCHEMA,
                    "protocol_version": PROTOCOL,
                    "history_id": self.history_id(q),
                    "sequence": verified["sequence"],
                    "root_id": verified["root_id"],
                    "recovery_id": verified["recovery_id"],
                    "prefix_commitment": verified["prefix_commitment"],
                    "base_sequence": base[0],
                    "base_archive_id": base[4],
                    "external_anchor_id": self.anchor,
                    "signer_id": self.signer_id,
                }
                cp = SignedCheckpoint(**unsigned, signature=mac(self.key, unsigned))
                wm = q.execute(
                    "SELECT sequence,checkpoint_id FROM signed_checkpoint_watermark WHERE singleton=1"
                ).fetchone()
                if wm and cp.sequence < wm[0]:
                    raise StaleCheckpoint("checkpoint rollback")
                if wm and cp.sequence == wm[0]:
                    row = q.execute(
                        "SELECT body_json FROM signed_compact_checkpoints WHERE checkpoint_id=?",
                        (wm[1],),
                    ).fetchone()
                    if not row:
                        raise AuthenticationError("missing checkpoint row")
                    old = SignedCheckpoint.parse(row[0])
                    if old.checkpoint_id != cp.checkpoint_id:
                        raise AuthenticationError("same-sequence checkpoint substitution")
                    q.commit()
                    return old
                body = json.dumps(asdict(cp), sort_keys=True, separators=(",", ":"))
                q.execute(
                    "INSERT INTO signed_compact_checkpoints VALUES(?,?,?)",
                    (cp.checkpoint_id, cp.sequence, body),
                )
                q.execute(
                    "INSERT INTO signed_checkpoint_watermark VALUES(1,?,?) "
                    "ON CONFLICT(singleton) DO UPDATE SET sequence=excluded.sequence,checkpoint_id=excluded.checkpoint_id",
                    (cp.sequence, cp.checkpoint_id),
                )
                q.commit()
                return cp
            except:
                if q.in_transaction:
                    q.rollback()
                raise
            finally:
                q.close()

    def _verify_manifest_identity(self, q, manifest):
            manifest = ArchiveManifest.parse(asdict(manifest))
            unsigned = asdict(manifest)
            unsigned.pop("archive_id")
            if sha(canon(unsigned)) != manifest.archive_id:
                raise ArchiveError("archive manifest content identity")
            if manifest.history_id != self.history_id(q):
                raise ArchiveError("archive history identity")
            return manifest
