from .core import *
from .live import LiveHistoryCore

class PrunableHistory(LiveHistoryCore):
    def _archive_paths(self,archive_id):
        return self.archive_dir/f"{archive_id}.json", self.archive_dir/f"{archive_id}.manifest.json"

    def _build_archive(self,q,cp):
        base_seq,base_root,base_rec,start_commitment,prev_archive,base_cp=self._base(q)
        rows=q.execute("""SELECT sequence,proposal_id,transition_digest,kind,predecessor_root_id,
          predecessor_recovery_id,successor_root_id,successor_recovery_id,proof_json
          FROM transitions WHERE sequence>? AND sequence<=? ORDER BY sequence""",(base_seq,cp.sequence)).fetchall()
        if len(rows)!=cp.sequence-base_seq: raise IntegrityError("archive range gap")
        artifact={"schema_version":SCHEMA,"protocol_version":PROTOCOL,"history_id":cp.history_id,
                  "previous_archive_id":prev_archive,"start_sequence":base_seq+1,"end_sequence":cp.sequence,
                  "rows":[row_obj(r) for r in rows]}
        artifact_bytes=canon(artifact)
        artifact_sha=sha(artifact_bytes)
        provisional={"schema_version":SCHEMA,"protocol_version":PROTOCOL,"history_id":cp.history_id,
                     "previous_archive_id":prev_archive,"start_sequence":base_seq+1,"end_sequence":cp.sequence,
                     "start_commitment":start_commitment,"end_commitment":cp.prefix_commitment,
                     "end_root_id":cp.root_id,"end_recovery_id":cp.recovery_id,"checkpoint_id":cp.checkpoint_id,
                     "artifact_sha256":artifact_sha,"row_count":len(rows)}
        archive_id=sha(canon(provisional))
        manifest=ArchiveManifest(archive_id=archive_id,**provisional)
        return artifact_bytes,manifest

    def _atomic_file(self,path,data):
        fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=str(path.parent))
        try:
            with os.fdopen(fd,"wb") as f:
                f.write(data); f.flush(); os.fsync(f.fileno())
            os.replace(tmp,path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)

    def compact(self,cp,*,fail_after_archive=False,fail_before_commit=False,timeout_after_commit=False):
        q=self._con()
        try:
            q.execute("BEGIN")
            cp=self._verify_checkpoint_locked(q,cp)
            artifact_bytes,manifest=self._build_archive(q,cp)
            q.commit()
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()

        artifact_path,manifest_path=self._archive_paths(manifest.archive_id)
        self._atomic_file(artifact_path,artifact_bytes)
        self._atomic_file(manifest_path,canon(asdict(manifest)))
        if fail_after_archive: raise UnknownOutcome("archive exported before live-store commit")

        q=self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            cp=self._verify_checkpoint_locked(q,cp)
            artifact2,manifest2=self._build_archive(q,cp)
            if manifest2!=manifest or sha(artifact2)!=manifest.artifact_sha256:
                raise ArchiveError("archive changed between export and commit")
            if not artifact_path.exists() or not manifest_path.exists():
                raise ArchiveError("archive files missing before commit")
            if sha(artifact_path.read_bytes())!=manifest.artifact_sha256:
                raise ArchiveError("archive artifact tampered before commit")
            if ArchiveManifest.parse(manifest_path.read_text())!=manifest:
                raise ArchiveError("archive manifest tampered before commit")
            body=json.dumps(asdict(manifest),sort_keys=True,separators=(",",":"))
            q.execute("INSERT INTO archives VALUES(?,?,?)",(manifest.archive_id,manifest.end_sequence,body))
            if fail_before_commit: raise UnknownOutcome("simulated crash before prune commit")
            q.execute("""UPDATE compaction_base SET base_sequence=?,root_id=?,recovery_id=?,
              prefix_commitment=?,archive_id=?,checkpoint_id=? WHERE singleton=1""",
                      (cp.sequence,cp.root_id,cp.recovery_id,cp.prefix_commitment,manifest.archive_id,cp.checkpoint_id))
            q.execute("DELETE FROM transitions WHERE sequence<=?",(cp.sequence,))
            q.commit()
            if timeout_after_commit: raise UnknownOutcome("commit outcome unknown")
            return manifest
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()

    def audit_archive(self,archive_id=None):
        q=self._con()
        try:
            base=self._base(q)
            aid=archive_id or base[4]
            if aid is None: raise ArchiveError("no archive")
            row=q.execute("SELECT manifest_json FROM archives WHERE archive_id=?",(aid,)).fetchone()
            if not row: raise ArchiveError("missing archive manifest")
            manifest=ArchiveManifest.parse(row[0])
        finally:q.close()
        artifact_path,manifest_path=self._archive_paths(aid)
        if not artifact_path.exists() or not manifest_path.exists(): raise ArchiveError("archive files missing")
        disk_manifest=ArchiveManifest.parse(manifest_path.read_text())
        if disk_manifest!=manifest: raise ArchiveError("archive manifest substitution")
        manifest_unsigned=asdict(manifest); manifest_unsigned.pop("archive_id")
        if sha(canon(manifest_unsigned))!=manifest.archive_id:
            raise ArchiveError("archive manifest content identity")
        q=self._con()
        try:
            if manifest.history_id!=self.history_id(q): raise ArchiveError("archive history identity")
        finally:q.close()
        data=artifact_path.read_bytes()
        if sha(data)!=manifest.artifact_sha256: raise ArchiveError("archive artifact digest")
        artifact=json.loads(data)
        if artifact.get("history_id")!=manifest.history_id or artifact.get("previous_archive_id")!=manifest.previous_archive_id:
            raise ArchiveError("archive identity")
        rows=artifact.get("rows")
        if not isinstance(rows,list) or len(rows)!=manifest.row_count: raise ArchiveError("archive row count")
        commitment=manifest.start_commitment
        expected=manifest.start_sequence
        for obj in rows:
            if not isinstance(obj,dict): raise ArchiveError("archive row")
            vals=tuple(obj[k] for k in ("sequence","proposal_id","transition_digest","kind","predecessor_root_id",
                                        "predecessor_recovery_id","successor_root_id","successor_recovery_id","proof_json"))
            if vals[0]!=expected: raise ArchiveError("archive sequence gap")
            commitment=advance_commitment(commitment,vals); expected+=1
        if expected-1!=manifest.end_sequence or commitment!=manifest.end_commitment:
            raise ArchiveError("archive commitment mismatch")
        return {"archive_id":aid,"rows_verified":len(rows),"end_sequence":manifest.end_sequence,
                "end_commitment":commitment}

    def live_transition_count(self):
        q=self._con()
        try:return q.execute("SELECT COUNT(*) FROM transitions").fetchone()[0]
        finally:q.close()

class UnsafeDeleteFirst:
    """Deliberately deletes live history before producing/verifying any durable archive boundary."""
    def prune(self,db_path,through):
        q=sqlite3.connect(str(db_path))
        try:
            q.execute("DELETE FROM transitions WHERE sequence<=?",(through,)); q.commit()
        finally:q.close()
