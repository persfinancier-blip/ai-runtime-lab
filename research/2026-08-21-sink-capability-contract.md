# LAB-073 — Sink idempotency/reconciliation capability contract

## Audit findings

The first slice stored `observed=True` and `behavioral_probe_passed=True` inside the same structural object an adapter could construct. That was forgeable. The corrected model separates an adapter/provider **claim** from a trusted probe authority. The authority behaviorally tests the exact claim and authenticates its digest plus probe generation. Planner and broker verify that attestation before deriving retry authority. A changed claim, stale probe generation, or forged attestation fails closed.

The audit also found that `retention_seconds=None` was accidentally treated as an infinite idempotency window. Unknown retention is now conservative `NO_AUTOMATIC_RETRY`. Clock rollback relative to key creation also fails closed.

A later audit found a subtler same-generation mutation bug: a plan created under a short finite retention could be revalidated against a newly attested claim with the same capability generation but a longer retention, silently extending retry authority. Plans now bind the exact authenticated claim digest as well as capability/probe generations. Any same-generation claim mutation invalidates the plan rather than changing its retry horizon.

Behavioral probing can test same-key deduplication, request binding and reconciliation. It cannot cheaply wait out a provider's documented retention horizon, so a finite retention claim is separately sourced contract material bound into the authenticated claim.

## Policy

- `SAFE_RETRY_RECONCILE`: authenticated, behaviorally verified, stable request-bound idempotency, finite live retention, and reconciliation.
- `SAFE_RETRY_IDEMPOTENT_ONLY`: the same without reconciliation; an already-UNKNOWN operation is not automatically repeated inside the generic broker.
- `NO_AUTOMATIC_RETRY`: non-idempotent, unbound, expired, unknown-retention, unauthenticated or failed-probe sink.
- `READ_ONLY`: no mutating effect.

Plan identity is part of the authority boundary. Capability generation, exact claim digest, or probe generation changes invalidate it, and a later stronger capability cannot silently upgrade an already-issued plan.

## Boundary

This remains a reference contract, not universal exactly-once delivery. External systems with no stable idempotency identity or no reconciliation path remain ambiguous after timeout-after-commit. The HMAC probe attestation models an authenticity boundary, not a production key-management service.
