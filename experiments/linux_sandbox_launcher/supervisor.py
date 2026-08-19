from __future__ import annotations

import os
import subprocess
import sys

from experiments.linux_sandbox_launcher.protocol import install_seccomp_errno_filter, set_no_new_privs


def _sandbox_preexec() -> None:
    set_no_new_privs()
    install_seccomp_errno_filter()


def main() -> int:
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "LAB030_PARENT_USERNS": os.environ["LAB030_PARENT_USERNS"],
        "LAB030_PROBE_FD": os.environ.get("LAB030_PROBE_FD", "-1"),
    }
    p = subprocess.run(
        [sys.executable, "-c", os.environ["LAB030_PAYLOAD_CODE"]],
        env=env,
        close_fds=True,
        pass_fds=(),
        preexec_fn=_sandbox_preexec,
        capture_output=True,
        text=True,
        timeout=8,
    )
    sys.stdout.write(p.stdout)
    sys.stderr.write(p.stderr)
    return p.returncode


if __name__ == "__main__":
    raise SystemExit(main())
