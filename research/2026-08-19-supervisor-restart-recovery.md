# LAB-032 — Supervisor restart recovery and orphan reconciliation

Date: 2026-08-19
Issue: #61
Branch: `lab/032-supervisor-restart-recovery`

## Question

How can a restarted supervisor safely recover authority over a still-running Linux child after its original pidfd was lost, without confusing PID reuse, stale generations, or a foreign task record with the same process instance?

## Primary-source mechanisms

### Linux pidfd

Linux `pidfd_open(pid, 0)` creates a fresh file descriptor referring to the task identified at acquisition time. A pidfd is pollable for process exit and is the preferred existing-process handle. `pidfd_send_signal` avoids the PID-reuse race inherent in signaling by numeric PID.

Sources:
- https://man7.org/linux/man-pages/man2/pidfd_open.2.html
- https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html

Transferable rule: the descriptor number itself is process-local and must never be serialized as durable authority. A restarted supervisor reacquires a new pidfd.

### `/proc/<pid>/stat` starttime

Field 22 `starttime` records the process start time after system boot. It is restart-reconstructible instance evidence and can distinguish a reused numeric PID from the persisted process instance.

Source:
- https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html

Transferable rule: PID + starttime is identity evidence, not live authority. It is used to bind a newly reacquired pidfd to the persisted instance.

## Corrected restart protocol

Persist only task id, numeric PID, `/proc` starttime, sandbox/credential/capability generations, and process-group identity. Never persist pidfd descriptor number.

After restart:
1. reject foreign task identity or generation drift;
2. read current `/proc/<pid>/stat` and require persisted starttime;
3. call `pidfd_open(pid)` to obtain fresh live authority;
4. read `/proc/self/fdinfo/<pidfd>` and require the pidfd target PID equals the record PID;
5. re-read process starttime after acquisition and require it still matches both the record and the pre-acquisition observation;
6. reject exited/zombie/unverifiable state;
7. only then return `SAME_INSTANCE` with a fresh authority object.

States are explicit: `SAME_INSTANCE`, `EXITED`, `IDENTITY_MISMATCH`, `UNVERIFIABLE`, `GENERATION_DRIFT`.

## Experiment

Unsafe seed: PID-only authority accepts mere `/proc/<pid>` existence. Against PID 1 the safety test fails as expected because a live PID without task/starttime binding is accepted.

Corrected real-process suite after audit: **9/9 passed**. `python -m compileall -q experiments` passed.

Covered: lost original pidfd, fresh pidfd reacquisition, generation drift, starttime mismatch, exited state, fresh-authority continuation gate, orphan process-group termination, process-group drift, foreign task record rejection, and absence of pidfd descriptor in serialized durable state.

## Audit finding

The first corrected implementation bound PID/starttime/generations but not the expected task. A valid live-process record from another task could therefore be accepted. `expected_task_id` is now checked before authority reacquisition and covered by a regression test.

## Limits

- The durable launch record itself still needs a trusted durable storage boundary; this prototype does not add record signatures/MACs.
- Without delegated writable cgroup v2, process-group termination cannot guarantee containment of descendants that deliberately escape the group/session. REQUIRED tree containment must fail closed.
- `UNVERIFIABLE` is not success; it requires quarantine/termination policy, never consequential continuation.
- This is not a general init system or container supervisor.

## Decision

A restarted supervisor may resume consequential work only after reconstructible identity and fresh live authority agree: `task + generations + PID + starttime + fresh pidfd target`. Any disagreement is a fencing/reconciliation outcome, not a reason to guess.
