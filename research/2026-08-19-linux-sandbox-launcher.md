# LAB-030 — Linux sandbox launcher enforcement and post-launch attestation

Date: 2026-08-19
Issue: #58
Branch: `lab/030-linux-sandbox-launcher`

## Question

How can the lab distinguish “the parent intended to enable a sandbox” from “the launched child is observably constrained by the expected Linux mechanisms”?

## Primary-source baseline

- Linux `no_new_privs`: https://docs.kernel.org/userspace-api/no_new_privs.html
- Linux seccomp filter API: https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html
- seccomp(2): https://man7.org/linux/man-pages/man2/seccomp.2.html
- Python subprocess FD inheritance semantics: https://docs.python.org/3/library/subprocess.html

Transferable rules:

1. `PR_SET_NO_NEW_PRIVS` is inherited across fork/clone/exec and cannot be unset; it prevents `execve()` from granting new privileges.
2. Unprivileged seccomp filter installation requires `no_new_privs` (or CAP_SYS_ADMIN in the namespace), and installed filters persist across allowed exec.
3. A seccomp filter must validate the syscall architecture before interpreting syscall numbers; this prototype fails closed outside x86_64 and the BPF program validates `AUDIT_ARCH_X86_64`.
4. Parent-side return codes are setup evidence, not launch enforcement evidence. The child must prove the resulting state.
5. File-descriptor inheritance should be default-deny; a parent FD deliberately marked inheritable is used as a child-side negative probe.

## Fresh runtime observations

Observed directly in this run on Linux 6.18.35 x86_64:

- `unshare -Ur true`: success — user namespace available;
- `unshare -n true`: `EPERM` — network namespace unavailable;
- `unshare -m true`: `EPERM` — mount namespace unavailable;
- `PR_SET_NO_NEW_PRIVS`: available;
- seccomp-BPF filter installation after `no_new_privs`: available.

These are per-run observations, not platform promises.

## Prototype

`experiments/linux_sandbox_launcher/` implements:

- fresh `CapabilityReport` with generation + digest;
- fail-closed request validation;
- user namespace launch only when freshly available and required;
- `no_new_privs` applied in the child setup path;
- deterministic seccomp-BPF filter with x86_64 audit-architecture validation and a probe syscall denied with `EPERM`;
- `close_fds=True` / empty `pass_fds` for default-deny FD inheritance;
- child-side inspection of `/proc/self/status` for `NoNewPrivs`, seccomp mode and filter count;
- child-side syscall probe proving the filter is active;
- child-side user-namespace inode comparison;
- child-side FD-negative probe;
- HMAC-bound `LaunchReceipt` tied to task, sandbox generation, credential generation, capability generation/digest, child PID, backend set, probe digest and explicit observed enforcement facts.

REQUIRED network/filesystem isolation remains fail-closed in this runtime because the kernel/runtime probes cannot supply those mechanisms.

## Unsafe seed

`UnsafeIntentOnlyLauncher` records that the parent *wanted* `no_new_privs` + seccomp and returns `claimed_enforced=True` without observing a child. The dedicated unsafe test expects post-launch evidence and fails with `unsafe launcher claimed success without post-launch evidence`.

This demonstrates why setup intent cannot be a completion claim.

## Validation

Corrected local suite after audit fixes:

- 11/11 deterministic tests passed;
- `python -m compileall -q experiments` passed;
- real child launch exercised userns, `no_new_privs`, seccomp and FD default-deny;
- unavailable REQUIRED network/filesystem isolation was rejected rather than downgraded.

Covered failure cases include stale capability generation, forged receipt, properly signed backend omission, properly signed false enforcement fact, sandbox-generation drift and inherited-FD leakage.

## Audit findings and fixes

### A1 — receipt relied too heavily on opaque probe digest

Initial receipt signed the backend names and probe digest but not explicit observed enforcement facts. This made later verification less transparent. Fixed by binding signed booleans for observed NNP, seccomp, userns and FD-default-deny and re-checking them in `verify()`.

### A2 — backend omission test originally only exercised signature failure

Initial mutation removed `seccomp-bpf` but retained the old signature, so rejection could happen before backend validation. Added a test that re-signs the malformed receipt with the legitimate test key; verifier still rejects the missing REQUIRED backend.

### A3 — seccomp syscall-number filter lacked audit-architecture validation

A syscall-number-only filter is unsafe across ABIs. Fixed by loading `seccomp_data.arch`, accepting only `AUDIT_ARCH_X86_64`, killing a mismatched ABI, and making the prototype explicitly x86_64-only.

## What this proves

Within the bounded Linux runtime exercised here, the lab can launch a child and obtain evidence that available sandbox primitives are actually active after launch. It can also reject forged/partial evidence and fail closed for unavailable REQUIRED confinement dimensions.

## What this does not prove

- This is not a full container runtime.
- The seccomp policy is deliberately tiny and demonstrates enforcement mechanics, not a production syscall allowlist.
- User namespaces do not provide filesystem/network isolation by themselves.
- `no_new_privs` is not a complete sandbox.
- HMAC receipt trust assumes launcher signing-key integrity.
- Landlock/network/mount isolation are not claimed because they were not available in this run.
- Cross-platform launchers remain separate work.

## Integration implications

A production launcher should preserve the contract rather than these exact implementation details:

`fresh capability evidence -> fail-closed plan -> apply kernel controls -> launch -> child/post-launch probes -> signed/bound receipt -> verifier`.

A task must not move to an externally consequential phase merely because sandbox setup APIs returned success; it needs current post-launch enforcement evidence bound to the exact task/generations.
