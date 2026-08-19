# LAB-031 — Sandbox lifetime supervision and attestation freshness

## Question

How can launch-time sandbox evidence remain safe over a process lifetime when numeric PIDs can be reused, generations can drift, and descendants may survive the directly observed child?

## Primary mechanisms

- Linux pidfds provide an instance-bound live process handle. The prototype uses `os.pidfd_open` and poll/select readiness to distinguish a live instance from an exited one.
- `/proc/<pid>/stat` field 22 (`starttime`) is retained as restart-reconstructible defense-in-depth identity. It is not treated as equivalent to a live pidfd.
- `/proc/self/fdinfo/<pidfd>` exposes the pidfd target PID in this runtime. The verifier binds the receipt PID to the pidfd target; merely having a live pidfd plus a separately valid receipt is insufficient.
- cgroup v2 `cgroup.kill` is the preferred investigated tree-kill primitive, but the current runtime exposes a non-writable cgroup hierarchy. REQUIRED cgroup-tree containment therefore fails closed.
- A fresh process group/session is usable as a bounded fallback for cooperative descendants. It is explicitly weaker than delegated cgroup containment because a descendant allowed to create a new session/process group can escape.

Primary-source provenance:
- Linux `pidfd_open(2)` and `pidfd_send_signal(2)` manual pages.
- Linux `proc_pid_stat(5)` manual page.
- Linux kernel cgroup v2 documentation (`cgroup.kill`).

## Experiment

The real-process harness launches external `/bin/sleep` children, obtains pidfds, reads starttime, mutates sandbox/credential/capability generations, and terminates a process group whose descendant stdio is redirected to `DEVNULL`.

The previous hanging harness was reproduced as a test-design problem: descendants inherited captured stdio pipes, so the runner could wait on pipe EOF after the leader died. The corrected harness gives both leader and descendant `DEVNULL` stdio and uses an external sleep descendant. Process-group termination then completes without the pipe hang.

## Audit finding

The first corrected prototype still accepted a *foreign* live pidfd paired with another process's valid receipt. Both facts were independently true, but they did not describe the same process instance. The audit added `pidfd_target_pid()` using pidfd fdinfo and requires the live handle target PID to equal the receipt PID before freshness can pass.

## Authority model

Launch attestation, liveness evidence, termination evidence, and task-completion evidence are distinct kinds. Liveness or successful termination never implies task completion.

A serialized numeric pidfd descriptor is not durable identity. After supervisor restart, PID + starttime can help reject obvious reuse, but reacquiring full live authority requires a fresh instance-bound observation.

## Observed validation

- Unsafe numeric-PID + old-receipt seed: expected assertion failure.
- Corrected deterministic suite: 8/8 tests passed.
- Real descendant process-group termination completed without the prior hang.
- REQUIRED cgroup-tree containment failed closed in the current non-delegated runtime.

## Limits

This is not a general container runtime. Process groups do not contain malicious descendants that can escape the group. pidfd protects process-instance identity but does not itself contain descendants. Strong tree containment remains conditional on an actually delegated kernel primitive such as cgroup v2.
