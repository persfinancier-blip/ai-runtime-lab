# Current Lab State

Last updated: 2026-08-19

## Active objective

Advance from launch-time sandbox proof to lifetime-safe supervision: bind attestation to a specific process instance, prevent replay after exit/PID reuse, handle generation drift, and prove descendant termination/containment where the runtime supports it.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-030.
- LAB-030: Issue #58 DONE; PR #59 squash-merged as `ad56179fc0730887c9a3aec7704b710c659c9a34`.
- Next: Issue #60 / LAB-031 `Sandbox lifetime supervision, process identity, and attestation freshness` — READY.

## Last completed step

LAB-030 built and exact-source validated a real Linux launcher. Fresh probes observed userns, `no_new_privs` and seccomp available, while network and mount namespace creation remained unavailable. A trusted supervisor now applies `no_new_privs` + seccomp at the pre-exec boundary and only then execs the actual payload. The launched payload proves the resulting state via `/proc/self/status`, a denied syscall, user-namespace identity and FD inheritance probes. Remote audit caught the earlier post-exec setup flaw and it was fixed before merge.

## Evidence produced

- `research/2026-08-19-linux-sandbox-launcher.md`.
- `experiments/linux_sandbox_launcher/`.
- Corrected exact-source suite: 11/11 passed.
- Unsafe parent-intent-only seed: expected failure.
- Exact executable/test blobs matched local executed sources after publication.
- LAB-030 merge: `ad56179fc0730887c9a3aec7704b710c659c9a34`.
- Primary sources: Linux `no_new_privs`, seccomp filter API/seccomp(2), Python subprocess FD controls.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- Current runtime supports userns but not network or mount namespaces; REQUIRED network/filesystem confinement must remain fail-closed.
- LAB-030 seccomp policy is x86_64-specific and deliberately minimal; it demonstrates enforcement mechanics, not a production syscall allowlist.
- Launch attestation is a point-in-time fact; numeric PID alone is not durable process identity and descendants may outlive the directly observed process.
- HMAC launch receipts depend on protecting the launcher signing key.
- PostgreSQL-specific validation and open-model serving remain deferred for representative environments.

## Exact next action

Start Issue #60 / LAB-031. Fresh-probe Linux supervision primitives such as pidfd, `/proc` start-time identity, process groups and cgroup v2 availability. Build a bounded real-process harness that binds liveness/termination evidence to a specific child instance, rejects stale launch receipts after exit or generation drift, detects numeric-PID reuse/forgery, and proves descendant termination using the strongest freshly available mechanism. Keep launch attestation, liveness, termination and task-completion evidence distinct. Seed an unsafe numeric-PID + old-receipt design, then audit, exact-source validate and integrate.

## Backlog

- #60 / LAB-031 — sandbox lifetime supervision + attestation freshness — READY.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
