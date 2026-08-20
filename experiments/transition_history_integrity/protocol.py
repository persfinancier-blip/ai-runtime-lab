from __future__ import annotations
import hashlib,hmac,json,sqlite3
from dataclasses import dataclass,asdict
class HistoryError(RuntimeError):pass
class IntegrityError(HistoryError):pass
class ThresholdError(HistoryError):pass
class StaleError(HistoryError):pass
class ConflictError(HistoryError):pass
class UnknownOutcome(HistoryError):pass
def canonical(o):return json.dumps(o,sort_keys=True,separators=(',',':')).encode()
def digest(o):return hashlib.sha256(canonical(o)).hexdigest()
def kid(k):return hashlib.sha256(k).hexdigest()[:16]
def sign(k,o):return hmac.new(k,canonical(o),hashlib.sha256).hexdigest()
@dataclass(frozen=True)
class Sig: signer_id:str; signature:str
@dataclass(frozen=True)
class Authority:
 kind:str; version:int; generation:int; threshold:int; keys:dict[str,str]
 @property
 def descriptor(self):return {'kind':self.kind,'version':self.version,'generation':self.generation,'threshold':self.threshold,'keys':dict(sorted(self.keys.items()))}
 @property
 def authority_id(self):return digest(self.descriptor)
def verify_threshold(a,p,ss):
 seen=set(); n=0
 for raw in ss:
  s=raw if isinstance(raw,Sig) else Sig(raw['signer_id'],raw['signature'])
  if s.signer_id in seen:continue
  seen.add(s.signer_id); hx=a.keys.get(s.signer_id)
  if hx and hmac.compare_digest(sign(bytes.fromhex(hx),p),s.signature):n+=1
 if n<a.threshold:raise ThresholdError(f'valid={n} threshold={a.threshold}')
def rotation_payload(root,old,new):return {'kind':'rotate_recovery','root':root.authority_id,'old':old.authority_id,'new':new.descriptor}
def recovery_payload(old,new,recovery):return {'kind':'recover_root','old_root':old.authority_id,'recovery':recovery.authority_id,'new':new.descriptor}
@dataclass(frozen=True)
class Proposal:
 proposal_id:str; kind:str; predecessor_root_id:str; predecessor_recovery_id:str; successor:Authority; sig1:tuple[Sig,...]; sig2:tuple[Sig,...]=(); sig3:tuple[Sig,...]=()
 @property
 def transition_digest(self):return digest({'proposal_id':self.proposal_id,'kind':self.kind,'predecessor_root_id':self.predecessor_root_id,'predecessor_recovery_id':self.predecessor_recovery_id,'successor':self.successor.descriptor})
class HistoryStore:
 def __init__(self,path,bootstrap_root,bootstrap_recovery):
  self.path=str(path); q=sqlite3.connect(self.path); q.execute('PRAGMA journal_mode=WAL');q.executescript('''CREATE TABLE IF NOT EXISTS authorities(authority_id TEXT PRIMARY KEY,kind TEXT NOT NULL,body TEXT NOT NULL);CREATE TABLE IF NOT EXISTS bootstrap(singleton INTEGER PRIMARY KEY CHECK(singleton=1),root_id TEXT NOT NULL,recovery_id TEXT NOT NULL);CREATE TABLE IF NOT EXISTS head(singleton INTEGER PRIMARY KEY CHECK(singleton=1),root_id TEXT NOT NULL,recovery_id TEXT NOT NULL,sequence INTEGER NOT NULL);CREATE TABLE IF NOT EXISTS transitions(sequence INTEGER PRIMARY KEY,proposal_id TEXT NOT NULL UNIQUE,transition_digest TEXT NOT NULL UNIQUE,kind TEXT NOT NULL,predecessor_root_id TEXT NOT NULL,predecessor_recovery_id TEXT NOT NULL,successor_root_id TEXT NOT NULL,successor_recovery_id TEXT NOT NULL,proof_json TEXT NOT NULL);''')
  if q.execute('SELECT COUNT(*) FROM bootstrap').fetchone()[0]==0:
   self._put(q,bootstrap_root);self._put(q,bootstrap_recovery);q.execute('INSERT INTO bootstrap VALUES(1,?,?)',(bootstrap_root.authority_id,bootstrap_recovery.authority_id));q.execute('INSERT INTO head VALUES(1,?,?,0)',(bootstrap_root.authority_id,bootstrap_recovery.authority_id));q.commit()
  q.close()
 def _con(self):q=sqlite3.connect(self.path,timeout=5,isolation_level=None);q.execute('PRAGMA busy_timeout=5000');return q
 def _put(self,q,a):
  body=json.dumps(a.descriptor,sort_keys=True,separators=(',',':'));q.execute('INSERT OR IGNORE INTO authorities VALUES(?,?,?)',(a.authority_id,a.kind,body));row=q.execute('SELECT body FROM authorities WHERE authority_id=?',(a.authority_id,)).fetchone();
  if not row or row[0]!=body:raise IntegrityError('authority substitution')
 def _get(self,q,aid):
  row=q.execute('SELECT body FROM authorities WHERE authority_id=?',(aid,)).fetchone()
  if not row:raise IntegrityError('missing authority')
  x=json.loads(row[0]);a=Authority(x['kind'],x['version'],x['generation'],x['threshold'],dict(x['keys']))
  if a.authority_id!=aid:raise IntegrityError('authority digest mismatch')
  return a
 def commit(self,p,timeout_after_commit=False):
  q=self._con()
  try:
   q.execute('BEGIN IMMEDIATE');old=q.execute('SELECT transition_digest,proof_json FROM transitions WHERE proposal_id=?',(p.proposal_id,)).fetchone()
   if old:
    if old[0]!=p.transition_digest:raise ConflictError('proposal substitution')
    q.commit();proof=json.loads(old[1]);
    if timeout_after_commit:raise UnknownOutcome(p.proposal_id)
    return proof
   r0,c0,seq=q.execute('SELECT root_id,recovery_id,sequence FROM head WHERE singleton=1').fetchone()
   if (r0,c0)!=(p.predecessor_root_id,p.predecessor_recovery_id):raise StaleError('predecessor changed')
   root=self._get(q,r0);rec=self._get(q,c0)
   if p.kind=='rotate_recovery':
    n=p.successor
    if n.kind!='recovery' or n.version!=rec.version+1 or n.generation<=rec.generation:raise IntegrityError('bad recovery successor')
    payload=rotation_payload(root,rec,n);verify_threshold(rec,payload,p.sig1);verify_threshold(n,payload,p.sig2);verify_threshold(root,payload,p.sig3);r1,c1=root,n
   elif p.kind=='recover_root':
    n=p.successor
    if n.kind!='root' or n.version!=root.version+1 or n.generation!=root.generation+1:raise IntegrityError('bad root successor')
    payload=recovery_payload(root,n,rec);verify_threshold(rec,payload,p.sig1);r1,c1=n,rec
   else:raise IntegrityError('unknown kind')
   self._put(q,r1);self._put(q,c1);proof={'proposal_id':p.proposal_id,'transition_digest':p.transition_digest,'kind':p.kind,'payload':payload,'sig1':[asdict(s) for s in p.sig1],'sig2':[asdict(s) for s in p.sig2],'sig3':[asdict(s) for s in p.sig3]}
   q.execute('INSERT INTO transitions VALUES(?,?,?,?,?,?,?,?,?)',(seq+1,p.proposal_id,p.transition_digest,p.kind,r0,c0,r1.authority_id,c1.authority_id,json.dumps(proof,sort_keys=True,separators=(',',':'))));changed=q.execute('UPDATE head SET root_id=?,recovery_id=?,sequence=? WHERE singleton=1 AND root_id=? AND recovery_id=? AND sequence=?',(r1.authority_id,c1.authority_id,seq+1,r0,c0,seq)).rowcount
   if changed!=1:raise StaleError('head CAS')
   q.commit()
   if timeout_after_commit:raise UnknownOutcome(p.proposal_id)
   return proof
  except:
   if q.in_transaction:q.rollback()
   raise
  finally:q.close()
 def verify_history(self):
  q=self._con()
  try:
   b=q.execute('SELECT root_id,recovery_id FROM bootstrap WHERE singleton=1').fetchone()
   if not b:raise IntegrityError('missing bootstrap')
   root=self._get(q,b[0]);rec=self._get(q,b[1]);rows=q.execute('SELECT sequence,proposal_id,transition_digest,kind,predecessor_root_id,predecessor_recovery_id,successor_root_id,successor_recovery_id,proof_json FROM transitions ORDER BY sequence').fetchall()
   for expected,row in enumerate(rows,1):
    seq,pid,td,kind,r0,c0,r1,c1,pj=row
    if seq!=expected:raise IntegrityError('transition sequence gap')
    if (r0,c0)!=(root.authority_id,rec.authority_id):raise IntegrityError('historical predecessor mismatch')
    proof=json.loads(pj)
    if proof.get('proposal_id')!=pid or proof.get('transition_digest')!=td or proof.get('kind')!=kind:raise IntegrityError('proof identity mismatch')
    if kind=='rotate_recovery':
     newrec=self._get(q,c1)
     if r1!=root.authority_id:raise IntegrityError('unexpected root successor')
     expected_payload=rotation_payload(root,rec,newrec)
     if proof.get('payload')!=expected_payload:raise IntegrityError('payload mismatch')
     verify_threshold(rec,expected_payload,proof.get('sig1',[]));verify_threshold(newrec,expected_payload,proof.get('sig2',[]));verify_threshold(root,expected_payload,proof.get('sig3',[]))
     expected_td=digest({'proposal_id':pid,'kind':kind,'predecessor_root_id':r0,'predecessor_recovery_id':c0,'successor':newrec.descriptor})
     if td!=expected_td:raise IntegrityError('transition digest mismatch')
     rec=newrec
    elif kind=='recover_root':
     newroot=self._get(q,r1)
     if c1!=rec.authority_id:raise IntegrityError('unexpected recovery successor')
     expected_payload=recovery_payload(root,newroot,rec)
     if proof.get('payload')!=expected_payload:raise IntegrityError('payload mismatch')
     verify_threshold(rec,expected_payload,proof.get('sig1',[]));expected_td=digest({'proposal_id':pid,'kind':kind,'predecessor_root_id':r0,'predecessor_recovery_id':c0,'successor':newroot.descriptor})
     if td!=expected_td:raise IntegrityError('transition digest mismatch')
     root=newroot
    else:raise IntegrityError('unknown historical kind')
   h=q.execute('SELECT root_id,recovery_id,sequence FROM head WHERE singleton=1').fetchone()
   if h!=(root.authority_id,rec.authority_id,len(rows)):raise IntegrityError('head/history mismatch')
   return {'root_id':root.authority_id,'recovery_id':rec.authority_id,'sequence':len(rows)}
  finally:q.close()
 def reconcile_verified(self,p):
  self.verify_history();q=self._con()
  try:
   row=q.execute('SELECT transition_digest,proof_json FROM transitions WHERE proposal_id=?',(p.proposal_id,)).fetchone()
   if not row:return None
   if row[0]!=p.transition_digest:raise ConflictError('proposal substitution')
   proof=json.loads(row[1])
   if proof.get('transition_digest')!=p.transition_digest:raise IntegrityError('proof mismatch')
   return proof
  finally:q.close()
class UnsafeEvidenceReader:
 def reconcile(self,conn,proposal_id):
  row=conn.execute('SELECT proof_json FROM transitions WHERE proposal_id=?',(proposal_id,)).fetchone();return None if not row else json.loads(row[0])
