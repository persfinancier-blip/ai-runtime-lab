from __future__ import annotations

import ctypes
import os
import platform
import shutil
import subprocess
import time

from .protocol import CapabilityReport, Enforcement, Mechanism


def _run(command: list[str]) -> tuple[bool, str]:
    p = subprocess.run(command, capture_output=True, text=True)
    detail = (p.stderr or p.stdout).strip()
    return p.returncode == 0, detail


def probe_linux(*, generation: int = 1, ttl_seconds: float = 300.0) -> CapabilityReport:
    mechanisms: list[Mechanism] = []

    nnp_code = "import ctypes,sys; l=ctypes.CDLL(None,use_errno=True); r=l.prctl(38,1,0,0,0); sys.exit(0 if r==0 else 1)"
    ok, detail = _run(["python", "-c", nnp_code])
    mechanisms.append(Mechanism("no_new_privs", "exec_privilege", Enforcement.KERNEL, ok, True, detail))

    if platform.machine() == "x86_64":
        libc = ctypes.CDLL(None, use_errno=True)
        ctypes.set_errno(0)
        r = libc.syscall(444, ctypes.c_void_p(0), ctypes.c_size_t(0), ctypes.c_uint(1))
        landlock_ok = r >= 0
        landlock_detail = f"landlock ABI result={r} errno={ctypes.get_errno()}"
        if r >= 0:
            os.close(r)
        mechanisms.append(Mechanism("landlock", "filesystem", Enforcement.KERNEL, landlock_ok, True, landlock_detail))
        mechanisms.append(Mechanism("landlock-network", "network", Enforcement.KERNEL, landlock_ok, True, landlock_detail))

        seccomp_code = '''
import ctypes,sys
class SockFilter(ctypes.Structure):
    _fields_=[("code",ctypes.c_ushort),("jt",ctypes.c_ubyte),("jf",ctypes.c_ubyte),("k",ctypes.c_uint32)]
class SockFprog(ctypes.Structure):
    _fields_=[("len",ctypes.c_ushort),("filter",ctypes.POINTER(SockFilter))]
libc=ctypes.CDLL(None,use_errno=True)
flt=(SockFilter*1)(SockFilter(0x06,0,0,0x7fff0000))
prog=SockFprog(1,flt)
r1=libc.prctl(38,1,0,0,0)
r2=libc.prctl(22,2,ctypes.byref(prog))
sys.exit(0 if r1==0 and r2==0 else 1)
'''
        seccomp_ok, seccomp_detail = _run(["python", "-c", seccomp_code])
        mechanisms.append(Mechanism("seccomp-bpf", "syscall_filter", Enforcement.KERNEL, seccomp_ok, True, seccomp_detail))
    else:
        mechanisms.append(Mechanism("landlock", "filesystem", Enforcement.UNAVAILABLE, False, True, "probe not implemented for architecture"))
        mechanisms.append(Mechanism("seccomp-bpf", "syscall_filter", Enforcement.UNAVAILABLE, False, True, "probe not implemented for architecture"))

    if shutil.which("unshare"):
        probes = (
            ("user_namespace", "userns", ["unshare", "-Ur", "true"]),
            ("network_namespace", "netns", ["unshare", "-n", "true"]),
            ("mount_namespace", "mountns", ["unshare", "-m", "true"]),
        )
        for dimension, name, args in probes:
            ok, detail = _run(args)
            mechanisms.append(Mechanism(name, dimension, Enforcement.KERNEL, ok, True, detail))

    mechanisms.append(Mechanism("subprocess-close_fds", "fd_inheritance", Enforcement.PROCESS, True, True, "Python subprocess close_fds/pass_fds"))

    return CapabilityReport(
        platform="linux",
        kernel=platform.release(),
        generation=generation,
        observed_at=time.time(),
        ttl_seconds=ttl_seconds,
        mechanisms=tuple(mechanisms),
    )
