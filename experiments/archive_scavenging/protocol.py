from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from contextlib import nullcontext
from dataclasses import dataclass

HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ScavengeError(RuntimeError): pass
class StaleRetentionGeneration(ScavengeError): pass
class CandidateBecameReachable(ScavengeError): pass
class ContentAddressSubstitution(ScavengeError): pass


@dataclass(frozen=True)
class Candidate:
    archive_id: str
    observed_generation: int
    first_seen_generation: int
    artifact: bool
    manifest: bool


class ArchiveScavenger:
    """Generation-fenced mark/sweep for LAB-062 content-addressed archives.

    SQL archive-chain state is reachability authority. On a LAB-065/066-capable
    layer, filesystem enumeration/read/unlink stays relative to one held directory
    FD and the configured pathname is re-bound to that object immediately before
    destructive unlink. Plain-path fallback exists only for older isolated tests.
    """

    def __init__(self, layer, grace_generations=2):
        if type(grace_generations) is not int or grace_generations < 1:
            raise ValueError("grace")
        self.layer = layer
        self.grace = grace_generations
        q = layer.store._con()
        try:
            q.executescript(
                """
                CREATE TABLE IF NOT EXISTS archive_retention_state(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1), generation INTEGER NOT NULL);
                INSERT OR IGNORE INTO archive_retention_state VALUES(1,0);
                CREATE TABLE IF NOT EXISTS archive_orphan_candidates(
                  archive_id TEXT PRIMARY KEY, first_seen_generation INTEGER NOT NULL,
                  last_seen_generation INTEGER NOT NULL);
                """
            )
        finally:
            q.close()

    def _require_namespace_authority(self):
        require = getattr(self.layer, "require_namespace_authority", None)
        return None if require is None else require()

    def _namespace_scope(self):
        self._require_namespace_authority()
        factory = getattr(self.layer, "_namespace_handle", None)
        return nullcontext(None) if factory is None else factory()

    def generation(self):
        q = self.layer.store._con()
        try: return q.execute("SELECT generation FROM archive_retention_state").fetchone()[0]
        finally: q.close()

    def advance_generation(self):
        q = self.layer.store._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            q.execute("UPDATE archive_retention_state SET generation=generation+1")
            value = q.execute("SELECT generation FROM archive_retention_state").fetchone()[0]
            q.commit(); return value
        except:
            if q.in_transaction: q.rollback()
            raise
        finally: q.close()

    def _reachable(self, q):
        return set(self.layer._reachable_archive_ids(q))

    @staticmethod
    def _kind(name):
        if name.endswith(".manifest.json"): return name[:-14], "manifest"
        if name.endswith(".json"): return name[:-5], "artifact"
        return None, None

    def _fs(self, handle=None):
        out = {}
        names = os.listdir(handle.fd) if handle is not None else [p.name for p in self.layer.archive_dir.iterdir()]
        for name in names:
            archive_id, kind = self._kind(name)
            if archive_id is not None and HEX64.fullmatch(archive_id):
                out.setdefault(archive_id, set()).add(kind)
        return out

    def scan(self):
        with self._namespace_scope() as handle:
            self._require_namespace_authority()
            q = self.layer.store._con()
            try:
                q.execute("BEGIN")
                reachable = self._reachable(q)
                generation = q.execute("SELECT generation FROM archive_retention_state").fetchone()[0]
                fs = self._fs(handle)
                out = []
                for archive_id, kinds in sorted(fs.items()):
                    if archive_id in reachable:
                        q.execute("DELETE FROM archive_orphan_candidates WHERE archive_id=?", (archive_id,)); continue
                    row = q.execute("SELECT first_seen_generation FROM archive_orphan_candidates WHERE archive_id=?", (archive_id,)).fetchone()
                    first = generation if row is None else row[0]
                    q.execute(
                        "INSERT INTO archive_orphan_candidates VALUES(?,?,?) "
                        "ON CONFLICT(archive_id) DO UPDATE SET last_seen_generation=excluded.last_seen_generation",
                        (archive_id, first, generation),
                    )
                    out.append(Candidate(archive_id, generation, first, "artifact" in kinds, "manifest" in kinds))
                for (archive_id,) in q.execute("SELECT archive_id FROM archive_orphan_candidates").fetchall():
                    if archive_id not in fs or archive_id in reachable:
                        q.execute("DELETE FROM archive_orphan_candidates WHERE archive_id=?", (archive_id,))
                q.commit(); return tuple(out)
            except:
                if q.in_transaction: q.rollback()
                raise
            finally: q.close()

    def _read_regular(self, handle, name):
        if handle is None:
            path = self.layer.archive_dir / name
            if not path.exists(): return None
            return path.read_bytes()
        flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
        try: fd = os.open(name, flags, dir_fd=handle.fd)
        except FileNotFoundError: return None
        except OSError as exc: raise ContentAddressSubstitution(str(exc)) from exc
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ContentAddressSubstitution("archive object is not a regular file")
            chunks=[]
            while True:
                chunk=os.read(fd,65536)
                if not chunk: break
                chunks.append(chunk)
            return b"".join(chunks)
        finally: os.close(fd)

    def _validate(self, q, archive_id, handle=None):
        artifact_name=f"{archive_id}.json"; manifest_name=f"{archive_id}.manifest.json"
        manifest_bytes=self._read_regular(handle, manifest_name)
        if manifest_bytes is None: return
        try: body=json.loads(manifest_bytes)
        except Exception as exc: raise ContentAddressSubstitution("unparseable manifest") from exc
        if body.get("archive_id") != archive_id: raise ContentAddressSubstitution("filename/manifest archive id")
        if hasattr(self.layer, "_verify_manifest_identity"):
            try:
                from experiments.signed_history_compaction.core import ArchiveManifest
                manifest=ArchiveManifest.parse(body); self.layer._verify_manifest_identity(q, manifest)
            except Exception as exc: raise ContentAddressSubstitution("authenticated manifest identity") from exc
            expected_artifact=manifest.artifact_sha256
        else:
            if not self.layer._gc_manifest_identity(body): raise ContentAddressSubstitution("manifest content identity")
            expected_artifact=body.get("artifact_sha256")
        artifact_bytes=self._read_regular(handle, artifact_name)
        if artifact_bytes is not None and hashlib.sha256(artifact_bytes).hexdigest()!=expected_artifact:
            raise ContentAddressSubstitution("artifact digest")

    def _unlink(self, handle, name):
        if handle is None:
            try: (self.layer.archive_dir/name).unlink()
            except FileNotFoundError: pass
            return
        try: os.unlink(name, dir_fd=handle.fd)
        except FileNotFoundError: pass

    def delete_candidate(self, candidate, expected_generation=None):
        if not isinstance(candidate, Candidate): raise TypeError("candidate")
        with self._namespace_scope() as handle:
            self._require_namespace_authority()
            q=self.layer.store._con()
            try:
                q.execute("BEGIN IMMEDIATE")
                self._require_namespace_authority()
                generation=q.execute("SELECT generation FROM archive_retention_state").fetchone()[0]
                if expected_generation is not None and generation!=expected_generation:
                    raise StaleRetentionGeneration("generation changed")
                row=q.execute("SELECT first_seen_generation FROM archive_orphan_candidates WHERE archive_id=?",(candidate.archive_id,)).fetchone()
                if row is None: q.commit(); return "ALREADY_GONE"
                if generation-row[0] < self.grace: raise StaleRetentionGeneration("grace")
                if candidate.archive_id in self._reachable(q):
                    q.execute("DELETE FROM archive_orphan_candidates WHERE archive_id=?",(candidate.archive_id,)); q.commit()
                    raise CandidateBecameReachable(candidate.archive_id)
                self._validate(q,candidate.archive_id,handle)
                assert_configured=getattr(self.layer,"_assert_configured_namespace",None)
                if handle is not None and assert_configured is not None: assert_configured(handle)
                self._require_namespace_authority()
                self._unlink(handle,f"{candidate.archive_id}.json")
                self._unlink(handle,f"{candidate.archive_id}.manifest.json")
                if handle is not None: os.fsync(handle.fd)
                q.execute("DELETE FROM archive_orphan_candidates WHERE archive_id=?",(candidate.archive_id,)); q.commit()
                return "DELETED"
            except:
                if q.in_transaction: q.rollback()
                raise
            finally: q.close()

    def scavenge(self, expected_generation=None):
        out={}
        for candidate in self.scan():
            try: out[candidate.archive_id]=self.delete_candidate(candidate,expected_generation)
            except StaleRetentionGeneration: out[candidate.archive_id]="RETAINED_GRACE"
            except CandidateBecameReachable: out[candidate.archive_id]="REACHABLE"
        return out


class UnsafeEagerDelete:
    def delete(self, layer, archive_id):
        for path in layer._archive_paths(archive_id):
            try: path.unlink()
            except FileNotFoundError: pass
