from __future__ import annotations
import hashlib,hmac,json,os,tempfile
from dataclasses import asdict,dataclass
from pathlib import Path
from typing import Mapping
class GossipError(RuntimeError): pass
class AuthenticationError(GossipError): pass
class ClockRollback(GossipError): pass
class IdentityError(GossipError): pass
def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
def digest(obj): return hashlib.sha256(canonical(obj)).hexdigest()
def sign(key,obj): return hmac.new(key,canonical(obj),hashlib.sha256).hexdigest()
@dataclass(frozen=True)
class SignedView:
    peer_id:str; event_ids:tuple[str,...]; signature:str
    @property
    def unsigned(self): return {'peer_id':self.peer_id,'event_ids':list(self.event_ids)}
    @property
    def view_id(self): return digest({**self.unsigned,'signature':self.signature})
    @classmethod
    def issue(cls,*,peer_id,event_ids,key):
        u={'peer_id':peer_id,'event_ids':list(event_ids)}
        return cls(peer_id,tuple(event_ids),sign(key,u))
@dataclass(frozen=True)
class Observation:
    observer_id:str; peer_id:str; view_id:str; event_ids:tuple[str,...]; received_at:int; observer_signature:str
    @property
    def unsigned(self): return {'observer_id':self.observer_id,'peer_id':self.peer_id,'view_id':self.view_id,'event_ids':list(self.event_ids),'received_at':self.received_at}
    @property
    def observation_id(self): return digest({**self.unsigned,'observer_signature':self.observer_signature})
def relation(left,right):
    common=min(len(left),len(right))
    if left[:common]!=right[:common]: return 'DIVERGENT'
    if len(left)==len(right): return 'SAME'
    return 'LEFT_PREFIX' if len(left)<len(right) else 'RIGHT_PREFIX'
class GossipStore:
    def __init__(self,path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def save(self,state):
        fd,tmp=tempfile.mkstemp(prefix=self.path.name+'.',dir=str(self.path.parent))
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as f:
                json.dump(state,f,sort_keys=True,separators=(',',':')); f.flush(); os.fsync(f.fileno())
            os.replace(tmp,self.path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
    def load(self): return json.loads(self.path.read_text(encoding='utf-8'))
class GossipTracker:
    def __init__(self,*,peer_keys:Mapping[str,bytes],observer_keys:Mapping[str,bytes],store:GossipStore|None=None,max_silence:int=30):
        self.peer_keys=dict(peer_keys); self.observer_keys=dict(observer_keys); self.store=store; self.max_silence=max_silence
        self.state={'last_clock':0,'observations':[],'seen_observer_view':{},'incidents':[]}
        if store and store.path.exists(): self.state=store.load()
    def _persist(self):
        if self.store: self.store.save(self.state)
    def _check_clock(self,now):
        if type(now) is not int or now<self.state['last_clock']: raise ClockRollback('trusted clock rollback/type')
        self.state['last_clock']=now
    def _verify_view(self,view):
        key=self.peer_keys.get(view.peer_id)
        if key is None: raise IdentityError('unknown peer')
        if not hmac.compare_digest(sign(key,view.unsigned),view.signature): raise AuthenticationError('peer view signature')
    def _sign_obs(self,observer_id,view,now):
        key=self.observer_keys.get(observer_id)
        if key is None: raise IdentityError('unknown observer')
        u={'observer_id':observer_id,'peer_id':view.peer_id,'view_id':view.view_id,'event_ids':list(view.event_ids),'received_at':now}
        return Observation(observer_id,view.peer_id,view.view_id,view.event_ids,now,sign(key,u))
    @staticmethod
    def _encode(o):
        r=asdict(o); r['event_ids']=list(o.event_ids); return r
    @staticmethod
    def _decode(r): return Observation(r['observer_id'],r['peer_id'],r['view_id'],tuple(r['event_ids']),r['received_at'],r['observer_signature'])
    def _incident(self,kind,peer,left,right):
        p={'kind':kind,'peer_id':peer,'left_observation_id':left.observation_id,'right_observation_id':right.observation_id,'left_view_id':left.view_id,'right_view_id':right.view_id}
        iid=digest(p)
        if all(i['incident_id']!=iid for i in self.state['incidents']): self.state['incidents'].append({'incident_id':iid,**p})
    def observe(self,*,observer_id,view,now):
        self._check_clock(now); self._verify_view(view)
        dk=f'{observer_id}:{view.peer_id}:{view.view_id}'
        if dk in self.state['seen_observer_view']:
            self._persist(); return 'DUPLICATE_IGNORED'
        obs=self._sign_obs(observer_id,view,now)
        prior=[self._decode(x) for x in self.state['observations'] if x['peer_id']==view.peer_id]
        for other in prior:
            rel=relation(other.event_ids,obs.event_ids)
            if rel=='DIVERGENT': self._incident('SPLIT_VIEW',view.peer_id,other,obs)
            elif rel=='RIGHT_PREFIX' and other.observer_id!=observer_id and other.received_at<=now:
                self._incident('FREEZE_SUSPECTED',view.peer_id,other,obs)
        self.state['observations'].append(self._encode(obs)); self.state['seen_observer_view'][dk]=obs.observation_id; self._persist()
        return self.classify(peer_id=view.peer_id,observer_id=observer_id,now=now)
    def missing_exchange(self,*,peer_id,observer_id,now):
        self._check_clock(now); self._persist(); return 'UNKNOWN_PARTITIONED'
    def _rebuild_incidents(self):
        self.verify_persisted_observations()
        observations=[self._decode(x) for x in self.state['observations']]
        rebuilt=[]
        for index, right in enumerate(observations):
            for left in observations[:index]:
                if left.peer_id != right.peer_id:
                    continue
                rel=relation(left.event_ids,right.event_ids)
                kind=None
                if rel=='DIVERGENT':
                    kind='SPLIT_VIEW'
                elif rel=='RIGHT_PREFIX' and left.observer_id!=right.observer_id and left.received_at<=right.received_at:
                    kind='FREEZE_SUSPECTED'
                if kind:
                    payload={'kind':kind,'peer_id':right.peer_id,'left_observation_id':left.observation_id,'right_observation_id':right.observation_id,'left_view_id':left.view_id,'right_view_id':right.view_id}
                    rebuilt.append({'incident_id':digest(payload),**payload})
        dedup={item['incident_id']:item for item in rebuilt}
        self.state['incidents']=list(dedup.values())
        self._persist()
        return self.state['incidents']
    def classify(self,*,peer_id,observer_id,now):
        self._check_clock(now)
        inc=[i for i in self._rebuild_incidents() if i['peer_id']==peer_id]
        if any(i['kind']=='SPLIT_VIEW' for i in inc): return 'SPLIT_VIEW'
        if any(i['kind']=='FREEZE_SUSPECTED' for i in inc): return 'FREEZE_SUSPECTED'
        obs=[self._decode(x) for x in self.state['observations'] if x['peer_id']==peer_id and x['observer_id']==observer_id]
        if not obs: return 'UNKNOWN_PARTITIONED'
        latest=max(obs,key=lambda x:x.received_at)
        return 'UNKNOWN_PARTITIONED' if now-latest.received_at>self.max_silence else 'CURRENT'
    def historical_incidents(self,peer_id): return tuple(i['kind'] for i in self._rebuild_incidents() if i['peer_id']==peer_id)
    def verify_persisted_observations(self):
        seen=set()
        for raw in self.state['observations']:
            o=self._decode(raw); key=self.observer_keys.get(o.observer_id)
            if key is None or not hmac.compare_digest(sign(key,o.unsigned),o.observer_signature): raise AuthenticationError('persisted observer evidence')
            if o.observation_id in seen: raise AuthenticationError('duplicate durable observation id')
            seen.add(o.observation_id)
class UnsafeTimeoutClassifier:
    def classify_timeout(self): return 'SPLIT_VIEW'
