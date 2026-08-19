from dataclasses import dataclass
from pathlib import PurePosixPath
import hashlib, json

class Denied(RuntimeError): pass
def canon(p): return str(PurePosixPath(p))
def within(path, root):
    p=PurePosixPath(canon(path)); r=PurePosixPath(canon(root))
    return p==r or r in p.parents

@dataclass(frozen=True)
class SandboxSpec:
    task_id:str; workspace:str; generation:int; credential_generation:int
    read_roots:tuple[str,...]=(); write_roots:tuple[str,...]=()
    exec_allow:tuple[str,...]=(); fd_allow:tuple[int,...]=()
    allow_local_socket:bool=False; allow_network:bool=False
    def fingerprint(self):
        return hashlib.sha256(json.dumps(self.__dict__,sort_keys=True).encode()).hexdigest()

@dataclass(frozen=True)
class Permit:
    task_id:str; sandbox_generation:int; credential_generation:int; fingerprint:str

class Policy:
    def issue(self,s):
        return Permit(s.task_id,s.generation,s.credential_generation,s.fingerprint())
    def check(self,s,p,op,target):
        if (p.task_id,p.sandbox_generation,p.credential_generation,p.fingerprint)!=(s.task_id,s.generation,s.credential_generation,s.fingerprint()):
            raise Denied("stale or mismatched permit")
        if op=="read":
            if not any(within(target,r) for r in s.read_roots+(s.workspace,)): raise Denied("read")
        elif op=="write":
            if not any(within(target,r) for r in s.write_roots+(s.workspace,)): raise Denied("write")
        elif op=="exec":
            if target not in s.exec_allow: raise Denied("exec")
        elif op=="fd":
            if int(target) not in s.fd_allow: raise Denied("fd")
        elif op=="local_socket":
            if not s.allow_local_socket: raise Denied("local_socket")
        elif op=="network":
            if not s.allow_network: raise Denied("network")
        else: raise Denied("unknown")
        return True

class UnsafeBroadPolicy:
    def check(self,*args,**kwargs): return True
