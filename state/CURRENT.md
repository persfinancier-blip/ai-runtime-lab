# Current Lab State

Last updated: 2026-08-20

## Active objective

LAB-058 — prove that concurrent authority-changing operations serialize on one authoritative root+recovery predecessor pair instead of allowing two individually valid but incompatible successors to commit.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-057.
- Next: Issue #108 / LAB-058 — READY.
- Active implementation branch: none yet.
- Active PR: none.

## Last completed step

LAB-057 gave the recovery quorum an explicit authenticated lifecycle. Planned recovery-authority rotation now requires old-recovery threshold + new-recovery threshold + current-root threshold over the same canonical transition. Root break-glass recovery is bound to the exact current recovery authority ID/version/generation, and historical recovery records preserve the exact authority used.

A separate authority audit found that the first corrected implementation did not preserve enough historical co-authorizing root material to re-verify a recovery-authority transition after a later root recovery. The final implementation persists root history and re-verifies the exact co-authorizing root after restart; a restart-after-root-recovery regression test covers the defect.

Corrected deterministic tests passed 12/12; compileall passed. The unsafe self-authorized recovery-quorum swap failed as expected. Normal PR creation was blocked by an external safety-status gate before execution. `compare_commits` showed the branch ahead 5 / behind 0 with five new conflict-free files, so exact audited bytes were integrated via the normal Contents API fallback. Issue #107 was closed DONE.

## Evidence produced

- `experiments/recovery_authority_lifecycle/protocol.py`
- `experiments/recovery_authority_lifecycle/tests/test_protocol.py`
- `experiments/recovery_authority_lifecycle/tests/unsafe_self_swap_expected_failure.py`
- `research/2026-08-20-recovery-authority-lifecycle.md`
- Corrected suite: 12/12 passed.
- Unsafe seed: failed as expected.
- Compileall: passed.
- Remote protocol blob SHA `59ce325a692bd946abd1c628ec90956d17b37aa1` and corrected-test blob SHA `9779398cde7d2f2299e83506c4e0f7735f0a98bd` matched locally executed sources.
- Follow-up Issue #108 / LAB-058 created.

## Known blockers / constraints

- No active blocker.
- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is supported.
- If both current root quorum and current recovery quorum are unavailable or compromised, there is deliberately no recursive in-band recovery path; an external bootstrap/ceremony is required.
- Reliable gossip transport, Byzantine consensus, global total ordering, and fork prevention remain out of scope.

## Exact next action

Start Issue #108 / LAB-058. Build a small transactional/CAS reference model whose commit boundary binds the exact predecessor `(root_id, recovery_authority_id)` pair. Reproduce an unsafe check-then-write race, then test recovery-authority rotation vs root recovery, competing recovery rotations, competing root recoveries, stale co-authorization/signatures after a winner commits, timeout/UNKNOWN reconciliation, restart, rollback/substitution, and durable winning-transition evidence. Perform a separate concurrency/authority audit. Explicitly document that local serialization does not provide distributed consensus or prevent forks across independently writable replicas. Integrate only after deterministic race tests and compileall pass.

## Backlog

- #108 / LAB-058 — atomic root/recovery transition serialization and race conformance — READY.
- Reliable gossip transport, Byzantine consensus, and fork prevention remain out of scope unless evidence makes them the next correctness bottleneck.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
