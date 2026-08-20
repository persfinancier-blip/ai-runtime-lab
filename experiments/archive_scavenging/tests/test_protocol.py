import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from experiments.archive_scavenging.protocol import *
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":")).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
class Store:
 def __init__(self,p):
  self.p=str(p);q=sqlite3.connect(self.p);q.executescript("CREATE TABLE base(id INTEGER PRIMARY KEY,archive_id TEXT);INSERT INTO base VALUES(1,NULL);CREATE TABLE manifests(archive_id TEXT PRIMARY KEY,previous_archive_id TEXT,body TEXT);");q.close()
 def _con(self):q=sqlite3.connect(self.p,timeout=5);q.execute("PRAGMA busy_timeout=5000");return q
class Layer:
 def __init__(self,td):self.store=Store(Path(td)/"db");self.archive_dir=Path(td)/"a";self.archive_dir.mkdir()
 def _archive_paths(self,a):return self.archive_dir/f"{a}.json",self.archive_dir/f"{a}.manifest.json"
 def _reachable_archive_ids(self,q):
  a=q.execute("SELECT archive_id FROM base").fetchone()[0];out=[];seen=set()
  while a:
   if a in seen:raise RuntimeError("cycle")
   seen.add(a);out.append(a);r=q.execute("SELECT previous_archive_id,body FROM manifests WHERE archive_id=?",(a,)).fetchone()
   if not r:raise RuntimeError("missing")
   if not self._gc_manifest_identity(json.loads(r[1])):raise RuntimeError("identity")
   a=r[0]
  return out
 def _gc_manifest_identity(self,b):
  c=dict(b);claimed=c.pop("archive_id",None);return claimed==sha(canon(c))
 def _gc_artifact_identity(self,b,data):return b.get("artifact_sha256")==sha(data)
 def export(self,previous=None,commit=False,artifact_only=False,manifest_only=False):
  data=b'{"rows":[]}';p={"previous_archive_id":previous,"artifact_sha256":sha(data)};a=sha(canon(p));b={"archive_id":a,**p};ap,mp=self._archive_paths(a)
  if not manifest_only:ap.write_bytes(data)
  if not artifact_only:mp.write_bytes(canon(b))
  if commit:
   q=self.store._con();q.execute("INSERT INTO manifests VALUES(?,?,?)",(a,previous,json.dumps(b,sort_keys=True,separators=(",",":"))));q.execute("UPDATE base SET archive_id=?",(a,));q.commit();q.close()
  return a
class Tests(unittest.TestCase):
 def age(self,g,n=2):
  for _ in range(n):g.advance_generation()
 def test_orphan_after_grace(self):
  with tempfile.TemporaryDirectory() as td:
   l=Layer(td);a=l.export();g=ArchiveScavenger(l,2);g.scan();self.assertEqual(g.scavenge()[a],"RETAINED_GRACE");self.age(g);self.assertEqual(g.scavenge()[a],"DELETED")
 def test_current_and_historical_reachable_protected(self):
  with tempfile.TemporaryDirectory() as td:
   l=Layer(td);a=l.export(commit=True);b=l.export(previous=a,commit=True);g=ArchiveScavenger(l);self.age(g,5);self.assertEqual(g.scan(),());self.assertTrue(all(p.exists() for x in (a,b) for p in l._archive_paths(x)))
 def test_artifact_and_manifest_only(self):
  with tempfile.TemporaryDirectory() as td:
   l=Layer(td);a=l.export(artifact_only=True);b=l.export(manifest_only=True);g=ArchiveScavenger(l,1);g.scan();self.age(g,1);r=g.scavenge();self.assertEqual(r[a],"DELETED");self.assertEqual(r[b],"DELETED")
 def test_candidate_becomes_reachable(self):
  with tempfile.TemporaryDirectory() as td:
   l=Layer(td);a=l.export();g=ArchiveScavenger(l,1);c=g.scan()[0];self.age(g);body=json.loads(l._archive_paths(a)[1].read_text());q=l.store._con();q.execute("INSERT INTO manifests VALUES(?,?,?)",(a,None,json.dumps(body,sort_keys=True,separators=(",",":"))));q.execute("UPDATE base SET archive_id=?",(a,));q.commit();q.close()
   with self.assertRaises(CandidateBecameReachable):g.delete_candidate(c)
   self.assertTrue(all(p.exists() for p in l._archive_paths(a)))
 def test_unknown_commit_reconciled_by_scan(self):
  with tempfile.TemporaryDirectory() as td:
   l=Layer(td);a=l.export();g=ArchiveScavenger(l,1);g.scan();body=json.loads(l._archive_paths(a)[1].read_text());q=l.store._con();q.execute("INSERT INTO manifests VALUES(?,?,?)",(a,None,json.dumps(body,sort_keys=True,separators=(",",":"))));q.execute("UPDATE base SET archive_id=?",(a,));q.commit();q.close();self.age(g);self.assertEqual(g.scan(),())
 def test_stale_generation(self):
  with tempfile.TemporaryDirectory() as td:
   l=Layer(td);l.export();g=ArchiveScavenger(l,1);c=g.scan()[0];old=g.generation();self.age(g)
   with self.assertRaises(StaleRetentionGeneration):g.delete_candidate(c,old)
 def test_restart_idempotent(self):
  with tempfile.TemporaryDirectory() as td:
   l=Layer(td);a=l.export();g=ArchiveScavenger(l,1);g.scan();self.age(g);g2=ArchiveScavenger(l,1);self.assertEqual(g2.scavenge()[a],"DELETED");self.assertEqual(g2.scavenge(),{})
 def test_substitution_fails_closed(self):
  with tempfile.TemporaryDirectory() as td:
   l=Layer(td);a=l.export();g=ArchiveScavenger(l,1);c=g.scan()[0];self.age(g);mp=l._archive_paths(a)[1];b=json.loads(mp.read_text());b["previous_archive_id"]="f"*64;mp.write_bytes(canon(b))
   with self.assertRaises(ContentAddressSubstitution):g.delete_candidate(c)
   self.assertTrue(mp.exists())
 def test_unsafe_can_delete_reachable(self):
  with tempfile.TemporaryDirectory() as td:
   l=Layer(td);a=l.export(commit=True);UnsafeEagerDelete().delete(l,a);self.assertFalse(any(p.exists() for p in l._archive_paths(a)))
if __name__=="__main__":unittest.main()
