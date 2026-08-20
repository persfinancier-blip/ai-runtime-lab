from __future__ import annotations
import json,re
from dataclasses import dataclass
HEX64=re.compile(r"^[0-9a-f]{64}$")
class ScavengeError(RuntimeError): pass
class StaleRetentionGeneration(ScavengeError): pass
class CandidateBecameReachable(ScavengeError): pass
class ContentAddressSubstitution(ScavengeError): pass
@dataclass(frozen=True)
class Candidate:
    archive_id:str; observed_generation:int; first_seen_generation:int; artifact:bool; manifest:bool
class ArchiveScavenger:
    def __init__(self,layer,grace_generations=2):
        if type(grace_generations) is not int or grace_generations<1: raise ValueError("grace")
        self.layer=layer; self.grace=grace_generations
        q=layer.store._con(); q.executescript("""CREATE TABLE IF NOT EXISTS archive_retention_state(singleton INTEGER PRIMARY KEY CHECK(singleton=1),generation INTEGER NOT NULL); INSERT OR IGNORE INTO archive_retention_state VALUES(1,0); CREATE TABLE IF NOT EXISTS archive_orphan_candidates(archive_id TEXT PRIMARY KEY,first_seen_generation INTEGER NOT NULL,last_seen_generation INTEGER NOT NULL);"""); q.close()
    def generation(self):
        q=self.layer.store._con()
        try:return q.execute("SELECT generation FROM archive_retention_state").fetchone()[0]
        finally:q.close()
    def advance_generation(self):
        q=self.layer.store._con()
        try:q.execute("BEGIN IMMEDIATE"); q.execute("UPDATE archive_retention_state SET generation=generation+1"); v=q.execute("SELECT generation FROM archive_retention_state").fetchone()[0]; q.commit(); return v
        finally:q.close()
    def _reachable(self,q): return set(self.layer._reachable_archive_ids(q))
    def _fs(self):
        out={}
        for p in self.layer.archive_dir.iterdir():
            n=p.name
            if n.endswith(".manifest.json"): aid=n[:-14]; kind="manifest"
            elif n.endswith(".json"): aid=n[:-5]; kind="artifact"
            else: continue
            if HEX64.fullmatch(aid): out.setdefault(aid,set()).add(kind)
        return out
    def scan(self):
        q=self.layer.store._con()
        try:
            q.execute("BEGIN"); reachable=self._reachable(q); gen=q.execute("SELECT generation FROM archive_retention_state").fetchone()[0]; fs=self._fs(); out=[]
            for aid,kinds in sorted(fs.items()):
                if aid in reachable: q.execute("DELETE FROM archive_orphan_candidates WHERE archive_id=?",(aid,)); continue
                row=q.execute("SELECT first_seen_generation FROM archive_orphan_candidates WHERE archive_id=?",(aid,)).fetchone(); first=gen if row is None else row[0]
                q.execute("INSERT INTO archive_orphan_candidates VALUES(?,?,?) ON CONFLICT(archive_id) DO UPDATE SET last_seen_generation=excluded.last_seen_generation",(aid,first,gen))
                out.append(Candidate(aid,gen,first,"artifact" in kinds,"manifest" in kinds))
            for (aid,) in q.execute("SELECT archive_id FROM archive_orphan_candidates").fetchall():
                if aid not in fs or aid in reachable:q.execute("DELETE FROM archive_orphan_candidates WHERE archive_id=?",(aid,))
            q.commit(); return tuple(out)
        finally:q.close()
    def _validate(self,aid,ap,mp):
        if mp.exists():
            body=json.loads(mp.read_text())
            if body.get("archive_id")!=aid: raise ContentAddressSubstitution("filename")
            if not self.layer._gc_manifest_identity(body): raise ContentAddressSubstitution("manifest identity")
            if ap.exists() and not self.layer._gc_artifact_identity(body,ap.read_bytes()): raise ContentAddressSubstitution("artifact digest")
    def delete_candidate(self,c,expected_generation=None):
        q=self.layer.store._con()
        try:
            q.execute("BEGIN IMMEDIATE"); gen=q.execute("SELECT generation FROM archive_retention_state").fetchone()[0]
            if expected_generation is not None and gen!=expected_generation: raise StaleRetentionGeneration("generation changed")
            row=q.execute("SELECT first_seen_generation FROM archive_orphan_candidates WHERE archive_id=?",(c.archive_id,)).fetchone()
            if row is None:q.commit(); return "ALREADY_GONE"
            if gen-row[0]<self.grace: raise StaleRetentionGeneration("grace")
            if c.archive_id in self._reachable(q):
                q.execute("DELETE FROM archive_orphan_candidates WHERE archive_id=?",(c.archive_id,)); q.commit(); raise CandidateBecameReachable(c.archive_id)
            ap,mp=self.layer._archive_paths(c.archive_id); self._validate(c.archive_id,ap,mp)
            for p in (ap,mp):
                try:p.unlink()
                except FileNotFoundError:pass
            q.execute("DELETE FROM archive_orphan_candidates WHERE archive_id=?",(c.archive_id,)); q.commit(); return "DELETED"
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def scavenge(self,expected_generation=None):
        out={}
        for c in self.scan():
            try:out[c.archive_id]=self.delete_candidate(c,expected_generation)
            except StaleRetentionGeneration:out[c.archive_id]="RETAINED_GRACE"
            except CandidateBecameReachable:out[c.archive_id]="REACHABLE"
        return out
class UnsafeEagerDelete:
    def delete(self,layer,aid):
        for p in layer._archive_paths(aid):
            try:p.unlink()
            except FileNotFoundError:pass
