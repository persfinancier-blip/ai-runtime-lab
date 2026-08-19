# Ephemeral credential delivery and process-boundary leakage

Date: 2026-08-19  
Issue: #52 / LAB-027  
Branch: `lab/027-ephemeral-credential-delivery`

## Question

How should an agent runtime deliver a credential to a tool/child process without turning argv, environment, temporary files, inherited descriptors, crash artifacts, or retry state into a second secret store?

## Primary-source mechanisms

### Linux process argv and environment

Linux `proc_pid_cmdline(5)` documents that `/proc/<pid>/cmdline` exposes the process command line. `proc_pid_environ(5)` documents that `/proc/<pid>/environ` exposes the initial environment supplied at `execve()`, subject to ptrace access checks. `environ(7)` also states that forked children inherit a copy of the parent's environment.

Sources:
- https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html
- https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html
- https://man7.org/linux/man-pages/man7/environ.7.html
- https://man7.org/linux/man-pages/man2/execve.2.html

Transferable rule: argv and ambient environment are transport/control surfaces, not secret containers. A secret placed there can outlive the narrow call boundary and become observable to process-inspection/debug tooling.

### Descriptor inheritance

POSIX exec semantics preserve open file descriptors unless `FD_CLOEXEC` is set. Current Python `subprocess` documentation states that `close_fds=True` closes all descriptors except standard streams before exec, while `pass_fds` explicitly preserves selected POSIX descriptors.

Sources:
- https://docs.python.org/3/library/subprocess.html
- https://man7.org/linux/man-pages/man3/execve.3p.html

Transferable rule: default-deny inheritance; pass only the exact credential-bearing handle required by the child.

### Memory-backed / OS credential delivery

Linux kernel documentation for memfd includes close-on-exec and non-executable/sealing controls, illustrating a stronger primitive than a named temporary file for scoped in-memory material. Systemd's credential mechanism is another production example of delivering service credentials through a dedicated credential boundary rather than treating the normal command line as the credential channel.

Sources:
- https://www.kernel.org/doc/html/latest/userspace-api/mfd_noexec.html
- https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html

Transferable rule: prefer dedicated OS credential handles/stores or narrow descriptors; named files are a fallback with weaker deletion semantics.

## Minimal model

A durable credential reference contains only:
- `credential_id`;
- `generation`;
- `scope`;
- keyed HMAC fingerprint for correlation/audit.

Raw secret bytes remain in a short-lived vault object and are borrowed only at the delivery boundary. Rotation increments generation; scope change or rotation makes an old reference stale.

## Failure-injection experiment

Unsafe baselines deliberately put `s3cr3t-low-entropy` in:
1. argv (`tool --token ...`);
2. environment (`API_TOKEN=...`).

Both expected-safety assertions failed, demonstrating the leak.

Corrected local suite: **12/12 passed** plus `compileall`.

Covered:
- raw argv rejection;
- ambient secret environment scrub;
- actual spawned child observes no scrubbed secret;
- ephemeral file mode `0600`;
- unlink on success;
- unlink on exception/failure;
- insecure file mode rejection;
- descriptor non-inheritance by default on POSIX;
- explicit `pass_fds` allowlist behavior;
- credential rotation rejects stale generation;
- scope change rejects stale reference;
- retry/UNKNOWN can retain stable non-secret identity without retaining a raw-secret evidence copy.

## Audit findings

1. **Environment scrubbing must be name-based and default-deny enough for the deployment.** The prototype uses a conservative key-marker scrub for demonstration; production should build the child env from a minimal allowlist rather than trying to enumerate every secret name.
2. **File cleanup is not forensic erasure.** Overwrite + unlink only reduces namespace/lifetime exposure and cannot guarantee storage media destruction due to filesystem/journaling/copy-on-write behavior.
3. **POSIX and Windows handle inheritance differ.** Python exposes `pass_fds` only on POSIX; Windows needs explicit handle-list semantics. Production adapters must implement per-platform delivery rather than pretending one mechanism is portable.
4. **Crash-before-finally remains a different failure class.** Filesystem fallbacks require startup scavenging/lease-based cleanup or OS-managed ephemeral storage; a `finally` block alone cannot cover SIGKILL/power loss.
5. **Credential identity is not authorization.** A stable credential ID/generation helps audit/retry but LAB-021/022 scope/destination/purpose authorization still governs whether use is permitted.

## Production implication

Preferred delivery hierarchy:

`dedicated OS credential facility / narrow memory-backed FD or pipe -> explicitly allowlisted child handle -> tightly scoped 0600 temp file fallback -> NEVER argv or ambient inherited environment`

Raw secret material must not become durable run state, evidence, logs, replay snapshots, or retry metadata. Retry should re-borrow the currently authorized generation by credential identity and re-check scope rather than replaying cached secret bytes.

## Non-goals

- no claim of physical secret erasure;
- no cross-platform credential-store implementation;
- no kernel-hardening benchmark;
- no replacement for destination/egress authorization from LAB-021–025;
- no secret manager implementation.
