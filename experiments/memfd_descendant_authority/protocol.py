from __future__ import annotations
import ctypes, errno, fcntl, hashlib, json, os, platform, subprocess, sys, tempfile, time
from dataclasses import asdict, dataclass
from pathlib import Path

PR_SET_NO_NEW_PRIVS=38; PR_SET_SECCOMP=22; SECCOMP_MODE_FILTER=2
BPF_LD=0x00; BPF_W=0x00; BPF_ABS=0x20; BPF_JMP=0x05; BPF_JEQ=0x10; BPF_JSET=0x40; BPF_K=0x00; BPF_RET=0x06
SECCOMP_RET_ALLOW=0x7FFF0000; SECCOMP_RET_KILL_PROCESS=0x80000000; SECCOMP_RET_ERRNO=0x00050000
AUDIT_ARCH_X86_64=0xC000003E; NR_OFF=0; ARCH_OFF=4
SYS_CLONE=56; SYS_FORK=57; SYS_VFORK=58; SYS_CLONE3=435
CLONE_THREAD=0x00010000; ARG0_LO_OFFSET=16

class AuthorityError(RuntimeError): pass
class UnsupportedMode(AuthorityError): pass
class EnforcementError(AuthorityError): pass
class SockFilter(ctypes.Structure): _fields_=[('code',ctypes.c_ushort),('jt',ctypes.c_ubyte),('jf',ctypes.c_ubyte),('k',ctypes.c_uint)]
class SockFprog(ctypes.Structure): _fields_=[('len',ctypes.c_ushort),('filter',ctypes.POINTER(SockFilter))]

@dataclass(frozen=True)
class CapabilityReport:
    arch_x86_64: bool; seccomp: bool; user_pidns: bool; cgroup_delegated: bool
@dataclass(frozen=True)
class Evidence:
    mode:str; outcome:str; credential_generation:int; target_pid:int|None; descendant_pid:int|None; facts:tuple[str,...]

def _run_ok(argv):
    try: return subprocess.run(argv,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=4).returncode==0
    except (FileNotFoundError,subprocess.TimeoutExpired): return False

def probe_capabilities():
    arch=platform.machine().lower() in {'x86_64','amd64'}
    sec=False
    if arch:
        code="from experiments.memfd_descendant_authority.protocol import install_no_descendants; install_no_descendants()"
        env=dict(os.environ); env['PYTHONPATH']=str(Path(__file__).resolve().parents[2])
        sec=subprocess.run([sys.executable,'-S','-c',code],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
    pidns=_run_ok(['unshare','-Urp','--fork','true'])
    cg=os.access('/sys/fs/cgroup',os.W_OK)
    return CapabilityReport(arch,sec,pidns,cg)

def install_no_descendants():
    if platform.machine().lower() not in {'x86_64','amd64'}: raise UnsupportedMode('x86_64 seccomp prototype only')
    libc=ctypes.CDLL(None,use_errno=True)
    if libc.prctl(PR_SET_NO_NEW_PRIVS,1,0,0,0)!=0: raise OSError(ctypes.get_errno(),'no_new_privs')
    ins=(SockFilter*14)(
      SockFilter(BPF_LD|BPF_W|BPF_ABS,0,0,ARCH_OFF),
      SockFilter(BPF_JMP|BPF_JEQ|BPF_K,1,0,AUDIT_ARCH_X86_64),
      SockFilter(BPF_RET|BPF_K,0,0,SECCOMP_RET_KILL_PROCESS),
      SockFilter(BPF_LD|BPF_W|BPF_ABS,0,0,NR_OFF),
      SockFilter(BPF_JMP|BPF_JEQ|BPF_K,7,0,SYS_FORK),
      SockFilter(BPF_JMP|BPF_JEQ|BPF_K,6,0,SYS_VFORK),
      SockFilter(BPF_JMP|BPF_JEQ|BPF_K,6,0,SYS_CLONE3),
      SockFilter(BPF_JMP|BPF_JEQ|BPF_K,1,0,SYS_CLONE),
      SockFilter(BPF_RET|BPF_K,0,0,SECCOMP_RET_ALLOW),
      SockFilter(BPF_LD|BPF_W|BPF_ABS,0,0,ARG0_LO_OFFSET),
      SockFilter(BPF_JMP|BPF_JSET|BPF_K,0,1,CLONE_THREAD),
      SockFilter(BPF_RET|BPF_K,0,0,SECCOMP_RET_ALLOW),
      SockFilter(BPF_RET|BPF_K,0,0,SECCOMP_RET_ERRNO|errno.EPERM),
      SockFilter(BPF_RET|BPF_K,0,0,SECCOMP_RET_ERRNO|errno.ENOSYS),
    )
    prog=SockFprog(len=14,filter=ctypes.cast(ins,ctypes.POINTER(SockFilter)))
    if libc.prctl(PR_SET_SECCOMP,SECCOMP_MODE_FILTER,ctypes.byref(prog))!=0: raise OSError(ctypes.get_errno(),'seccomp')

def sealed_memfd(secret:bytes):
    flags=getattr(os,'MFD_CLOEXEC',1)|getattr(os,'MFD_ALLOW_SEALING',2)
    fd=os.memfd_create('lab070-credential',flags)
    os.write(fd,secret); os.lseek(fd,0,os.SEEK_SET)
    seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL
    fcntl.fcntl(fd,fcntl.F_ADD_SEALS,seals)
    return fd

def _pid_alive(pid:int):
    try: os.kill(pid,0); return True
    except ProcessLookupError: return False

def _single_target_code():
    return r'''import json,os,subprocess,sys
fd=int(os.environ['LAB070_FD']); os.lseek(fd,0,0); data=os.read(fd,4096)
import threading
hit=[]; th=threading.Thread(target=lambda: hit.append(1)); th.start(); th.join(); thread_ok=(hit==[1])
try:
 p=subprocess.run([sys.executable,'-S','-c','print(1)'],pass_fds=(fd,),capture_output=True,text=True)
 spawned=(p.returncode==0); err=p.stderr
except OSError as e:
 spawned=False; err=f'{e.errno}:{e.strerror}'
print(json.dumps({'pid':os.getpid(),'read_len':len(data),'spawned':spawned,'spawn_error':err,'thread_ok':thread_ok}))
'''

def run_single_process(secret:bytes,bundle_generation:int,caps:CapabilityReport|None=None):
    caps=caps or probe_capabilities()
    if not (caps.arch_x86_64 and caps.seccomp): raise UnsupportedMode('SINGLE_PROCESS requires observed x86_64 seccomp')
    fd=sealed_memfd(secret)
    try:
        env={'PATH':os.environ.get('PATH','/usr/bin:/bin'),'LAB070_FD':str(fd)}
        supervisor=r'''from experiments.memfd_descendant_authority.protocol import install_no_descendants
import os,sys
install_no_descendants(); os.execve(sys.executable,[sys.executable,'-S','-c',os.environ['LAB070_CODE']],os.environ)
'''
        env['LAB070_CODE']=_single_target_code(); env['PYTHONPATH']=str(Path(__file__).resolve().parents[2])
        p=subprocess.run([sys.executable,'-S','-c',supervisor],env=env,pass_fds=(fd,),close_fds=True,capture_output=True,text=True,timeout=8)
        if p.returncode!=0: raise EnforcementError(p.stderr)
        raw=json.loads(p.stdout.strip().splitlines()[-1])
        if raw['spawned']: raise EnforcementError('descendant creation unexpectedly succeeded')
        if not raw['thread_ok']: raise EnforcementError('same-process thread unexpectedly blocked')
        facts=('credential-read-by-target','process-creation-denied','same-process-thread-allowed','seccomp-inherited-across-exec')
        return Evidence('SINGLE_PROCESS','ENFORCED',bundle_generation,raw['pid'],None,facts)
    finally: os.close(fd)

def _tree_target_code():
    return r'''import json,os,subprocess,sys,time
fd=int(os.environ['LAB070_FD']); os.lseek(fd,0,0); os.read(fd,4096)
gcode="""import os,time
fd=int(os.environ['LAB070_FD']); os.lseek(fd,0,0); os.read(fd,4096)
for line in open('/proc/self/status'):
    if line.startswith('NSpid:'):
        print(line.split()[1],flush=True); break
time.sleep(30)
"""
p=subprocess.Popen([sys.executable,'-S','-c',gcode],env=os.environ,pass_fds=(fd,),stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
host_pid=int(p.stdout.readline().strip())
print(json.dumps({'target_nspid':open('/proc/self/status').read().split('NSpid:')[1].splitlines()[0].split()[0],'descendant_host_pid':host_pid}),flush=True)
'''

def run_supervised_tree(secret:bytes,bundle_generation:int,caps:CapabilityReport|None=None):
    caps=caps or probe_capabilities()
    if not caps.user_pidns: raise UnsupportedMode('SUPERVISED_TREE requires observed user+pid namespace')
    fd=sealed_memfd(secret)
    try:
        env={'PATH':os.environ.get('PATH','/usr/bin:/bin'),'LAB070_FD':str(fd),'PYTHONPATH':str(Path(__file__).resolve().parents[2])}
        p=subprocess.run(['unshare','-Urp','--fork',sys.executable,'-S','-c',_tree_target_code()],env=env,pass_fds=(fd,),close_fds=True,capture_output=True,text=True,timeout=8)
        if p.returncode!=0: raise EnforcementError(p.stderr)
        raw=json.loads(p.stdout.strip().splitlines()[-1]); dpid=int(raw['descendant_host_pid'])
        deadline=time.time()+2
        while time.time()<deadline and _pid_alive(dpid): time.sleep(.02)
        if _pid_alive(dpid): raise EnforcementError('descendant survived PID namespace init exit')
        facts=('credential-read-by-authorized-tree','descendant-explicitly-inherited-fd','namespace-init-exit-killed-descendant')
        return Evidence('SUPERVISED_TREE','ENFORCED',bundle_generation,int(raw['target_nspid']),dpid,facts)
    finally: os.close(fd)

def unsafe_propagation(secret:bytes):
    fd=sealed_memfd(secret)
    try:
        g="import os; fd=int(os.environ['LAB070_FD']); os.lseek(fd,0,0); print(os.read(fd,4096).decode())"
        t=f"import os,subprocess,sys; fd=int(os.environ['LAB070_FD']); subprocess.run([sys.executable,'-S','-c',{g!r}],env=os.environ,pass_fds=(fd,))"
        env=dict(os.environ); env['LAB070_FD']=str(fd)
        p=subprocess.run([sys.executable,'-S','-c',t],env=env,pass_fds=(fd,),capture_output=True,text=True)
        return p.stdout.strip()==secret.decode()
    finally: os.close(fd)

def rotation_is_not_revocation(held_fd:int,new_generation:int):
    os.lseek(held_fd,0,0); return len(os.read(held_fd,4096))>0

def evidence_contains_secret(ev:Evidence,secret:bytes):
    return secret.decode(errors='ignore') in json.dumps(asdict(ev),sort_keys=True)
