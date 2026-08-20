from __future__ import annotations
import hashlib,hmac,json,os,tempfile
from dataclasses import dataclass,asdict
from pathlib import Path

def can(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def dig(x): return hashlib.sha256(can(x)).hexdigest()
def sig(k,x): return hmac.new(k,can(x),hashlib.sha256).hexdigest()

class E(RuntimeError): pass
class Auth(E): pass
class Rollback(E): pass
class Pred(E): pass
class Equiv(E): pass

@dataclass(frozen=True)
class View:
    peer:str
    events:tuple
    signature:str
    @property
    def unsigned(self): return {"peer":self.peer,"events":list(self.events)}
    @property
    def id(self): return dig({**self.unsigned,"signature":self.signature})
    @classmethod
    def issue(cls,peer,events,key):
        u={"peer":peer,"events":list(events)}
        return cls(peer,tuple(events),sig(key,u))

@dataclass(frozen=True)
class Obs:
    observer:str
    seq:int
    pred:str|None
    peer:str
    view_id:str
    events:tuple
    peer_signature:str
    claimed_time:int
    signature:str
    @property
    def peer_view(self): return View(self.peer,self.events,self.peer_signature)
    @property
    def unsigned(self):
        return {"observer":self.observer,"seq":self.seq,"pred":self.pred,"peer":self.peer,
                "view_id":self.view_id,"events":list(self.events),"peer_signature":self.peer_signature,
                "claimed_time":self.claimed_time}
    @property
    def id(self): return dig({**self.unsigned,"signature":self.signature})

def rel(a,b):
    n=min(len(a),len(b))
    if a[:n]!=b[:n]: return "DIVERGENT"
    if len(a)==len(b): return "SAME"
    return "LEFT_PREFIX" if len(a)<len(b) else "RIGHT_PREFIX"

class Store:
    def __init__(self,p): self.path=Path(p)
    def save(self,s):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(dir=self.path.parent)
        try:
            with os.fdopen(fd,"w") as f:
                json.dump(s,f,sort_keys=True); f.flush(); os.fsync(f.fileno())
            os.replace(tmp,self.path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
    def load(self): return json.loads(self.path.read_text())

class Tracker:
    def __init__(self,peer_keys,observer_keys,store=None,quorum=2):
        self.pk=peer_keys; self.ok=observer_keys; self.store=store; self.quorum=quorum
        self.s={"obs":[],"heads":{},"equiv":[]}
        if store and store.path.exists(): self.s=store.load(); self.verify()
    def persist(self):
        if self.store:self.store.save(self.s)
    def verify_view(self,v):
        key=self.pk.get(v.peer)
        if key is None: raise Auth("unknown peer")
        if not hmac.compare_digest(sig(key,v.unsigned),v.signature): raise Auth("peer signature")
    def issue(self,observer,v,claimed_time=0):
        self.verify_view(v)
        if observer not in self.ok: raise Auth("unknown observer")
        h=self.s["heads"].get(observer); seq=1 if not h else h["seq"]+1; pred=None if not h else h["id"]
        u={"observer":observer,"seq":seq,"pred":pred,"peer":v.peer,"view_id":v.id,
           "events":list(v.events),"peer_signature":v.signature,"claimed_time":claimed_time}
        return Obs(observer,seq,pred,v.peer,v.id,v.events,v.signature,claimed_time,sig(self.ok[observer],u))
    def dec(self,r):
        return Obs(r["observer"],r["seq"],r["pred"],r["peer"],r["view_id"],tuple(r["events"]),
                   r["peer_signature"],r["claimed_time"],r["signature"])
    def verify_obs(self,o):
        if o.observer not in self.ok or type(o.seq) is not int or o.seq<1: raise Auth("observer identity/sequence")
        if not hmac.compare_digest(sig(self.ok[o.observer],o.unsigned),o.signature): raise Auth("observer signature")
        v=o.peer_view
        self.verify_view(v)
        if v.id!=o.view_id: raise Auth("peer view id binding")
    def accept(self,o):
        self.verify_obs(o); h=self.s["heads"].get(o.observer)
        if not h:
            if o.seq!=1 or o.pred is not None: raise Pred()
        else:
            if o.seq<h["seq"]: raise Rollback()
            if o.seq==h["seq"]:
                if o.id==h["id"]: return "DUPLICATE_IGNORED"
                self.s["equiv"].append([o.observer,o.seq,h["id"],o.id]); self.persist(); raise Equiv()
            if o.seq!=h["seq"]+1: raise Rollback()
            if o.pred!=h["id"]: raise Pred()
        self.s["obs"].append({**asdict(o),"events":list(o.events)})
        self.s["heads"][o.observer]={"seq":o.seq,"id":o.id}; self.persist(); return self.classify(o.peer)
    def chains(self):
        d={}
        for r in self.s["obs"]: d.setdefault(r["observer"],[]).append(self.dec(r))
        for x in d.values():x.sort(key=lambda o:o.seq)
        return d
    def freezes(self,peer):
        out=set()
        for who,xs in self.chains().items():
            xs=[x for x in xs if x.peer==peer]
            for i,a in enumerate(xs):
                for b in xs[i+1:]:
                    if rel(a.events,b.events)=="RIGHT_PREFIX":out.add(who)
        return out
    def classify(self,peer):
        self.verify(); xs=[self.dec(r) for r in self.s["obs"] if r["peer"]==peer]
        if any(rel(a.events,b.events)=="DIVERGENT" for i,a in enumerate(xs) for b in xs[i+1:]): return "SPLIT_VIEW"
        f=self.freezes(peer)
        return "CORROBORATED_FREEZE" if len(f)>=self.quorum else "LOCAL_FREEZE_SUSPECTED" if f else "CURRENT"
    def missing(self,peer): return "UNKNOWN_PARTITIONED"
    def verify(self):
        heads={}
        for who,xs in self.chains().items():
            prev=None
            for n,o in enumerate(xs,1):
                self.verify_obs(o)
                if o.seq!=n: raise Rollback()
                if o.pred!=(None if prev is None else prev.id): raise Pred()
                prev=o
            heads[who]={"seq":prev.seq,"id":prev.id}
        if heads!=self.s["heads"]: raise Auth("head cache")
        return True

class Unsafe:
    def classify(self,newer_time,older_time): return "FREEZE_SUSPECTED" if newer_time<=older_time else "CURRENT"
