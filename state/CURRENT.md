# Current Lab State

Last updated: 2026-08-20

## Active objective

LAB-060 — bound restart verification cost with authenticated history checkpoints without weakening LAB-059 bootstrap→head integrity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-059.
- Completed Issue #109 / LAB-059.
- Merged PR #110 / LAB-059 as `3eb014cbad28cc590b02d61dd7cb25a3708db9d0`.
- Next: Issue #111 / LAB-060 — READY.
- Active PR: none.

## Last completed step

LAB-059 added exact durable threshold proof material for every winning root/recovery transition and a restart verifier that reconstructs bootstrap→head, reloads historical authorities by content ID, reconstructs canonical payloads, re-verifies historical threshold signatures, recomputes transition digests, and requires the derived terminal pair to equal the SQL head. `UNKNOWN` reconciliation now performs full history verification before returning persisted evidence.

Corrected deterministic suite passed 9/9. The unsafe evidence-trusting baseline failed as expected after a predecessor row was tampered while its JSON proof remained plausible. Compileall passed. Remote `protocol.py` and corrected-test Git blob SHAs matched the locally executed bytes. PR #110 was remote patch-audited and squash-merged.

## Evidence produced

- `experiments/transition_history_integrity/protocol.py`
- `experiments/transition_history_integrity/tests/test_protocol.py`
- `experiments/transition_history_integrity/tests/unsafe_evidence_expected_failure.py`
- `experiments/transition_history_integrity/README.md`
- `research/2026-08-20-transition-history-integrity.md`
- Corrected suite: 9/9 passed.
- Unsafe seed: failed as expected.
- Compileall: passed.
- Branch protocol blob SHA `2c983c2a0b4ec00bb01f2837e382b6857a6eca20`; corrected-test blob SHA `c5b6b5258246124224eb73d0f8ab5259e39337be`; both matched locally executed sources.

## Known blockers / constraints

- No active blocker.
- Full bootstrap→head replay is intentionally O(N) in transition history length.
- Internal history verification cannot distinguish a complete rollback to an older internally valid database snapshot; LAB-034–037 external monotonic-anchor work remains the authority for whole-store rollback detection.
- Local SQL history integrity is not distributed consensus/fork prevention across independently writable replicas.

## Exact next action

Start Issue #111 / LAB-060. Build authenticated history checkpoints only from fully verified prefixes. Bind checkpoint sequence, derived root/recovery IDs, prefix commitment, schema/protocol version and external-anchor identity. Verify checkpoint authenticity before replaying only the suffix, and prove equivalence against full replay. Inject checkpoint tamper, substitution, rollback, head mismatch and skipped-suffix failures. Keep whole-store freshness delegated to LAB-034–037 rather than duplicating anchor protocols.

## Backlog

- #111 / LAB-060 — authenticated history checkpoints and bounded restart verification — READY.
- Reliable gossip transport, Byzantine consensus, and fork prevention remain out of scope unless evidence makes them the next correctness bottleneck.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
