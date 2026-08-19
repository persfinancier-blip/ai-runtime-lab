# Current Lab State

Last updated: 2026-08-19

## Active objective

LAB-033: protect restart-reconstructible launch records from tampering, rollback, cross-task substitution, and replay before LAB-032 fresh process authority is reacquired.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-032.
- Completed Issue #61 / LAB-032.
- Merged PR #62 / LAB-032, squash merge `e5176420375ebafe649b5836f4d78d8679c87ab2`.
- Active next: Issue #63 / LAB-033 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-032 built and validated real-process supervisor restart recovery. The original pidfd was deliberately closed, a fresh pidfd was reacquired after simulated restart, its target PID was rebound to persisted PID/starttime/task/generations, and consequential continuation was allowed only on full agreement. The corrected suite passed 9/9; the PID-only unsafe baseline failed as expected. Remote patch audit found no remaining blocker and PR #62 was squash-merged.

## Evidence produced

- `experiments/supervisor_restart/protocol.py`
- `experiments/supervisor_restart/tests/test_protocol.py`
- `experiments/supervisor_restart/tests/unsafe_pid_only_expected_failure.py`
- `research/2026-08-19-supervisor-restart-recovery.md`
- Corrected local real-process suite: 9/9 passed.
- `python -m compileall -q experiments` passed.
- Published protocol blob SHA matched locally executed source hash `8b99c1663b800384cdd8a984c6ac699f47567ecd`.
- Audit fix: durable record must also match expected task identity.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- cgroup v2 remains non-writable/non-delegated here; process-group cleanup cannot guarantee containment of deliberately escaping descendants.
- Fresh pidfd + starttime establishes process-instance authority only after restart; it does not prove that the persisted launch record itself was authentic or non-replayed.
- Durable record integrity/anti-replay is intentionally the next gap.

## Exact next action

Start Issue #63 / LAB-033. Build a canonical authenticated durable launch-record envelope (standard-library HMAC reference is sufficient), bind it to task + authority/generation domain, persist no raw key material, and test field tamper, cross-task substitution, rollback/replay, key/authority rotation, canonicalization ambiguity, truncation/corruption, and restart verification. Keep authenticity distinct from liveness: after record verification, LAB-032 fresh pidfd/starttime reconciliation remains mandatory. Include an unsafe unsigned/structural-trust seed, run deterministic tests/audit, persist research, and integrate only after observed validation.

## Backlog

- #63 / LAB-033 — durable launch-record integrity + anti-replay — READY.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
