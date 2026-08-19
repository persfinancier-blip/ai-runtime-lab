# Current Lab State

Last updated: 2026-08-19

## Active objective

Advance from capability reporting to actual post-launch enforcement verification: a child-process sandbox is not considered active merely because setup calls or an adapter plan say so.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-029.
- LAB-029: Issue #56 DONE; PR #57 remote patch-audited and squash-merged as `4baf1b5176af17c436bf99807d5ed6a2bc6b93d1`.
- Next: Issue #58 / LAB-030 `Linux sandbox launcher enforcement and post-launch attestation` — READY.

## Last completed step

LAB-029 built a fresh enforcement-capability report and fail-closed adapter contract. Direct Linux probes on kernel 6.18.35 observed `no_new_privs`, seccomp-BPF filter installation, user namespaces and explicit subprocess FD controls as available; Landlock returned `ENOSYS`, while network and mount namespace creation returned `EPERM`. The corrected exact-source suite passed 13/13 and compileall. Audit found and fixed a forged-plan gap by requiring launch-time revalidation of every binding against the current observed capability report.

## Evidence produced

- `research/2026-08-19-kernel-sandbox-adapter.md`
- `experiments/kernel_sandbox_adapter/`
- LAB-029 merge: `4baf1b5176af17c436bf99807d5ed6a2bc6b93d1`.
- Primary sources: Linux kernel no_new_privs, Landlock and seccomp userspace API docs; Microsoft AppContainer/LPAC docs.

## Known blockers / constraints

- Local shell DNS to GitHub remains unreliable/unavailable; GitHub connector plus local execution is the supported path.
- Current Linux capability observations are per-run facts, not durable platform promises: userns was available in this run despite failing in an earlier run.
- Current runtime still lacks observed Landlock, network namespace and mount namespace enforcement; REQUIRED filesystem/network confinement must fail closed rather than downgrade.
- OS/kernel sandbox mechanisms differ across Linux/Windows/macOS.
- PostgreSQL-specific locking/performance validation remains deferred until representative PostgreSQL is available.
- Open-model serving efficiency remains deferred pending representative hardware/runtime.

## Exact next action

Start Issue #58 / LAB-030. Create a branch and build an actual Linux child-process launcher for the mechanisms freshly observed available in that run. Apply `no_new_privs`, a deterministic seccomp policy and explicit FD inheritance controls; use userns only if freshly observed available. Add child-side/post-launch probes and an attestation bound to task/sandbox/credential/capability generations. Prove the harness rejects missing/forged/partial enforcement and continues to fail closed for unavailable REQUIRED filesystem/network isolation. Seed a parent-intent-only unsafe launcher, then audit, exact-source validate and integrate.

## Backlog

- #58 / LAB-030 — Linux sandbox launcher + post-launch enforcement attestation — READY.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
