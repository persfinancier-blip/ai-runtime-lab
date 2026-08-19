# Current Lab State

Last updated: 2026-08-19

## Active objective

LAB-032: prove restart-safe supervisor recovery and orphan-process reconciliation after the live pidfd held by LAB-031 is lost with the supervisor process.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-031.
- Active: Issue #61 / LAB-032 — READY.
- Branch: not created yet.
- PR: none.

## Last completed step

LAB-031 completed. The prior descendant-termination hang was removed by preventing descendants from inheriting captured stdout/stderr and using an external `/bin/sleep` descendant. The corrected real-process suite passed 8/8. An audit then found that a foreign live pidfd could be paired with another process's valid receipt; this was fixed by binding the pidfd target PID from `/proc/self/fdinfo/<pidfd>` to the receipt PID. Normal PR creation was blocked before execution by an external safety-status gate, so after `main..branch` comparison showed four new conflict-free paths, the audited files were integrated through the normal Contents API fallback. Issue #60 is DONE.

## Evidence produced

- `experiments/sandbox_lifetime/protocol.py`
- `experiments/sandbox_lifetime/tests/test_protocol.py`
- `experiments/sandbox_lifetime/tests/unsafe_numeric_pid_replay.py`
- `research/2026-08-19-sandbox-lifetime-supervision.md`
- Corrected local real-process suite: 8/8 passed.
- Unsafe numeric-PID/old-receipt seed: expected failure.
- Protocol branch blob SHA matched the locally executed protocol source (`4ba8827a4ca612ddece21cb99da141e80e880a31`).
- cgroup v2 remains visible but non-writable/non-delegated; REQUIRED tree containment fails closed.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- cgroup v2 is not writable/delegated in this runtime; process-group fallback is weaker and cannot contain a deliberately escaping descendant.
- A pidfd is strong live instance authority but its descriptor number is not durable across supervisor restart.
- PID + `/proc` starttime is restart-reconstructible identity evidence, not equivalent to retaining the original pidfd.
- PR creation may be blocked by the external safety-status gate; the repository's audited file-scoped Contents API fallback remains available when conflict checks pass.

## Exact next action

Start Issue #61 / LAB-032. Create a branch, build a real-process restart harness that persists only PID/starttime/task/generations, deliberately discards the original pidfd, then reacquires a fresh pidfd and accepts SAME_INSTANCE only when fresh pidfd target + current `/proc` starttime + persisted identity + current generations all agree. Add EXITED / IDENTITY_MISMATCH / UNVERIFIABLE states, generation-drift fencing, orphan terminate/quarantine behavior, and an unsafe seed that treats serialized pidfd number or PID alone as durable authority. Run bounded tests, audit handle/receipt binding again, persist research/evidence, and integrate only after observed validation.

## Backlog

- #61 / LAB-032 — supervisor restart recovery + orphan reconciliation — READY.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
