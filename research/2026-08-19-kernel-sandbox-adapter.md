# Kernel sandbox adapter conformance and fail-closed degradation

Date: 2026-08-19  
Issue: #56 / LAB-029  
Branch: `lab/029-kernel-sandbox-adapter`

## Question

How should an autonomous runtime turn a policy-level child-process sandbox permit into real OS enforcement without silently downgrading security when kernel/platform mechanisms are absent, stale, or only partially available?

## Primary-source mechanisms

### Linux `no_new_privs`

Source: Linux kernel documentation, `No New Privileges Flag`: https://www.kernel.org/doc/html/latest/userspace-api/no_new_privs.html

Transferable mechanism: `PR_SET_NO_NEW_PRIVS` is inherited across fork/clone/execve and cannot be unset; it prevents `execve()` from granting new privilege through setuid/setgid/file capabilities. It does **not** by itself isolate filesystem/network/syscalls and therefore maps only to the `exec_privilege` dimension.

### Linux Landlock

Sources:
- https://cdn.kernel.org/doc/html/latest/userspace-api/landlock.html
- https://www.kernel.org/doc/html/latest/security/landlock.html

Transferable mechanism: Landlock is an unprivileged, stackable LSM that can only add restrictions. Its rulesets explicitly describe handled filesystem rights and, on supported ABIs, network rights. Compatibility must be probed; unsupported access rights/mechanisms must not be guessed.

### Linux seccomp-BPF

Source: Linux kernel userspace API documentation: https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html

Transferable mechanism: seccomp filters constrain syscall execution and persist across exec. Unprivileged filter installation is tied to `no_new_privs`. Seccomp is a syscall-filter dimension, not a substitute for filesystem or network authority modeling.

### Linux namespaces

Namespace operations are platform/runtime capabilities rather than stable assumptions. A namespace being implemented by the kernel does not imply the current execution environment permits creating it. The adapter therefore probes each namespace operation required by policy.

### Windows AppContainer / LPAC

Primary sources:
- Microsoft AppContainer isolation: https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation
- Launching/implementing AppContainer: https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer

Transferable mechanism: AppContainer combines a low-integrity process token, AppContainer/package SID and capability SIDs to constrain access to files/registry/network/devices/processes. LPAC is stricter and requires explicit capabilities for resources that regular AppContainers may receive. This is a credible Windows backend mapping, but it was **not executed** in this Linux run and is not marked observed.

## Observed Linux capability report in this run

Runtime: Linux `6.18.35`, x86_64.

Direct probes performed by the executing assistant:

| Dimension | Mechanism | Observed result |
|---|---|---|
| exec privilege | `PR_SET_NO_NEW_PRIVS` | available; child `prctl()` returned success |
| syscall filter | seccomp-BPF | available; child installed an allow-all BPF filter after `no_new_privs` |
| filesystem | Landlock ABI syscall | unavailable; syscall returned `ENOSYS` (errno 38) |
| network via Landlock | Landlock ABI syscall | unavailable for same reason |
| user namespace | `unshare -Ur true` | available in this run |
| network namespace | `unshare -n true` | unavailable; `EPERM` / operation not permitted |
| mount namespace | `unshare -m true` | unavailable; `EPERM` / operation not permitted |
| FD inheritance | Python `subprocess` `close_fds/pass_fds` | available process-launch enforcement |

This differs from a prior run where user namespace probing failed. The difference is itself evidence that sandbox capabilities must be treated as **fresh observations** with generation/expiry rather than cross-run constants.

## Adapter contract

The reference adapter represents every requested sandbox dimension as either:

- `REQUIRED`: launch must fail if no current observed enforcing backend exists;
- `AUDIT`: policy-only logging is allowed only when the task explicitly declares itself non-security-critical.

An enforcing backend must be both `available=True` and `observed=True`. Merely knowing that a platform normally supports Landlock/AppContainer/etc. is insufficient.

The plan binds:

- task identity;
- sandbox generation;
- credential generation;
- capability-report generation and digest;
- each dimension to an exact mechanism and enforcement class.

The launch boundary then revalidates the bindings against the fresh capability report. This second check is important: a structurally forged `SandboxPlan` must not be able to upgrade `policy_only` into kernel enforcement or name an unavailable backend.

## Failure-injection results

Unsafe seeded design: `UnsafeAdapter` treats a declared `landlock` mechanism as kernel-enforced even when the report says `available=False`. The retained unsafe safety assertion fails as expected because the adapter falsely reports `Enforcement.KERNEL`.

Corrected exact local suite:

```text
13 tests passed
python -m compileall -q experiments  -> success
```

Covered cases:

1. REQUIRED dimension with observed backend succeeds;
2. REQUIRED unavailable backend fails closed;
3. declared-but-unobserved backend fails closed;
4. AUDIT-only downgrade is allowed only for explicitly non-security-critical tasks;
5. stale capability report is rejected;
6. partial enforcement is rejected when any REQUIRED dimension is missing;
7. capability report generation drift is rejected at launch;
8. sandbox generation drift is rejected;
9. credential generation drift is rejected;
10. kernel enforcement is preferred over weaker process-level mechanism where both exist;
11. unsafe false-success is exposed;
12. forged kernel binding is revalidated and rejected;
13. forged policy-only binding for a REQUIRED dimension is rejected.

## Audit findings

The first corrected implementation still trusted the already-created `SandboxPlan` at launch. That would have allowed a forged binding to claim kernel enforcement while retaining a valid capability-report digest. The audit added launch-time binding revalidation against observed mechanisms plus policy-only authorization checks.

## Design conclusions

1. **Policy correctness and enforcement availability are separate facts.** LAB-028 proves the former; LAB-029 gates execution on the latter.
2. **Kernel version is not capability evidence.** This Linux 6.18.35 runtime returned `ENOSYS` for Landlock while seccomp and userns worked.
3. **Security dimensions do not substitute for one another.** `no_new_privs` does not satisfy filesystem isolation; userns does not satisfy network isolation; seccomp does not itself prove path confinement.
4. **Freshness is part of authority.** Report generation/TTL must be checked again at launch because runtime permissions can change between invocations or between planning and execution.
5. **Fail closed is the default.** An unavailable REQUIRED backend is a correct blocker. Policy-only degradation is an explicit opt-in only for non-security-critical work.
6. **A launch plan is not a trusted authority token by structure alone.** Bindings must be revalidated at the enforcement boundary.

## Production implications

A production adapter should expose platform-specific probes and launchers behind the same contract:

- Linux: `no_new_privs`, seccomp, Landlock where actually available, namespaces/cgroups where permission allows, explicit FD allowlists;
- Windows: AppContainer/LPAC capability/token construction and resource ACL binding;
- macOS: future dedicated adapter rather than pretending Linux semantics apply.

For high-assurance execution, capability probes should be tied to the same host/runtime identity that performs launch, and launch should emit evidence identifying the exact backend and generation used.

## Non-goals

- no claim that the current Linux runtime has a complete filesystem/network sandbox;
- no claim that user namespaces alone constitute a secure sandbox;
- no Windows execution claim;
- no general container runtime;
- no weakening of LAB-028 policy to fit available mechanisms.
