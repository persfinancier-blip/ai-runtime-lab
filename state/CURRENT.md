# Current Lab State

Last updated: 2026-08-19

## Active objective

LAB-031: extend launch-time sandbox proof to lifetime-safe supervision: bind authority to a process instance, reject stale/replayed launch evidence, fence generation drift, and prove bounded descendant termination with freshly available primitives.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-030.
- Active: Issue #60 / LAB-031 — IN_PROGRESS.
- Branch: `lab/031-sandbox-lifetime`.
- PR: not opened yet; implementation is not yet acceptance-ready.

## Last completed step

Fresh runtime probes and primary-source research were completed. Python exposes `os.pidfd_open`; a real sleeping child produced a pidfd that was non-readable while live and readable after SIGKILL/wait. `/proc/<pid>/stat` starttime is readable. cgroup v2 and `cgroup.kill` are visible but the cgroup filesystem is not writable, so delegated cgroup-tree containment cannot be claimed in this runtime. Process-group creation/kill is available as a weaker bounded fallback. Issue #60 records these observations and primary-source decisions. A local prototype was started, but the descendant process-group test hung under the current harness and therefore no implementation/test success has been claimed or published.

## Evidence produced

- Fresh real-process pidfd liveness/exit probe succeeded.
- Fresh `/proc/<pid>/stat` starttime observation succeeded.
- Fresh cgroup probe: v2 mounted; `cgroup.kill` visible; cgroup root not writable.
- Primary sources: Linux `pidfd_open(2)`, `pidfd_send_signal(2)`, `proc_pid_stat(5)`, kernel cgroup-v2 documentation.
- Issue #60 updated with runtime evidence and design decisions.
- Partial local tests for pidfd liveness, generation drift, foreign receipt, numeric-PID/starttime mismatch and fail-closed cgroup capability passed individually; full suite is NOT accepted because descendant termination harness timed out.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- cgroup v2 is not writable/delegated in this runtime; REQUIRED cgroup-tree containment must fail closed.
- Process groups are weaker than cgroups: a deliberately escaping descendant can evade group kill unless another containment mechanism prevents escape.
- The first descendant termination test harness hung; likely causes include child/pipe inheritance or zombie/reaping behavior. This must be reproduced and fixed before publishing code.
- Numeric PID + starttime is restart-reconstructible evidence but pidfd is the stronger live instance handle; do not serialize a pidfd number as durable identity.
- Launch attestation, liveness evidence, termination evidence and task-completion evidence remain distinct authority classes.

## Exact next action

Resume LAB-031 on `lab/031-sandbox-lifetime`. Rebuild the descendant test so descendants cannot keep the test runner's captured stdout/stderr pipes open (redirect child stdio to DEVNULL and use an external `/bin/sleep` descendant or close inherited descriptors), then prove process-group termination without a hang. Add explicit unsafe numeric-PID/old-receipt replay failure, stale-after-exit, generation-drift, forged starttime, and evidence-kind separation tests. If cgroup containment is REQUIRED, assert fail-closed because delegation is absent. Only after the complete bounded suite passes should code/research be published to the branch, remote-patch audited, exact-source validated, and integrated.

## Backlog

- #60 / LAB-031 — sandbox lifetime supervision + attestation freshness — IN_PROGRESS.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
