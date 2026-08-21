from __future__ import annotations
import fcntl,hashlib,hmac,os,subprocess,sys
from dataclasses import dataclass

class MemfdError(RuntimeError): pass
class UnsupportedMemfd(MemfdError): pass
class StaleCredential(MemfdError): pass
class CompatibilityError(MemfdError): pass

@dataclass(frozen=True)
class CredentialPermit:
    credential_id:str
    generation:int
    scope:str
    fingerprint:str

@dataclass
class MemfdTransport:
    fd:int
    permit:CredentialPermit
    sealed:bool=True

    @property
    def path(self): return f'/proc/self/fd/{self.fd}'
    def close(self):
        if self.fd>=0:
            os.close(self.fd); self.fd=-1

class MemfdVault:
    def __init__(self,audit_key:bytes):
        self.audit_key=bytes(audit_key); self.generation=0; self.current_id=''; self.scope=''; self._secret=None
    def rotate(self,credential_id:str,scope:str,secret:bytes)->CredentialPermit:
        self.generation+=1; self.current_id=credential_id; self.scope=scope; self._secret=bytes(secret); return self.permit()
    def permit(self):
        if self._secret is None: raise MemfdError('no credential')
        return CredentialPermit(self.current_id,self.generation,self.scope,hmac.new(self.audit_key,self._secret,hashlib.sha256).hexdigest())
    def open_transport(self,permit:CredentialPermit)->MemfdTransport:
        if permit!=self.permit(): raise StaleCredential('stale credential permit')
        required_os=('memfd_create','MFD_ALLOW_SEALING','MFD_CLOEXEC')
        required_fcntl=('F_ADD_SEALS','F_GET_SEALS','F_SEAL_WRITE','F_SEAL_GROW','F_SEAL_SHRINK','F_SEAL_SEAL')
        if any(not hasattr(os,name) for name in required_os) or any(not hasattr(fcntl,name) for name in required_fcntl):
            raise UnsupportedMemfd('required memfd sealing primitives unavailable')
        fd=os.memfd_create(f'credential-{permit.credential_id}',os.MFD_CLOEXEC|os.MFD_ALLOW_SEALING)
        try:
            assert self._secret is not None
            offset=0
            while offset<len(self._secret): offset+=os.write(fd,self._secret[offset:])
            os.lseek(fd,0,os.SEEK_SET)
            seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL
            try: fcntl.fcntl(fd,fcntl.F_ADD_SEALS,seals)
            except OSError as exc: raise UnsupportedMemfd(f'memfd sealing failed: {exc}') from exc
            transport=MemfdTransport(fd,permit,True)
            if not verify_seals(transport): raise UnsupportedMemfd('required seals not active')
            return transport
        except:
            os.close(fd); raise

def evidence(permit:CredentialPermit):
    return {'credential_id':permit.credential_id,'generation':permit.generation,'scope':permit.scope,'fingerprint':permit.fingerprint,'transport':'memfd'}

def child_read_via_path(transport:MemfdTransport)->bytes:
    code="import pathlib,sys;sys.stdout.buffer.write(pathlib.Path(sys.argv[1]).read_bytes())"
    return subprocess.check_output([sys.executable,'-c',code,transport.path],pass_fds=(transport.fd,),env={'PATH':os.environ.get('PATH','')})

def child_can_read_without_inheritance(transport:MemfdTransport)->bool:
    code="import pathlib,sys;sys.stdout.buffer.write(pathlib.Path(sys.argv[1]).read_bytes())"
    result=subprocess.run([sys.executable,'-c',code,transport.path],close_fds=True,capture_output=True,env={'PATH':os.environ.get('PATH','')})
    expected=os.pread(transport.fd,1<<20,0)
    return result.returncode==0 and result.stdout==expected

def verify_seals(transport:MemfdTransport):
    got=fcntl.fcntl(transport.fd,fcntl.F_GET_SEALS)
    required=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL
    return transport.sealed and (got & required)==required

def path_compatibility_probe(transport:MemfdTransport):
    try: return child_read_via_path(transport)==os.pread(transport.fd,1<<20,0)
    except (subprocess.SubprocessError,OSError): return False

def route_for_path_only_tool(vault:MemfdVault,permit:CredentialPermit):
    try: t=vault.open_transport(permit)
    except UnsupportedMemfd as exc: return {'route':'LAB-068_NAMED_FALLBACK','reason':str(exc)}
    if not path_compatibility_probe(t):
        t.close(); return {'route':'LAB-068_NAMED_FALLBACK','reason':'procfd path incompatible'}
    return {'route':'MEMFD_PROCFD','transport':t}

class UnsafeNamedPath:
    def create(self,directory,secret):
        p=os.path.join(directory,'credential.txt')
        with open(p,'wb') as f:f.write(secret)
        return p
