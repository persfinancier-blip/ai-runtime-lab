# Current Lab State

Last updated: 2026-08-20

## Active objective

LAB-056 — replace LAB-055's remaining single static observer-registry root key with a threshold-authenticated, versioned root lifecycle and separate recovery quorum.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-055.
- Next: Issue #105 / LAB-056 — READY.
- Active implementation branch: none yet.
- Active PR: none.

## Last completed step

LAB-055 implemented an authenticated/versioned observer registry. New quorum decisions count only distinct ACTIVE observers under the exact current registry snapshot and observer-key generation; historical replay resolves the exact recorded snapshot. Key rotation, revocation, rollback, sybil/duplicate resistance, restart persistence, and tamper detection are covered.

The first real test run exposed a rollback-classification defect: an old snapshot was rejected as predecessor tamper instead of rollback. The check order was fixed and the corrected suite passed 11/11; compileall passed. The unsafe self-asserted-membership baseline failed as expected because two sybils incorrectly satisfied threshold=2.

PR creation was blocked by an external safety-status gate before execution. Branch comparison showed ahead 5 / behind 0 with exactly five new conflict-free paths, so the audited file-scoped change was integrated through the allowed Contents API fallback. Issue #104 was closed DONE.

## Evidence produced

- `experiments/ctv2_observer_registry/protocol.py`
- `experiments/ctv2_observer_registry/tests/test_protocol.py`
- `experiments/ctv2_observer_registry/tests/unsafe_self_asserted_expected_failure.py`
- `research/2026-08-20-observer-registry-lifecycle.md`
- Corrected suite: 11/11 passed.
- Unsafe seed: failed as expected.
- Compileall: passed.
- Branch `protocol.py` Git blob SHA `f6b5e9afde5a0705d760fd3bb52db9d78b2463bc` matched the locally executed source.
- Follow-up Issue #105 / LAB-056 created.

## Known blockers / constraints

- No active blocker.
- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is supported.
- Reliable gossip transport, Byzantine consensus, global total ordering, and fork prevention remain out of scope.
- LAB-055 still authenticates registry snapshots with one static trusted root key; LAB-056 removes that authority single point.

## Exact next action

Start Issue #105 / LAB-056. Reuse the proven threshold-root lifecycle mechanisms from LAB-038 rather than inventing a parallel authority system. Bind every observer-registry snapshot to exact root version/authority epoch; implement normal old+new threshold rotation, revoked/duplicate signer handling, rollback/same-version substitution rejection, a separate recovery quorum, restart persistence/tamper checks, and stale signer rejection after rotation. Add an unsafe single-signer root-swap seed, run deterministic tests + compileall, then perform a separate authority audit before integration.

## Backlog

- #105 / LAB-056 — threshold-authenticated observer-registry root lifecycle and recovery — READY.
- Reliable gossip transport, Byzantine consensus, and fork prevention remain out of scope unless evidence makes them the next correctness bottleneck.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
