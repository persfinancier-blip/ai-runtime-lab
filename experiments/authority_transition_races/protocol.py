from __future__ import annotations
import hashlib,hmac,json,sqlite3
from dataclasses import dataclass
class E(RuntimeError):pass
class Stale(E):pass
class Conflict(E):pass
class Unknown(E):pass
def can(o):return json.dumps(o,sort_keys=True,separators=(",",":")).encode()
def dig(o):return hashlib.sha256(can(o)).hexdigest()
def kid(k):return hashlib.sha256(k).hexdigest()[:16]
def sign(k,o):return hmac.new(k,can(o),hashlib.sha256).hexdigest()
@dataclass(frozen=True)
class Sig: signer_id:str; signature:str
@dataclass(frozen=True)
class A:
 kind:str; version:int; generation:int; threshold:int; keys:dict
 @property
 def desc(self):return {"kind":self.kind,"version":self.version,"generation":self.generation,"threshold":self.threshold,"keys":dict(sorted(self.keys.items()))}
 @property
 def id(self):return dig(self.desc)
def verify(a,p,ss):
 seen=set(); n=0
 for s in ss:
  if s.signer_id in seen:continue
  seen.add(s.signer_id); hx=a.keys.get(s.signer_id)
  if hx and hmac.compare_digest(sign(bytes.fromhex(hx),p),s.signature):n+=1
 if n<a.threshold:raise E("threshold")
def rotp(r,c,n):return {"kind":"rot","root":r.id,"old":c.id,"new":n.desc}
def recp(r,n,c):return {"kind":"recover","old":r.id,"recovery":c.id,"new":n.desc}
@dataclass(frozen=True)
class P:
 pid:str; kind:str; pre_r:str; pre_c:str; new:A; sig1:tuple; sig2:tuple=(); sig3:tuple=()
 @property
 def td(self):return dig({"pid":self.pid,"kind":self.kind,"pre_r":self.pre_r,"pre_c":self.pre_c,"new":self.new.desc})
class Store:
 def __init__(self,path,r,c):
  self.path=str(path); q=sqlite3.connect(self.path);q.execute("PRAGMA journal_mode=WAL");q.executescript("CREATE TABLE IF NOT EXISTS auth(id TEXT PRIMARY KEY,body TEXT);CREATE TABLE IF NOT EXISTS head(x INTEGER PRIMARY KEY,r TEXT,c TEXT,seq INTEGER);CREATE TABLE IF NOT EXISTS tr(pid TEXT PRIMARY KEY,td TEXT,r0 TEXT,c0 TEXT,r1 TEXT,c1 TEXT,seq INTEGER,ev TEXT);")
  if not q.execute("select count(*) from head").fetchone()[0]:
   self.put(q,r);self.put(q,c);q.execute("insert into head values(1,?,?,0)",(r.id,c.id));q.commit()
  q.close()
 def con(self):
  q=sqlite3.connect(self.path,timeout=5,isolation_level=None,check_same_thread=False);q.execute("pragma busy_timeout=5000");return q
 def put(self,q,a):q.execute("insert or ignore into auth values(?,?)",(a.id,json.dumps(a.desc,sort_keys=True)))
 def get(self,q,i):
  x=json.loads(q.execute("select body from auth where id=?",(i,)).fetchone()[0]);a=A(x["kind"],x["version"],x["generation"],x["threshold"],x["keys"])
  if a.id!=i: raise E("digest")
  return a
 def head(self):
  q=self.con();x=q.execute("select r,c,seq from head").fetchone();q.close();return x
 def commit(self,p,timeout=False):
  q=self.con()
  try:
   q.execute("begin immediate"); old=q.execute("select td,r1,c1,seq,ev from tr where pid=?",(p.pid,)).fetchone()
   if old:
    if old[0]!=p.td:raise Conflict()
    q.commit();return json.loads(old[4])
   r0,c0,seq=q.execute("select r,c,seq from head").fetchone()
   if (r0,c0)!=(p.pre_r,p.pre_c):raise Stale()
   r=self.get(q,r0);c=self.get(q,c0)
   if p.kind=="rot":
    if p.new.kind!="recovery" or p.new.version!=c.version+1:raise E("successor")
    z=rotp(r,c,p.new);verify(c,z,p.sig1);verify(p.new,z,p.sig2);verify(r,z,p.sig3);r1,c1=r,p.new
   else:
    if p.new.kind!="root" or p.new.version!=r.version+1 or p.new.generation!=r.generation+1:raise E("successor")
    z=recp(r,p.new,c);verify(c,z,p.sig1);r1,c1=p.new,c
   self.put(q,r1);self.put(q,c1); ev={"pid":p.pid,"td":p.td,"r0":r0,"c0":c0,"r1":r1.id,"c1":c1.id,"seq":seq+1}
   q.execute("insert into tr values(?,?,?,?,?,?,?,?)",(p.pid,p.td,r0,c0,r1.id,c1.id,seq+1,json.dumps(ev,sort_keys=True)))
   if q.execute("update head set r=?,c=?,seq=? where x=1 and r=? and c=? and seq=?",(r1.id,c1.id,seq+1,r0,c0,seq)).rowcount!=1:raise Stale()
   q.commit()
   if timeout:raise Unknown()
   return ev
  except:
   if q.in_transaction:q.rollback()
   raise
  finally:q.close()
 def reconcile(self,p):
  q=self.con();x=q.execute("select td,ev from tr where pid=?",(p.pid,)).fetchone();q.close()
  if not x:return None
  if x[0]!=p.td:raise Conflict()
  return json.loads(x[1])
class Unsafe:
 def __init__(self,r,c):self.r=r;self.c=c;self.accepted=[]
 def check(self,p):return (self.r,self.c)==(p.pre_r,p.pre_c)
 def write(self,p,r,c):self.r,self.c=r,c;self.accepted.append(p.pid)
