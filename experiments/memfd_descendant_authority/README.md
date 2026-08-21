# LAB-070 memfd descendant authority

Two explicit modes:

- `SINGLE_PROCESS`: valid only when a probed pre-exec seccomp policy blocks process creation while still allowing same-process threads; otherwise fail closed.
- `SUPERVISED_TREE`: descendants may hold the credential, but the target is PID 1 in a fresh user+PID namespace; when it exits, the kernel tears down remaining namespace processes.

Sealing gives immutability, not secrecy or revocation. After deliberate `pass_fds`, `MFD_CLOEXEC` is no longer a single-target authority guarantee. Credential generation rotation also cannot revoke an already-held live file descriptor.
