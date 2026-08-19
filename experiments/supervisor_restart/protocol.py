from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
import json, os, select, signal, subprocess, time
from pathlib import Path

class ReconcileState(str, Enum):
    SAME_INSTANCE='same_instance'
    EXITED='exited'
    IDENTITY_MISMATCH='identity_mismatch'
    UNVERIFIABLE='unverifiable'
    GENERATION_DRIFT='generation_drift'

@dataclass(frozen=True)
class Generations:
    sandbox:int
    credential:int
    capability:int

@dataclass(frozen=True)
class DurableLaunchRecord:
    task_id:str
    pid:int
    starttime:int
    generations:Generations
    process_group:int

    def to_json(self)->str:
        raw=asdict(self)
        return json.dumps(raw,sort_keys=True)

    @classmethod
    def from_json(cls,text:str)->'DurableLaunchRecord':
        raw=json.loads(text)
        raw['generations']=Generations(**raw['generations'])
        return cls(**raw)

@dataclass
class FreshAuthority:
    record:DurableLaunchRecord
    pidfd:int


def proc_stat(pid:int)->tuple[str,int]:
    text=Path(f'/proc/{pid}/stat').read_text()
    rest=text[text.rfind(')')+2:].split()
    state=rest[0]
    starttime=int(rest[19])
    return state,starttime


def proc_starttime(pid:int)->int:
    return proc_stat(pid)[1]


def pidfd_live(fd:int)->bool:
    return not bool(select.select([fd],[],[],0)[0])


def pidfd_target_pid(fd:int)->int:
    for line in Path(f'/proc/self/fdinfo/{fd}').read_text().splitlines():
        if line.startswith('Pid:'):
            return int(line.split(':',1)[1].strip())
    raise RuntimeError('pidfd target identity unavailable')


def launch(task_id:str,generations:Generations,seconds:float=30.0)->tuple[subprocess.Popen,DurableLaunchRecord,int]:
    proc=subprocess.Popen(['/bin/sleep',str(seconds)],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    record=DurableLaunchRecord(task_id,proc.pid,proc_starttime(proc.pid),generations,os.getpgid(proc.pid))
    pidfd=os.pidfd_open(proc.pid,0)
    return proc,record,pidfd


def reconcile(record:DurableLaunchRecord,current:Generations,expected_task_id:str|None=None)->tuple[ReconcileState,FreshAuthority|None,str]:
    if expected_task_id is not None and record.task_id != expected_task_id:
        return ReconcileState.IDENTITY_MISMATCH,None,'durable record belongs to another task'
    if record.generations != current:
        return ReconcileState.GENERATION_DRIFT,None,'persisted generations are stale'
    try:
        state,starttime_before=proc_stat(record.pid)
    except FileNotFoundError:
        return ReconcileState.EXITED,None,'process absent'
    except PermissionError:
        return ReconcileState.UNVERIFIABLE,None,'cannot read proc identity'
    if starttime_before != record.starttime:
        return ReconcileState.IDENTITY_MISMATCH,None,'pid reused or record mismatched before pidfd reacquire'
    try:
        fd=os.pidfd_open(record.pid,0)
    except ProcessLookupError:
        return ReconcileState.EXITED,None,'process exited during reacquire'
    except (PermissionError,OSError) as exc:
        return ReconcileState.UNVERIFIABLE,None,f'pidfd reacquire failed: {exc}'
    try:
        target=pidfd_target_pid(fd)
        if target != record.pid:
            os.close(fd)
            return ReconcileState.IDENTITY_MISMATCH,None,'fresh pidfd targets another pid'
        try:
            state_after,starttime_after=proc_stat(record.pid)
        except FileNotFoundError:
            os.close(fd)
            return ReconcileState.EXITED,None,'process exited after pidfd reacquire'
        if starttime_after != record.starttime or starttime_after != starttime_before:
            os.close(fd)
            return ReconcileState.IDENTITY_MISMATCH,None,'identity changed across reacquire'
        if not pidfd_live(fd):
            os.close(fd)
            return ReconcileState.EXITED,None,'pidfd already indicates exit'
        if state_after == 'Z':
            os.close(fd)
            return ReconcileState.EXITED,None,'process is zombie'
        return ReconcileState.SAME_INSTANCE,FreshAuthority(record,fd),'fresh authority reacquired'
    except Exception:
        try: os.close(fd)
        except Exception: pass
        raise


def can_continue(state:ReconcileState,authority:FreshAuthority|None)->bool:
    return state is ReconcileState.SAME_INSTANCE and authority is not None and pidfd_live(authority.pidfd)


def terminate_orphan(authority:FreshAuthority,timeout:float=.5)->dict:
    r=authority.record
    if pidfd_target_pid(authority.pidfd) != r.pid:
        return {'terminated':False,'reason':'pidfd_binding_mismatch'}
    try:
        _,start=proc_stat(r.pid)
    except FileNotFoundError:
        return {'terminated':True,'reason':'already_exited'}
    if start != r.starttime:
        return {'terminated':False,'reason':'identity_mismatch'}
    try:
        pgid=os.getpgid(r.pid)
    except ProcessLookupError:
        return {'terminated':True,'reason':'already_exited'}
    if pgid != r.process_group:
        return {'terminated':False,'reason':'process_group_drift'}
    try: os.killpg(pgid,signal.SIGTERM)
    except ProcessLookupError: pass
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline and pidfd_live(authority.pidfd): time.sleep(.01)
    if pidfd_live(authority.pidfd):
        try: os.killpg(pgid,signal.SIGKILL)
        except ProcessLookupError: pass
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline and pidfd_live(authority.pidfd): time.sleep(.01)
    return {'terminated':not pidfd_live(authority.pidfd),'reason':'group_signal'}

# Deliberately unsafe: treats persisted PID alone as durable process authority.
def unsafe_pid_only_alive(pid:int)->bool:
    return Path(f'/proc/{pid}').exists()
