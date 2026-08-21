# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-073 — replace LAB-072's trusted external-sink idempotency/reconciliation assumption with an explicit observed capability contract and fail-closed UNKNOWN policy.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-072.
- LAB-072 PR #136 squash-merged as `4f2b58abd08e80af175d5e75e29439de44f6d56a`; Issue #135 DONE.
- Active Issue #137 / LAB-073 — IN_PROGRESS.
- Active branch: `lab/073-sink-capability-contract`.
- Draft PR #138 `[LAB-073] Sink idempotency/reconciliation capability contract`.
- Current PR head at publication: `38b44c61f4a3c4bb538020fea702c75fd520c4db`.

## Last completed step

The previous integration-only LAB-072 blocker cleared: the normal draft→ready operation succeeded on the unchanged audited HEAD, followed by a normal squash merge.

No open issues remained, so the next correctness bottleneck was selected from LAB-072's explicit boundary: its strong timeout/UNKNOWN behavior requires a concrete sink to provide stable request-bound idempotency and, for automatic reconciliation, durable lookup of a committed result. LAB-073 turns this from an adapter assumption into a versioned capability contract.

A first deterministic reference prototype was implemented and published. Policy is derived only from observed, behaviorally verified capabilities; adapter/tool self-description alone cannot upgrade retry authority. Capability generation changes invalidate stale plans, known idempotency retention expiry downgrades retry authority, and a later stronger capability observation cannot silently upgrade an already-issued plan.

## Evidence produced

- `experiments/sink_capability_contract/protocol.py`
- `experiments/sink_capability_contract/tests/test_protocol.py`
- `experiments/sink_capability_contract/tests/unsafe_generic_retry_expected_failure.py`
- `experiments/sink_capability_contract/README.md`
- `research/2026-08-21-sink-capability-contract.md`
- Local corrected suite before publication: 12/12 passed.
- Unsafe generic-retry seed failed as intended because timeout-after-commit followed by a new retry key produced 2 side effects instead of 1.
- compileall passed.
- Primary-source evidence recorded from current AWS idempotency guidance, AWS Durable Execution replay/idempotency guidance, and Google Cloud idempotent-vs-non-idempotent retry guidance.

## Known blockers / constraints

- No owner-level blocker.
- PR #138 is intentionally draft pending remote patch audit and exact published-source revalidation.
- The first slice uses a deterministic simulated sink; it does not yet prove a generic behavioral-probe interface cannot be forged by adapter-returned metadata. The audit should specifically examine the trust boundary between probe execution and capability issuance.
- `SAFE_RETRY_IDEMPOTENT_ONLY` intentionally does not auto-retry an already-UNKNOWN outcome when reconciliation is unavailable; a stable key makes duplicate processing less likely within its retention window but does not prove whether the first attempt committed.
- Idempotency-key retention expiry is a real semantic boundary: after expiry, the generic broker must not assume the old key still deduplicates.
- This work does not claim universal exactly-once delivery or distributed transactions.

## Exact next action

Re-fetch draft PR #138 at HEAD `38b44c61f4a3c4bb538020fea702c75fd520c4db`, fetch the full patch and perform a separate security/correctness audit. Focus on whether `observed=True` / `behavioral_probe_passed=True` can be structurally forged, whether retention-window boundaries are conservative enough, and whether an idempotent-but-non-reconcilable sink can ever safely auto-retry after an UNKNOWN outcome. Fix any findings in-branch, then reconstruct exact published bytes and rerun LAB-073 corrected/unsafe suites before considering ready/merge.

## Backlog

- #137 / LAB-073 — sink idempotency/reconciliation capability contract — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
