# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-074 — integrate LAB-073's authenticated sink capability/retry contract directly into LAB-072's transactional broker journal so durable request state and external retry authority cannot diverge across concurrency, rotation, UNKNOWN outcomes, or restart.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-073.
- Completed Issue #137 / LAB-073.
- Merged PR #138 as `46effa2330bf970f25a712fc0fbf03452b2592ee`.
- Next: Issue #139 / LAB-074 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

A final remote audit of LAB-073 found a third material defect after the earlier forgeable-attestation and unknown-retention fixes: a new valid attestation with the same capability generation but a longer retention could silently extend an already-issued plan's retry horizon. The plan now binds the exact authenticated capability claim digest as well as capability/probe generations; any same-generation claim mutation invalidates the plan.

Exact published executable bytes were reconstructed and run locally after the fix. The corrected suite passed, the unsafe generic-retry seed still duplicated the side effect as intended, and the PR was marked ready and squash-merged.

## Evidence produced

- LAB-073 protocol blob: `fc05d27d5512ece585d7d6313e079ae6a234f737`.
- LAB-073 corrected-tests blob: `55e42d5027fbbe1c7b66b11f08162765eba90a25`.
- LAB-073 unsafe-seed blob: `d6513bcfb13e0cafe1dee1fec182e60dbc40f858`.
- Corrected exact-source suite: 18/18 passed.
- Unsafe generic-retry seed failed as intended with 2 side effects instead of 1.
- compileall passed.
- PR #138 squash-merged as `46effa2330bf970f25a712fc0fbf03452b2592ee`.
- Issue #139 / LAB-074 created as the next concrete cross-layer integration task.

## Known blockers / constraints

- No active blocker.
- LAB-073 behaviorally verifies same-key deduplication, request binding and reconciliation, but finite provider retention remains separately sourced authenticated contract material rather than something the fast probe can directly wait out.
- `SAFE_RETRY_IDEMPOTENT_ONLY` intentionally does not automatically execute a second attempt after UNKNOWN when reconciliation is unavailable.
- Universal exactly-once delivery remains a non-goal.

## Exact next action

Start Issue #139 / LAB-074. Inspect the real LAB-072 transactional journal and LAB-073 protocol on `main`, create a feature branch, and extend the existing durable request rows rather than creating a parallel state machine. Persist the exact LAB-073 capability generation, claim digest, probe generation, policy/key creation time and effect identity with every reservation. Revalidate current authenticated capability before new execution/reconciliation, while preserving exact already-committed reconciliation across later capability rotation without a duplicate effect. Add the full concurrency/restart/retention/UNKNOWN failure matrix from Issue #139, run LAB-072 and LAB-073 regressions, audit independently, then integrate only if the combined authority boundary remains fail-closed.

## Backlog

- #139 / LAB-074 — transactional broker + authenticated sink-capability integration — READY.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
