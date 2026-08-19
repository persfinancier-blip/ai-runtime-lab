from __future__ import annotations
import hashlib,hmac,json
from dataclasses import dataclass,asdict
from typing import Any
SCHEMA_VERSION=1; ALG='HMAC-SHA256'
class RecordError(RuntimeError): pass
class ParseError(RecordError): pass
class AuthError(RecordError): pass
class ReplayError(RecordError): pass
class DomainError(RecordError): pass
class KeyErrorRecord(RecordError): pass
def _no_dups(pairs):
    out={}
    for k,v in pairs:
        if k in out: raise ParseError(f'duplicate key: {k}')
        out[k]=v
    return out
def parse_json_strict(raw):
    try: obj=json.loads(raw,object_pairs_hook=_no_dups,parse_float=lambda _: (_ for _ in ()).throw(ParseError('floats forbidden')))
    except RecordError: raise
    except Exception as e: raise ParseError(str(e)) from e
    if not isinstance(obj,dict): raise ParseError('envelope must be object')
    return obj
def canonical_bytes(obj):
    def check(x):
        if x is None or isinstance(x,(str,bool,int)): return
        if isinstance(x,list):
            for v in x: check(v)
            return
        if isinstance(x,dict):
            for k,v in x.items():
                if not isinstance(k,str): raise ParseError('non-string key')
                check(v)
            return
        raise ParseError(f'unsupported type: {type(x).__name__}')
    check(obj)
    return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
@dataclass(frozen=True)
class LaunchRecord:
    task_id:str; pid:int; starttime:int; process_group:int; sandbox_generation:int; credential_generation:int; capability_generation:int; authority_epoch:int; record_seq:int; launch_nonce:str
    def validate(self):
        if not self.task_id or not self.launch_nonce: raise DomainError('empty identity')
        for n,v in asdict(self).items():
            if n in {'task_id','launch_nonce'}: continue
            if not isinstance(v,int) or isinstance(v,bool) or v<0: raise DomainError(f'invalid integer {n}')
@dataclass
class Keyring:
    current_key_id:str; keys:dict[str,bytes]; authority_epoch:int
    def key(self,key_id):
        if key_id!=self.current_key_id: raise KeyErrorRecord('non-current key')
        if key_id not in self.keys: raise KeyErrorRecord('unknown key')
        return self.keys[key_id]
@dataclass
class ReplayGuard:
    min_seq_by_task:dict[str,int]
    def require_fresh(self,task,seq):
        if seq<self.min_seq_by_task.get(task,0): raise ReplayError('record sequence rolled back')
    def accept(self,task,seq): self.min_seq_by_task[task]=max(seq,self.min_seq_by_task.get(task,0))
def sign_record(record,*,key_id,key):
    record.validate(); payload={'schema_version':SCHEMA_VERSION,'alg':ALG,'key_id':key_id,'record':asdict(record)}
    mac=hmac.new(key,canonical_bytes(payload),hashlib.sha256).hexdigest()
    return json.dumps({'payload':payload,'mac':mac},sort_keys=True,separators=(',',':'),ensure_ascii=False)
def verify_record(raw,*,expected_task,expected_generations,keyring,replay_guard,accept=True):
    env=parse_json_strict(raw)
    if set(env)!={'payload','mac'} or not isinstance(env['payload'],dict) or not isinstance(env['mac'],str): raise ParseError('invalid envelope shape')
    p=env['payload']
    if set(p)!={'schema_version','alg','key_id','record'}: raise ParseError('invalid payload shape')
    if p['schema_version']!=SCHEMA_VERSION or p['alg']!=ALG: raise DomainError('unsupported schema/alg')
    key=keyring.key(p['key_id'])
    if not hmac.compare_digest(hmac.new(key,canonical_bytes(p),hashlib.sha256).hexdigest(),env['mac']): raise AuthError('record MAC mismatch')
    try: r=LaunchRecord(**p['record'])
    except Exception as e: raise ParseError(str(e)) from e
    r.validate()
    if r.task_id!=expected_task: raise DomainError('task mismatch')
    if r.authority_epoch!=keyring.authority_epoch: raise DomainError('authority epoch mismatch')
    if (r.sandbox_generation,r.credential_generation,r.capability_generation)!=expected_generations: raise DomainError('generation mismatch')
    replay_guard.require_fresh(r.task_id,r.record_seq)
    if accept: replay_guard.accept(r.task_id,r.record_seq)
    return r
def evidence_summary(raw):
    env=parse_json_strict(raw); p=env['payload']; r=p['record']
    return {'task_id':r['task_id'],'record_seq':r['record_seq'],'authority_epoch':r['authority_epoch'],'key_id':p['key_id'],'record_fingerprint':hashlib.sha256(canonical_bytes(p)).hexdigest()}
def unsafe_accept_unsigned(raw,expected_task):
    return json.loads(raw).get('task_id')==expected_task
