from __future__ import annotations
import hashlib, hmac, json, re
from dataclasses import dataclass
from typing import Any

SECRET_KEYS = {'authorization','proxy-authorization','cookie','set-cookie','password','token','access-token','refresh-token','api-key','secret','session'}
REDACTED='[REDACTED]'

@dataclass(frozen=True)
class CredentialMeta:
    kind:str
    scope:str
    credential_id:str
    generation:int

class SecretBoundary:
    def __init__(self, audit_key: bytes):
        self.audit_key=audit_key
        self._secrets:set[str]=set()
    def register_secret(self, value:str)->str:
        self._secrets.add(value)
        return hmac.new(self.audit_key,value.encode(),hashlib.sha256).hexdigest()
    def _key_sensitive(self,k:str)->bool:
        lk=k.lower().replace('_','-')
        return any(s in lk for s in SECRET_KEYS)
    def _sanitize_string(self,s:str)->str:
        out=s
        for sec in sorted(self._secrets,key=len,reverse=True):
            if sec:
                out=out.replace(sec,REDACTED)
        out=re.sub(r'(?i)\b(Bearer|Basic)\s+[A-Za-z0-9._~+\-/=]+',lambda m:f'{m.group(1)} {REDACTED}',out)
        return out
    def sanitize(self,obj:Any,key_hint:str='')->Any:
        if isinstance(obj,dict):
            out={}
            for k,v in obj.items():
                if self._key_sensitive(str(k)):
                    out[k]=REDACTED
                else:
                    out[k]=self.sanitize(v,str(k))
            return out
        if isinstance(obj,(list,tuple)):
            return [self.sanitize(v,key_hint) for v in obj]
        if isinstance(obj,Exception):
            return {'exception.type':type(obj).__name__,'exception.message':self._sanitize_string(str(obj))}
        if isinstance(obj,str):
            if self._key_sensitive(key_hint): return REDACTED
            return self._sanitize_string(obj)
        return obj
    def emit(self,channel:str,event:str,payload:Any,credential:CredentialMeta|None=None)->dict[str,Any]:
        rec={'channel':channel,'event':event,'payload':self.sanitize(payload)}
        if credential:
            rec['credential']={'kind':credential.kind,'scope':credential.scope,'credential_id':credential.credential_id,'generation':credential.generation}
        return rec
    def serialize(self,record:dict[str,Any])->str:
        return json.dumps(self.sanitize(record),sort_keys=True,separators=(',',':'))

class UnsafeRecorder:
    def serialize(self,obj:Any)->str:
        return json.dumps(obj,default=str,sort_keys=True)
