from __future__ import annotations

import ctypes
import errno
import hashlib
import hmac
import json
import os
import platform
import secrets
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

PR_SET_NO_NEW_PRIVS = 38
PR_GET_NO_NEW_PRIVS = 39
PR_SET_SECCOMP = 22
SECCOMP_MODE_FILTER = 2

BPF_LD = 0x00
BPF_W = 0x00
BPF_ABS = 0x20
BPF_JMP = 0x05
BPF_JEQ = 0x10
BPF_K = 0x00
BPF_RET = 0x06
SECCOMP_RET_ALLOW = 0x7FFF0000
SECCOMP_RET_KILL_PROCESS = 0x80000000
SECCOMP_RET_ERRNO = 0x00050000
AUDIT_ARCH_X86_64 = 0xC000003E
SECCOMP_DATA_NR_OFFSET = 0
SECCOMP_DATA_ARCH_OFFSET = 4

SYS_GETPPID = getattr(os, "SYS_getppid", 110)


class SandboxError(RuntimeError):
    pass


class CapabilityError(SandboxError):
    pass


class AttestationError(SandboxError):
    pass


class SockFilter(ctypes.Structure):
    _fields_ = [("code", ctypes.c_ushort), ("jt", ctypes.c_ubyte), ("jf", ctypes.c_ubyte), ("k", ctypes.c_uint)]


class SockFprog(ctypes.Structure):
    _fields_ = [("len", ctypes.c_ushort), ("filter", ctypes.POINTER(SockFilter))]


@dataclass(frozen=True)
class CapabilityReport:
    generation: int
    no_new_privs: bool
    seccomp_filter: bool
    arch_x86_64: bool
    userns: bool
    network_isolation: bool
    filesystem_isolation: bool
    digest: str

    @classmethod
    def build(cls, generation: int) -> "CapabilityReport":
        facts = {
            "generation": generation,
            "no_new_privs": probe_no_new_privs(),
            "seccomp_filter": probe_seccomp_filter(),
            "arch_x86_64": platform.machine().lower() in {"x86_64", "amd64"},
            "userns": probe_userns(),
            "network_isolation": probe_unshare("-n"),
            "filesystem_isolation": probe_unshare("-m"),
        }
        digest = hashlib.sha256(json.dumps(facts, sort_keys=True).encode()).hexdigest()
        return cls(**facts, digest=digest)


@dataclass(frozen=True)
class SandboxRequest:
    task_id: str
    sandbox_generation: int
    credential_generation: int
    capability_generation: int
    require_userns: bool = True
    require_network_isolation: bool = False
    require_filesystem_isolation: bool = False


@dataclass(frozen=True)
class LaunchReceipt:
    task_id: str
    sandbox_generation: int
    credential_generation: int
    capability_generation: int
    capability_digest: str
    child_pid: int
    backends: tuple[str, ...]
    child_probe_digest: str
    observed_nnp: bool
    observed_seccomp: bool
    observed_userns: bool
    observed_fd_default_deny: bool
    signature: str


def _libc():
    return ctypes.CDLL(None, use_errno=True)


def set_no_new_privs() -> None:
    libc = _libc()
    if libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0:
        e = ctypes.get_errno()
        raise OSError(e, os.strerror(e))


def get_no_new_privs() -> int:
    libc = _libc()
    result = libc.prctl(PR_GET_NO_NEW_PRIVS, 0, 0, 0, 0)
    if result < 0:
        e = ctypes.get_errno()
        raise OSError(e, os.strerror(e))
    return int(result)


def install_seccomp_errno_filter(syscall_nr: int = SYS_GETPPID, err: int = errno.EPERM) -> None:
    insns = (SockFilter * 7)(
        SockFilter(BPF_LD | BPF_W | BPF_ABS, 0, 0, SECCOMP_DATA_ARCH_OFFSET),
        SockFilter(BPF_JMP | BPF_JEQ | BPF_K, 1, 0, AUDIT_ARCH_X86_64),
        SockFilter(BPF_RET | BPF_K, 0, 0, SECCOMP_RET_KILL_PROCESS),
        SockFilter(BPF_LD | BPF_W | BPF_ABS, 0, 0, SECCOMP_DATA_NR_OFFSET),
        SockFilter(BPF_JMP | BPF_JEQ | BPF_K, 0, 1, syscall_nr),
        SockFilter(BPF_RET | BPF_K, 0, 0, SECCOMP_RET_ERRNO | (err & 0xFFFF)),
        SockFilter(BPF_RET | BPF_K, 0, 0, SECCOMP_RET_ALLOW),
    )
    prog = SockFprog(len=7, filter=ctypes.cast(insns, ctypes.POINTER(SockFilter)))
    libc = _libc()
    if libc.prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, ctypes.byref(prog)) != 0:
        e = ctypes.get_errno()
        raise OSError(e, os.strerror(e))


def probe_no_new_privs() -> bool:
    code = "import ctypes,sys; l=ctypes.CDLL(None,use_errno=True); sys.exit(0 if l.prctl(38,1,0,0,0)==0 else 1)"
    return subprocess.run([sys.executable, "-c", code], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def probe_seccomp_filter() -> bool:
    code = (
        "from experiments.linux_sandbox_launcher.protocol import set_no_new_privs,install_seccomp_errno_filter;"
        "set_no_new_privs();install_seccomp_errno_filter()"
    )
    env = dict(os.environ)
    root = str(Path(__file__).resolve().parents[2])
    env["PYTHONPATH"] = root + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return subprocess.run([sys.executable, "-c", code], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def probe_unshare(flag: str) -> bool:
    try:
        return subprocess.run(["unshare", flag, "true"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3).returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def probe_userns() -> bool:
    try:
        return subprocess.run(["unshare", "-Ur", "true"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3).returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _validate_request(req: SandboxRequest, caps: CapabilityReport) -> None:
    if req.capability_generation != caps.generation:
        raise CapabilityError("stale capability generation")
    if not caps.arch_x86_64:
        raise CapabilityError("prototype seccomp policy supports x86_64 only")
    if not caps.no_new_privs or not caps.seccomp_filter:
        raise CapabilityError("required no_new_privs/seccomp unavailable")
    if req.require_userns and not caps.userns:
        raise CapabilityError("required user namespace unavailable")
    if req.require_network_isolation and not caps.network_isolation:
        raise CapabilityError("required network isolation unavailable")
    if req.require_filesystem_isolation and not caps.filesystem_isolation:
        raise CapabilityError("required filesystem isolation unavailable")


def _receipt_message(fields: dict) -> bytes:
    return json.dumps(fields, sort_keys=True, separators=(",", ":")).encode()


class LinuxSandboxLauncher:
    def __init__(self, signing_key: bytes | None = None):
        self.signing_key = signing_key or secrets.token_bytes(32)

    def launch(self, req: SandboxRequest, caps: CapabilityReport, *, inherited_fd: int | None = None) -> LaunchReceipt:
        _validate_request(req, caps)
        parent_userns = os.readlink("/proc/self/ns/user")
        child_code = r'''
import ctypes, errno, json, os
from experiments.linux_sandbox_launcher.protocol import set_no_new_privs, install_seccomp_errno_filter, SYS_GETPPID
set_no_new_privs()
install_seccomp_errno_filter()
status = {}
for line in open('/proc/self/status', encoding='utf-8'):
    if line.startswith(('NoNewPrivs:', 'Seccomp:', 'Seccomp_filters:')):
        k,v=line.split(':',1); status[k]=v.strip()
libc=ctypes.CDLL(None,use_errno=True)
ctypes.set_errno(0)
r=libc.syscall(SYS_GETPPID)
seccomp_errno=ctypes.get_errno()
fd=int(os.environ.get('LAB030_PROBE_FD','-1'))
fd_closed=False
if fd >= 0:
    try: os.fstat(fd)
    except OSError as e: fd_closed=(e.errno==errno.EBADF)
probe={
 'pid':os.getpid(),
 'nnp':status.get('NoNewPrivs')=='1',
 'seccomp_mode':int(status.get('Seccomp','0')),
 'seccomp_filters':int(status.get('Seccomp_filters','0')),
 'denied_syscall': r == -1 and seccomp_errno == errno.EPERM,
 'userns':os.readlink('/proc/self/ns/user'),
 'parent_userns':os.environ['LAB030_PARENT_USERNS'],
 'fd_closed':fd_closed,
}
print(json.dumps(probe, sort_keys=True))
'''
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "PYTHONPATH": str(Path(__file__).resolve().parents[2]),
            "LAB030_PARENT_USERNS": parent_userns,
            "LAB030_PROBE_FD": str(inherited_fd if inherited_fd is not None else -1),
        }
        argv = [sys.executable, "-c", child_code]
        backends = ["no_new_privs", "seccomp-bpf", "fd-default-deny"]
        if req.require_userns:
            argv = ["unshare", "-Ur", "--"] + argv
            backends.append("userns")
        p = subprocess.run(argv, env=env, close_fds=True, pass_fds=(), capture_output=True, text=True, timeout=10)
        if p.returncode != 0:
            raise SandboxError(f"child failed rc={p.returncode}: {p.stderr.strip()}")
        probe = json.loads(p.stdout.strip().splitlines()[-1])
        expected = {
            "nnp": True,
            "seccomp": probe["seccomp_mode"] == 2 and probe["seccomp_filters"] >= 1 and probe["denied_syscall"],
            "fd": (inherited_fd is None or probe["fd_closed"]),
            "userns": (not req.require_userns or probe["userns"] != probe["parent_userns"]),
        }
        if not all(expected.values()):
            raise AttestationError(f"post-launch enforcement failed: {expected}; probe={probe}")
        probe_digest = hashlib.sha256(json.dumps(probe, sort_keys=True).encode()).hexdigest()
        fields = {
            "task_id": req.task_id,
            "sandbox_generation": req.sandbox_generation,
            "credential_generation": req.credential_generation,
            "capability_generation": req.capability_generation,
            "capability_digest": caps.digest,
            "child_pid": int(probe["pid"]),
            "backends": tuple(sorted(backends)),
            "child_probe_digest": probe_digest,
            "observed_nnp": bool(expected["nnp"]),
            "observed_seccomp": bool(expected["seccomp"]),
            "observed_userns": bool(expected["userns"]),
            "observed_fd_default_deny": bool(expected["fd"]),
        }
        sig = hmac.new(self.signing_key, _receipt_message(fields), hashlib.sha256).hexdigest()
        return LaunchReceipt(**fields, signature=sig)

    def verify(self, receipt: LaunchReceipt, req: SandboxRequest, caps: CapabilityReport) -> None:
        _validate_request(req, caps)
        fields = asdict(receipt)
        sig = fields.pop("signature")
        expected_sig = hmac.new(self.signing_key, _receipt_message(fields), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            raise AttestationError("forged launch receipt")
        if receipt.task_id != req.task_id:
            raise AttestationError("task binding mismatch")
        if receipt.sandbox_generation != req.sandbox_generation or receipt.credential_generation != req.credential_generation:
            raise AttestationError("generation binding mismatch")
        if receipt.capability_generation != caps.generation or receipt.capability_digest != caps.digest:
            raise AttestationError("capability binding mismatch")
        required = {"no_new_privs", "seccomp-bpf", "fd-default-deny"}
        if req.require_userns:
            required.add("userns")
        if not required.issubset(set(receipt.backends)):
            raise AttestationError("required backend missing from receipt")
        if not (receipt.observed_nnp and receipt.observed_seccomp and receipt.observed_fd_default_deny):
            raise AttestationError("receipt lacks observed enforcement facts")
        if req.require_userns and not receipt.observed_userns:
            raise AttestationError("receipt lacks observed user namespace separation")


class UnsafeIntentOnlyLauncher:
    """Seeded unsafe design: attests requested setup without observing the launched child."""

    def launch(self, req: SandboxRequest, caps: CapabilityReport) -> dict:
        return {
            "task_id": req.task_id,
            "claimed_enforced": True,
            "backends": ["no_new_privs", "seccomp-bpf"],
            "observed_child": False,
        }
