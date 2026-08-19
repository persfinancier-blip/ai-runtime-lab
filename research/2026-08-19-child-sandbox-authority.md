# LAB-028 — Child-process ambient authority and local sandbox conformance

Date: 2026-08-19

## Finding
Safe credential delivery is not least privilege. The child also needs an execution permit whose authority is explicit and generation-bound.

## Primary-source donors
- Linux `no_new_privs`: inherited across fork/clone/exec and cannot be unset; prevents `execve` from granting privileges it otherwise could gain. It is not a general sandbox and does not block unrelated ambient file/socket access. Source: Linux kernel no_new_privs documentation.
- Linux Landlock: unprivileged, stackable access-control designed to restrict ambient filesystem/network rights; rules add restrictions and do not replace system DAC/LSM. Enforcement commonly pairs with `no_new_privs`. Source: Linux kernel Landlock documentation.
- Python `subprocess`: `close_fds` and POSIX `pass_fds` / Windows handle lists make descriptor inheritance explicit; `cwd` sets child working directory but is not an access-control boundary. Source: Python 3.14 subprocess documentation.
- Windows AppContainer/LPAC: capability-SID based least-privilege boundary for file, registry, network and process resources; LPAC is stricter and requires explicit capabilities for resources ordinary AppContainer may access. Source: Microsoft AppContainer isolation/launch documentation.

## Runtime probe
Observed Linux kernel `6.18.35`; `unshare` exists. Unprivileged user namespace probe failed with `EINVAL`; network namespace probe failed with `EPERM`. `/sys/kernel/security/landlock` was not exposed in this container. Therefore this run does not claim real namespace/Landlock enforcement.

## Protocol
`SandboxSpec` binds task/workspace, sandbox generation, LAB-027 credential generation, explicit read/write roots, exec allowlist, inherited FD allowlist, and separate local-socket/network capabilities. `Permit` fingerprints that complete authority set. Any generation or authority drift invalidates the permit.

## Experiment
The unsafe broad-authority seed allows writing `/home/user/.ssh/authorized_keys` and fails its safety assertion as expected. Corrected deterministic suite: 9/9 passed.

## Audit
This is a policy/conformance model, not a kernel security boundary. `cwd` and environment scrubbing are hygiene only. Production adapters must map the same permit to platform enforcement (e.g. Landlock/seccomp/no_new_privs or AppContainer/LPAC) and fail closed when a required enforcement feature is unavailable. Filesystem, local sockets, network, exec and inherited descriptors remain separate capabilities.

## Integration implication
LAB-027 credential delivery must occur only after a matching sandbox permit exists; changing either sandbox generation or credential generation requires a new permit. Do not grant HOME, config directories, local sockets, network, or shell execution merely because a credential is authorized.
