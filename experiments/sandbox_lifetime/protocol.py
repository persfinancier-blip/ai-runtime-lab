from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import os, select, signal, subprocess, time
from pathlib import Path

class EvidenceKind(str, Enum):
    LAUNCH="launch"
    LIVENESS="liveness"
    TERMINATION="termination"
    COMPLETION="completion"

@dataclass(frozen=True)
class Generations:
    sandbox:int
    credential:int
    capability:int

@dataclass(frozen=True)
class LaunchReceipt:
    task_id:str
    pid:int
    starttime:int
    generations:Generations
    evidence_kind:EvidenceKind=EvidenceKind.LAUNCH

@dataclass
class SupervisionHandle:
    receipt:LaunchReceipt
    pidfd:int

def proc_starttime(pid:int)->int:
    text=Path(f"/proc/{pid}/stat").read_text()
    # comm may contain spaces/parens; starttime is field 22, so parse after final ')'
    rest=text[text.rfind(")")+2:].split()
    return int(rest[19])

def bind(task_id:str, proc:subprocess.Popen, generations:Generations)->SupervisionHandle:
    return SupervisionHandle(
        LaunchReceipt(task_id, proc.pid, proc_starttime(proc.pid), generations),
        os.pidfd_open(proc.pid,0)
    )

def pidfd_live(fd:int)->bool:
    return not bool(select.select([fd],[],[],0)[0])

def pidfd_target_pid(fd:int)->int:
    # Linux exposes the instance target in pidfd fdinfo; this binds the live
    # handle to the receipt instead of trusting two independently valid facts.
    for line in Path(f"/proc/self/fdinfo/{fd}").read_text().splitlines():
        if line.startswith("Pid:"):
            return int(line.split(":",1)[1].strip())
    raise RuntimeError("pidfd target identity unavailable")

def validate_fresh(handle:SupervisionHandle, current:Generations)->bool:
    r=handle.receipt
    if r.evidence_kind is not EvidenceKind.LAUNCH or r.generations != current:
        return False
    if not pidfd_live(handle.pidfd):
        return False
    try:
        if pidfd_target_pid(handle.pidfd) != r.pid:
            return False
        return proc_starttime(r.pid)==r.starttime
    except (FileNotFoundError, ProcessLookupError):
        return False

def reconstructible_identity_matches(receipt:LaunchReceipt)->bool:
    try:
        return proc_starttime(receipt.pid)==receipt.starttime
    except (FileNotFoundError, ProcessLookupError):
        return False

def require_cgroup_tree_containment(cgroup_root:str="/sys/fs/cgroup")->None:
    root=Path(cgroup_root)
    if not (root/"cgroup.kill").exists() or not os.access(root,os.W_OK):
        raise RuntimeError("required cgroup-tree containment unavailable")

def terminate_process_group(handle:SupervisionHandle, timeout:float=1.0)->dict:
    r=handle.receipt
    if not reconstructible_identity_matches(r):
        return {"kind":EvidenceKind.TERMINATION.value,"terminated":False,"reason":"identity_mismatch"}
    try:
        pgid=os.getpgid(r.pid)
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return {"kind":EvidenceKind.TERMINATION.value,"terminated":True,"reason":"already_exited"}
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline and pidfd_live(handle.pidfd):
        time.sleep(.01)
    if pidfd_live(handle.pidfd):
        try: os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError: pass
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline and pidfd_live(handle.pidfd):
        time.sleep(.01)
    return {"kind":EvidenceKind.TERMINATION.value,"terminated":not pidfd_live(handle.pidfd),"reason":"group_signal"}

def completion_evidence(success:bool)->dict:
    return {"kind":EvidenceKind.COMPLETION.value,"success":bool(success)}
