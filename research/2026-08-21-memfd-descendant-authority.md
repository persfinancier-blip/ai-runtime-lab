# LAB-070 — Memfd descendant authority and lifetime

## Result

A sealed memfd is a kernel capability. `MFD_CLOEXEC` protects default exec inheritance before handoff, but ordinary descriptor inheritance semantics still apply: after deliberate `pass_fds`, the target can deliberately pass the same readable capability to a descendant. Linux documents both the close-on-exec behavior and normal fork/exec inheritance for `memfd_create`: https://man7.org/linux/man-pages/man2/memfd_create.2.html

The experiment therefore separates two policy modes.

### SINGLE_PROCESS

This mode is selected only when the current runtime actually probes usable x86_64 seccomp. A trusted pre-exec wrapper installs `no_new_privs` plus a filter that denies `fork`/`vfork`, makes `clone3` unavailable, and permits classic `clone` only with `CLONE_THREAD`. This blocks creation of descendant processes without breaking ordinary same-process pthreads. Seccomp filters persist across `execve`, per Linux semantics: https://man7.org/linux/man-pages/man2/seccomp.2.html

If this enforcement cannot be observed, the mode is unsupported rather than silently weakened.

### SUPERVISED_TREE

When descendants are intentionally allowed to share the credential, the target runs as PID 1 in a fresh user+PID namespace. Linux guarantees that when a PID namespace's init process exits, the kernel sends SIGKILL to the remaining processes in that namespace: https://man7.org/linux/man-pages/man7/pid_namespaces.7.html

The real-process harness proves a descendant can inherit/read the descriptor while the target lives and that the descendant is gone after namespace-init exit. The current runtime probes user+PID namespaces as available, while cgroup v2 is mounted read-only; cgroup delegation is therefore not claimed as an enforcement backend.

## Rotation and lifetime

Credential-generation rotation is metadata freshness, not revocation of an already-held kernel descriptor. A live authorized process/tree retains readable authority until the descriptor is closed or the holder exits. This remains separate from LAB-031/032 process identity/liveness.

## Fundamental boundary

Once an untrusted process can read plaintext, no memfd, seal, CLOEXEC bit, seccomp filter, PID namespace, or descriptor-lifetime policy can prevent that process from copying the bytes through another channel that policy permits. This work constrains OS capability propagation and lifetime; it is not DRM for secrets.
