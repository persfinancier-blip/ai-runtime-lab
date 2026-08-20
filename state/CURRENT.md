# Current Lab State

Last updated: 2026-08-20

## Active objective

LAB-055 — authenticate and version observer identity/key/quorum membership so causal-gossip corroboration cannot be satisfied by self-asserted, stale, revoked, or replayed observer membership.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-054.
- Next: Issue #104 / LAB-055 — READY.
- Active implementation branch: none yet.
- Active PR: none.

## Last completed step

LAB-054 was corrected after its self-found authority-boundary defect. Each causal observation now preserves the exact peer signature; `accept()` reconstructs and verifies the peer-authenticated view and checks exact `view_id` binding before using observer evidence. The corrected exact-source suite passed 13/13 tests, the unsafe wall-clock baseline failed as expected, and compileall passed.

PR creation was blocked by an external safety-status gate before execution. `compare_commits` showed exactly five new LAB-054 paths and no path conflicts with `main`, so the exact audited bytes were integrated via the allowed Contents API fallback. Issue #103 was closed DONE.

## Evidence produced

- `experiments/ctv2_bundle_causal_gossip/protocol.py`
- `experiments/ctv2_bundle_causal_gossip/tests/test_protocol.py`
- `experiments/ctv2_bundle_causal_gossip/tests/unsafe_wallclock_expected_failure.py`
- `research/2026-08-20-causal-gossip-ordering.md`
- Corrected suite: 13/13 passed.
- Unsafe wall-clock seed: failed as expected.
- Compileall passed.
- Main `protocol.py` Git blob SHA: `021486287201b8f471461d6909b92d20593a86c0`, matching the tested branch/local source.
- Audit regression coverage now includes fabricated observer content without a valid peer signature and `view_id` substitution.
- Follow-up Issue #104 / LAB-055 created.

## Known blockers / constraints

- No active blocker.
- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is supported.
- Reliable gossip delivery, Byzantine consensus, global total ordering, and fork prevention remain out of scope.
- LAB-054 still assumes `observer_keys` is a trusted static map; LAB-055 removes that assumption.

## Exact next action

Start Issue #104 / LAB-055. Create a task branch from current `main`, inspect primary mechanisms for authenticated witness/observer membership lifecycle, then build `experiments/ctv2_observer_registry/` with versioned authenticated registry snapshots, key rotation/revocation, rollback protection, exact snapshot-bound quorum evaluation, historical replay, restart/tamper checks, and an unsafe self-asserted-membership seed. Run deterministic tests and a separate authority audit before integration.

## Backlog

- #104 / LAB-055 — authenticated observer registry lifecycle and quorum-membership conformance — READY.
- Reliable gossip transport, Byzantine consensus, and fork prevention remain out of scope unless evidence makes them the next correctness bottleneck.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
